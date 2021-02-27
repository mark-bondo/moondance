import decimal
import django.urls as urlresolvers
from django.utils.safestring import mark_safe
from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Inventory_Onhand,
    Supplier,
    Supplier_Product,
    Raw_Material_Proxy,
    Invoice,
    Invoice_Line,
)
from .forms import(
    Inventory_Onhand_Form
)

def get_sku_quantity(sku_id):
    total_quantity = 0
    
    for q in Inventory_Onhand.objects.filter(sku_id=sku_id):
        total_quantity += q.quantity_onhand or 0
    
    return total_quantity


@admin.register(Inventory_Onhand)
class Inventory_Onhand_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Inventory_Onhand
    form = Inventory_Onhand_Form
    list_display = [
        "sku",
        "location",
        "quantity_onhand",
        "unit_of_measure",
        "to_location",
        "transfer_quantity",
        # "_last_updated",
    ]
    list_editable = [
        "quantity_onhand",
        "to_location",
        "transfer_quantity",
    ]
    list_filter = [
        "location",
    ]
    search_fields = [
        "sku__description",
        "sku__sku"
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
    fieldsets = (
        (
            "Current Inventory",
            {
                "fields": (
                    "sku",
                    "location",
                    "quantity_onhand",
                    "unit_of_measure",
                )
            },
        ),
        (
            "Transfer Inventory",
            {
                "fields": (
                    "to_location",
                    "transfer_quantity",
                )
            },
        ),
    )
    readonly_fields = (
        "_last_updated",
        "unit_of_measure",
    )

    def unit_of_measure(self, obj):
        return obj.sku.unit_of_measure

    def get_changelist_form(self, request, **kwargs):
        kwargs['form'] = Inventory_Onhand_Form
        return super().get_changelist_form(request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)

        # recalculate inventory weights and costs
        location_inventory = Inventory_Onhand.objects.filter(sku=obj.sku)
        total_quantity_onhand = 0

        for i in location_inventory:
            total_quantity_onhand += (i.quantity_onhand or 0)

        parent_obj = Raw_Material_Proxy.objects.get(pk=obj.sku.id)
        parent_obj.total_quantity_onhand = total_quantity_onhand
        parent_obj.total_material_cost = total_quantity_onhand * parent_obj.unit_material_cost
        parent_obj.total_freight_cost = (decimal.Decimal(parent_obj.product_code.freight_factor_percentage or 0) / decimal.Decimal(100)) * parent_obj.total_material_cost
        parent_obj.total_cost = parent_obj.total_material_cost + (parent_obj.total_freight_cost or 0)
        parent_obj.save()

        # move inventory
        if obj.to_location:
            to_location = Inventory_Onhand.objects.get_or_create(
                sku=obj.sku,
                location=obj.to_location,
                defaults={
                    "quantity_onhand": 0,
                }
            )
            to_location[0].quantity_onhand += obj.transfer_quantity
            to_location[0].transfer_quantity = None
            to_location[0].to_location = None
            to_location[0].save()

            from_location = obj
            from_location.quantity_onhand -= obj.transfer_quantity
            from_location.transfer_quantity = None
            from_location.to_location = None
            from_location.save()


class Supplier_Product_Admin_Inline(admin.TabularInline):
    model = Supplier_Product
    extra = 1
    fields = (
        "supplier",
        "supplier_sku",
        "supplier_sku_description",
        "sku",
        "supplier_sku_link",
    )
    autocomplete_fields = [
        "sku",
    ]


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
class Invoice_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Invoice
    inlines = (Invoice_Line_Inline,)
    list_display = [
        "date_invoiced",
        "supplier",
        "invoice",
        "order",
        "freight_charges",
        "material_cost",
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
        "date_invoiced",
        "invoice",
        "order",
        "freight_charges",
        "material_cost",
        "total_cost",
    )
    readonly_fields = (
        "total_cost",
        "material_cost",
    )

    def total_cost(self, obj):
        invoice_lines = Invoice_Line.objects.filter(invoice=obj.pk).select_related()
        total_cost = (obj.freight_charges or 0)

        for row in invoice_lines:
            total_cost += (row.total_cost or 0)

        return round(total_cost, 2)

    def material_cost(self, obj):
        invoice_lines = Invoice_Line.objects.filter(invoice=obj.pk).select_related()
        total_cost = 0

        for row in invoice_lines:
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