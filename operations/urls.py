from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from .views import get_products, get_recipe, operations_home

urlpatterns = [
    path("", operations_home),
    path("recipes/", get_products),
    path("recipes/<int:id>/", get_recipe),
]