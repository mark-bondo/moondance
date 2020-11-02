#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import datetime
import json
import psycopg2
import os
import contextlib

order_field_list = [
    "id",
    "email",
    "closed_at",
    "created_at",
    "updated_at",
    "number",
    "note",
    "token",
    "gateway",
    "test",
    "total_price",
    "subtotal_price",
    "total_weight",
    "total_tax",
    "taxes_included",
    "currency",
    "financial_status",
    "confirmed",
    "total_discounts",
    "total_line_items_price",
    "cart_token",
    "buyer_accepts_marketing",
    "name",
    "referring_site",
    "landing_site",
    "cancelled_at",
    "cancel_reason",
    "total_price_usd",
    "checkout_token",
    "reference",
    "user_id",
    "location_id",
    "source_identifier",
    "source_url",
    "processed_at",
    "device_id",
    "phone",
    "customer_locale",
    "app_id",
    "browser_ip",
    "landing_site_ref",
    "order_number",
    "discount_applications",
    "discount_codes",
    "note_attributes",
    "payment_gateway_names",
    "processing_method",
    "checkout_id",
    "source_name",
    "fulfillment_status",
    "tax_lines",
    "tags",
    "contact_email",
    "order_status_url",
    "presentment_currency",
    "total_line_items_price_set",
    "total_discounts_set",
    "total_shipping_price_set",
    "subtotal_price_set",
    "total_price_set",
    "total_tax_set",
    "line_items",
    "fulfillments",
    "refunds",
    "total_tip_received",
    "original_total_duties_set",
    "current_total_duties_set",
    "admin_graphql_api_id",
    "shipping_lines",
    "billing_address",
    "client_details",
    "payment_details",
    "customer",
    "shipping_address"
]

escape_list = [
    ("\b", "\\b"),
    ("\n", "\\n"),
    ("\r", "\\r"),
    ("\t", "\\t")
]

def escape_value(value):
    for e in escape_list:
        if e[0] in value:
            value = value.replace(e[0], e[1])

    return value


def get_shopify_orders(start_datetime):
    file_name = "test.tsv"
    username = os.environ.get("SHOPIFY_USERNAME")
    password = os.environ.get("SHOPIFY_PASSWORD")
    params = {
        "updated_at_min": start_datetime,
        "status": "any"
    }

    with open(file_name, encoding="utf-8", mode="w") as w:
        row_count = 0
        order_url = "https://{}:{}@{}/admin/api/2020-10/orders.json?{}".format(
            username,
            password,
            os.environ.get("SHOPIFY_URL"),
            "&".join(["{}={}".format(k, v) for k, v in params.items()])
        )

        w.write("\t".join(order_field_list))
        w.write("\n")

        while True:
            print("fetching order batch starting {}".format(row_count))
            print(order_url)
            print("x" * 50)
            response = requests.get(order_url)
            json_string = response.json()

            for order in json_string["orders"]:
                row = []

                for field in order_field_list:
                    if field in order:
                        v = order[field]
                        if v is None:
                            v = ""
                        elif isinstance(v, (list, dict)):
                            v = json.dumps(v)

                        v = escape_value(str(v))
                        row.append(v)
                    else:
                        print("{} order is missing key {}".format(order["name"], field))
                        row.append("")

                line = "{}\n".format("\t".join(row))
                w.write(line)
                row_count+=1

            next_page = response.headers["link"] if "link" in response.headers else None
            
            if next_page and 'rel="next"' in next_page:
                next_page = next_page.split(",")[-1]
                order_url = next_page.replace("<", "").replace("https://", "https://{}:{}@".format(username, password)).split(">")[0]
            else:
                break

    load_data(file_name, row_count)


def load_data(file_name, row_count):
    table_name = "sales_orders_shopify"
    primary_key_list = ["id"]

    with open("templates/sql/{}.sql".format("pk_append"), "r") as f:
        sql = f.read() % {
            "schema": "public",
            "table_name": table_name,
            "column_select": ",".join([x for x in order_field_list]),
            "delim": "\t",
            "date_append_column": "datetime_updated",
            "primary_key_join": " AND ".join(['a."{0}"=b."{0}"'.format(x) for x in primary_key_list if primary_key_list])
        }

    with contextlib.closing(psycopg2.connect(os.environ.get("DB_STRING"))) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            print("{}: starting data load for {} order lines".format(table_name, row_count))
            print(sql)
            cursor.copy_expert(sql, open(file_name, "r", encoding="utf-8"))

        conn.commit()
        os.remove(file_name)
        print("{}: completed data load".format(table_name))


if __name__ == "__main__":
    interval = {"days": 1000}
    start_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()
    # end_datetime = (datetime.datetime.utcnow() - datetime.timedelta(**interval)).isoformat()

    get_shopify_orders(start_datetime)