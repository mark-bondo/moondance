import json
import os
from dotenv import load_dotenv
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

load_dotenv()
SQL_DD = {}


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
    category = chart["extraOptions"]["category"]
    drillDowns = chart["extraOptions"]["drillDowns"]
    server_params = chart["extraOptions"]["sql"]
    filters = [""]

    # check for server params
    for d in drillDowns:
        if d["filter"]:
            filters.push(d["filter"])
        if d["isCurrent"]:
            grouping = d["value"]
        d["filter"] = None

    # check for user parameters
    if request.body != b"":
        user_params = json.loads(request.body)

        for f in user_params["filters"]:
            column = f["value"].replace("'", "''")
            filter = f["filter"].replace("'", "''")
            filters.append(f"{column}='{filter}'")

        user_params["filters"] = " AND ".join(filters)
        user_params["grouping"] = (
            user_params["grouping"]["value"] if "grouping" in user_params else grouping
        )
        server_params.update(user_params)

    # get series data and totals
    data = get_data(name=f"get_{category}_data", replace_dd=server_params)[0][0]

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
