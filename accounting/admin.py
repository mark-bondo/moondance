from django.contrib import admin
from .models import (
    Tax_Rate_State,
    Tax_Rate_County,
)
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from simple_history.admin import SimpleHistoryAdmin


class Tax_Rate_County_Admin_Inline(admin.TabularInline):
    model = Tax_Rate_County
    extra = 1
    fields = (
        "county",
        "base_rate",
        "transit_rate",
        "_last_updated",
    )
    readonly_fields = ("_last_updated",)


@admin.register(Tax_Rate_State)
class Tax_Rate_State_Admin(AdminStaticMixin, SimpleHistoryAdmin):
    model = Tax_Rate_State
    inlines = (Tax_Rate_County_Admin_Inline,)
    list_display = [
        "state",
        "base_rate",
        "_last_updated",
    ]
    list_filter = [
        "state",
    ]
    search_fields = [
        "state",
    ]
    fields = (
        "state",
        "base_rate",
        "_last_updated",
    )
    readonly_fields = ("_last_updated",)

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
