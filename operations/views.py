from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
from .models import recalculate_bom_cost

SQL_DD = {}


def get_data(name, args={}, dd={}):
    if name not in SQL_DD:
        with open(f"moondance/templates/operations/sql/{name}.sql", "r") as f:
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
def recalculate_cost(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT DISTINCT
                product_id
            FROM
                staging.products
            ;
        """
        cursor.execute(sql)
        products = cursor.fetchall()

    for p in products:
        recalculate_bom_cost(p[0])

    return HttpResponse(products, content_type="application/json")


@login_required
def get_product_families(request):
    json_data = get_data(name="get_product_families")
    return HttpResponse(json_data[0], content_type="application/json")


@login_required
def get_product_data(request, family):
    json_data = get_data(name="get_product_data", args={"family": family})
    return HttpResponse(json_data[0], content_type="application/json")


@login_required
def get_pie(request, group):
    dd = {"group": group, "filters": "", "yaxis": "net_sales"}

    json_data = get_data(name="get_pie", dd=dd)
    return HttpResponse(json_data[0][0], content_type="application/json")


@login_required
def make_soap(request):
    return render(request, "operations/make-soap.html", context={})


@login_required
def get_products(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT
                JSON_AGG(jsonb_build_object('value', p.id, 'text', p.description || ' (' || p.sku || ')'))::TEXT as json_data
            FROM
                public.operations_product p
                JOIN public.operations_product_code pcode ON p.product_code_id = pcode.id
            WHERE
                pcode.type IN ('Finished Goods', 'WIP', 'Labor Groups') AND
                p._active = TRUE
            ;
        """
        cursor.execute(sql)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data, content_type="application/json")


@login_required
def get_materials(request):
    sku_list = [int(x) for x in request.GET.getlist("skus[]")]
    json_data = get_data(name="get_bom", args={"sku_list": sku_list})

    return HttpResponse(json_data[0][0], content_type="application/json")
