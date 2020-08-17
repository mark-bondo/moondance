#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import xlsxwriter
import codecs
import contextlib
import datetime
import psycopg2
import os
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

order_header_list = [
    {
        "name": "Order Status",
        "api_name": "orderstatus",
        "parent": "order",
        "type": "str"
    },
    {
        "name": "Datetime Updated",
        "api_name": "date",
        "parent": "lastupd",
        "type": "datetime"
    },
    {
        "name": "Order Number",
        "api_name": "orderno",
        "parent": "order",
        "type": "integer"
    },
    {
        "name": "Order Line",
        "api_name": "lineno",
        "parent": "lineitem",
        "type": "integer"
    },
    {
        "name": "Order Line Status",
        "api_name": "linestatus",
        "parent": "lineitem",
        "type": "str"
    },
    {
        "name": "Datetime Ordered",
        "api_name": "date",
        "parent": "orderdate",
        "type": "datetime"
    },
    {
        "name": "Datetime Shipped",
        "api_name": "date",
        "parent": "shipto",
        "type": "date"
    },
    {
        "name": "Customer Type",
        "api_name": "customertype",
        "parent": "customer",
        "type": "str"
    },
    {
        "name": "Product Category",
        "api_name": "category",
        "parent": "lineitem",
        "type": "str"
    },
    {
        "name": "Product Name",
        "api_name": "productname",
        "parent": "lineitem",
        "type": "str"
    },
    {
        "name": "Product SKU",
        "api_name": "productsku",
        "parent": "lineitem",
        "type": "str"
    },
    {
        "name": "Product Attribute",
        "api_name": "attribute",
        "parent": "lineitem",
        "type": "str"
    },
    {
        "name": "Extended Price",
        "api_name": "extprice",
        "parent": "lineitem",
        "type": "integer"
    },
    {
        "name": "Quantity",
        "api_name": "quantity",
        "parent": "lineitem",
        "type": "integer"
    },
    {
        "name": "Unit Price",
        "api_name": "unitprice",
        "parent": "lineitem",
        "type": "integer"
    },
    {
        "name": "Tracking Number",
        "api_name": "trackingnumber",
        "parent": "lineitem",
        "type": "str"
    },
    {
        "name": "Ship To State", 
        "api_name": "stateprovcode",
        "parent": "shipto",
        "type": "str"
    },
    {
        "name": "Shipping Method",
        "api_name": "shipmethod",
        "parent": "order",
        "type": "str"
    },
    {
        "name": "Shipping Rate",
        "api_name": "shiprate",
        "parent": "order",
        "type": "integer"
    },
    {
        "name": "Shipping Weight",
        "api_name": "shipweight",
        "parent": "order",
        "type": "integer"
    },
    {
        "name": "Unit Weight",
        "api_name": "unitweight",
        "parent": "lineitem",
        "type": "integer"
    },
    {
        "name": "Total Weight",
        "api_name": "totalweight",
        "parent": "lineitem",
        "type": "integer"
    },
    {
        "name": "Browser Platform",
        "api_name": "platformname",
        "parent": "browser",
        "type": "str"
    },
    {
        "name": "Browser Name",
        "api_name": "browsername",
        "parent": "browser",
        "type": "str"
    },
    {
        "name": "Sales Tax Rate",
        "api_name": "salestaxrate",
        "parent": "order",
        "type": "integer"
    },
]

product_header_list = [
    {
        "name": "Name",
        "api_name": "productname",
        "parent": "product",
        "type": "str"
    },
    {
        "name": "Attribute",
        "api_name": "attribute",
        "parent": "product",
        "type": "str"
    },
    {
        "name": "Product ID",
        "api_name": "productno",
        "parent": "product",
        "type": "integer"
    },
    {
        "name": "SKU",
        "api_name": "productsku",
        "parent": "product",
        "type": "str"
    },
    {
        "name": "Inventory Onhand",
        "api_name": "inventory",
        "parent": "product",
        "type": "integer"
    },
    {
        "name": "Product Category",
        "api_name": "categoryname",
        "parent": "categories",
        "type": "str"
    },
    {
        "name": "Status",
        "api_name": "status",
        "parent": "product",
        "type": "str"
    },
    {
        "name": "Short Description",
        "api_name": "short",
        "parent": "description",
        "type": "str"
    },
    {
        "name": "Long Description",
        "api_name": "long",
        "parent": "description",
        "type": "str"
    },
    {
        "name": "Key Words",
        "api_name": "keywords",
        "parent": "description",
        "type": "str"
    },
    {
        "name": "Unit Weight",
        "api_name": "weight",
        "parent": "product",
        "type": "integer"
    },
    {
        "name": "Unit Price",
        "api_name": "price",
        "parent": "pricing",
        "type": "integer"
    },
    {
        "name": "Visibility",
        "api_name": "visibility",
        "parent": "product",
        "type": "str"
    },
    {
        "name": "Store Front Link",
        "api_name": "storefront",
        "parent": "productlink",
        "type": "str"
    },
    {
        "name": "Direct Checkout Link",
        "api_name": "directcheckout",
        "parent": "productlink",
        "type": "str"
    },
    {
        "name": "Datetime Created",
        "api_name": "date",
        "parent": "created",
        "type": "datetime"
    },
    {
        "name": "Datetime Updated",
        "api_name": "date",
        "parent": "lastupd",
        "type": "datetime"
    },
]


