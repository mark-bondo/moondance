import requests
import sys, os, base64, datetime, hashlib, hmac 
import json
import urllib
import collections
from common import get_table_columns, insert_data, escape_value
from dotenv import load_dotenv

load_dotenv()

class Amazon_API(object):
    def __init__(self, request_parameters):
        self.access_token_url = "https://api.amazon.com/auth/o2/token"
        self.access_token = None
        self.service = "execute-api"
        self.host = "sellingpartnerapi-na.amazon.com"
        self.region = "us-east-1"
        self.user_agent = "MoonDance Reporting Tool/1.0 (Language=Python/3.7.6; Platform=Windows/10)"
        self.request_parameters = {}
        self.current_timestamp = 'xxxxxxxx'
        self.object_map = {
            "sales_orders": {
                "pk_list": ["AmazonOrderId"],
                "table_name": "amazon_sales_order",
                "json_set": "Orders",
                "api_url": "/orders/v0/orders",
                "api_params": {
                    "MarketplaceIds": "ATVPDKIKX0DER"
                }
            },
            "sales_order_lines": {
                "pk_list": ["OrderItemId"],
                "table_name": "amazon_sales_order_line",
                "json_set": "OrderItems",
                "api_url": "/orders/v0/orders/{}/orderItems".format(request_parameters["AmazonOrderId"]),
                "api_params": {
                    "MarketplaceIds": "ATVPDKIKX0DER"
                }
            },
            "products": {
                "pk_list": ["id"],
                "table_name": "amazon_product",
                "json_set": "products",
                "api_url": "2020-10/products.json",
                "api_params": {
                    "updated_at_min": self.current_timestamp
                }
            }
        }
        self.db_string = os.getenv("DB_STRING")
        self.amazon_client_id =  os.environ.get("AMAZON_CLIENT_IDENTIFIER2")
        self.amazon_client_secret =  os.environ.get("AMAZON_CLIENT_SECRET2")
        self.amazon_refresh_token = os.environ.get("AMAZON_REFRESH_TOKEN2")
        self.aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")

    def process_data(self, command):
        if command in self.object_map:
            self.object_dd = self.object_map[command]
            self.object_dd.update({
                "table_columns": get_table_columns(self.db_string, self.object_dd["table_name"]),
                "file_name": "amazon_orders_{}.tsv".format(self.current_timestamp.replace(":", "-"))
            })
        else:
            raise "{} is not a valid command".format(command)

        self.get_access_token()
        self.build_parameters_string(request_parameters)
        self.build_headers()
        self.get_data()
        insert_data(self.object_dd, self.db_string, self.row_count)

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

    def build_parameters_string(self, request_parameters):
        # encode URL parameters and create string
        self.request_parameters = collections.OrderedDict(sorted(request_parameters.items()))
        self.request_parameter_string = "&".join(["{}={}".format(urllib.parse.quote_plus(k), urllib.parse.quote_plus(v)) for k, v in self.request_parameters.items()])

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
        canonical_uri = self.object_dd["api_url"]
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

    def get_data(self):
        self.row_count = 0
        next_token = "NextToken"

        with open(self.object_dd["file_name"], "w") as w:
            w.write("\t".join(self.object_dd["table_columns"]))
            w.write("\n")

            while True:
                print("fetching order batch starting {}".format(self.row_count))
                print(self.request_url)
                print("x" * 50)

                r = requests.get(url=self.request_url, headers=self.headers)
                json_response = r.json()
                # print( json_response["payload"])
                payload = json_response["payload"][self.object_dd["json_set"]]

                for p in payload:
                    print(p)
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
                        else:
                            row.append("")

                    line = "{}\n".format("\t".join(row))
                    w.write(line)

                self.row_count += len(payload)
                if next_token in json_response["payload"]:
                    # add in next parameter
                    self.request_parameters[next_token] = json_response["payload"][next_token]
                    self.build_parameters_string(self.request_parameters)
                    self.build_headers()
                else:
                    break


if __name__ == "__main__":
    start_interval = {"days": 3}
    end_interval = {"minutes": 3}
    now = datetime.datetime.utcnow()

    # start_datetime = (now - datetime.timedelta(**start_interval)).isoformat()
    # end_datetime = (now - datetime.timedelta(**end_interval)).isoformat()
    LastUpdatedBefore = "2021-01-19T20:58:11.858899"
    LastUpdatedAfter = "2019-12-31T20:56:11.858899"

        # datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    request_parameters = {
        # "details": "true",
        # "granularityType": "Marketplace",
        # "granularityId": "ATVPDKIKX0DER",
        # "LastUpdatedBefore": LastUpdatedBefore,
        # "LastUpdatedAfter": LastUpdatedAfter,
        "MarketplaceIds": "ATVPDKIKX0DER",
        "AmazonOrderId": "111-7288587-2982629"
    }

    amazon = Amazon_API(request_parameters)
    amazon.process_data("sales_order_lines")