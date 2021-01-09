import simplejson as json
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .admin import convert_weight
from . import forms, models

def get_products(request):
    skus = models.Product.objects.filter(product_type__in=["Finished Goods", "WIP"]).order_by("description")
    
    return render(
        request, 
        "operations/recipes.html", 
        context ={
            "skus": skus
        }
    )

def get_recipe(request, id):
    recipe = models.Recipe.objects.filter(sku_parent_id=id).select_related().order_by("sku__description")
    recipe_cost = 0
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