class Nexternal_API(object):
    def __init__(self, data_dir, table_name, primary_key_list, data_type, start_date, end_date, load_method):
        self.data_dir = data_dir
        self.url_dict = {
            "sales_orders": "https://www.nexternal.com/shared/xml/orderquery.rest",
            "products": "https://www.nexternal.com/shared/xml/productquery.rest"
        }
        self.table_name = table_name
        self.file_name = "{}.tsv".format(self.table_name)
        self.primary_key_list = primary_key_list
        self.data_type = data_type
        self.start_date = start_date
        self.end_date = end_date
        self.load_method = load_method
        self.xml_file_name =  "{}/nexternal/{}/{}_to_{}.xml".format(
            self.data_dir,
            self.data_type,
            self.start_date.strftime("%Y-%m-%d"),
            self.end_date.strftime("%Y-%m-%d")
        )

    def get_data(self):
        with open("templates/xml/{}.xml".format(self.data_type), "r") as f:
            xml = f.read()

        current_page = 1
        page_number = ""

        with open(self.xml_file_name, "w", encoding="utf-8") as w:
            print("{}: connecting to {}".format(self.table_name, self.url_dict[self.data_type]))
            while True:
                data = xml % {
                    "start_date": self.start_date.strftime("%m/%d/%Y"),
                    "end_date": self.end_date.strftime("%m/%d/%Y"),
                    "page_number": page_number,
                    "key": os.environ.get("NEXTERNAL_API_KEY")
                }

                print("{}: writing page {}".format(self.table_name, current_page))
                response = requests.get(
                    self.url_dict[self.data_type],
                    data=data,
                    headers={"Content-Type": "application/xml"}
                ).text
                w.write(response)
                current_page += 1
                page_number = f"<Page>{current_page}</Page>"

                if "<NextPage />" not in response:
                    break

    def parse_order_data(self, header_list=order_header_list):
        self.row_count = 0

        with open(self.file_name, encoding="utf-8", mode="w") as w:
            w.write("{}\t{}\n".format(
                 [h["name"] for h in header_list],
                "Source File"
            ))

            with codecs.open(self.xml_file_name, "r", encoding="utf-8", errors="ignore") as f:
                root = BeautifulSoup(f, features="html.parser")
                order_list = root.find_all("order")

                for order_element in order_list:
                    order_line_list = order_element.find_all('lineitem')

                    for line in order_line_list:
                        row = []

                        for h in header_list:
                            if h["parent"] != "lineitem":
                                if h["parent"] == "order" and order_element:
                                    element = order_element.find(h["api_name"])
                                else:
                                    element = order_element.find(h["parent"])

                                    if element:
                                        element = element.find(h["api_name"])
                            else:
                                element = line.find(h["api_name"])

                            if element:
                                element = element.get_text()

                                if h["type"] == "datetime":
                                    element = "{} {}".format(
                                        datetime.datetime.strptime(element, "%m/%d/%Y").strftime("%Y-%m-%d"),
                                        order_element.find(h["parent"]).find("time").get_text()
                                    )
                            else:
                                element = ""

                            row.append(element)
                        row.append(self.xml_file_name)
                        self.row_count+=1
                        w.write("{}\n".format("\t".join(row)))

        header_list.append({
            "name": "Source File"
        })
        self.header_list = header_list

    def parse_product_data(self, header_list=product_header_list):
        self.row_count = 1

        with open(self.file_name, encoding="utf-8", mode="w") as w:
            w.write("{}\t{}\n".format(
                    "\t".join([h["name"] for h in header_list]),
                "Source File"
            ))

            with codecs.open(self.xml_file_name, "r", encoding="utf-8", errors="ignore") as f:
                root = BeautifulSoup(f, features="html.parser")
                product_list = root.find_all("product")

                for product in product_list:
                    sku_list = product.find_all("sku")
                    product_name = product.find("productname")
                    attributes = []

                    if sku_list:
                        attributes = []

                        for sku in sku_list:
                            attribute_list = sku.find_all("attribute")


                            for a in attribute_list:
                                attribute_string = "{}: {}".format(a.get("name"), a.get_text())
                                attributes.append(attribute_string)

                    if product_name:
                        row = []

                        for h in header_list:
                            if h["api_name"] == "attribute":
                                element = product.find(h["api_name"])

                                if not element:
                                    element = ";".join(attributes)
                            if h["parent"] != "product":
                                element = product.find(h["parent"])

                                if element:
                                    element = element.find(h["api_name"])
                            else:
                                element = product.find(h["api_name"])

                            if element and element is not str:
                                element = element.get_text()

                                if h["type"] == "datetime":
                                    element = "{} {}".format(
                                        datetime.datetime.strptime(element, "%m/%d/%Y").strftime("%Y-%m-%d"),
                                        product.find(h["parent"]).find("time").get_text()
                                    )
                            else:
                                element = ""

                            row.append(element.replace("\n", "    ").replace("\t", "    ").replace("\r", "    "))
                        self.row_count += 1
                        w.write("{}\n".format("\t".join(row)))

        self.header_list = header_list
                        # if row_number >= 50:
                        #     break
    def load_data(self):
        with open("templates/sql/{}.sql".format(self.load_method), "r") as f:
            sql = f.read() % {
                "schema": "public",
                "table_name": self.table_name,
                "column_select": ",".join(['"{}"'.format(x["name"].lower().replace(" ", "_")) for x in self.header_list]),
                "delim": "\t",
                "date_append_column": "datetime_updated",
                "primary_key_join": " AND ".join(['a."{0}"=b."{0}"'.format(x) for x in self.primary_key_list if self.primary_key_list]),
                "start_date": "{} 00:00:00.000000".format(self.start_date),
                "end_date": "{} 23:59:59.000000".format(self.end_date),
            }

        with contextlib.closing(psycopg2.connect(os.environ.get("DB_STRING"))) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                print("{}: starting data load for {} order lines".format(self.table_name, self.row_count))
                print(sql)
                cursor.copy_expert(sql, open(self.file_name, "r", encoding="utf-8"))

            conn.commit()
            os.remove(self.file_name)
            print("{}: completed data load".format(self.table_name))


