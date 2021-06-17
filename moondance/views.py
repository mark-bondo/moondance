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

    print(sql)

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
    category = chart["chart"]["category"]
    replace_dd = chart["sql"]

    # check for user parameters
    filters = [""]
    if request.body != b"":
        user_params = json.loads(request.body)["data"]

        for f in user_params["filters"]:
            column = f["value"].replace("'", "''")
            filter = f["filter"].replace("'", "''")
            filters.append(f"{column}='{filter}'")

        user_params["filters"] = " AND ".join(filters)

        if not user_params["grouping"]:
            user_params["grouping"] = replace_dd["grouping"]

        replace_dd.update(user_params)

    # get chart data
    if category == "summary":
        data = get_data(name="get_summary_data", replace_dd=replace_dd)[0][0]
    elif category == "phased":
        data = get_data(name="get_phased_data", replace_dd=replace_dd)[0][0]

    # clean up and format json for HighCharts response
    chart["series"] = data["data"]
    chart.pop("sql", None)
    chart["title"]["text"] = "{}<br>{}{:,}".format(
        chart["title"]["text"],
        chart["title"]["prefix"],
        int(data["options"]["total"]),
    )

    return HttpResponse(json.dumps(chart), content_type="application/json")
