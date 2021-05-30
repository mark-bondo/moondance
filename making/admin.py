import decimal
from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from operations.admin import convert_weight
from .models import (
    Recipe_Line,
    Recipe_Proxy,
    Product_Bundle_Header,
    Product_Bundle_Line,
)


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
        # print(obj.sku, obj.quantity, obj.sku.unit_material_cost)

        if obj.pk:
            if obj.unit_of_measure == "each":
                converted_weight = obj.quantity
            else:
                new_weight_dict = convert_weight(
                    unit_of_measure=obj.unit_of_measure, weight=obj.quantity
                )
                converted_weight = new_weight_dict[obj.sku.unit_of_measure]

            # print(obj.sku, obj.unit_of_measure, obj.quantity, converted_weight)

            return round(
                decimal.Decimal(obj.sku.unit_material_cost or 0)
                * decimal.Decimal(converted_weight or 0),
                5,
            )


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
        return qs.filter(product_type__in=["WIP", "WIP - Labor", "Finished Goods"])

    def recipe_cost(self, obj):
        cost = Recipe_Line.objects.filter(sku_parent=obj.pk).select_related()
        recipe_cost = 0

        for c in cost:
            # print(c.sku, c.sku.unit_of_measure, c.sku.unit_material_cost)

            if c.unit_of_measure == "each":
                converted_weight = c.quantity
            else:
                new_weight_dict = convert_weight(
                    unit_of_measure=c.unit_of_measure, weight=c.quantity
                )
                converted_weight = new_weight_dict[c.sku.unit_of_measure]

            recipe_cost += (c.sku.unit_material_cost or 0) * (converted_weight or 0)

        return round(recipe_cost, 5)

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

    # def get_queryset(self, request):
    #     bundles = Product_Bundle_Line.objects.values("bundle").annotate(n=Count("pk"))
    #     qs = super().get_queryset(request).filter(pk__in=bundles)
    #     return qs
