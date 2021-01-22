import sys
from django.db import models
from moondance.meta_models import MetaModel


class Tax_Rate_State(MetaModel):
    state = models.CharField(max_length=200, unique=True)
    base_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.state)

    class Meta:
        verbose_name = "State Tax Rate"
        verbose_name_plural = "State Tax Rates"
        ordering = ("state",)


class Tax_Rate_County(MetaModel):
    state = models.ForeignKey(
        Tax_Rate_State,
        on_delete=models.PROTECT,
        related_name="Tax_Rate_County_state_fk"
    )
    county = models.CharField(max_length=200)
    base_rate = models.DecimalField(max_digits=4, decimal_places=2)
    transit_rate = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return "{}".format(self.county)

    class Meta:
        verbose_name = "County Tax Rate"
        verbose_name_plural = "County Tax Rates"
        ordering = ("state", "county",)
        unique_together = (("state", "county",),)