from django.db import models
from moondance.meta_models import MetaModel


class Chart(MetaModel):
    type_choices = (
        ("pie", "pie"),
        ("donut", "donut"),
        ("line", "line"),
        ("spline", "spline"),
        ("area", "area"),
        ("column", "column"),
        ("bar", "bar"),
    )

    table = models.CharField(max_length=200)
    title = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200, choices=type_choices)
    ordering = models.IntegerField(null=True, blank=True)
    show_legend = models.BooleanField(default=True)
    show_title = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Chart"
        verbose_name_plural = "Charts"


class Dashboard(MetaModel):
    type_choices = (
        ("Operations", "Operations"),
        ("Sales", "Sales"),
        ("Marketing", "Marketing"),
        ("Finance", "Finance"),
    )

    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200, choices=type_choices)
    charts = models.ManyToManyField(Chart, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"


class Chart_Options(MetaModel):
    yaxis_prefix_choices = (
        ("$", "$"),
        (None, "----"),
    )
    xaxis_type_list = (
        ("datetime", "datetime"),
        ("category", "category"),
    )
    type_list = {
        ("grouping", "grouping"),
        ("xaxis", "xaxis"),
        ("yaxis", "yaxis"),
    }

    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    field = models.CharField(max_length=200)
    name = models.CharField(max_length=200, blank=True, null=True)
    filter = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200)
    yaxis_prefix = models.CharField(
        max_length=200, choices=yaxis_prefix_choices, null=True, blank=True
    )
    yaxis_decimals = models.IntegerField(default=0)
    xaxis_type = models.CharField(
        max_length=200, choices=xaxis_type_list, null=True, blank=True
    )

    def __str__(self):
        return self.field

    class Meta:
        verbose_name = "Chart Option"
        verbose_name_plural = "Chart Options"
        unique_together = (
            (
                "chart",
                "name",
                "type",
            ),
        )


class Chart_XAxis(Chart_Options):
    class Meta:
        verbose_name = "X-Axis Option"
        verbose_name_plural = "X-Axis Options"
        proxy = True


class Chart_YAxis(Chart_Options):
    class Meta:
        verbose_name = "Y-Axis Option"
        verbose_name_plural = "Y-Axis Options"
        proxy = True


class Chart_Grouping(Chart_Options):
    class Meta:
        verbose_name = "Grouping Option"
        verbose_name_plural = "Grouping Options"
        proxy = True
