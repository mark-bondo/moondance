import requests
import sys, os, base64, datetime, hashlib, hmac 
import json
import urllib
import collections


class Amazon_API(object):
    def __init__(self, request_parameters):
        self.access_token_url = "https://api.amazon.com/auth/o2/token"
        self.access_token = None
        self.service = "execute-api"
        self.host = "sellingpartnerapi-na.amazon.com"
        self.region = "us-east-1"
        self.user_agent = "MoonDance Reporting Tool/1.0 (Language=Python/3.7.6; Platform=Windows/10)"
        self.request_parameters = {}

        self.amazon_client_id =  os.environ.get("AMAZON_CLIENT_IDENTIFIER2")
        self.amazon_client_secret =  os.environ.get("AMAZON_CLIENT_SECRET2")
        self.amazon_refresh_token = os.environ.get("AMAZON_REFRESH_TOKEN2")
        self.aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")

        self.get_access_token()
        self.build_parameters_string(request_parameters)
        self.build_headers()

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
        canonical_uri = '/orders/v0/orders' 
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
        print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        print('Request URL = ' + self.request_url)
        r = requests.get(
            url=self.request_url,
            headers=self.headers
        )

        order_count = 0

        with open("orders.txt", "w") as w:
            w.write(r.text)

            json_response = r.json()
            nextToken ="NextToken"
            order_count == len(json_response["payload"]["Orders"])

            while nextToken in json_response["payload"]:
                # add in next parameter
                self.request_parameters[nextToken] = json_response["payload"][nextToken]
                self.build_parameters_string(self.request_parameters)

                # rebuild headers
                self.build_headers()
                print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
                print('Request URL = ' + self.request_url)

                r = requests.get(
                    url=self.request_url,
                    headers=self.headers
                )
                json_response = r.json()
                orders = json_response["payload"]["Orders"]
                order_count += len(orders)
                # w.write(r.text)
                print("fetched {} orders so far".format(order_count))

                headers = "\t".join(["{}".format(k) for k, v in orders[0]]
                )

                for k, v in orders.items():
                    row = []

                    for field in self.object_dd["table_columns"]:
                        if field in order:
                            v = order[field]
                            if v is None:
                                v = ""
                            elif isinstance(v, (list, dict)):
                                v = json.dumps(v)

                            v = self.escape_value(str(v))
                            row.append(v)
                        else:
                            # print("{} id is missing key {}".format(order["id"], field))
                            row.append("")

                    line = "{}\n".format("\t".join(row))
                    w.write(line)
                    self.row_count+=1


if __name__ == "__main__":
    interval = {"days": 30}
    start_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()
        # datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    request_parameters = {
        # "details": "true",
        # "granularityType": "Marketplace",
        # "granularityId": "ATVPDKIKX0DER",
        "CreatedAfter": start_datetime,
        "MarketplaceIds": "ATVPDKIKX0DER"
    }

    amazon = Amazon_API(request_parameters)
    amazon.get_data()