import decimal
from django.db import models
from django.db import connection
from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Product_Code,
    Raw_Material_Proxy,
    Finished_Goods_Proxy,
    Labor_Proxy,
    Labor_Rate,
    Labor_Code,
    Order_Cost_Overlay,
)
from purchasing.admin import Supplier_Product_Admin_Inline, get_sku_quantity
from purchasing.models import (
    Inventory_Onhand,
)
from .forms import (
    Raw_Material_Proxy_Form,
    Finished_Goods_Proxy_Form,
    Labor_Code_Form,
    Labor_Proxy_Form,
    Product_Code_Form,
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


@admin.register(Labor_Proxy)
class Labor_Proxy_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Labor_Proxy
    form = Labor_Proxy_Form
    save_as = True

    list_display = [
        "sku",
        "description",
        "_active",
        "product_code",
        "unit_of_measure",
    ]
    history_list_display = [
        "sku",
        "description",
        "_active",
        "product_code",
        "unit_of_measure",
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
        ("product_code", admin.RelatedOnlyFieldListFilter),
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "sku",
                    "description",
                    "product_code",
                    "unit_of_measure",
                    "_active",
                ]
            },
        ),
    )
    readonly_fields = (
        "unit_labor_cost",
        "_last_updated",
        "_created",
        "_created_by",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("product_code")
        return qs.filter(product_code__type__in=["Labor", "WIP - Labor"])

    def save_model(self, request, obj, form, change):
        obj.save()
        super().save_model(request, obj, form, change)


class Labor_Rate_Inline_Admin(admin.TabularInline):
    model = Labor_Rate
    extra = 1

    fields = (
        "labor_rate",
        "start_date",
        "end_date",
        "_active",
    )
    readonly_fields = (
        "_last_updated",
        "_last_updated_by",
        "_created",
        "_created_by",
    )


@admin.register(Labor_Code)
class Labor_Code_Admin(admin.ModelAdmin):
    model = Labor_Code
    form = Labor_Code_Form
    save_as = True
    inlines = (Labor_Rate_Inline_Admin,)

    list_display = [
        "type",
        "family",
        "category",
        "sales_channel_type",
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
                    "sales_channel_type",
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            type__in=[
                "Labor",
                "WIP - Labor",
            ]
        )

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)


@admin.register(Product_Code)
class Product_Code_Admin(admin.ModelAdmin):
    model = Product_Code
    form = Product_Code_Form
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            type__in=[
                "Finished Goods",
                "Raw Materials",
                "WIP",
            ]
        )

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)

        if obj.original_freight_factor_percentage != obj.freight_factor_percentage:
            skus = Raw_Material_Proxy.objects.filter(product_code=obj.pk)

            for sku in skus:
                sku.unit_freight_cost = (sku.unit_material_cost or 0) * (
                    (obj.freight_factor_percentage or 0) / decimal.Decimal(100)
                )
                sku.save()


