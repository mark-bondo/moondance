from django.contrib import admin
from meta_models import set_meta_fields
from .models import (
    Product,
    Product_Code,
    Inventory_Onhand,
    Amazon_Product,
    Shopify_Product,
    Supplier,
    Supplier_Product,
    Materials_Management_Proxy
)
from .forms import Materials_Management_Proxy_Form


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
    list_filter = [
        "_active",
        "family",
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
        "_active",
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
        "_active",
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



class Supplier_Product_Admin_Inline(admin.TabularInline):
    model = Supplier_Product
    extra = 1
    fields = (
        "supplier",
        "supplier_sku",
        "supplier_sku_description",
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

class Amazon_Product_Admin_Inline(admin.TabularInline):
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

class Shopify_Product_Admin_Inline(admin.TabularInline):
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

class Inventory_Onhand_Admin_Inline(admin.TabularInline):
    model = Inventory_Onhand
    extra = 1
    fields = (
        "location",
        "quantity_onhand",
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


@admin.register(Materials_Management_Proxy)
class Materials_Management_Proxy_Admin(admin.ModelAdmin):
    model = Materials_Management_Proxy
    form = Materials_Management_Proxy_Form
    inlines = (
        Inventory_Onhand_Admin_Inline,
        Supplier_Product_Admin_Inline,
    )

    list_display = [
        "sku",
        "description",
        "_active",
        "product_type",
        "product_code",
        "unit_of_measure",
        "quantity_onhand",
        "unit_cost",
        "total_cost",
    ]
    autocomplete_fields = [
        "product_code",
    ]
    search_fields = [
        "sku",
        "upc",
        "description",
        "product_code__category",
        "product_code__family",
    ]
    list_filter = [
        ("_active", admin.BooleanFieldListFilter),
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
                    "unit_cost",
                    "unit_of_measure",
                    "quantity_onhand",
                    "_active",
                ]
            },
        ),
        # (
        #     "Change History",
        #     {
        #         "fields": (
        #             "_last_updated",
        #             "_last_updated_by",
        #             "_created",
        #             "_created_by",
        #         )
        #     },
        # ),
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
        "quantity_onhand",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(product_type__in=["WIP", "Raw Materials"])

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in instances:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "category":
    #         kwargs["queryset"] = Category.objects.filter(name__in=['God', 'Demi God'])
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


