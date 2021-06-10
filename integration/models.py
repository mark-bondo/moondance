from django.db import models
from moondance.meta_models import MetaModel
from simple_history.models import HistoricalRecords
from operations.models import Product


class Amazon_Product(MetaModel):
    history = HistoricalRecords()

    asin = models.CharField(max_length=200, unique=True)
    sku_description = models.CharField(max_length=200)
    product = models.ForeignKey(
        Product,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="amazon_product_product_fk",
    )

    def __str__(self):
        return "{}".format(self.sku_description)

    class Meta:
        verbose_name = "Amazon Product"
        verbose_name_plural = "Amazon Products"
        ordering = (
            "product__sku",
            "asin",
        )


class Shopify_Product(MetaModel):
    history = HistoricalRecords()

    shopify_id = models.BigIntegerField()
    variant_id = models.BigIntegerField(unique=True)
    shopify_sku = models.CharField(max_length=200)
    status = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200)
    inventory_policy = models.CharField(max_length=200, blank=True, null=True)
    inventory_management = models.CharField(max_length=200, blank=True, null=True)
    grams = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    inventory_quantity = models.IntegerField(null=True, blank=True)
    customer_type = models.CharField(max_length=200)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    tags = models.CharField(max_length=1000, blank=True, null=True)
    handle = models.CharField(max_length=200, blank=True, null=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="shopify_product_sku_fk",
    )

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        verbose_name = "Shopify Product"
        verbose_name_plural = "Shopify Products"
        ordering = (
            "product__sku",
            "variant_id",
        )


class Product_Missing_SKU(MetaModel):
    source_system_choices = (
        ("Amazon", "Amazon"),
        ("Shopify", "Shopify"),
    )
    source_system = models.CharField(max_length=200, choices=source_system_choices)
    product_description = models.CharField(max_length=200)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="Product_Missing_SKU_product_fk",
    )

    def __str__(self):
        return "{} ({})".format(self.source_system, self.product_description)

    class Meta:
        verbose_name = "Product Description Mapping"
        verbose_name_plural = "Product Description Mappings"
        unique_together = (
            "source_system",
            "product_description",
        )
