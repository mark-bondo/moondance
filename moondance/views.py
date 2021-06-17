import json
import os
from dotenv import load_dotenv
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

load_dotenv()
SQL_DD = {}


def get_data(name, args={}, dd={}):
    if name not in SQL_DD or os.getenv("NODE_ENV") == "development":
        with open(f"./templates/sql/{name}.sql", "r") as f:
            SQL_DD[name] = f.read()

    sql = SQL_DD[name]

    if dd:
        sql = sql % dd

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
def get_chart(request):
    # chart = json.loads(request.body)["data"]
    # dd = {"group": chart["group"], "filters": "", "yaxis": chart["yaxis"]}

    if chart["type"] in (
        "pie",
        "donut",
    ):
        json_data = get_data(name="get_pie", dd=chart)
    elif chart["type"] in (
        "area",
        "line",
        "spline",
        "column",
        "bar",
    ):
        json_data = get_data(name="get_line", dd=chart)

    return HttpResponse(json_data[0], content_type="application/json")
