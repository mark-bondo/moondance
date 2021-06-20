import json
import os
from dotenv import load_dotenv
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

load_dotenv()
SQL_DD = {}
CHART_TYPES = [
    {"category": "summary", "type": "pie", "icon": "mdi-chart-pie"},
    {
        "category": "summary",
        "type": "donut",
        "icon": "mdi-chart-donut",
    },
    {
        "category": "phased",
        "type": "area",
        "icon": "mdi-chart-areaspline-variant",
    },
    {
        "category": "phased",
        "type": "line",
        "icon": "mdi-chart-line",
    },
    {
        "category": "phased",
        "type": "spline",
        "icon": "mdi-chart-bell-curve-cumulative",
    },
    {
        "category": "phased",
        "type": "bar",
        "icon": "mdi-chart-gantt",
    },
    {
        "category": "phased",
        "type": "column",
        "icon": "mdi-chart-bar",
    },
]


def get_data(name, args={}, replace_dd={}):
    if name not in SQL_DD or os.getenv("NODE_ENV") == "development":
        with open(f"./templates/sql/{name}.sql", "r") as f:
            SQL_DD[name] = f.read()

    sql = SQL_DD[name]

    if replace_dd:
        sql = sql % replace_dd

    # print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, args)
        data = cursor.fetchall()

    return data


@login_required
def render_home(request):
    return render(request, "home.html", context={})


@login_required
def get_dashboards(request):
    json_data = get_data(name="get_dashboards")[0][0]

    return HttpResponse(json_data, content_type="application/json")


@login_required
def get_chart(request, id):
    # get chart options
    chart = json.loads(get_data(name="get_chart_options", args={"id": id})[0][0])
    drillDowns = chart["extraOptions"]["drillDowns"]
    server_params = chart["extraOptions"]["sql"]
    filters = []

    # check for server params
    for d in drillDowns:
        if d["filter"]:
            filters.push(d["filter"])
        if d["isCurrent"]:
            grouping = d["value"]
        d["filter"] = None

    # check for user parameters and overwrite default server parameters
    user_params = json.loads(request.body)
    server_params["grouping"] = (
        user_params["grouping"]["value"] if "grouping" in user_params else grouping
    )

    for f in user_params["filters"]:
        column = f["value"].replace("'", "''")
        filter = f["filter"].replace("'", "''")
        filters.append(f"{column}='{filter}'")

    server_params["filters"] = " AND ".join(filters)

    # get series data and totals
    chartCategory = (
        user_params["chartCategory"]
        if "chartCategory" in user_params
        else chart["extraOptions"]["chartCategory"]
    )
    data = get_data(
        name="get_{}_data".format(chartCategory),
        replace_dd=server_params,
    )[0][0]

    # clean up and format json for HighCharts response
    chart["highCharts"]["series"] = data["data"]
    chart["extraOptions"].pop("sql")
    chart["extraOptions"]["drillDowns"] = [d for d in drillDowns if d["isVisible"]]
    chart["extraOptions"]["title"] = "{} {}{:,}".format(
        chart["extraOptions"]["title"],
        chart["extraOptions"]["prefix"],
        int(data["options"]["total"]),
    )

    return HttpResponse(json.dumps(chart), content_type="application/json")
