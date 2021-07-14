from django.urls import path
from .views import product_hook

urlpatterns = [
    path("webhook/<str:object>/<str:action>", product_hook),
]
