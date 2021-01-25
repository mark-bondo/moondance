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


class Product_Code(MetaModel):
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
        ordering = ("family", "category",)

class Product(MetaModel):
    history = HistoricalRecords(inherit=True)

    type_list = (
        ("Finished Goods", "Finished Goods"),
        ("WIP", "WIP"),
        ("Raw Materials",  "Raw Materials"),
    )
    product_type = models.CharField(max_length=200, choices=type_list)
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


class Recipe_Proxy(Product):

    def __str__(self):
        return "{} ({})".format(self.description, self.sku)
    class Meta:
        proxy = True
        verbose_name = "Making - Recipe"
        verbose_name_plural = "Making - Recipes"
        ordering = ("sku",)

class Materials_Management_Proxy(Product):
    class Meta:
        proxy = True
        verbose_name = "Product - Raw Material"
        verbose_name_plural = "Product - Raw Materials"
        ordering = ("sku",)

    original_unit_of_measure = None
    original_unit_material_cost = None

    def __init__(self, *args, **kwargs):
        super(Materials_Management_Proxy, self).__init__(*args, **kwargs)
        self.original_unit_of_measure = self.unit_of_measure
        self.original_unit_material_cost = self.unit_material_cost


class Finished_Goods_Proxy(Product):
    class Meta:
        proxy = True
        verbose_name = "Product - Finished Good"
        verbose_name_plural = "Product - Finished Goods"
        ordering = ("sku",)


class Product_Bundle_Header(MetaModel):
    history = HistoricalRecords()

    product_bundle = models.OneToOneField(
        Finished_Goods_Proxy,
        on_delete=models.PROTECT,
        related_name="Product_Bundle_product_bundle_fk",
        primary_key=True
    )

    def __str__(self):
        return self.product_bundle

    class Meta:
        verbose_name = "Product - Bundle"
        verbose_name_plural = "Product - Bundles"
        ordering = ("product_bundle__sku",)


class Product_Bundle_Line(MetaModel):
    history = HistoricalRecords()

    bundle = models.ForeignKey(
        Product_Bundle_Header,
        on_delete=models.PROTECT,
        related_name="Product_Bundle_product_bundle_fk",
    )
    product_used = models.ForeignKey(
        Finished_Goods_Proxy,
        on_delete=models.PROTECT,
        related_name="Product_Bundle_product_used_fk"
    )
    quantity = models.IntegerField()

    def __str__(self):
        return self.bundle

    class Meta:
        verbose_name = "Bundle Item"
        verbose_name_plural = "Bundle Items"
        ordering = ("product_used__sku",)


class Inventory_Onhand(MetaModel):
    history = HistoricalRecords()

    location_list = (
        ("Bondo - Garage", "Bondo - Garage"),
        ("Bondo - 2nd Floor", "Bondo - 2nd Floor"),
        ("MoonDance HQ - Workshop",  "MoonDance HQ - Workshop"),
        ("MoonDance HQ - Fulfillment Center",  "MoonDance HQ - Fulfillment Center"),
    )

    sku = models.ForeignKey(
        Materials_Management_Proxy,
        on_delete=models.PROTECT,
        related_name="Inventory_Onhand_sku_fk"
    )
    location = models.CharField(max_length=200, choices=location_list)
    quantity_onhand = models.DecimalField(max_digits=12, decimal_places=2)
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)

    def __str__(self):
        return "{} ({})".format(self.sku, self.location)

    class Meta:
        verbose_name = "Buying - Inventory Onhand"
        verbose_name_plural = "Buying - Inventory Onhand"
        ordering = ("sku", "location")


class Amazon_Product(MetaModel):
    asin = models.CharField(max_length=200)
    seller_sku = models.CharField(max_length=200, unique=True)
    sku_description = models.CharField(max_length=200)
    product = models.ForeignKey(
        Finished_Goods_Proxy,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="amazon_product_product_fk"
    )


    def __str__(self):
        return "{}: {}".format(self.asin, self.seller_sku)

    class Meta:
        verbose_name = "Integrations - Amazon"
        verbose_name_plural = "Integrations - Amazon"
        ordering = ("product__sku", "seller_sku", "asin",)


