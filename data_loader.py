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
        "name": "Order Date",
        "api_name": "date",
        "parent": "orderdate",
        "type": "date"
    },
    {
        "name": "Ship Date",
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
        "name": "Product Name",
        "api_name": "productname",
        "parent": "product",
        "type": "str"
    },
    {
        "name": "Product Attribute",
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
        "name": "Product SKU",
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
        "name": "Product Number",
        "api_name": "productno",
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
        "name": "Date Created",
        "api_name": "date",
        "parent": "created",
        "type": "date"
    },
    {
        "name": "Date Last Updated",
        "api_name": "date",
        "parent": "lastupd",
        "type": "date"
    },
]


class Nexternal_API(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.url_dict = {
            "orders": "https://www.nexternal.com/shared/xml/orderquery.rest",
            "products": "https://www.nexternal.com/shared/xml/productquery.rest"
        }
        self.headers = {"Content-Type": "application/xml"}
        self.xml_dict = {
            "key": os.environ.get("NEXTERNAL_API_KEY"),
        }

    def get_order_data(self, start_date, end_date):
        self.data_type = "orders"
        self.xml_dict["start_date"] = start_date
        self.xml_dict["end_date"] = end_date
        self.xml_dict["page_number"] = ""

        with open("templates/xml/orders.xml", "r") as f:
            self.xml = f

        self.write_to_file()

    def get_product_data(self, start_date, end_date):
        self.data_type = "products"
        self.xml_dict["start_date"] = start_date
        self.xml_dict["end_date"] = end_date
        self.xml_dict["page_number"] = ""

        with open("templates/xml/products.xml", "r") as f:
            self.xml = f

        self.write_to_file()

    def write_to_file(self):
        self.xml_file_name =  "{}/{}/moondance_{}_{}_to_{}.xml".format(
            self.data_dir,
            self.data_type,
            self.data_type,
            self.xml_dict["start_date"].replace("/", "-"),
            self.xml_dict["end_date"].replace("/", "-")
        )
        current_page = 1

        with open(self.xml_file_name, "w", encoding="utf-8") as w:
            while True:
                data = self.xml % self.xml_dict
                print("connecting to {}".format(self.url_dict[self.data_type]))
                print(data)
                response = requests.get(self.url_dict[self.data_type], data=data, headers=self.headers).text
                w.write(response)
                current_page += 1
                self.xml_dict["page_number"] = f"<Page>{current_page}</Page>"

                if "<NextPage />" not in response:
                    break

    def merge_order_data(self, header_list=order_header_list):
        self.order_file_name = "Moondance - Nexternal Order Data.tsv"
        with open(self.order_file_name, encoding="utf-8", mode="w") as w:

            w.write("{}\t{}\n".format(
                 [h["name"] for h in header_list],
                "Source File"
            ))

            self.data_type = "orders"

            # for data_file in data_file_list:
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
                            else:
                                element = ""

                            row.append(element)
                        row.append(self.xml_file_name)
                        w.write("{}\n".format("\t".join(row)))

        header_list.append({
            "name": "Source File"
        })
        self.header_list = header_list

    def load_order_data(self):
        with open("templates/sql/date_append.sql", "r") as f:
            sql = f % {
                "schema": "public",
                "table_name": "sales_orders_nexternal",
                "column_select": ",".join(['"{}"'.format(x["name"].lower().replace(" ", "_")) for x in self.header_list]),
                "delim": "\t",
                "date_append_column": "order_date",
                "start_date": self.xml_dict["start_date"],
                "end_date": self.xml_dict["end_date"]
            }

        with contextlib.closing(psycopg2.connect(os.environ.get("DB_STRING"))) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                print(sql)
                cursor.copy_expert(sql, open(self.order_file_name, "r", encoding="utf-8"))
            conn.commit()

    def merge_product_data(self, header_list):
        workbook = xlsxwriter.Workbook(
            "Moondance - Nexternal Product Data.xlsx",
            {
                "constant_memory": False,
                "default_date_format": "m/d/yyyy",
                "remove_timezone": True,
            }
        )
        workbook.add_format({"num_format": "m/d/yyyy"})
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, [h["name"] for h in header_list])
        row_number = 1
        self.data_type = "products"
        data_file_list = ["{}/{}/{}".format(self.data_dir, self.data_type, f) for f in listdir("{}/{}".format(self.data_dir, self.data_type)) if isfile(join("{}/{}".format(self.data_dir, self.data_type), f))]

        for data_file in data_file_list:
            with codecs.open(data_file, "r", encoding="utf-8", errors="ignore") as f:
                root = BeautifulSoup(f, features="html.parser")
                product_list = root.find_all("product")


                for line in product_list:
                    sku_list = line.find_all("sku")
                    product_name = line.find("productname")

                    if sku_list:
                        for s in sku_list:
                            row = []

                            for h in header_list:
                                if h["api_name"] == "productsku":
                                    element = s.get("sku")

                                    if not element:
                                        element = line.find(h["api_name"])

                                elif h["api_name"] == "attribute":
                                    element = s.find("attribute")
                                elif h["parent"] != "product":
                                    element = line.find(h["parent"])

                                    if element:
                                        element = element.find(h["api_name"])
                                else:
                                    element = line.find(h["api_name"])

                                if element and type(element) is not str:
                                    element = element.get_text()

                                    if h["type"] == "date":
                                        element = datetime.datetime.strptime(element, "%m/%d/%Y")
                                    elif h["type"] == "integer":
                                        element = float(element)
                                elif type(element) is str:
                                    element = element
                                else:
                                    element = None

                                row.append(element)
                            worksheet.write_row(row_number, 0, row)
                            row_number += 1
                    elif product_name:
                        row = []

                        for h in header_list:
                            if h["parent"] != "product":
                                element = line.find(h["parent"])

                                if element:
                                    element = element.find(h["api_name"])
                            else:
                                element = line.find(h["api_name"])

                            if element:
                                element = element.get_text()

                                if h["type"] == "date":
                                    element = datetime.datetime.strptime(element, "%m/%d/%Y")
                                elif h["type"] == "integer":
                                    element = float(element)
                            else:
                                element = None

                            row.append(element)
                        worksheet.write_row(row_number, 0, row)
                        row_number += 1

                    # if row_number >= 50:
                    #     break
        workbook.close()


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


if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(14)).strftime("%m/%d/%Y")
    end_date = datetime.datetime.now().strftime("%m/%d/%Y")
    data_dir = "data"

    api = Nexternal_API(data_dir=data_dir)
    api.get_product_data(start_date='01/01/1900', end_date="12/31/2030")
    api.merge_product_data(product_header_list)

    # data_dir = "data/amazon"
    # combine_amazon_files(data_dir)