@admin.register(Raw_Material_Proxy)
class Raw_Material_Proxy_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Raw_Material_Proxy
    form = Raw_Material_Proxy_Form
    inlines = (Supplier_Product_Admin_Inline,)
    save_as = True

    list_display = [
        "sku",
        "description",
        "_active",
        "product_code",
        "unit_of_measure",
        "onhand_quantity",
        "unit_cost_total",
        "total_cost",
    ]
    history_list_display = [
        "sku",
        "description",
        "_active",
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
        ("product_code", admin.RelatedOnlyFieldListFilter),
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": [
                    "sku",
                    "description",
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

    def onhand_quantity(self, obj):
        return get_sku_quantity(obj.pk)

    def total_material_cost(self, obj):
        return (obj.unit_material_cost or 0) * get_sku_quantity(obj.pk)

    def total_freight_cost(self, obj):
        return (obj.unit_freight_cost or 0) * get_sku_quantity(obj.pk)

    def total_cost(self, obj):
        return (
            (obj.unit_material_cost or 0) + (obj.unit_freight_cost or 0)
        ) * get_sku_quantity(obj.pk)

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("product_code")
        return qs.filter(~models.Q(product_code__type__in=["Finished Goods"]))

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
                total_cost_previous_unit_of_measure += (
                    i.quantity_onhand * parent_obj.original_unit_material_cost
                )

                if parent_obj.original_unit_of_measure != parent_obj.unit_of_measure:
                    converted_weight = convert_weight(
                        from_measure=parent_obj.original_unit_of_measure,
                        to_measure=parent_obj.unit_of_measure,
                        weight=i.quantity_onhand,
                    )
                    i.quantity_onhand = converted_weight

                i.unit_of_measure = parent_obj.unit_of_measure
                i.save()

                total_quantity_onhand += i.quantity_onhand or 0

            if (
                parent_obj.original_unit_of_measure != parent_obj.unit_of_measure
                and parent_obj.unit_of_measure != "each"
            ):
                if location_inventory:
                    parent_obj.unit_material_cost = (
                        total_cost_previous_unit_of_measure / total_quantity_onhand
                    )
                else:
                    converted_weight = convert_weight(
                        from_measure=parent_obj.unit_of_measure,
                        to_measure=parent_obj.original_unit_of_measure,
                        weight=parent_obj.unit_material_cost,
                    )
                    parent_obj.unit_material_cost = converted_weight

            parent_obj.total_quantity_onhand = total_quantity_onhand
            parent_obj.total_material_cost = (
                total_quantity_onhand * parent_obj.unit_material_cost
            )
            parent_obj.total_freight_cost = (
                decimal.Decimal(parent_obj.product_code.freight_factor_percentage or 0)
                / decimal.Decimal(100)
            ) * parent_obj.total_material_cost
            parent_obj.total_cost = parent_obj.total_material_cost + (
                parent_obj.total_freight_cost or 0
            )
            parent_obj.save()


@admin.register(Finished_Goods_Proxy)
class Finished_Goods_Proxy_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Finished_Goods_Proxy
    form = Finished_Goods_Proxy_Form
    save_as = True
    list_display = [
        "sku",
        "description",
        "_active",
        "product_code",
        "onhand_quantity",
        "unit_sales_price",
        "unit_cost_total",
        "total_cost",
    ]
    history_list_display = [
        "sku",
        "description",
        "_active",
        "product_code",
        "onhand_quantity",
        "unit_sales_price",
        "unit_cost_total",
        "total_cost",
    ]
    fields = (
        "sku",
        "description",
        "product_code",
        "unit_sales_price",
        (
            "unit_material_cost",
            "unit_labor_cost",
            "unit_freight_cost",
        ),
        "onhand_quantity",
        (
            "unit_cost_total",
            "total_cost",
        ),
        "_active",
    )
    autocomplete_fields = [
        "product_code",
    ]
    list_editable = ["product_code"]
    search_fields = [
        "sku",
        "description",
        "product_code__category",
        "product_code__family",
    ]
    list_filter = [
        ("_active", admin.BooleanFieldListFilter),
        ("product_code", admin.RelatedOnlyFieldListFilter),
    ]
    readonly_fields = (
        "onhand_quantity",
        "total_cost",
        "unit_cost_total",
    )

    def unit_cost_total(self, obj):
        return (
            (obj.unit_material_cost or 0)
            + (obj.unit_labor_cost or 0)
            + (obj.unit_freight_cost or 0)
        )

    def onhand_quantity(self, obj):
        return get_sku_quantity(obj.pk)

    def total_cost(self, obj):
        return (
            (obj.unit_material_cost or 0)
            + (obj.unit_labor_cost or 0)
            + (obj.unit_freight_cost or 0)
        ) * get_sku_quantity(obj.pk)

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("product_code")
        return qs.filter(product_code__type__in=["Finished Goods"])

    def save_formset(self, request, form, formset, change):
        # set meta fields
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()


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
