import decimal
import django.urls as urlresolvers
from django.utils.safestring import mark_safe
from django.contrib import admin
from meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
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



def update_inventory(instance):
    location_instance = Inventory_Onhand.objects.filter(sku=instance)
    total_inventory_onhand = 0

    for i in location_instance:
        total_inventory_onhand += (i.quantity_onhand or 0)
    
    instance.total_quantity_onhand = total_inventory_onhand
    instance.total_material_cost = (total_inventory_onhand * (instance.unit_material_cost or 0))
    instance.total_freight_cost = (decimal.Decimal(Product.objects.get(pk=instance.pk).product_code.freight_factor_percentage or 0) / decimal.Decimal(100)) * instance.total_material_cost
    instance.total_cost = instance.total_material_cost + (instance.total_freight_cost or 0)
    instance.save()

@admin.register(Product_Code)
class Product_Code_Admin(admin.ModelAdmin):
    model = Product_Code
    list_display = [
        "_active",
        "family",
        "category",
        "freight_factor_percentage",
    ]
    list_editable = [
        "family",
        "category",
        "freight_factor_percentage",
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
                    "freight_factor_percentage",
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


class Supplier_Product_Admin_Inline(admin.TabularInline):
    model = Supplier_Product
    extra = 1
    fields = (
        "supplier",
        "supplier_sku",
        "supplier_sku_description",
        "_last_updated",

    )
    autocomplete_fields = [
        "supplier",
    ]
    readonly_fields = (
        "_last_updated",
    )


@admin.register(Supplier)
class Supplier_Admin(SimpleHistoryAdmin):
    model = Supplier
    inlines = (Supplier_Product_Admin_Inline,)
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
    history_list_display = [
        "name",
        "_active",
        "contact_name",
        "contact_email",
        "street_address",
        "city",
        "state",
        "postal_code",
        "country",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
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
        )
    )

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

@admin.register(Inventory_Onhand)
class Inventory_Onhand_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Inventory_Onhand
    list_display = [
        "sku",
        "location",
        "quantity_onhand",
        "_last_updated",
    ]
    list_editable = [
        "quantity_onhand",
    ]
    list_filter = [
        "location",
    ]
    autocomplete_fields = [
        "sku",
    ]
    history_list_display = [
        "sku",
        "location",
        "quantity_onhand",
        "_last_updated",
    ]
    fields = (
        "sku",
        "location",
        "quantity_onhand",
    )

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)

        instance = Materials_Management_Proxy.objects.get(pk=obj.sku.id)
        update_inventory(instance=instance)
    # def save_formset(self, request, form, formset, change):
    #     instances = formset.save(commit=False)

    #     for obj in instances:
    #         obj = set_meta_fields(request, obj, form, change, inline=True)
    #         obj.save()

    #     for obj in formset.deleted_objects:
    #         obj.delete()

    #     formset.save_m2m()
    #     update_inventory(instance=form.instance)


class Inventory_Onhand_Admin_Inline(admin.TabularInline):
    model = Inventory_Onhand
    extra = 1
    fields = (
        "sku",
        "location",
        "quantity_onhand",
        "history_link",
    )
    readonly_fields = (
        "history_link",
    )

    def history_link(self, obj):
        """
        Generate a link to the history view for the line item.
        """
        app = obj._meta.app_label
        url_str = "admin:{}_{}_history".format(app, "inventory_onhand")
        url = urlresolvers.reverse(url_str, args=[obj.id])
        return mark_safe(u'<a href="{}">Change History Link</a>'.format(url))

    history_link.allow_tags = True
    history_link.short_description = "History"

@admin.register(Materials_Management_Proxy)
class Materials_Management_Proxy_Admin(AdminStaticMixin, SimpleHistoryAdmin):
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
        "total_quantity_onhand",
        "unit_material_cost",
        "total_cost",
    ]
    history_list_display = [
        "sku",
        "description",
        "_active",
        "product_type",
        "product_code",
        "unit_of_measure",
        "total_quantity_onhand",
        "unit_material_cost",
        "total_cost",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    ]
    autocomplete_fields = [
        "product_code",
    ]
    search_fields = [
        "sku",
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
                    "description",
                    "product_type",
                    "product_code",
                    "unit_of_measure",
                    "unit_material_cost",
                    "total_material_cost",
                    "total_freight_cost",
                    "total_cost",
                    "total_quantity_onhand",
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
        "total_quantity_onhand",
        "total_material_cost",
        "total_freight_cost",
        "total_cost",
    )

    # def total_material_cost(self, obj):
    #     return obj._hero_count

    # total_material_cost.admin_order_field = '_hero_count'

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

        if formset.model == Inventory_Onhand:
            # location_inventory = Inventory_Onhand.objects.filter(sku=form.instance)
            # total_inventory_onhand = 0

            # for i in location_inventory:
            #     total_inventory_onhand += (i.quantity_onhand or 0)
            
            # form.instance.total_quantity_onhand = total_inventory_onhand
            # form.instance.total_material_cost = (total_inventory_onhand * (form.instance.unit_material_cost or 0))
            # form.instance.total_freight_cost = (decimal.Decimal(Product.objects.get(pk=form.instance.pk).product_code.freight_factor_percentage or 0) / decimal.Decimal(100)) * form.instance.total_material_cost
            # form.instance.total_cost = form.instance.total_material_cost + (form.instance.total_freight_cost or 0)
            # form.instance.save()

            update_inventory(instance=form.instance)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "category":
    #         kwargs["queryset"] = Category.objects.filter(name__in=['God', 'Demi God'])
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


