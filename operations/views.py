import simplejson as json
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.views import generic
from .admin import convert_weight
from django.contrib.auth.decorators import login_required
from . import forms, models


@login_required
def make_soap(request):
    return render(
        request, 
        "operations/make-soap.html", 
        context={}
    )

@login_required
def get_products(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT
                JSON_AGG(jsonb_build_object('value', id, 'text', description || ' (' || sku || ')'))::TEXT as json_data
            FROM
                public.operations_product p
            WHERE
                product_type IN ('Finished Goods', 'WIP') AND
                _active = TRUE
            ;
        """
        cursor.execute(sql)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data , content_type="application/json")

@login_required
def get_materials(request):
    print(request.GET.getlist("skus[]"), 'x' * 50)
    print(request.GET)
    sku_list = [int(x) for x in request.GET.getlist("skus[]")]

    with connection.cursor() as cursor:
        sql = """
            SELECT
                JSONB_AGG(json)
            FROM
                (
                SELECT 
                    (select row_to_json(_) from (select product_id, product_description, family, sku, description, unit_of_measure, quantity_needed::NUMERIC(16, 5), total_cost::NUMERIC(16, 5), quantity_onhand::NUMERIC(16, 5)) as _) as json
                FROM
                    public.vw_recipes
                WHERE
                    product_id = ANY(%s)
            ) s
            ;
        """
        cursor.execute(sql, [sku_list])
        json_data = cursor.fetchall()[0][0]
    
    return HttpResponse(json_data , content_type="application/json")

