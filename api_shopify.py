#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import datetime
import json
import psycopg2
import os
import contextlib
from dotenv import load_dotenv
from common import get_table_columns, escape_value, insert_data

load_dotenv()


class ShopifyAPI(object):
    def __init__(self, start_datetime):
        self.username = os.getenv("SHOPIFY_USERNAME")
        self.password = os.getenv("SHOPIFY_PASSWORD")
        self.db_string = os.getenv("DB_STRING")
        self.shopify_url = os.getenv("SHOPIFY_URL")
        self.start_datetime = start_datetime
        self.object_map = {
            "sales_orders": {
                "pk_list": ["id"],
                "table_name": "shopify_sales_order",
                "json_set": "orders",
                "api_url": "2020-10/orders.json",
                "api_params": {
                    "updated_at_min": self.start_datetime,
                    "status": "any"
                }
            },
            "products": {
                "pk_list": ["id"],
                "table_name": "shopify_product",
                "json_set": "products",
                "api_url": "2020-10/products.json",
                "api_params": {
                    "updated_at_min": self.start_datetime
                }
            }
        }

    def process_data(self, command):
        if command in self.object_map:
            self.object_dd = self.object_map[command]
            self.object_dd.update({
                "table_columns": get_table_columns(self.db_string, self.object_dd["table_name"]),
                "file_name": "{}.tsv".format(self.object_dd["table_name"]),
            })
        else:
            raise "{} is not a valid command".format(command)

        self.get_data()
        insert_data(self.object_dd, self.db_string, self.row_count)

    def get_data(self):
        with open(self.object_dd["file_name"], encoding="utf-8", mode="w") as w:
            self.row_count = 0
            order_url = "https://{}:{}@{}/admin/api/{}?{}".format(
                self.username,
                self.password,
                self.shopify_url,
                self.object_dd["api_url"],
                "&".join(["{}={}".format(k, v) for k, v in self.object_dd["api_params"].items()])
            )

            w.write("\t".join(self.object_dd["table_columns"]))
            w.write("\n")

            while True:
                print("fetching order batch starting {}".format(self.row_count))
                print(order_url)
                print("x" * 50)
                response = requests.get(order_url)
                json_string = response.json()

                for order in json_string[self.object_dd["json_set"]]:
                    row = []

                    for field in self.object_dd["table_columns"]:
                        if field in order:
                            v = order[field]
                            if v is None:
                                v = ""
                            elif isinstance(v, (list, dict)):
                                v = json.dumps(v)

                            v = escape_value(str(v))
                            row.append(v)
                        else:
                            # print("{} id is missing key {}".format(order["id"], field))
                            row.append("")

                    line = "{}\n".format("\t".join(row))
                    w.write(line)
                    self.row_count+=1

                next_page = response.headers["link"] if "link" in response.headers else None
                
                if next_page and 'rel="next"' in next_page:
                    next_page = next_page.split(",")[-1]
                    order_url = next_page.replace("<", "").replace("https://", "https://{}:{}@".format(self.username, self.password)).split(">")[0]
                else:
                    break


if __name__ == "__main__":
    interval = {"days": 1}
    start_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()
    # end_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()

    shopify = ShopifyAPI(start_datetime)
    shopify.process_data(command="products")
    shopify.process_data(command="sales_orders")