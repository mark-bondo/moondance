from django.urls import path
from .views import product_hook

urlpatterns = [
    path("products/<str:action>", product_hook),
]
