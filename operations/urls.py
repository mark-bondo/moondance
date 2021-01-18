from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from .views import get_products, get_materials, make_soap

urlpatterns = [
    # path("", operations_home),
    path("make-soap/", make_soap),
    path("recipes/", get_products),
    path("get-materials/", get_materials),
]