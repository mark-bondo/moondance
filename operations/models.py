import decimal
from django.db import models
from moondance.meta_models import MetaModel
from utils import common
from simple_history.models import HistoricalRecords
from django.forms import ValidationError
from django.contrib.postgres.fields.ranges import DateRangeField
from datetime import date
from django.apps import apps
from dateutil.relativedelta import relativedelta


class Weight_Conversions(models.Model):
    from_measure = models.CharField(max_length=200, choices=common.UNIT_OF_MEASURES)
    to_measure = models.CharField(max_length=200, choices=common.UNIT_OF_MEASURES)
    conversion_rate = models.DecimalField(max_digits=16, decimal_places=6)

    class Meta:
        verbose_name = "Weight Conversion"
        verbose_name_plural = "Weight Conversions"


class Product_Code(MetaModel):
    type = models.CharField(max_length=200, choices=common.PRODUCT_TYPES)
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
    sales_channel_type = models.CharField(max_length=100, choices=common.SALES_CHANNEL_TYPES, default="All")
    unit_of_measure = models.CharField(max_length=200, choices=common.UNIT_OF_MEASURES)
    unit_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit_sales_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    costing_method = models.CharField(max_length=100, choices=common.COSTING_METHOD_CHOICES, default="Manual")
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
    def onhand_quantity(self):
        return common.get_sku_quantity(self.pk)

    @property
    def total_cost(self):
        return round(self.unit_cost_total * self.onhand_quantity, 5)

    def __str__(self):
        return "{} ({})".format(self.description, self.sku)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_unit_of_measure = self.unit_of_measure
        self.original_unit_material_cost = self.original_unit_material_cost
        self.original_unit_labor_cost = self.original_unit_labor_cost
        self.original_unit_freight_cost = self.original_unit_freight_cost

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)

        if self.product_code and self.product_code.type in (
            "Finished Goods",
            "WIP",
            "Labor Group",
        ):
            self.costing_method = "Recipe Cost Rollup"
        elif self.product_code and self.product_code.type in ("Labor",):
            self.costing_method = "Manual Estimate"
        elif self.costing_method != "Manual Override":
            invoice_lines = (
                apps.get_model("purchasing.Invoice_Line").objects.filter(sku=self).order_by("-invoice__date_invoiced")
            )

            if not invoice_lines:
                if self.unit_material_cost is None or self.unit_material_cost == 0:
                    self.costing_method = "No Cost Found"
                else:
                    freight = (
                        self.product_code.freight_factor_percentage
                        if self.product_code and self.product_code.freight_factor_percentage
                        else 0
                    ) / decimal.Decimal(100)
                    self.unit_freight_cost = (self.unit_material_cost or 0) * freight
                    self.costing_method = "Manual Estimate"
            else:
                # first try past 6 months
                month_delta = 6
                start_date = date.today() - relativedelta(months=month_delta)
                invoice_history = invoice_lines.filter(invoice__date_invoiced__gte=start_date)

                # then try past 12 months
                if not invoice_history:
                    month_delta = 12
                    start_date = date.today() - relativedelta(months=month_delta)
                    invoice_history = invoice_lines.filter(invoice__date_invoiced__gte=start_date)

                    if invoice_history:
                        self.costing_method = f"{month_delta} Month Average"
                    else:
                        # last resort try most recent
                        invoice_history = [invoice_lines.first()]
                        self.costing_method = "Last Invoice"
                else:
                    self.costing_method = f"{month_delta} Month Average"

                total_material_cost = 0
                total_freight_cost = 0
                total_quantity = 0

                for i in invoice_history:
                    total_material_cost += i.converted_quantity * (
                        (i.unit_material_cost or 0) + (i.unit_adjustments or 0)
                    )
                    total_freight_cost += i.converted_quantity * (i.unit_freight_cost or 0)
                    total_quantity += i.converted_quantity

                if total_quantity > 0:
                    self.unit_material_cost = total_material_cost / total_quantity
                    self.unit_freight_cost = total_freight_cost / total_quantity

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

    @property
    def standard_total_cost(self):
        cost = (self.standard_material_cost or 0) + (self.standard_freight_cost or 0) + (self.standard_labor_cost or 0)
        return round(cost, 5)

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

    class Meta:
        verbose_name = "Product Cost History"
        verbose_name_plural = "Product Cost History"
        ordering = ("start_date",)


class Recipe_Line(MetaModel):
    history = HistoricalRecords()
    sku = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="Recipe_sku_fk",
    )
    sku_parent = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="Recipe_sku_parent_fk")
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_of_measure = models.CharField(max_length=200, choices=common.UNIT_OF_MEASURES, default="grams")

    @property
    def unit_cost(self):
        return common.calculate_unit_cost(self, 1)

    @property
    def extended_cost(self):
        return common.calculate_unit_cost(self, self.quantity or 0)

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
