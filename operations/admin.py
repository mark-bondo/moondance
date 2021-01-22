import decimal
import django.urls as urlresolvers
from django.utils.safestring import mark_safe
from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Recipe_Line,
    Recipe_Proxy,
    Product,
    Product_Code,
    Inventory_Onhand,
    Amazon_Product,
    Shopify_Product,
    Supplier,
    Supplier_Product,
    Materials_Management_Proxy,
    Invoice,
    Invoice_Line
)
from .forms import Materials_Management_Proxy_Form


def convert_weight(unit_of_measure, weight):
    if unit_of_measure == "oz":
        return {
            "grams": weight * decimal.Decimal(28.3495),
            "lbs": weight / decimal.Decimal(16),
            "oz": weight
        }
    elif unit_of_measure == "lbs":
        return {
            "grams":  weight * decimal.Decimal(453.592),
            "lbs": weight,
            "oz": weight * decimal.Decimal(16)
        }
    elif unit_of_measure == "grams":
        return {
            "grams":  weight,
            "lbs": weight * decimal.Decimal(453.592),
            "oz": weight / decimal.Decimal(28.3495)
        }


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

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)

        if obj.original_freight_factor_percentage != obj.freight_factor_percentage:
            skus = Materials_Management_Proxy.objects.filter(product_code=obj.pk)

            for sku in skus:
                sku.unit_freight_cost = (sku.unit_material_cost or 0) * ((obj.freight_factor_percentage or 0)  / decimal.Decimal(100))
                sku.save()


class Supplier_Product_Admin_Inline(admin.TabularInline):
    model = Supplier_Product
    extra = 1
    fields = (
        "supplier",
        "supplier_sku",
        "supplier_sku_description",
        "sku",
        "supplier_sku_link",
        # "_last_updated",

    )
    autocomplete_fields = [
        "sku",
    ]
    # readonly_fields = (
    #     "_last_updated",
    # )


