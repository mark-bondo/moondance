from django.db import models
from moondance.meta_models import MetaModel

TYPE_CHOICES = (
    ("Operations", "Operations"),
    ("Sales", "Sales"),
    ("Marketing", "Marketing"),
    ("Finance", "Finance"),
)


class Dashboard(MetaModel):
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"


class Chart(MetaModel):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Chart"
        verbose_name_plural = "Charts"
