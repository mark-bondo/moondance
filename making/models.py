import sys
from django.db import models
from moondance.meta_models import MetaModel
from simple_history.models import HistoricalRecords
from datetime import datetime
from django.utils import timezone
import decimal
from operations.models import(
    Finished_Goods_Proxy,
    Raw_Material_Proxy,
    Product,
)
from purchasing.models import(
    unit_of_measure_choices,
)


class Recipe_Proxy(Product):
    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    class Meta:
        proxy = True
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("sku",)


class Product_Bundle_Proxy(Finished_Goods_Proxy):
    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    class Meta:
        proxy = True
        verbose_name = "Product Bundle"
        verbose_name_plural = "Product Bundles"
        ordering = ("sku",)


class Recipe_Line(MetaModel):
    history = HistoricalRecords()
    sku = models.ForeignKey(Raw_Material_Proxy, on_delete=models.PROTECT, related_name="Recipe_sku_fk")
    sku_parent = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="Recipe_sku_parent_fk")
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices, default="grams")

    def __str__(self):
        return "{} ({})".format(self.sku, self.sku_parent)

    class Meta:
        verbose_name = "Recipe Line"
        verbose_name_plural = "Recipe Lines"
        unique_together = (("sku", "sku_parent",),)
        ordering = ("sku_parent", "sku")


class Weight_Conversions(models.Model):
    from_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)
    to_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)
    conversion_rate = models.DecimalField(max_digits=16, decimal_places=6)

    class Meta:
        verbose_name = "Weight Conversion"
        verbose_name_plural = "Weight Conversions"


class Product_Bundle_Line(MetaModel):
    history = HistoricalRecords()

    bundle = models.ForeignKey(
        Product_Bundle_Proxy,
        on_delete=models.PROTECT,
        related_name="Product_Bundle_product_bundle_fk",
    )
    product_used = models.ForeignKey(
        Product_Bundle_Proxy,
        on_delete=models.PROTECT,
        related_name="Product_Bundle_product_used_fk"
    )
    quantity = models.IntegerField()

    def __str__(self):
        return self.bundle

    class Meta:
        verbose_name = "Bundled Product"
        verbose_name_plural = "Bundled Products"
        ordering = ("bundle__sku", "product_used__sku",)