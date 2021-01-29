import sys
from django.db import models
from moondance.meta_models import MetaModel
from simple_history.models import HistoricalRecords
from datetime import datetime
from django.utils import timezone
import decimal

unit_of_measure_choices = (
    ("grams", "grams"),
    ("oz", "oz"),
    ("lbs", "lbs"),
    ("each", "each"),
)
TYPE_LIST = (
    ("Finished Goods", "Finished Goods"),
    ("WIP", "WIP"),
    ("Raw Materials",  "Raw Materials"),
)


class Product_Code(MetaModel):
    type = models.CharField(max_length=200, choices=TYPE_LIST)
    family = models.CharField(max_length=200)
    category = models.CharField(max_length=200, unique=True)
    freight_factor_percentage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Percentage adder to material cost. Use whole numbers with 2 decimals maximum.")
    original_freight_factor_percentage = None

    def __str__(self):
        return "{}".format(self.category)

    def __init__(self, *args, **kwargs):
        super(Product_Code, self).__init__(*args, **kwargs)
        self.original_freight_factor_percentage = self.freight_factor_percentage

    class Meta:
        verbose_name = "Product - Category"
        verbose_name_plural = "Product - Categories"
        ordering = ("type", "family", "category",)

class Product(MetaModel):
    history = HistoricalRecords(inherit=True)

    product_type = models.CharField(max_length=200, choices=TYPE_LIST)
    product_code = models.ForeignKey(
        Product_Code,
        on_delete=models.PROTECT,
        related_name="Product_product_code_fk",
        blank=True,
        null=True
    )
    sku = models.CharField(max_length=200, unique=True, verbose_name="SKU")
    description = models.CharField(max_length=200)
    upc = models.CharField(max_length=200, null=True, blank=True, verbose_name="UPC")
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices, default="lbs")
    unit_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_sales_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_material_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    unit_freight_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    product_notes = models.TextField(null=True, blank=True, verbose_name="Product Notes")

    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("sku",)


class Raw_Material_Proxy(Product):
    class Meta:
        proxy = True
        verbose_name = "Product - Raw Material"
        verbose_name_plural = "Product - Raw Materials"
        ordering = ("sku",)

    original_unit_of_measure = None
    original_unit_material_cost = None

    def __init__(self, *args, **kwargs):
        super(Raw_Material_Proxy, self).__init__(*args, **kwargs)
        self.original_unit_of_measure = self.unit_of_measure
        self.original_unit_material_cost = self.unit_material_cost


class Finished_Goods_Proxy(Product):
    class Meta:
        proxy = True
        verbose_name = "Product - Finished Good"
        verbose_name_plural = "Product - Finished Goods"
        ordering = ("sku",)


class Order_Cost_Overlay(MetaModel):
    history = HistoricalRecords()
    sales_channel_list = (
        ("Shopify Website", "Shopify Website"),
        ("Amazon FBA", "Amazon FBA"),
        ("Amazon FBM", "Amazon FBM"),
        ("POS", "POS"),
    )
    type_list = (
        ("Fulfillment Labor", "Fulfillment Labor"),
        ("Shipping Materials", "Shipping Materials"),
    )
    apply_to_list = (
        ("Each Order", "Each Order"),
        ("Each Order Line", "Each Order Line"),
    )

    sales_channel = models.CharField(max_length=200, choices=sales_channel_list)
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200, choices=type_list)
    apply_to = models.CharField(max_length=200, choices=apply_to_list)
    labor_hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    labor_minutes = models.IntegerField(null=True, blank=True)
    material_cost = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Order Cost Overlay"
        verbose_name_plural = "Order Cost Overlays"
        ordering = ("sales_channel", "name",)
