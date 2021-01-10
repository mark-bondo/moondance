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
        cursor.execute("""
            SELECT
                JSON_AGG(jsonb_build_object('value', id, 'text', description || ' (' || sku || ')'))::TEXT as json_data
            FROM
                public.operations_product p
            WHERE
                product_type IN ('Finished Goods', 'WIP') AND
                _active = TRUE
            ;
        """)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data , content_type="application/json")


def get_recipe(request, id):
    recipe = models.Recipe.objects.filter(sku_parent_id=id).select_related().order_by("sku__description")
    recipe_list = []

    for c in recipe:
        if c.unit_of_measure == 'each':
            converted_weight = c.quantity
        else:
            new_weight_dict = convert_weight(unit_of_measure=c.unit_of_measure, weight=c.quantity)
            converted_weight = new_weight_dict[c.sku.unit_of_measure]
        
        recipe_list.append({
            "SKU": c.sku.sku,
            "Description": c.sku.description,
            "Quantity Needed": c.quantity,
            "Unit of Measure": c.unit_of_measure,
            "Cost": (c.sku.unit_material_cost or 0) * (converted_weight or 0)
        })
    
    return HttpResponse(json.dumps(recipe_list) , content_type="application/json")

