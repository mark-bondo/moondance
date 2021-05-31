from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Product_Bundle_Header,
    Product_Bundle_Line,
)


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
