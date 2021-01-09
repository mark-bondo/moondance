from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from .views import get_products, get_recipe

urlpatterns = [
    path("recipes/", get_products),
    path("get-recipe/<int:id>/", get_recipe),
]