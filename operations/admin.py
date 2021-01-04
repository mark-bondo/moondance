from django.contrib import admin
from .models import Product, Product_Code, Amazon_Product, Shopify_Product, Supplier

@admin.register(Product_Code)
class Product_Code_Admin(admin.ModelAdmin):
    model = Product_Code
    list_display = [
        "_active",
        "family",
        "category",
    ]
    list_editable = [
        "family",
        "category",
    ]
    search_fields = [
        "family",
        "category",
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "family",
                    "category",
                    "_active",
                ]
            },
        ),
        (
            "Change History",
            {
                "fields": (
                    "_last_updated",
                    "_last_updated_by",
                    "_created",
                    "_created_by",
                )
            },
        ),
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )


@admin.register(Supplier)
class Supplier_Admin(admin.ModelAdmin):
    model = Supplier
    list_display = [
        "name",
        "contact_name",
        "contact_email",
        "street_address",
        "city",
        "state",
        "postal_code",
        "country",
    ]
    search_fields = [
        "name",
        "contact_name",
    ]
    list_filter = [
        "state",
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "name",
                    "contact_name",
                    "contact_email",
                    "notes",
                    "_active",
                ]
            },
        ),
        (
            "Address",
            {
                "fields": [
                    "street_address",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                ]
            },
        ),
        (
            "Change History",
            {
                "fields": (
                    "_last_updated",
                    "_last_updated_by",
                    "_created",
                    "_created_by",
                )
            },
        ),
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )

class Amazon_Product_Admin(admin.TabularInline):
    model = Amazon_Product
    extra = 1
    fields = (
        "asin",
        "_active",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )

class Shopify_Product_Admin(admin.TabularInline):
    model = Shopify_Product
    extra = 1
    fields = (
        "shopify_product_id",
        "_active",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )

@admin.register(Product)
class Product_Admin(admin.ModelAdmin):
    model = Product
    inlines = (
        Shopify_Product_Admin,
        Amazon_Product_Admin
    )

    list_display = [
        "sku",
        "description",
        "product_type",
        "product_code",
        "unit_of_measure",
        "quantity_onhand",
        "unit_weight",
        "unit_price",
        "unit_cost",
    ]
    search_fields = [
        "sku",
        "upc",
        "description",
        "product_code__category",
        "product_code__family",
    ]
    list_filter = [
        "product_type",
        "product_code",
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "sku",
                    "product_type",
                    "product_code",
                    "description",
                    "upc",
                    "_active",
                ]
            },
        ),
        (
            "Weights & Measures",
            {
                "fields": [
                    "unit_of_measure",
                    "unit_weight",
                    "unit_price",
                    "unit_cost",
                    "quantity_onhand",
                ]
            },
        ),

        (
            "Change History",
            {
                "fields": (
                    "_last_updated",
                    "_last_updated_by",
                    "_created",
                    "_created_by",
                )
            },
        ),
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
        "quantity_onhand"
    )


