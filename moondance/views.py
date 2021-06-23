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


def get_date(dte):
    today = datetime.now()
    end = today + timedelta(days=1)

    if dte == "Today":
        start = datetime.now()
    elif dte == "This Week":
        start = today - timedelta(days=today.weekday())
    elif dte == "This Month":
        start = today.replace(day=1)
    elif dte == "This Year":
        start = today.replace(day=1, month=1)

    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))


@login_required
def get_chart(request, id):
    # get chart options
    chart = json.loads(get_sql_data(name="get_chart_options", args={"id": id})[0][0])
    drillDowns = chart["extraOptions"]["drillDowns"]
    server_params = chart["extraOptions"]["sql"]
    filters = [""]

    # check for server params
    for d in drillDowns:
        if d["filter"]:
            filters.append(d["filter"])
            d["filter"] = None
        if d["isCurrent"]:
            grouping = d["value"]

    # check for user parameters and overwrite default server parameters
    user_params = json.loads(request.body)
    server_params["grouping"] = (
        user_params["grouping"]["value"] if "grouping" in user_params else grouping
    )

    for f in user_params["filters"]:
        if f["type"] == "grouping":
            column = f["value"].replace("'", "''")
            filter = f["filter"].replace("'", "''")
            filters.append(f"{column}='{filter}'")
        elif f["type"] == "xaxis" and f["filter"] != "All Dates":
            column = chart["extraOptions"]["xAxis"] if "value" not in f else f["value"]
            start, end = get_date(f["filter"])
            filters.append(f"{column} BETWEEN '{start}' AND '{end}'")
        else:
            continue

    server_params["filters"] = " AND ".join(filters)
    print(server_params["filters"])

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
    chart["extraOptions"]["title"] = "{} by {} {}{:,}".format(
        chart["highCharts"]["yAxis"]["title"]["text"],
        chart["highCharts"]["xAxis"]["title"]["text"],
        chart["highCharts"]["tooltip"]["valuePrefix"],
        int(data["options"]["total"]),
    )

    return HttpResponse(json.dumps(chart), content_type="application/json")
