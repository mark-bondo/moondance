from django.db import models
from moondance.meta_models import MetaModel
from simple_history.models import HistoricalRecords


UNIT_OF_MEASURES = (
    ("grams", "grams"),
    ("oz", "oz"),
    ("lbs", "lbs"),
    ("each", "each"),
    (
        "hours",
        "hours",
    ),
    (
        "minutes",
        "minutes",
    ),
)
PRODUCT_TYPES = (
    ("Finished Goods", "Finished Goods"),
    ("Raw Materials", "Raw Materials"),
    ("Labor", "Labor"),
    ("WIP", "WIP"),
)
SALES_CHANNEL_TYPES = (
    ("All", "All"),
    ("FBA", "FBA"),
    ("MoonDance", "MoonDance"),
)


class Product_Code(MetaModel):
    type = models.CharField(max_length=200, choices=PRODUCT_TYPES)
    family = models.CharField(max_length=200)
    category = models.CharField(max_length=200, unique=True)
    freight_factor_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage adder to material cost. Use whole numbers with 2 decimals maximum.",
    )

    def __str__(self):
        return "{}".format(self.category)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = (
            "type",
            "family",
            "category",
        )


class Product(MetaModel):
    history = HistoricalRecords(inherit=True)

    product_code = models.ForeignKey(
        Product_Code,
        on_delete=models.PROTECT,
        related_name="Product_product_code_fk",
        blank=True,
        null=True,
    )
    sku = models.CharField(max_length=200, unique=True, verbose_name="SKU")
    description = models.CharField(max_length=200)
    upc = models.CharField(max_length=200, null=True, blank=True, verbose_name="UPC")
    sales_channel_type = models.CharField(
        max_length=100, choices=SALES_CHANNEL_TYPES, default="All"
    )
    unit_of_measure = models.CharField(
        max_length=200, choices=UNIT_OF_MEASURES, default="lbs"
    )
    unit_weight = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    unit_sales_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    unit_material_cost = models.DecimalField(
        max_digits=12, decimal_places=5, null=True, blank=True
    )
    unit_labor_cost = models.DecimalField(
        max_digits=12, decimal_places=5, null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)

    original_unit_of_measure = None
    original_unit_material_cost = None
    original_unit_labor_cost = None

    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_unit_of_measure = self.unit_of_measure
        self.original_unit_material_cost = self.original_unit_material_cost
        self.original_unit_labor_cost = self.original_unit_labor_cost

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product List"
        ordering = ("sku",)


class Recipe_Line(MetaModel):
    history = HistoricalRecords()
    sku = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="Recipe_sku_fk",
        limit_choices_to=~models.Q(product_code__type__in=["Finished Goods"]),
    )
    sku_parent = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="Recipe_sku_parent_fk"
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_of_measure = models.CharField(
        max_length=200, choices=UNIT_OF_MEASURES, default="grams"
    )

    def __str__(self):
        return "{} ({})".format(self.sku, self.sku_parent)

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipe"
        unique_together = (
            (
                "sku",
                "sku_parent",
            ),
        )
        ordering = ("sku_parent", "sku")


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
    labor_hourly_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    labor_minutes = models.IntegerField(null=True, blank=True)
    material_cost = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Cost Overlay"
        verbose_name_plural = "Cost Overlays"
        ordering = (
            "sales_channel",
            "name",
        )
