from django.contrib import admin
from moondance.meta_models import set_meta_fields, AdminStaticMixin
from .models import (
    Chart,
    Chart_XAxis,
    Chart_YAxis,
    Chart_Grouping,
    Dashboard,
)


class Chart_XAxis_Inline(admin.TabularInline):
    model = Chart_XAxis
    extra = 0
    verbose_name = "X-Axis Option"
    verbose_name_plural = "X-Axis Options"
    fields = (
        "is_default",
        "field",
        "name",
        "xaxis_type",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type="xaxis")


class Chart_YAxis_Inline(admin.TabularInline):
    model = Chart_YAxis
    extra = 0
    verbose_name = "Y-Axis Option"
    verbose_name_plural = "Y-Axis Options"
    fields = (
        "is_default",
        "field",
        "name",
        "yaxis_prefix",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type="yaxis")


class Chart_Grouping_Inline(admin.TabularInline):
    model = Chart_Grouping
    extra = 0
    verbose_name = "Grouping Option"
    verbose_name_plural = "Grouping Options"
    fields = ("is_default", "field", "name", "is_visible", "filter")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type="grouping")


@admin.register(Chart)
class Chart_Admin(AdminStaticMixin):
    save_as = True
    inlines = (
        Chart_Grouping_Inline,
        Chart_XAxis_Inline,
        Chart_YAxis_Inline,
    )
    list_display = [
        "title",
        "table",
        "type",
        "ordering",
    ]
    search_fields = ["title", "table"]
    fields = ("title", "table", "type", "ordering", "show_legend", "show_title")

    def save_model(self, request, obj, form, change):
        obj = set_meta_fields(request, obj, form, change)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in instances:
            obj = set_meta_fields(request, obj, form, change, inline=True)

            if formset.model == Chart_Grouping:
                obj.type = "grouping"
            elif formset.model == Chart_XAxis:
                obj.type = "xaxis"
            elif formset.model == Chart_YAxis:
                obj.type = "yaxis"

            obj.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()


@admin.register(Dashboard)
class Dashboard_Admin(AdminStaticMixin):
    list_display = [
        "name",
        "type",
    ]
    list_filter = [
        "type",
    ]
    search_fields = [
        "name",
    ]
    filter_horizontal = [
        "charts",
    ]
    fields = ("name", "type", "charts")

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
