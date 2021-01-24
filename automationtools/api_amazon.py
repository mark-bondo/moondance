import requests
import sys, os, base64, datetime, hashlib, hmac 
import json
import urllib
import time
import collections
import contextlib
import psycopg2
from datetime import datetime
from common import get_table_columns, insert_data, escape_value
from dotenv import load_dotenv

load_dotenv()

class Amazon_API(object):
    def __init__(self, logger):
        self.logger = logger
        self.access_token_url = "https://api.amazon.com/auth/o2/token"
        self.access_token = None
        self.service = "execute-api"
        self.host = "sellingpartnerapi-na.amazon.com"
        self.region = "us-east-1"
        self.user_agent = "MoonDance Reporting Tool/1.0 (Language=Python/3.7.6; Platform=Windows/10)"
        self.current_timestamp =  datetime.now().strftime("%Y-%m-%d %H%M%S")

        self.db_string = os.getenv("DB_STRING")
        self.amazon_client_id =  os.environ.get("AMAZON_CLIENT_IDENTIFIER")
        self.amazon_client_secret =  os.environ.get("AMAZON_CLIENT_SECRET")
        self.amazon_refresh_token = os.environ.get("AMAZON_REFRESH_TOKEN")
        self.aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")

    def process_data(self, command, request_parameters):
        self.command = command
        self.object_map = {
            "sales_orders": {
                "pk_list": ["AmazonOrderId"],
                "table_name": "amazon_sales_order",
                "json_set": "Orders",
                "api_url": "/orders/v0/orders",
                "request_parameters": request_parameters
            },
            "sales_order_lines": {
                "pk_list": ["OrderItemId"],
                "table_name": "amazon_sales_order_line",
                "json_set": "OrderItems",
                "api_url": "/orders/v0/orders/{}/orderItems",
                "request_parameters": request_parameters
            },
            "catalog": {
                "pk_list": ["id"],
                "table_name": "amazon_catalog",
                "json_set": "CatalogItems",
                "api_url": "/catalog/v0/items/B002UD6C16",
                "request_parameters": request_parameters
            }
        }

        self.logger.info("sync amazon {}: getting table columns".format(self.command))
        if command in self.object_map:
            self.object_dd = self.object_map[command]
            self.object_dd.update({
                "table_columns": get_table_columns(self.db_string, self.object_dd["table_name"]),
                "file_name": "automationtools/data/{}_{}.tsv".format(
                    self.object_dd["table_name"], 
                    self.current_timestamp.replace(":", "-")
                ),
                "api_url_formatted": self.object_dd["api_url"]
            })
        else:
            raise "{} is not a valid command".format(command)

        self.logger.info("sync amazon {}: getting access token".format(self.command))
        self.refresh_access_token()

        if command == "sales_order_lines":
            self.logger.info("sync amazon {}: getting order lines to sync".format(self.command))
            order_lines = self.get_orders()
            self.logger.info("sync amazon {}: retrieved {} order lines to sync".format(self.command, len(order_lines)))

            error_count = 0
            for i, o in enumerate(order_lines):
                try:
                    extra_context = {
                        "AmazonOrderId": o["AmazonOrderId"],
                        "LastUpdateDate": o["LastUpdateDate"],
                    }

                    self.object_dd["api_url_formatted"] = self.object_dd["api_url"].format(o["AmazonOrderId"])
                    self.sync_data(extra_context)
                except Exception:
                    if error_count <= 1:
                        self.logger.warning("sync amazon {}: failed getting order lines, getting new refresh token".format(self.command), exc_info=1)
                        self.refresh_access_token()
                        self.sync_data(extra_context)

                        error_count+=1
                    else:
                        self.logger.error("sync amazon {}: failed getting order lines {} times, exiting program".format(self.command, error_count), exc_info=1)
                        break
        else:
            self.sync_data()

    def sync_data(self, extra_context={}):
        self.logger.info("sync amazon {}: creating headers".format(self.command))
        self.build_parameters_string()
        self.build_headers()
        self.get_data(extra_context)

        self.logger.info('sync amazon {}: inserting {} rows into "{}"'.format(self.command, self.row_count, self.object_dd["table_name"]))
        insert_data(self.object_dd, self.db_string)

    def get_orders(self):
        with contextlib.closing(psycopg2.connect(self.db_string)) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                sql = """
                    SELECT
                        COALESCE(JSONB_AGG(json), '[]'::JSONB) as order_json
                    FROM (
                        SELECT
                            (select row_to_json(_) from (SELECT DISTINCT o."AmazonOrderId", o."LastUpdateDate")  as _) as json
                        FROM
                            public.amazon_sales_order o LEFT JOIN
                            public.amazon_sales_order_line ol ON o."AmazonOrderId" = ol."AmazonOrderId"
                        WHERE
                            ol."LastUpdateDate" IS NULL OR
                            ol."LastUpdateDate" <> o."LastUpdateDate"
                        LIMIT
                            10000
                    ) sub 
                    ;
                """
                cursor.execute(sql)
                return cursor.fetchall()[0][0]

    def refresh_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "client_id": self.amazon_client_id,
            "client_secret": self.amazon_client_secret,
            "refresh_token": self.amazon_refresh_token,
        }
        response = requests.post(
            url=self.access_token_url,
            data=json.dumps(data),
        )

        access_json = response.json()
        self.access_token = access_json["access_token"]

    def build_parameters_string(self):
        # encode URL parameters and create string
        self.object_dd["request_parameters"] = collections.OrderedDict(sorted(self.object_dd["request_parameters"].items()))
        self.request_parameter_string = "&".join(["{}={}".format(urllib.parse.quote_plus(k), urllib.parse.quote_plus(v)) for k, v in self.object_dd["request_parameters"].items()])

    def sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(self, key, dateStamp, regionName, serviceName):
        kDate = self.sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = self.sign(kDate, regionName)
        kService = self.sign(kRegion, serviceName)
        kSigning = self.sign(kService, 'aws4_request')
        return kSigning

    def build_headers(self):
        t = datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

        method = 'GET'
        algorithm = 'AWS4-HMAC-SHA256'
        signed_headers = 'host;x-amz-date'
        payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
        
        canonical_uri = self.object_dd["api_url_formatted"]
        canonical_headers = 'host:' + self.host + '\n' + 'x-amz-date:' + amzdate + '\n'
        
        payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
        canonical_request = method + '\n' + canonical_uri + '\n' + self.request_parameter_string + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
        credential_scope = datestamp + '/' + self.region + '/' + self.service + '/' + 'aws4_request'
        
        string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

        signing_key = self.getSignatureKey(self.aws_secret_key, datestamp, self.region, self.service)
        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
        authorization_header = algorithm + ' ' + 'Credential=' + self.aws_access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
        self.request_url = "https://{}{}?{}".format(self.host, canonical_uri, self.request_parameter_string)
        self.headers = {
            'x-amz-date': amzdate,
            "x-amz-access-token": self.access_token,
            "user-agent": self.user_agent,
            'Authorization': authorization_header,
        }

    def get_data(self, extra_context={}):
        self.row_count = 0
        next_token = "NextToken"

        with open(self.object_dd["file_name"], "w") as w:
            w.write("\t".join(self.object_dd["table_columns"]))
            w.write("\n")

            while True:
                self.logger.info('sync amazon {}: getting data from "{}"'.format(self.command, self.request_url))
                r = requests.get(url=self.request_url, headers=self.headers)
                json_response = r.json()

                try:
                    json_data = json_response["payload"][self.object_dd["json_set"]]
                except KeyError:
                    print(r.text)

                self.row_count += len(json_data)
                self.logger.info("sync amazon {}: fetched {} rows".format(self.command, len(json_data)))
                for p in json_data:
                    row = []

                    for field in self.object_dd["table_columns"]:
                        if field in p:
                            v = p[field]
                            if v is None:
                                v = ""
                            elif isinstance(v, (list, dict)):
                                v = json.dumps(v)

                            v = escape_value(str(v))
                            row.append(v)
                        elif field in extra_context:
                            row.append(extra_context[field])
                        else:
                            row.append("")

                    line = "{}\n".format("\t".join(row))
                    w.write(line)

                if next_token in json_response["payload"]:
                    # add in next parameter
                    self.object_dd["request_parameters"][next_token] = json_response["payload"][next_token]
                    self.build_parameters_string()
                    self.build_headers()
                else:
                    break
                
                time.sleep(1.5)

            self.logger.info('sync amazon {}: written {} rows to file "{}"'.format(self.command, self.row_count, self.object_dd["file_name"]))


if __name__ == "__main__":
    pass