class Shopify_Product(MetaModel):
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
    product = models.ForeignKey(Finished_Goods_Proxy, on_delete=models.PROTECT, null=True, blank=True, related_name="shopify_product_sku_fk")

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        verbose_name = "Integration - Shopify"
        verbose_name_plural = "Integrations - Shopify"
        ordering = ("product__sku", "variant_id",)


class Supplier(MetaModel):
    type_choices = (
        ("Distributor", "Distributor"),
        ("Manufacturer", "Manufacturer"),
    )

    history = HistoricalRecords()

    type = models.CharField(max_length=200, choices=type_choices, default="Manufacturer")
    name = models.CharField(max_length=200, unique=True)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    street_address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True, default="United States")
    supplier_website = models.URLField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Buying - Supplier"
        verbose_name_plural = "Buying - Suppliers"
        ordering = ("name",)


class Supplier_Product(MetaModel):
    history = HistoricalRecords()

    sku = models.ForeignKey(Materials_Management_Proxy, on_delete=models.PROTECT, related_name="Supplier_Product_product_fk")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="supplier_product_supplier_fk")
    supplier_sku = models.CharField(max_length=200)
    supplier_sku_description = models.CharField(max_length=200)
    supplier_sku_link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "{}: {} ({})".format(self.sku, self.supplier, self.supplier_sku)

    class Meta:
        verbose_name = "Buying - Supplier Product"
        verbose_name_plural = "Buying - Supplier Products"
        unique_together = (("supplier", "supplier_sku"))
        ordering = ("sku", "supplier_sku")


class Recipe_Line(MetaModel):
    history = HistoricalRecords()
    sku = models.ForeignKey(Materials_Management_Proxy, on_delete=models.PROTECT, related_name="Recipe_sku_fk")
    sku_parent = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="Recipe_sku_parent_fk")
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices, default="grams")

    def __str__(self):
        return "{} ({})".format(self.sku, self.sku_parent)

    class Meta:
        verbose_name = "Buying - Recipe Line"
        verbose_name_plural = "Buying - Recipe Lines"
        unique_together = (("sku", "sku_parent",),)
        ordering = ("sku_parent", "sku")

class Invoice(MetaModel):
    history = HistoricalRecords()
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="Invoice_supplier_fk", verbose_name="Invoicing Supplier")
    invoice = models.CharField(max_length=200)
    order = models.CharField(max_length=200, blank=True, null=True)
    date_invoiced = models.DateField(default=timezone.now)
    freight_charges = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.invoice, self.supplier)

    class Meta:
        verbose_name = "Buying - Invoice"
        verbose_name_plural = "Buying - Invoices"
        ordering = ("-date_invoiced", "invoice")

class Invoice_Line(MetaModel):
    history = HistoricalRecords()
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="Invoice_Line_invoice_fk")
    sku = models.ForeignKey(Materials_Management_Proxy, on_delete=models.PROTECT, related_name="Invoice_Line_sku_fk", verbose_name="MoonDance SKU")
    manufacturer = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="Invoice_Manufacturer_fk", verbose_name="Manufacturer", blank=True, null=True)
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return "{} ({})".format(self.invoice, self.sku)

    class Meta:
        verbose_name = "Buying - Invoice Line"
        verbose_name_plural = "Buying - Invoice Lines"
        unique_together = (("sku", "invoice",),)
        ordering = ("sku",)

class Weight_Conversions(models.Model):
    from_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)
    to_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)
    conversion_rate = models.DecimalField(max_digits=16, decimal_places=6)

    class Meta:
        verbose_name = "Weight Conversion"
        verbose_name_plural = "Weight Conversions"