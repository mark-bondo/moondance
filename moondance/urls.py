from django.contrib import admin
from django.urls import path, include
from moondance.views import get_dashboards, get_chart, get_default_settings
from automationtools.views import report_home
from operations.views import (
    get_products,
    get_product_data,
)

urlpatterns = [
    path("", report_home),
    path("data-manager/", admin.site.urls),
    path("operations/", include("operations.urls")),
    path("select2/", include("django_select2.urls")),
    path("product/", get_products),
    path("product-data/<str:family>", get_product_data),
    path("chart/<int:id>", get_chart),
    path("default-settings/<str:name>", get_default_settings),
    path("dashboards/", get_dashboards),
]

# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
