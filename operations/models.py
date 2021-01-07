import sys
sys.path.append('.')
from django.db import models
from meta_models import MetaModel
from simple_history.models import HistoricalRecords
import decimal


class Product_Code(MetaModel):
    family = models.CharField(max_length=200)
    category = models.CharField(max_length=200, unique=True)
    freight_factor_percentage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Percentage adder to material cost. Use whole numbers with 2 decimals maximum.")

    def __str__(self):
        return "{}".format(self.category)

    class Meta:
        verbose_name = "Product - Category"
        verbose_name_plural = "Product - Categories"
        ordering = ("family", "category",)

class Product(MetaModel):
    history = HistoricalRecords()

    unit_of_measure_choices = (
        ("grams", "grams"),
        ("oz", "oz"),
        ("lbs", "lbs"),
        ("each", "each"),
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
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices, default="grams", verbose_name="Default Unit of Measure")
    total_quantity_onhand = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Total Onhand Quantity",
        help_text="Total inventory across all locations.  Updates to quantites to should be done using the Inventory Onhand form below."
    )
    total_freight_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Calculated using a percentage adder to account for inbound freight based upon type of material.")
    total_material_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_sales_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_material_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    freight_factor_percentage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    __original_unit_of_measure = None

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.__original_unit_of_measure = self.unit_of_measure

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.unit_of_measure != self.__original_unit_of_measure:
            if self.quantity_onhand:
                if self.__original_unit_of_measure == "lbs":
                    if self.unit_of_measure == "oz":
                        math = decimal.Decimal(16)
                        self.unit_cost = self.unit_cost / math
                        self.quantity_onhand = self.quantity_onhand * math
                    if self.unit_of_measure == "grams":
                        math = decimal.Decimal(453.592)
                        self.unit_cost = self.unit_cost / math
                        self.quantity_onhand = self.quantity_onhand * math
                elif self.__original_unit_of_measure == "oz":
                    if self.unit_of_measure == "lbs":
                        math = decimal.Decimal(16)
                        self.unit_cost = self.unit_cost * math
                        self.quantity_onhand = self.quantity_onhand / math
                    if self.unit_of_measure == "grams":
                        math = decimal.Decimal(28.3495)
                        self.unit_cost = self.unit_cost / math
                        self.quantity_onhand = self.quantity_onhand * math
                elif self.__original_unit_of_measure == "grams":
                    if self.unit_of_measure == "lbs":
                        math = decimal.Decimal(453.592)
                        self.unit_cost = self.unit_cost * math
                        self.quantity_onhand = self.quantity_onhand / math
                    if self.unit_of_measure == "oz":
                        math = decimal.Decimal(28.3495)
                        self.unit_cost = self.unit_cost * math
                        self.quantity_onhand = self.quantity_onhand / math

        super(Product, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_unit_of_measure = self.unit_of_measure

    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    class Meta:
        verbose_name = "Product Master"
        verbose_name_plural = "Product Master"
        ordering = ("sku",)


class Materials_Management_Proxy(Product):
    # history = HistoricalRecords()
    class Meta:
        proxy = True
        verbose_name = "Product - Raw Material"
        verbose_name_plural = "Product - Raw Materials"
        ordering = ("sku",)


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

    def __str__(self):
        return "{} ({})".format(self.sku, self.location)

    class Meta:
        verbose_name = "Inventory Onhand"
        verbose_name_plural = "Inventory Onhand"
        ordering = ("sku", "location")



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
        ordering = ("asin",)


class Shopify_Product(MetaModel):
    shopify_product_id = models.CharField(max_length=200, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="shopify_product_sku_fk")

    def __str__(self):
        return "{}".format(self.shopify_product_id)

    class Meta:
        verbose_name = "Shopify Product"
        verbose_name_plural = "Shopify Products"


class Supplier(MetaModel):
    history = HistoricalRecords()

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

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ("name",)


class Supplier_Product(MetaModel):
    history = HistoricalRecords()

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="Supplier_Product_product_fk")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="supplier_product_supplier_fk")
    supplier_sku = models.CharField(max_length=200)
    supplier_sku_description = models.CharField(max_length=200)
    supplier_sku_link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "{}: {} ({})".format(self.product, self.supplier, self.supplier_sku)

    class Meta:
        verbose_name = "Supplier Product"
        verbose_name_plural = "Supplier Products"
        unique_together = (("product", "supplier_sku"))
        ordering = ("product", "supplier_sku")

