from django.contrib import admin
from django.urls import path, include
from automationtools.views import report_home
from operations.views import (
    get_products,
    get_product_families,
    get_product_data,
    get_pie,
    get_chart_data,
)

urlpatterns = [
    # path("", render_home),
    path("", report_home),
    path("data-manager/", admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path("operations/", include("operations.urls")),
    path("product/", get_products),
    path("product-data/<str:family>", get_product_data),
    path("product-family/", get_product_families),
    path("get-pie/<str:group>", get_pie),
    path("get-chart-data/", get_chart_data),
]

# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
