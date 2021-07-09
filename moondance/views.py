import json
import os
import io
from wsgiref.util import FileWrapper
from xlsxwriter.workbook import Workbook
from datetime import datetime, timedelta
from dotenv import load_dotenv
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

load_dotenv()
FILE_PATH = "" if os.getenv("NODE_ENV") == "development" else "moondance/"
SQL_DD = {}
JSON_DD = {}


def get_sql_data(name, args={}, replace_dd={}):
    if name not in SQL_DD or os.getenv("NODE_ENV") == "development":
        with open(f"{FILE_PATH}templates/sql/{name}.sql", "r") as f:
            SQL_DD[name] = f.read()

    sql = SQL_DD[name]

    if replace_dd:
        sql = sql % replace_dd

    with connection.cursor() as cursor:
        cursor.execute(sql, args)
        data = cursor.fetchall()

    return data


def get_json_data(name):
    if name not in JSON_DD or os.getenv("NODE_ENV") == "development":
        with open(f"{FILE_PATH}templates/json/{name}.json", "r") as f:
            JSON_DD[name] = f.read()
    return JSON_DD[name]


def get_wholesale_form(request):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            WITH skus AS (
                SELECT
                    id,
                    handle,
                    tags,
                    status,
                    title,
                    images,
                    product_type,
                    jsonb_array_elements(variants) as v
                FROM
                    shopify.shopify_product
            )

            SELECT
                COALESCE(product_type, 'Other') as product_type,
                (
                    CASE
                        WHEN title = '' THEN v->>'title' 
                        ELSE title
                    END || 
                    CASE
                        WHEN COALESCE((v->>'option1'), 'Default Title') = 'Default Title' THEN ''
                        ELSE ' - ' || (v->>'option1')
                    END ||
                    CASE
                        WHEN COALESCE((v->>'option2'), 'Default Title') = 'Default Title' THEN ''
                        ELSE ' - ' || (v->>'option2')
                    END ||
                    CASE
                        WHEN COALESCE((v->>'option3'), 'Default Title') = 'Default Title' THEN ''
                        ELSE ' - ' || (v->>'option3')
                    END
                ) as description,
                v->>'sku' as SKU,
                v->>'barcode' as UPC,
                (v->>'price')::NUMERIC(16, 2) as retail_price,
                ((v->>'price')::NUMERIC(16, 2) * 0.60)::NUMERIC(16, 2) as wholesale_price,
                'https:/moondancesoaps.com/' || handle as url
            FROM
                skus
            WHERE
                status = 'active'
            ORDER BY
                1,2
                
        """
        )
        data = cursor.fetchall()
        headers = [c[0].replace("_", " ").title() for c in cursor.description]

    today = datetime.now().strftime("%B-%d-%Y")
    name = f"MoonDance Soaps Wholesale Order Form {today}"
    output = io.BytesIO()
    workbook = Workbook(
        output,
        {
            "in_memory": False,
            "constant_memory": True,
            "default_date_format": "m/d/yyyy",
            "remove_timezone": True,
        },
    )
    bold = workbook.add_format({"bold": True})
    ws = workbook.add_worksheet("order sheet")
    ws.write(0, 0, "MoonDance Soaps", bold)
    ws.write(1, 0, "Wholesale Order Form", bold)
    ws.write(2, 0, today)
    ws.write_row(4, 0, headers, bold)
    start_row = 5

    for r, row in enumerate(data, start_row):
        ws.write_row(r, 0, row)

    workbook.close()

    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(FixedFileWrapper(output), content_type=mime)
    response["Content-Disposition"] = f'attachment; filename="{name}.xlsx"'
    return response


class FixedFileWrapper(FileWrapper):
    def __iter__(self):
        self.filelike.seek(0)
        return self


@login_required
def home(request):
    return render(request, "home.html", context={})


@login_required
def get_default_settings(request, name):
    json_data = get_json_data(name=name)

    return HttpResponse(json_data, content_type="application/json")


@login_required
def get_dashboards(request):
    json_data = get_sql_data(name="get_dashboards")[0][0]

    return HttpResponse(json_data, content_type="application/json")


def get_xaxis_fields(dte):
    today = datetime.now()
    end_date = today + timedelta(days=1)

    if dte == "Today":
        start_date = datetime.now()
        date_grouping = "hour"
    elif dte == "This Week":
        start_date = today - timedelta(days=today.weekday())
        date_grouping = "day"
    elif dte == "This Month":
        start_date = today.replace(day=1)
        date_grouping = "day"
    elif dte == "This Quarter":
        if today.month < 4:
            m = 1
        elif today.month < 7:
            m = 4
        elif today.month < 10:
            m = 7
        else:
            m = 10

        start_date = today.replace(day=1, month=m)
        date_grouping = "week"
    elif dte == "This Year":
        start_date = today.replace(day=1, month=1)
        date_grouping = "month"
    elif dte == "All Dates":
        start_date = datetime.now()
        date_grouping = "month"

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "date_grouping": "DATE_TRUNC('{}', {})".format(date_grouping, "%(xaxis)s"),
    }


def quote_sql(value):
    return value.replace("'", "''").replace(r"%", r"%%")


@login_required
def get_chart(request, id):
    # get server chart options and sql
    chart = json.loads(get_sql_data(name="get_chart_options", args={"id": id})[0][0])
    fields = chart["extraOptions"]["fields"]
    server_params = chart["extraOptions"]["sql"]
    filters = [""]

    # prepopulate sql using server params
    for f in fields:
        if f["filter"]:
            filters.append(f["filter"])
            f["filter"] = None
        if f["isCurrent"] and f["type"] == "grouping":
            grouping = f["value"]

    # overwrite server parameters with user parameters
    user_params = json.loads(request.body)
    server_params["grouping"] = (
        user_params["grouping"]["value"] if "grouping" in user_params else grouping
    )

    # parse filters and resolve x-axis grouping
    for f in user_params["filters"]:
        if f["type"] == "grouping":
            column = quote_sql(f["value"])
            filter = quote_sql(f["filter"])
            filters.append(f"{column}='{filter}'")
        elif f["type"] == "xaxis":
            xaxis = get_xaxis_fields(f["filter"])
            server_params["xaxis"] = xaxis["date_grouping"] % server_params

            # don't apply a date filter for all dates
            if f["filter"] == "All Dates":
                continue

            column = chart["extraOptions"]["xAxis"] if "value" not in f else f["value"]
            filters.append(
                "{} BETWEEN '{}' AND '{}'".format(
                    column,
                    xaxis["start_date"],
                    xaxis["end_date"],
                )
            )
        else:
            continue

    server_params["filters"] = " AND ".join(filters)
    field_list = [d for d in fields if d["isVisible"]]
    server_params["table_fields"] = server_params["grouping"]

    # get series data and totals
    chartCategory = (
        user_params["chartCategory"]
        if "chartCategory" in user_params
        else chart["extraOptions"]["chartCategory"]
    )
    data = get_sql_data(
        name="get_{}_data".format(chartCategory),
        replace_dd=server_params,
    )[0][0]

    # clean up and format json for HighCharts response
    chart["highCharts"]["series"] = data["data"]
    chart["extraOptions"]["chartCategory"] = chartCategory
    chart["extraOptions"].pop("sql")
    chart["extraOptions"]["fields"] = field_list
    chart["extraOptions"]["title"] = "{} {}{:,}".format(
        chart["highCharts"]["yAxis"]["title"]["text"],
        chart["highCharts"]["tooltip"]["valuePrefix"],
        int(data["options"]["total"]),
    )

    return HttpResponse(json.dumps(chart), content_type="application/json")
