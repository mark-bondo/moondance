from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Shopify_Product,
    Amazon_Product,
    Nexternal_Product,
    Product_Missing_SKU,
)


@admin.register(Shopify_Product)
class Shopify_Product_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Shopify_Product
    list_display = [
        "variant_id",
        "shopify_sku",
        "product",
        "status",
        "title",
        "inventory_management",
        "customer_type",
    ]
    history_list_display = [
        "variant_id",
        "shopify_sku",
        "product",
        "status",
        "title",
        "inventory_management",
        "customer_type",
    ]
    fields = (
        "variant_id",
        "shopify_sku",
        "product",
        "status",
        "title",
        "inventory_policy",
        "inventory_management",
        "grams",
        "price",
        "customer_type",
        "handle",
    )
    readonly_fields = ("variant_id",)
    list_editable = [
        "product",
    ]
    search_fields = [
        "product__sku",
        "shopify_sku",
        "variant_id",
    ]
    list_filter = [
        "status",
        "inventory_management",
    ]
    autocomplete_fields = [
        "product",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("product")
        return qs


@admin.register(Nexternal_Product)
class Nexternal_Product_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Nexternal_Product
    list_display = [
        "sku",
        "product",
        "sku_description",
    ]
    fields = (
        "sku",
        "sku_description",
        "product",
    )
    list_editable = [
        "product",
    ]
    autocomplete_fields = [
        "product",
    ]
    search_fields = [
        "sku",
        "sku_description",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("product")


@admin.register(Amazon_Product)
class Amazon_Product_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Amazon_Product
    list_display = [
        "asin",
        "product",
        "sku_description",
    ]
    fields = (
        "asin",
        "sku_description",
        "product",
    )
    list_editable = [
        "product",
    ]
    autocomplete_fields = [
        "product",
    ]
    search_fields = [
        "asin",
        "sku_description",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("product")


@admin.register(Product_Missing_SKU)
class Product_Missing_SKU_Admin(AdminStaticMixin):
    model = Product_Missing_SKU
    save_as = True
    list_display = [
        "id",
        "source_system",
        "product_description",
        "product",
    ]
    list_editable = [
        "source_system",
        "product_description",
        "product",
    ]
    autocomplete_fields = [
        "product",
    ]
    fields = (
        "source_system",
        "product_description",
        "product",
    )

    def save_formset(self, request, form, formset, change):
        # set meta fields
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()