@admin.register(Supplier)
class Supplier_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Supplier
    inlines = (Supplier_Product_Admin_Inline,)
    list_display = [
        "name",
        "type",
        "_active",
        "supplier_website",
        "contact_name",
        "contact_email",
        "phone_number",
        "city",
        "state",
    ]
    history_list_display = [
        "name",
        "type",
        "_active",
        "supplier_website",
        "contact_name",
        "contact_email",
        "phone_number",
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
        "contact_email",
    ]
    list_filter = [
        "_active",
        "type",
        "state",
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "type",
                    "name",
                    "supplier_website",
                    "contact_name",
                    "contact_email",
                    "phone_number",
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

        # recalculate inventory weights and costs
        location_inventory = Inventory_Onhand.objects.filter(sku=obj.sku)
        total_quantity_onhand = 0

        for i in location_inventory:
            total_quantity_onhand += (i.quantity_onhand or 0)

        parent_obj = Materials_Management_Proxy.objects.get(pk=obj.sku.id)
        parent_obj.total_quantity_onhand = total_quantity_onhand
        parent_obj.total_material_cost = total_quantity_onhand * parent_obj.unit_material_cost
        parent_obj.total_freight_cost = (decimal.Decimal(parent_obj.product_code.freight_factor_percentage or 0) / decimal.Decimal(100)) * parent_obj.total_material_cost
        parent_obj.total_cost = parent_obj.total_material_cost + (parent_obj.total_freight_cost or 0)
        parent_obj.save()


class Invoice_Line_History_Inline(admin.TabularInline):
    model = Invoice_Line
    extra = 1
    fields = (
        "unit_of_measure",
        "quantity",
        "total_cost",
    )
    readonly_fields = (
        "unit_of_measure",
        "quantity",
        "total_cost",
    )


class Inventory_Onhand_Admin_Inline(admin.TabularInline):
    model = Inventory_Onhand
    extra = 1
    fields = (
        "sku",
        "location",
        "quantity_onhand",
        "unit_of_measure",
        "history_link",
    )
    readonly_fields = (
        "unit_of_measure",
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
        Invoice_Line_History_Inline,
        Supplier_Product_Admin_Inline,
    )
    save_as = True

    list_display = [
        "sku",
        "description",
        "_active",
        "product_type",
        "product_code",
        "unit_of_measure",
        "onhand_quantity",
        "unit_cost_total",
        "total_cost"
    ]
    history_list_display = [
        "sku",
        "description",
        "_active",
        "product_type",
        "product_code",
        "unit_of_measure",
        "onhand_quantity",
        "unit_material_cost",
        "unit_freight_cost",
        "unit_cost_total",
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
                    "onhand_quantity",
                    ("unit_material_cost", "total_material_cost"),
                    ("unit_freight_cost", "total_freight_cost"),
                    ("unit_cost_total", "total_cost"),
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
        "unit_freight_cost",
        "unit_cost_total",
        "onhand_quantity",
        "total_material_cost",
        "total_freight_cost",
        "total_cost",
        "_last_updated",
        "total_cost",
        "_created",
        "_created_by",
    )

    def unit_cost_total(self, obj):
        return (obj.unit_material_cost or 0) + (obj.unit_freight_cost or 0)

    def get_quantity(self, sku_id):
        total_quantity = 0
        
        for q in Inventory_Onhand.objects.filter(sku_id=sku_id):
            total_quantity += q.quantity_onhand or 0
        
        return total_quantity

    def onhand_quantity(self, obj):
        return self.get_quantity(obj.pk)

    def total_material_cost(self, obj):
        return (obj.unit_material_cost or 0) * self.get_quantity(obj.pk)

    def total_freight_cost(self, obj):
        return (obj.unit_freight_cost or 0) * self.get_quantity(obj.pk)

    def total_cost(self, obj):
        return (obj.unit_material_cost or 0) * self.get_quantity(obj.pk)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(product_type__in=["WIP", "Raw Materials"])

    def save_formset(self, request, form, formset, change):
        # set meta fields
        parent_obj = set_meta_fields(request, form.instance, form, change)
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

        # recalculate inventory weights and costs
        if formset.model == Inventory_Onhand:
            location_inventory = Inventory_Onhand.objects.filter(sku=form.instance)
            total_quantity_onhand = 0
            total_cost_previous_unit_of_measure = 0

            for i in location_inventory:
                total_cost_previous_unit_of_measure += i.quantity_onhand * parent_obj.original_unit_material_cost

                if parent_obj.original_unit_of_measure != parent_obj.unit_of_measure:
                    new_weight_dict = convert_weight(unit_of_measure=parent_obj.original_unit_of_measure, weight=i.quantity_onhand)
                    i.quantity_onhand = new_weight_dict[parent_obj.unit_of_measure]
                
                i.unit_of_measure = parent_obj.unit_of_measure
                i.save()

                total_quantity_onhand += (i.quantity_onhand or 0)

            if parent_obj.original_unit_of_measure != parent_obj.unit_of_measure and parent_obj.unit_of_measure != 'each':
                if location_inventory:
                    parent_obj.unit_material_cost = total_cost_previous_unit_of_measure / total_quantity_onhand
                else:
                    new_weight_dict = convert_weight(unit_of_measure=parent_obj.unit_of_measure, weight=parent_obj.unit_material_cost)
                    parent_obj.unit_material_cost = new_weight_dict[parent_obj.original_unit_of_measure]


            parent_obj.total_quantity_onhand = total_quantity_onhand
            parent_obj.total_material_cost = total_quantity_onhand * parent_obj.unit_material_cost
            parent_obj.total_freight_cost = (decimal.Decimal(parent_obj.product_code.freight_factor_percentage or 0) / decimal.Decimal(100)) * parent_obj.total_material_cost
            parent_obj.total_cost = parent_obj.total_material_cost + (parent_obj.total_freight_cost or 0)
            parent_obj.save()


class Recipe_Line_Inline_Admin(admin.TabularInline):
    model = Recipe_Line
    fk_name = "sku_parent"
    fields = (
        "sku",
        "quantity",
        "unit_of_measure",
        "cost",
        "_active",
    )
    readonly_fields = (
        "cost",
    )
    history_list_display = [
        "sku",
        "quantity",
        "unit_of_measure",
        "_active",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    ]
    autocomplete_fields = [
        "sku",
    ]

    def cost(self, obj):
        # print(obj.sku, obj.quantity, obj.sku.unit_material_cost)

        if obj.pk:
            if obj.unit_of_measure == 'each':
                converted_weight = obj.quantity
            else:
                new_weight_dict = convert_weight(unit_of_measure=obj.unit_of_measure, weight=obj.quantity)
                converted_weight = new_weight_dict[obj.sku.unit_of_measure]
            
        # print(obj.sku, obj.unit_of_measure, obj.quantity, converted_weight)

            return round(decimal.Decimal(obj.sku.unit_material_cost or 0) * decimal.Decimal(converted_weight or 0), 5)

@admin.register(Recipe_Proxy)
class Product_Recipe_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Recipe_Proxy
    inlines = (Recipe_Line_Inline_Admin,)
    list_display = [
        "sku",
        "description",
        "_active",
        "product_type",
        "product_code",
        "unit_of_measure",
        "unit_material_cost",
        "unit_freight_cost",
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
    history_list_display = [
        "sku",
        "description",
        "_active",
        "product_type",
        "product_code",
        "unit_of_measure",
        "unit_material_cost",
        "unit_freight_cost",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    ]
    fields = (
        "sku",
        "description",
        "unit_of_measure",
        "recipe_cost",
    )
    readonly_fields = (
        "sku",
        "description",
        "unit_of_measure",
        "recipe_cost",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(product_type__in=["WIP", "Finished Goods"])

    def recipe_cost(self, obj):
        cost = Recipe_Line.objects.filter(sku_parent=obj.pk).select_related()
        recipe_cost = 0

        for c in cost:
            # print(c.sku, c.sku.unit_of_measure, c.sku.unit_material_cost)

            if c.unit_of_measure == 'each':
                converted_weight = c.quantity
            else:
                new_weight_dict = convert_weight(unit_of_measure=c.unit_of_measure, weight=c.quantity)
                converted_weight = new_weight_dict[c.sku.unit_of_measure]
            
            recipe_cost += (c.sku.unit_material_cost or 0) * (converted_weight or 0)

        return round(recipe_cost, 5)

    def save_formset(self, request, form, formset, change):
        # set meta fields
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

class Invoice_Line_Inline(admin.TabularInline):
    model = Invoice_Line
    fields = (
        "sku",
        "unit_of_measure",
        "quantity",
        "total_cost",
        "manufacturer",
    )
    history_list_display = [
        "sku",
        "unit_of_measure",
        "quantity",
        "total_cost",
        "manufacturer",
        "_active",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    ]
    autocomplete_fields = [
        "sku",
        "manufacturer",
    ]

@admin.register(Invoice)
class Invocie_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Invoice
    inlines = (Invoice_Line_Inline,)
    list_display = [
        "date_invoiced",
        "supplier",
        "invoice",
        "order",
        "freight_charges",
        "total_cost"
    ]
    search_fields = [
        "supplier__name",
        "invoice",
        "order",
    ]
    list_filter = (
        ("supplier", admin.RelatedOnlyFieldListFilter),
        "date_invoiced"
    )
    autocomplete_fields = [
        "supplier",
    ]
    history_list_display = [
        "date_invoiced",
        "supplier",
        "invoice",
        "order",
        "freight_charges",
        "total_cost",
        "_active",
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    ]
    fields = (
        "supplier",
        "invoice",
        "order",
        "date_invoiced",
        "freight_charges",
        "total_cost",
    )
    readonly_fields = (
        "total_cost",
    )

    def total_cost(self, obj):
        invoice_lines = Invoice_Line.objects.filter(invoice=obj.pk).select_related()
        total_cost = 0  + (obj.freight_charges or 0)

        for row in invoice_lines:
            # print(c.sku, c.sku.unit_of_measure, c.sku.unit_material_cost)
            
            total_cost += (row.total_cost or 0)

        return round(total_cost, 2)

    def save_formset(self, request, form, formset, change):
        # set meta fields
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

# class Amazon_Product_Admin_Inline(admin.TabularInline):
#     model = Amazon_Product
#     extra = 1
#     fields = (
#         "asin",
#         "_active",
#         "_last_updated",
#         "_last_updated_by",
#         "_created",
#         "_created_by",
#     )
#     readonly_fields = (
#         "_last_updated",
#         "_last_updated_by",
#         "_created",
#         "_created_by",
#     )

# class Shopify_Product_Admin_Inline(admin.TabularInline):
#     model = Shopify_Product
#     extra = 1
#     fields = (
#         "shopify_product_id",
#         "_active",
#         "_last_updated",
#         "_last_updated_by",
#         "_created",
#         "_created_by",
#     )
#     readonly_fields = (
#         "_last_updated",
#         "_last_updated_by",
#         "_created",
#         "_created_by",
#     )