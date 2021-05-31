import decimal
from django.db import connection
from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Product_Code,
    Product,
    Recipe_Line,
    Order_Cost_Overlay,
)
from purchasing.admin import Supplier_Product_Admin_Inline, get_sku_quantity
from purchasing.models import (
    Inventory_Onhand,
)


def convert_weight(to_measure, from_measure, weight):

    with connection.cursor() as cursor:
        sql = f"""
            SELECT
                (conversion_rate * {weight})::NUMERIC(16, 5) as converted_weight
            FROM
                public.making_weight_conversions
            WHERE
                from_measure = '{from_measure}' AND
                to_measure = '{to_measure}'
        """
        cursor.execute(sql)
        return cursor.fetchall()[0][0]


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
        super().save_model(request, obj, form, change)


class Recipe_Line_Inline_Admin(admin.TabularInline):
    model = Recipe_Line
    fk_name = "sku_parent"
    fields = (
        "sku",
        "quantity",
        "unit_of_measure",
        "unit_cost",
        "extended_cost",
        "_active",
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
    readonly_fields = (
        "unit_cost",
        "extended_cost",
    )

    def unit_cost(self, obj):
        converted_weight = convert_weight(
            from_measure=obj.unit_of_measure,
            to_measure=obj.sku.unit_of_measure,
            weight=1,
        )
        cost = (
            (obj.sku.unit_material_cost or 0)
            + (obj.sku.unit_labor_cost or 0)
            + (
                (obj.sku.unit_material_cost or 0)
                * (
                    (obj.sku.product_code.freight_factor_percentage or 0)
                    / decimal.Decimal(100)
                )
            )
        ) * (converted_weight or 0)
        return round(cost, 5)

    def extended_cost(self, obj):
        converted_weight = convert_weight(
            from_measure=obj.unit_of_measure,
            to_measure=obj.sku.unit_of_measure,
            weight=obj.quantity,
        )
        cost = (
            (obj.sku.unit_material_cost or 0)
            + (obj.sku.unit_labor_cost or 0)
            + (
                (obj.sku.unit_material_cost or 0)
                * (
                    (obj.sku.product_code.freight_factor_percentage or 0)
                    / decimal.Decimal(100)
                )
            )
        ) * (converted_weight or 0)
        return round(cost, 5)


@admin.register(Product)
class Product_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Product
    inlines = (
        Recipe_Line_Inline_Admin,
        Supplier_Product_Admin_Inline,
    )
    save_as = True

    list_display = [
        "sku",
        "description",
        "product_code",
        "onhand_quantity",
        "sales_channel_type",
        "unit_of_measure",
        "unit_material_cost",
        "unit_labor_cost",
        "_active",
    ]
    list_editable = [
        "sales_channel_type",
        "unit_of_measure",
        "unit_material_cost",
        "unit_labor_cost",
    ]
    history_list_display = [
        "sku",
        "description",
        "sales_channel_type",
        "_active",
        "product_code",
        "unit_of_measure",
        "onhand_quantity",
        "unit_material_cost",
        "unit_labor_cost",
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
                ]
            },
        ),
        (
            "Pricing & Costing",
            {
                "fields": [
                    "unit_sales_price",
                    "unit_material_cost",
                    "unit_labor_cost",
                    "unit_freight_cost",
                    "unit_cost_total",
                ]
            },
        ),
    )
    readonly_fields = (
        "unit_freight_cost",
        "unit_cost_total",
        "onhand_quantity",
        "unit_freight_cost",
        "_last_updated",
        "total_cost",
        "_created",
        "_created_by",
    )

    def unit_freight_cost(self, obj):
        cost = (obj.unit_material_cost or 0) * (
            (obj.product_code.freight_factor_percentage or 0) / decimal.Decimal(100)
        )
        return round(cost, 5)

    def unit_cost_total(self, obj):
        cost = (
            (obj.unit_material_cost or 0)
            + (obj.unit_labor_cost or 0)
            + (
                (obj.unit_material_cost or 0)
                * (
                    (obj.product_code.freight_factor_percentage or 0)
                    / decimal.Decimal(100)
                )
            )
        )
        return round(cost, 5)

    def onhand_quantity(self, obj):
        return get_sku_quantity(obj.pk)

    def total_cost(self, obj):
        cost = (
            (obj.unit_material_cost or 0)
            + (obj.unit_labor_cost or 0)
            + (
                (obj.unit_material_cost or 0)
                * (
                    (obj.product_code.freight_factor_percentage or 0)
                    / decimal.Decimal(100)
                )
            )
        ) * get_sku_quantity(obj.pk)
        return round(cost, 5)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("product_code")

    def save_formset(self, request, form, formset, change):
        # set meta fields
        parent = set_meta_fields(request, form.instance, form, change)
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

        # recalculate inventory weights
        if parent.original_unit_of_measure != parent.unit_of_measure:
            location_inventory = Inventory_Onhand.objects.filter(sku=form.instance)

            for i in location_inventory:
                converted_weight = convert_weight(
                    from_measure=parent.original_unit_of_measure,
                    to_measure=parent.unit_of_measure,
                    weight=i.quantity_onhand,
                )
                i.quantity_onhand = converted_weight
                i.save()


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
