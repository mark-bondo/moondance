import sys
sys.path.append('.')
from django.db import models
from meta_models import MetaModel


class Product_Code(MetaModel):
    family = models.CharField(max_length=200)
    category = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return "{}: {}".format(self.family, self.category)

    class Meta:
        verbose_name = "Product Hierarchy"
        verbose_name_plural = "Product Hierarchy"


class Product(MetaModel):
    unit_of_measure_choices = (
        ("grams", "grams"),
        ("ounces", "ounces"),
    )
    type_list = (
        ("Finished Goods", "Finished Goods"),
        ("WIP", "WIP"),
        ("Raw Materials",  "Raw Materials"),
    )
    product_type = models.CharField(max_length=200, choices=type_list)
    product_code = models.ForeignKey(
        Product_Code,
        on_delete=models.PROTECT,
        related_name="Product_product_code_fk"
    )
    sku = models.CharField(max_length=200, unique=True, verbose_name="SKU")
    description = models.CharField(max_length=200)
    upc = models.CharField(max_length=200, null=True, blank=True, verbose_name="UPC")
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices, default="grams")
    quantity_onhand = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Unit Sales Price")
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.sku, self.description)

    class Meta:
        verbose_name = "Product Master"
        verbose_name_plural = "Product Master"


class Amazon_Product(MetaModel):
    asin = models.CharField(max_length=200, unique=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="amazon_product_product_fk"
    )

    def __str__(self):
        return "{}".format(self.asin)

    class Meta:
        verbose_name = "Amazon Product"
        verbose_name_plural = "Amazon Products"


class Shopify_Product(MetaModel):
    shopify_product_id = models.CharField(max_length=200, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="shopify_product_sku_fk")

    def __str__(self):
        return "{}".format(self.shopify_product_id)

    class Meta:
        verbose_name = "Shopify Product"
        verbose_name_plural = "Shopify Products"


class Supplier(MetaModel):
    name = models.CharField(max_length=200, unique=True)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    street_address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True, default="United States")
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"


class Supplier_Product(MetaModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="Supplier_Product_product_fk")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="supplier_product_supplier_fk")
    supplier_sku = models.CharField(max_length=200)

    def __str__(self):
        return "{}: {} ({})".format(self.product, self.supplier, self.supplier_sku)

    class Meta:
        verbose_name = "Supplier Product"
        verbose_name_plural = "Supplier Products"
        unique_together = (("product", "supplier_sku"))


