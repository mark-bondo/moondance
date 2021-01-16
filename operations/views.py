import simplejson as json
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.views import generic
from .admin import convert_weight
from . import forms, models


def operations_home(request):
    return render(
        request, 
        "operations/home.html", 
        context={}
    )


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


def get_recipe(request, id):
    with connection.cursor() as cursor:
        sql = """
            SELECT
                JSONB_AGG(json)
            FROM
                (
                SELECT 
                    (select row_to_json(_) from (select family, sku, description, unit_of_measure, quantity_needed, total_cost) as _) as json
                FROM
                    public.vw_recipes
                WHERE
                    product_id = %s
            ) s
            ;
        """
        cursor.execute(sql, [id])
        json_data = cursor.fetchall()[0][0]
    
    return HttpResponse(json_data , content_type="application/json")

