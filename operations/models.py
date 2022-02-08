from django.db import connection
from django.db import models
from django.apps import apps
from moondance.meta_models import MetaModel
from simple_history.models import HistoricalRecords
from django.forms import ValidationError
from django.contrib.postgres.fields.ranges import DateRangeField


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
    ("Labor Groups", "Labor Groups"),
    ("Services", "Services"),
    ("WIP", "WIP"),
)
SALES_CHANNEL_TYPES = (
    ("All", "All"),
    ("FBA", "FBA"),
    ("MoonDance", "MoonDance"),
)


def get_sku_quantity(sku_id):
    total_quantity = 0
    Inventory_Onhand = apps.get_model("purchasing", "Inventory_Onhand")

    for q in Inventory_Onhand.objects.filter(sku_id=sku_id):
        total_quantity += q.quantity_onhand or 0

    return total_quantity


def convert_weight(to_measure, from_measure, weight):
    with connection.cursor() as cursor:
        sql = f"""
            SELECT
                (conversion_rate * {weight})::NUMERIC(16, 5) as converted_weight
            FROM
                public.operations_weight_conversions
            WHERE
                from_measure = '{from_measure}' AND
                to_measure = '{to_measure}'
        """
        cursor.execute(sql)
        return cursor.fetchall()[0][0]


def calculate_unit_cost(obj, weight):
    converted_weight = convert_weight(
        from_measure=obj.unit_of_measure,
        to_measure=obj.sku.unit_of_measure,
        weight=weight,
    )
    cost = ((obj.sku.unit_material_cost or 0) + (obj.sku.unit_labor_cost or 0) + (obj.sku.unit_freight_cost or 0)) * (
        converted_weight or 0
    )
    return round(cost, 5)


def recalculate_bom_cost(p):
    bom = (
        Recipe_Line.objects.filter(sku_parent_id=p)
        .select_related("sku")
        .only(
            "quantity",
            "sku__unit_material_cost",
            "sku__unit_labor_cost",
            "sku__unit_freight_cost",
            "sku__unit_of_measure",
        )
    )

    if bom:
        unit_material_cost = 0
        unit_labor_cost = 0
        unit_freight_cost = 0

        for b in bom:
            converted_weight = convert_weight(
                to_measure=b.sku.unit_of_measure,
                from_measure=b.unit_of_measure,
                weight=(b.quantity or 0),
            )

            unit_material_cost += (b.sku.unit_material_cost or 0) * converted_weight
            unit_labor_cost += (b.sku.unit_labor_cost or 0) * converted_weight
            unit_freight_cost += (b.sku.unit_freight_cost or 0) * converted_weight

        Product.objects.filter(id=p).update(
            unit_material_cost=unit_material_cost,
            unit_labor_cost=unit_labor_cost,
            unit_freight_cost=unit_freight_cost,
        )

    return p


class Weight_Conversions(models.Model):
    from_measure = models.CharField(max_length=200, choices=UNIT_OF_MEASURES)
    to_measure = models.CharField(max_length=200, choices=UNIT_OF_MEASURES)
    conversion_rate = models.DecimalField(max_digits=16, decimal_places=6)

    class Meta:
        verbose_name = "Weight Conversion"
        verbose_name_plural = "Weight Conversions"


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

    original_freight_factor_percentage = None

    def __str__(self):
        return "{}".format(self.category)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_freight_factor_percentage = self.freight_factor_percentage

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
    sales_channel_type = models.CharField(max_length=100, choices=SALES_CHANNEL_TYPES, default="All")
    unit_of_measure = models.CharField(max_length=200, choices=UNIT_OF_MEASURES)
    unit_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_sales_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_material_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    unit_labor_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    unit_freight_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    original_unit_of_measure = None
    original_unit_material_cost = None
    original_unit_labor_cost = None
    original_unit_freight_cost = None

    @property
    def unit_cost_total(self):
        cost = (self.unit_material_cost or 0) + (self.unit_labor_cost or 0) + (self.unit_freight_cost or 0)
        return round(cost, 5)

    @property
    def total_cost(self):
        cost = (
            (self.unit_material_cost or 0) + (self.unit_labor_cost or 0) + (self.unit_freight_cost or 0)
        ) * get_sku_quantity(self.pk)
        return round(cost, 5)

    @property
    def onhand_quantity(self):
        return get_sku_quantity(self.pk)

    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_unit_of_measure = self.unit_of_measure
        self.original_unit_material_cost = self.original_unit_material_cost
        self.original_unit_labor_cost = self.original_unit_labor_cost
        self.original_unit_freight_cost = self.original_unit_freight_cost

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product List"
        ordering = ("sku",)


class Product_Cost_History(MetaModel):
    sku = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="Product_Cost_History_sku_fk",
    )
    standard_material_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    standard_freight_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    standard_labor_cost = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    date_range = DateRangeField()

    class Meta:
        verbose_name = "Product Cost History"
        verbose_name_plural = "Product Cost History"
        ordering = ("start_date",)

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)

        if not self.end_date or not self.start_date:
            raise ValidationError("This field is required")
        elif self.end_date < self.start_date:
            raise ValidationError("Start date must be less than or equal to end date")

        self.date_range = (self.start_date, self.end_date)
        overlap = (
            Product_Cost_History.objects.filter(
                sku=self.sku,
                date_range__overlap=self.date_range,
            )
            .exclude(pk=self.pk)
            .first()
        )

        if overlap:
            raise ValidationError("Date range overlaps with another record")


class Recipe_Line(MetaModel):
    history = HistoricalRecords()
    sku = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="Recipe_sku_fk",
    )
    sku_parent = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="Recipe_sku_parent_fk")
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_of_measure = models.CharField(max_length=200, choices=UNIT_OF_MEASURES, default="grams")

    @property
    def unit_cost(self):
        return calculate_unit_cost(self, 1)

    @property
    def extended_cost(self):
        return calculate_unit_cost(self, self.quantity)

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
        ordering = (
            "sku__product_code__family",
            "sku__sku",
        )


class Order_Cost_Overlay(MetaModel):
    history = HistoricalRecords()
    sales_channel_list = (
        ("Shopify Retail", "Shopify Retail"),
        ("Wholesale", "Wholesale"),
        ("Amazon FBA", "Amazon FBA"),
        ("Amazon FBM", "Amazon FBM"),
        ("Farmers Market - Wake Forest", "Farmers Market - Wake Forest"),
        ("Farmers Market - Durham", "Farmers Market - Durham"),
    )
    type_list = (
        ("Fulfillment Labor", "Fulfillment Labor"),
        ("Shipping Materials", "Shipping Materials"),
        ("Sales Channel Fees", "Sales Channel Fees"),
    )
    apply_to_list = (
        ("Each Order", "Each Order"),
        ("Each Order Line", "Each Order Line"),
    )

    sales_channel = models.CharField(max_length=200, choices=sales_channel_list)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices=type_list)
    apply_to = models.CharField(max_length=200, choices=apply_to_list)
    labor_hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    labor_minutes = models.IntegerField(null=True, blank=True)
    material_cost = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    sales_percentage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Cost Overlay"
        verbose_name_plural = "Cost Overlays"
        unique_together = (
            "name",
            "sales_channel",
        )
        ordering = (
            "sales_channel",
            "name",
        )
