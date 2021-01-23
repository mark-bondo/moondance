import requests
import sys, os, base64, datetime, hashlib, hmac 
import json
import urllib
import time
import collections
import contextlib
import psycopg2
from common import get_table_columns, insert_data, escape_value
from dotenv import load_dotenv

load_dotenv()

class Amazon_API(object):
    def __init__(self):
        self.access_token_url = "https://api.amazon.com/auth/o2/token"
        self.access_token = None
        self.service = "execute-api"
        self.host = "sellingpartnerapi-na.amazon.com"
        self.region = "us-east-1"
        self.user_agent = "MoonDance Reporting Tool/1.0 (Language=Python/3.7.6; Platform=Windows/10)"
        self.current_timestamp =  now.strftime("%Y-%m-%d %H%M%S")

        self.db_string = os.getenv("DB_STRING")
        self.amazon_client_id =  os.environ.get("AMAZON_CLIENT_IDENTIFIER2")
        self.amazon_client_secret =  os.environ.get("AMAZON_CLIENT_SECRET2")
        self.amazon_refresh_token = os.environ.get("AMAZON_REFRESH_TOKEN2")
        self.aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")

    def process_data(self, command, request_parameters):
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
                "api_url": "/catalog/v0/items/",
                "request_parameters": request_parameters
            }
        }

        if command in self.object_map:
            self.object_dd = self.object_map[command]
            self.object_dd.update({
                # "table_columns": get_table_columns(self.db_string, self.object_dd["table_name"]),
                "file_name": "amazon_orders_{}.tsv".format(self.current_timestamp.replace(":", "-")),
                "api_url_formatted": self.object_dd["api_url"]
            })
        else:
            raise "{} is not a valid command".format(command)

        self.get_access_token()

        if command == "sales_order_lines":
            order_lines = self.get_orders()

            for o in order_lines:
                self.object_dd["api_url_formatted"] = self.object_dd["api_url"].format(o["AmazonOrderId"])
                self.build_parameters_string()
                self.build_headers()

                extra_context = {
                    "AmazonOrderId": o["AmazonOrderId"],
                    "LastUpdateDate": o["LastUpdateDate"],
                }
                self.get_data(extra_context)
                insert_data(self.object_dd, self.db_string, self.row_count)
                time.sleep(1.5)
        # else:
        #     insert_data(self.object_dd, self.db_string, self.row_count)

    def get_orders(self):
        with contextlib.closing(psycopg2.connect(self.db_string)) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                sql = """
                    SELECT
                        COALESCE(JSONB_AGG(json), '[]'::JSONB) as order_json
                    FROM (
                        SELECT
                            (select row_to_json(_) from (select o."AmazonOrderId", o."LastUpdateDate")  as _) as json
                        FROM
                            public.amazon_sales_order o LEFT JOIN
                            public.amazon_sales_order_line ol ON o."AmazonOrderId" = ol."AmazonOrderId"
                        WHERE
                            ol."LastUpdateDate" IS NULL OR
                            ol."LastUpdateDate" <> o."LastUpdateDate"
                        LIMIT
                            1000
                    ) sub 
                    ;
                """
                cursor.execute(sql)
                return cursor.fetchall()[0][0]

    def get_access_token(self):
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
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

        method = 'GET'
        algorithm = 'AWS4-HMAC-SHA256'
        signed_headers = 'host;x-amz-date'
        payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
        
        # canonical_uri = '/orders/v0/orders/' 
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
                print("fetching order batch starting {}\n{}\n{}".format(
                    self.row_count,
                    self.request_url,
                    "x" * 50
                ))

                r = requests.get(url=self.request_url, headers=self.headers)
                print(r.text)
                json_response = r.json()

                payload = json_response["payload"][self.object_dd["json_set"]]

                for p in payload:
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

                self.row_count += len(payload)
                if next_token in json_response["payload"]:
                    # add in next parameter
                    self.object_dd["request_parameters"][next_token] = json_response["payload"][next_token]
                    self.build_parameters_string()
                    self.build_headers()
                else:
                    break


if __name__ == "__main__":
    start_interval = {"days": 1}
    end_interval = {"minutes": 3}
    now = datetime.datetime.utcnow()

    MarketplaceIds = "ATVPDKIKX0DER"
    LastUpdatedAfter = (now - datetime.timedelta(**start_interval)).isoformat()
    LastUpdatedBefore = (now - datetime.timedelta(**end_interval)).isoformat()
    # LastUpdatedBefore = "2021-01-19T20:58:11.858899"
    # LastUpdatedAfter = "2019-12-31T20:56:11.858899"

    amazon = Amazon_API()
    # amazon.process_data(
    #     command="sales_orders",
    #     request_parameters={
    #         "MarketplaceIds": MarketplaceIds,
    #         "LastUpdatedBefore": LastUpdatedBefore,
    #         "LastUpdatedAfter": LastUpdatedAfter,
    # })

    # amazon.process_data(
    #     command="sales_order_lines",
    #     request_parameters={
    #         "MarketplaceIds": MarketplaceIds,
    # })

    amazon.process_data(
        command="catalog",
        request_parameters={
            "MarketplaceIds": MarketplaceIds,
    })