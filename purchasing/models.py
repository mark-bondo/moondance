import sys
from django.db import models
from moondance.meta_models import MetaModel
from operations.models import Raw_Material_Proxy, unit_of_measure_choices
from simple_history.models import HistoricalRecords
from datetime import datetime
from django.utils import timezone
import decimal

LOCATION_LIST = [
    ("Bondo - Garage", "Bondo - Garage"),
    ("Bondo - 2nd Floor", "Bondo - 2nd Floor"),
    ("MoonDance - Workshop",  "MoonDance - Workshop"),
    ("MoonDance - Fulfillment Center",  "MoonDance - Fulfillment Center"),
]


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
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ("name",)


class Supplier_Product(MetaModel):
    history = HistoricalRecords()

    sku = models.ForeignKey(Raw_Material_Proxy, on_delete=models.PROTECT, related_name="Supplier_Product_product_fk")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="supplier_product_supplier_fk")
    supplier_sku = models.CharField(max_length=200)
    supplier_sku_description = models.CharField(max_length=200)
    supplier_sku_link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "{}: {} ({})".format(self.sku, self.supplier, self.supplier_sku)

    class Meta:
        verbose_name = "Supplier Product"
        verbose_name_plural = "Supplier Products"
        unique_together = (("supplier", "supplier_sku"))
        ordering = ("sku", "supplier_sku")


class Invoice(MetaModel):
    history = HistoricalRecords()
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="Invoice_supplier_fk", verbose_name="Invoicing Supplier")
    invoice = models.CharField(max_length=200, blank=True, null=True)
    order = models.CharField(max_length=200, blank=True, null=True)
    date_invoiced = models.DateField(default=timezone.now)
    freight_charges = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.invoice, self.supplier)

    class Meta:
        verbose_name = "Inventory Receipt"
        verbose_name_plural = "Inventory Receipts"
        ordering = ("-date_invoiced", "invoice")


class Invoice_Line(MetaModel):
    history = HistoricalRecords()
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="Invoice_Line_invoice_fk")
    sku = models.ForeignKey(Raw_Material_Proxy, on_delete=models.PROTECT, related_name="Invoice_Line_sku_fk", verbose_name="MoonDance SKU")
    manufacturer = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT, 
        related_name="Invoice_Manufacturer_fk", 
        verbose_name="Manufacturer", 
        blank=True, 
        null=True,
        help_text="Only needs to be populated if the manufacturer is different than the invoicing supplier."
    )
    unit_of_measure = models.CharField(max_length=200, choices=unit_of_measure_choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return "{} ({})".format(self.invoice, self.sku)

    class Meta:
        verbose_name = "Recipt Line"
        verbose_name_plural = "Recipt Lines"
        unique_together = (("sku", "invoice",),)
        ordering = ("sku",)


class Inventory_Onhand(MetaModel):
    history = HistoricalRecords()

    sku = models.ForeignKey(
        Raw_Material_Proxy,
        on_delete=models.PROTECT,
        related_name="Inventory_Onhand_sku_fk"
    )
    location = models.CharField(max_length=200, choices=LOCATION_LIST, verbose_name="Current Location")
    quantity_onhand = models.DecimalField(max_digits=12, decimal_places=2)
    to_location = models.CharField(max_length=200, null=True, blank=True, choices=LOCATION_LIST, verbose_name="Transfer To Location")
    transfer_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.sku.sku, self.location)

    class Meta:
        verbose_name = "Inventory Onhand"
        verbose_name_plural = "Inventory Onhand"
        ordering = ("sku", "location")
        unique_together = (("sku", "location",),)