from django.urls import path
from .views import get_products, get_materials, make_soap, recalculate_cost

urlpatterns = [
    # path("", operations_home),
    path("make-soap/", make_soap),
    path("recipes/", get_products),
    path("get-materials/", get_materials),
    path("recalculate-cost/", recalculate_cost),
]
