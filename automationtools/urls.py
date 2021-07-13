from django.urls import path
from .views import product_hook

urlpatterns = [
    path("product/<str:action>", product_hook),
]
