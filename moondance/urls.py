from django.contrib import admin
from django.urls import path, include
from moondance.views import (
    get_dashboards,
    get_chart,
    get_default_settings,
    home,
    get_wholesale_form,
)
from operations.views import (
    get_products,
    get_product_data,
)

urlpatterns = [
    path("", home),
    path("data-manager/", admin.site.urls),
    path("automationtools/", include("automationtools.urls")),
    path("operations/", include("operations.urls")),
    path("select2/", include("django_select2.urls")),
    path("product/", get_products),
    path("product-data/<str:family>", get_product_data),
    path("chart/<int:id>", get_chart),
    path("default-settings/<str:name>", get_default_settings),
    path("dashboards/", get_dashboards),
    path("wholesale/order-form/", get_wholesale_form),
]

# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns()