def combine_amazon_files(data_dir):
    data_file_list = ["{}/{}".format(data_dir,  f) for f in listdir(data_dir) if isfile(join(data_dir, f))]

    with codecs.open("Moondance - Amazon Order Data.tsv", "w", encoding="utf-8", errors="ignore") as w:
        for file_number, file in enumerate(data_file_list, 1):
            with codecs.open(file, "r", encoding="utf-8", errors="ignore") as r:
                if file_number == 1:
                    extra_headers = [
                        "File Name",
                        "Year Ordered",
                        "Month Ordered",
                        "Period Ordered",
                    ]
                    headers = "{}\t{}".format(
                        "\t".join(extra_headers),
                        r.readline()
                    )
                    w.write(headers)
                else:
                    r.readline()
                
                for line in r:
                    columns = line.split("\t")
                    year_ordered = columns[2][:4]
                    month_ordered = columns[2][5:7]
                    purchase_date = "{}/{}/{}".format(
                        month_ordered,
                        1,
                        year_ordered
                    )
                    extra_columns = [
                        file,
                        year_ordered,
                        month_ordered,
                        purchase_date
                    ]
                    line = "{}\t{}".format(
                        "\t".join(extra_columns),
                        line
                    )
                    w.write(line)


# if __name__ == "__main__":
#     start_date = (datetime.datetime.now() - datetime.timedelta(14)).strftime("%m/%d/%Y")
#     end_date = datetime.datetime.now().strftime("%m/%d/%Y")
#     data_dir = "data"

#     api = Nexternal_API(data_dir=data_dir)
#     api.get_product_data(start_date='01/01/1900', end_date="12/31/2030")
#     api.merge_product_data(product_header_list)

    # data_dir = "data/amazon"
    # combine_amazon_files(data_dir)