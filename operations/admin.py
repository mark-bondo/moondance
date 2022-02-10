import decimal
import django.urls as urlresolvers
from django.utils.safestring import mark_safe
from django.contrib import admin
from utils import common
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from purchasing.models import Invoice_Line
from .models import (
    Product_Code,
    Product,
    Recipe_Line,
    Order_Cost_Overlay,
)
from purchasing.admin import Supplier_Product_Admin_Inline


@admin.register(Product_Code)
class Product_Code_Admin(admin.ModelAdmin):
    model = Product_Code
    save_as = True

    list_display = [
        "type",
        "family",
        "category",
        "freight_factor_percentage",
        "_active",
    ]
    list_filter = [
        "_active",
        "type",
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
                    "type",
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

        if obj.original_freight_factor_percentage != obj.freight_factor_percentage:
            products = Product.objects.filter(product_code=obj)

            for p in products:
                p.unit_freight_cost = (p.unit_material_cost or 0) * (
                    (obj.freight_factor_percentage or 0) / decimal.Decimal(100)
                )
                p.save()

        super().save_model(request, obj, form, change)


class Recipe_Line_Inline_Admin(admin.TabularInline):
    model = Recipe_Line
    fk_name = "sku_parent"
    fields = (
        "product_code",
        "sku",
        "modify_link",
        "quantity",
        "unit_of_measure",
        "unit_cost",
        "extended_cost",
        "_active",
    )
    history_list_display = [
        "sku",
        "modify_link",
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
    readonly_fields = (
        "unit_cost",
        "extended_cost",
        "modify_link",
        "product_code",
    )

    def product_code(self, obj):
        return obj.sku.product_code.family

    def modify_link(self, obj):
        """Generates link to the view for the line item"""
        app = obj._meta.app_label
        url_str = "admin:{}_{}_change".format(app, "product")
        url = urlresolvers.reverse(url_str, args=[obj.sku_id])
        return mark_safe('<a href="{}">Modify</a>'.format(url))

    modify_link.allow_tags = True
    modify_link.short_description = "Modify Link"


class Invoice_Line_Inline(admin.TabularInline):
    model = Invoice_Line
    fields = (
        "total_cost",
        "quantity",
        "unit_of_measure",
        "manufacturer",
    )
    readonly_fields = (
        "total_cost",
        "quantity",
        "unit_of_measure",
        "manufacturer",
    )


@admin.register(Product)
class Product_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Product
    inlines = (
        # Product_Cost_History_Inline_Admin,
        Invoice_Line_Inline,
        Recipe_Line_Inline_Admin,
        Supplier_Product_Admin_Inline,
    )
    save_as = True

    list_display = [
        "sku",
        "description",
        "product_code",
        "unit_cost_total",
        "onhand_quantity",
        "sales_channel_type",
        "unit_of_measure",
        "_active",
    ]
    list_editable = [
        "sales_channel_type",
        "unit_of_measure",
        "_active",
    ]
    history_list_display = [
        "sku",
        "description",
        "sales_channel_type",
        "_active",
        "product_code",
        "unit_of_measure",
        "unit_cost_total",
        "onhand_quantity",
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
        "product_code__type",
        "product_code__family",
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "sku",
                    "description",
                    "sales_channel_type",
                    "unit_of_measure",
                    "product_code",
                    "onhand_quantity",
                    "total_cost",
                    "_active",
                    "notes",
                ]
            },
        ),
        (
            "Current Costing",
            {
                "fields": [
                    # "unit_sales_price",
                    "unit_material_cost",
                    "unit_labor_cost",
                    "unit_freight_cost",
                    "unit_cost_total",
                ]
            },
        ),
    )

    def add_view(self, request, form_url="", extra_context=None):
        self.inlines = []

        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.model.objects.get(pk=object_id)

        if obj.product_code:
            if obj.product_code.type in ("Finished Goods"):
                self.inlines = [
                    Recipe_Line_Inline_Admin,
                    Supplier_Product_Admin_Inline,
                ]
            elif obj.product_code.type in ("Raw Materials"):
                self.inlines = [
                    Supplier_Product_Admin_Inline,
                ]
            elif obj.product_code.type in ("Labor Groups", "WIP"):
                self.inlines = [
                    Recipe_Line_Inline_Admin,
                ]
            else:
                self.inlines = []
        else:
            self.inlines = []

        return super().change_view(request, object_id, form_url, extra_context)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = (
            "unit_cost_total",
            "onhand_quantity",
            "_last_updated",
            "total_cost",
            "_created",
            "_created_by",
        )

        if obj and obj.product_code:
            ptype = obj.product_code.type
            if ptype in (
                "WIP",
                "Labor Groups",
            ):
                readonly_fields += (
                    "unit_material_cost",
                    "unit_labor_cost",
                )
            elif ptype == "Labor":
                readonly_fields += ("unit_material_cost",)
            elif ptype == "Raw Materials":
                readonly_fields += ("unit_labor_cost",)
        return readonly_fields

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("product_code")

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        freight = (
            obj.product_code.freight_factor_percentage
            if obj.product_code and obj.product_code.freight_factor_percentage
            else 0
        ) / decimal.Decimal(100)
        obj.unit_freight_cost = (obj.unit_material_cost or 0) * freight
        obj.save()

    def save_formset(self, request, form, formset, change):
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

        if formset.model == Recipe_Line:
            common.recalculate_bom_cost(form.instance.id)


@admin.register(Order_Cost_Overlay)
class Order_Cost_Overlay_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Order_Cost_Overlay
    save_as = True

    list_display = [
        "sales_channel",
        "name",
        "type",
        "apply_to",
        "labor_hourly_rate",
        "labor_minutes",
        "material_cost",
        "sales_percentage",
        "_active",
    ]
    history_list_display = [
        "sales_channel",
        "name",
        "type",
        "apply_to",
        "labor_hourly_rate",
        "labor_minutes",
        "material_cost",
        "sales_percentage",
        "_active",
    ]
    fields = (
        "sales_channel",
        "name",
        "type",
        "apply_to",
        "labor_hourly_rate",
        "labor_minutes",
        "material_cost",
        "sales_percentage",
        "_active",
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
