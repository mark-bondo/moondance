#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import datetime
import json
import psycopg2
import os
import contextlib

escape_list = [
    ("\b", "\\b"),
    ("\n", "\\n"),
    ("\r", "\\r"),
    ("\t", "\\t")
]


class ShopifyAPI(object):
    def __init__(self, start_datetime):
        self.username = os.environ.get("SHOPIFY_USERNAME")
        self.password = os.environ.get("SHOPIFY_PASSWORD")
        self.db_string = os.environ.get("DB_STRING")
        self.shopify_url = os.environ.get("SHOPIFY_URL")
        self.start_datetime = start_datetime
        self.object_map = {
            "sales_orders": {
                "table_name": "sales_orders_shopify",  
                "json_set": "orders",
                "api_url": "2020-10/orders.json",
                "api_params": {
                    "updated_at_min": self.start_datetime,
                    "status": "any"
                }
            },
            "products": {
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
                "table_columns": self.fetch_table_columns(),
                "file_name": "{}.tsv".format(self.object_dd["table_name"]),
            })
        else:
            raise "{} is not a valid command".format(command)

        self.get_data()
        self.insert_data()

    def fetch_table_columns(self):
        with contextlib.closing(psycopg2.connect(self.db_string)) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                sql = """
                    SELECT
                        *
                    FROM
                        staging.{}
                    WHERE
                        0=1
                    ;
                """.format(self.object_dd["table_name"])
                cursor.execute(sql)
        return [x[0] for x in cursor.description]

    def escape_value(self, value):
        for e in escape_list:
            if e[0] in value:
                value = value.replace(e[0], e[1])

        return value

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

                            v = self.escape_value(str(v))
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

    def insert_data(self):
        primary_key_list = ["id"]

        with open("templates/sql/{}.sql".format("pk_append"), "r") as f:
            sql = f.read() % {
                "schema": "public",
                "table_name": self.object_dd["table_name"],
                "column_select": ",".join([x for x in self.object_dd["table_columns"]]),
                "delim": "\t",
                "date_append_column": "datetime_updated",
                "primary_key_join": " AND ".join(['a."{0}"=b."{0}"'.format(x) for x in primary_key_list if primary_key_list])
            }

        with contextlib.closing(psycopg2.connect(self.db_string)) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                print("{}: starting data load for {} order lines".format(self.object_dd["table_name"], self.row_count))
                print(sql)
                cursor.copy_expert(sql, open(self.object_dd["file_name"], "r", encoding="utf-8"))

            conn.commit()
            os.remove(self.object_dd["file_name"])
            print("{}: completed data load".format(self.object_dd["table_name"]))


if __name__ == "__main__":
    interval = {"days": 60}
    start_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()
    # end_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()

    shopify = ShopifyAPI(start_datetime)
    shopify.process_data(command="products")
    shopify.process_data(command="sales_orders")