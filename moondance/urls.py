from django.contrib import admin
from django.urls import path, include
from automationtools.views import report_home, get_top_sellers
from operations.views import get_products, get_product_families, get_product_data

urlpatterns = [
    # path("", render_home),
    path("", admin.site.urls),
    path("admin/", admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path("operations/", include("operations.urls")),
    path("reports/", report_home),
    path("reports/top-sellers/", get_top_sellers),
    path("product/", get_products),
    path("product-data/<str:family>", get_product_data),
    path("product-family/", get_product_families),
]

# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
