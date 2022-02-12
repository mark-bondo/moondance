from django.db import connection
from django.apps import apps


LOCATION_LIST = [
    ("Bondo - Garage", "Bondo - Garage"),
    ("Workshop", "Workshop"),
    ("Fulfillment Area", "Fulfillment Area"),
    ("DFM Staging", "DFM Staging"),
    ("Curing Room", "Curing Room"),
    ("WomanCraft", "WomanCraft"),
    ("FBA", "FBA"),
    ("Offsite Wrapping", "Offsite Wrapping"),
]
TRANSACTION_TYPES = (
    ("Opening Balance", "Opening Balance"),
    ("Closing Balance", "Closing Balance"),
)
COSTING_METHOD_CHOICES = (
    ("Manual", "Manual"),
    ("Last Invoice", "Last Invoice"),
    ("6 Month Average", "6 Month Average"),
    ("12 Month Average", "12 Month Average"),
)

UNIT_OF_MEASURES = (
    ("grams", "grams"),
    ("oz", "oz"),
    ("lbs", "lbs"),
    ("each", "each"),
    ("hours", "hours"),
    ("minutes", "minutes"),
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
SUPPLIER_CHOICES = (
    ("Distributor", "Distributor"),
    ("Manufacturer", "Manufacturer"),
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
    Recipe_Line = apps.get_model("operations", "Recipe_Line")

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

        Product = apps.get_model("operations", "Product")
        Product.objects.filter(id=p).update(
            unit_material_cost=unit_material_cost,
            unit_labor_cost=unit_labor_cost,
            unit_freight_cost=unit_freight_cost,
        )

    return p
