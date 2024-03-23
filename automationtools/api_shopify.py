#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import json
import psycopg2
import os
import time
import contextlib
from datetime import datetime
from dotenv import load_dotenv
from common import get_table_columns, escape_value, insert_data

load_dotenv()


class Shopify_API(object):
    def __init__(self, logger):
        self.logger = logger
        self.current_timestamp = datetime.now().strftime("%Y-%m-%d %H%M%S")
        self.username = os.getenv("SHOPIFY_USERNAME")
        self.password = os.getenv("SHOPIFY_PASSWORD")
        self.db_string = os.getenv("DB_STRING")
        self.shopify_url = os.getenv("SHOPIFY_URL")
        self.extra_context = {}

    def process_data(self, command, request_parameters):
        self.command = command
        self.object_map = {
            "sales_orders": {
                "pk_list": ["id"],
                "table_name": "shopify_sales_order",
                "schema": "shopify",
                "json_set": "orders",
                "api_url": "2024-01/orders.json",
                "request_parameters": request_parameters,
            },
            "products": {
                "pk_list": ["id"],
                "table_name": "shopify_product",
                "schema": "shopify",
                "json_set": "products",
                "api_url": "2024-01/products.json",
                "request_parameters": request_parameters,
            },
            "sync_shopify_order_events": {
                "pk_list": ["id"],
                "table_name": "shopify_order_events",
                "schema": "shopify",
                "json_set": "events",
                "api_url": "2024-01/orders/{}/events.json",
                "request_parameters": request_parameters,
            },
            "customers": {
                "pk_list": ["id"],
                "table_name": "shopify_customer",
                "schema": "shopify",
                "json_set": "customers",
                "api_url": "2024-01/customers.json",
                "request_parameters": request_parameters,
            },
        }

        self.logger.info("sync shopify {}: getting table columns".format(self.command))
        if command in self.object_map:
            self.object_dd = self.object_map[command]
            self.object_dd.update(
                {
                    "table_columns": get_table_columns(
                        self.db_string, self.object_dd["table_name"]
                    ),
                    "file_name": "automationtools/data/{}_{}.tsv".format(
                        self.object_dd["table_name"],
                        self.current_timestamp.replace(":", "-"),
                    ),
                    "api_url_formatted": self.object_dd["api_url"],
                }
            )
        else:
            raise "{} is not a valid command".format(command)

        if command == "sync_shopify_order_events":
            self.logger.info(
                "sync shopify {}: getting order events to sync".format(self.command)
            )
            order_lines = self.get_orders()
            self.logger.info(
                "sync shopify {}: retrieved {} order events to sync".format(
                    self.command, len(order_lines)
                )
            )

            for i, o in enumerate(order_lines):
                try:
                    self.extra_context = {
                        "order_id": o["id"],
                        "order_updated_at": o["updated_at"],
                    }
                    self.object_dd["api_url_formatted"] = self.object_dd[
                        "api_url"
                    ].format(o["id"])
                    self.sync_data()
                except Exception:
                    self.logger.error(
                        "sync shopify {}: failed getting order events, exiting program".format(
                            self.command
                        ),
                        exc_info=1,
                    )
        else:
            self.sync_data()

    def sync_data(self):
        self.get_data()
        self.logger.info(
            'sync shopify {}: inserting {} rows into" {}"'.format(
                self.command, self.row_count, self.object_dd["table_name"]
            )
        )
        insert_data(self.object_dd, self.db_string)

    def get_orders(self):
        with contextlib.closing(psycopg2.connect(self.db_string)) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                sql = """
                    SELECT
                        COALESCE(JSONB_AGG(json), '[]'::JSONB) as order_json
                    FROM (
                        SELECT DISTINCT ON (o.id)
                            (select row_to_json(_) from (SELECT DISTINCT o.id, o.updated_at)  as _) as json
                        FROM
                            shopify.shopify_sales_order o LEFT JOIN
                            shopify.shopify_order_events e ON o.id = e.order_id
                        WHERE
                            e.order_updated_at IS NULL OR
                            o.updated_at <> e.order_updated_at
                        ORDER BY
                            o.id
                        LIMIT
                            1000
                    ) sub 
                    ;
                """
                cursor.execute(sql)
                return cursor.fetchall()[0][0]

    def get_data(self):
        with open(self.object_dd["file_name"], encoding="utf-8", mode="w") as w:
            self.row_count = 0
            url = "https://{}:{}@{}/admin/api/{}?{}".format(
                self.username,
                self.password,
                self.shopify_url,
                self.object_dd["api_url_formatted"],
                "&".join(
                    [
                        "{}={}".format(k, v)
                        for k, v in self.object_dd["request_parameters"].items()
                    ]
                ),
            )

            w.write("\t".join(self.object_dd["table_columns"]))
            w.write("\n")

            while True:
                self.logger.info(
                    'sync shopify {}: getting data from "https://{}"'.format(
                        self.command, url.split("@")[1]
                    )
                )
                time.sleep(1)

                response = requests.get(url)
                json_string = response.json()
                json_data = json_string[self.object_dd["json_set"]]
                self.row_count += len(json_data)

                self.logger.info(
                    "sync shopify {}: fetched {} rows".format(
                        self.command, len(json_data)
                    )
                )
                for order in json_data:
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
                        elif field in self.extra_context:
                            row.append(str(self.extra_context[field]))
                        else:
                            # print("{} id is missing key {}".format(order["id"], field))
                            row.append("")

                    line = "{}\n".format("\t".join(row))
                    w.write(line)

                next_page = (
                    response.headers["link"] if "link" in response.headers else None
                )

                if next_page and 'rel="next"' in next_page:
                    next_page = next_page.split(",")[-1]
                    url = (
                        next_page.replace("<", "")
                        .replace(
                            "https://",
                            "https://{}:{}@".format(self.username, self.password),
                        )
                        .split(">")[0]
                    )
                else:
                    break

            self.logger.info(
                'sync shopify {}: written {} rows to file "{}"'.format(
                    self.command, self.row_count, self.object_dd["file_name"]
                )
            )


if __name__ == "__main__":
    pass
