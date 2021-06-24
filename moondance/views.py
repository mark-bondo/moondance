import json
import os
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

    # print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, args)
        data = cursor.fetchall()

    return data


def get_json_data(name):
    if name not in JSON_DD or os.getenv("NODE_ENV") == "development":
        with open(f"{FILE_PATH}templates/json/{name}.json", "r") as f:
            JSON_DD[name] = f.read()
    return JSON_DD[name]


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
        print(start_date)
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
    drillDowns = chart["extraOptions"]["drillDowns"]
    server_params = chart["extraOptions"]["sql"]
    filters = [""]

    # prepopulate sql using server params
    for d in drillDowns:
        if d["filter"]:
            filters.append(d["filter"])
            d["filter"] = None
        if d["isCurrent"]:
            grouping = d["value"]

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
    chart["extraOptions"]["drillDowns"] = [d for d in drillDowns if d["isVisible"]]
    chart["extraOptions"]["title"] = "{} {}{:,}".format(
        chart["highCharts"]["yAxis"]["title"]["text"],
        chart["highCharts"]["tooltip"]["valuePrefix"],
        int(data["options"]["total"]),
    )

    return HttpResponse(json.dumps(chart), content_type="application/json")
