import decimal
from django.contrib import admin
from django.utils.timezone import datetime
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from operations.admin import convert_weight
from .models import (
    Recipe_Line,
    Recipe_Proxy,
    Product_Bundle_Header,
    Product_Bundle_Line,
)
from operations.models import Labor_Rate


def calculate_cost(obj):
    if obj.sku.product_code.type in (
        "Labor",
        "WIP - Labor",
    ):
        today = datetime.today()
        labor = Labor_Rate.objects.get(
            labor_code=obj.sku.product_code,
            start_date__lte=today,
            end_date__gte=today,
        )
        cost = (obj.quantity or 0) * ((labor.labor_rate or 0) / decimal.Decimal(60))
    elif obj.unit_of_measure == "each":
        cost = (obj.sku.unit_material_cost * obj.quantity) or 0
    else:
        converted_weight = convert_weight(
            from_measure=obj.unit_of_measure,
            to_measure=obj.sku.unit_of_measure,
            weight=obj.quantity,
        )

        cost = (
            decimal.Decimal(obj.sku.unit_material_cost or 0)
            * obj.quantity
            * decimal.Decimal(converted_weight or 0)
        )

    return round(cost, 5)


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
    readonly_fields = ("cost",)
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
        if obj.pk:
            return calculate_cost(obj)


@admin.register(Recipe_Proxy)
class Product_Recipe_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Recipe_Proxy
    inlines = (Recipe_Line_Inline_Admin,)
    list_display = [
        "sku",
        "description",
        "_active",
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
        "product_code",
    ]
    history_list_display = [
        "sku",
        "description",
        "_active",
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
        return qs.filter(
            product_code__type__in=["WIP", "WIP - Labor", "Finished Goods"]
        )

    def recipe_cost(self, obj):
        cost = Recipe_Line.objects.filter(sku_parent=obj.pk).select_related()
        recipe_cost = 0

        for c in cost:
            recipe_cost += calculate_cost(c)

        return recipe_cost

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_formset(self, request, form, formset, change):
        # set meta fields
        inline_formsets = formset.save(commit=False)

        for obj in inline_formsets:
            obj = set_meta_fields(request, obj, form, change, inline=True)
            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()


class Product_Bundle_Line_Admin(admin.TabularInline):
    model = Product_Bundle_Line
    extra = 1
    fk_name = "bundle"
    fields = (
        "product_used",
        "quantity",
        "_active",
        "_last_updated",
    )
    history_list_display = [
        "bundle",
        "product_used",
        "quantity",
        "_active",
        "_last_updated",
    ]
    autocomplete_fields = [
        "product_used",
    ]
    readonly_fields = ("_last_updated",)


@admin.register(Product_Bundle_Header)
class Product_Bundle_Header_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Product_Bundle_Header
    inlines = (Product_Bundle_Line_Admin,)
    search_fields = [
        "bundle__sku",
        "bundle__description",
    ]
    list_display = [
        "bundle",
        "_active",
        "_last_updated",
    ]
    list_filter = [
        ("bundle__product_code", admin.RelatedOnlyFieldListFilter),
    ]
    autocomplete_fields = [
        "bundle",
    ]
    history_list_display = [
        "id",
        "bundle",
        "_last_updated",
        "_active",
    ]
    fields = (
        "bundle",
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
