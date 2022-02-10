from django.dispatch import receiver
from django.db.models.signals import post_save
from operations.models import Product, Recipe_Line
from utils import common
from purchasing.models import Inventory_Onhand


@receiver(post_save, sender=Product)
def post_save(sender, instance, created, **kwargs):
    if created:
        return

    # recalculate rolled BOM costs
    if (
        instance.original_unit_material_cost != instance.unit_material_cost
        or instance.original_unit_labor_cost != instance.unit_labor_cost
        or instance.original_unit_freight_cost != instance.unit_freight_cost
    ):
        parents = list(
            Recipe_Line.objects.filter(sku=instance)
            .order_by("sku_parent_id")
            .distinct("sku_parent_id")
            .values_list("sku_parent_id", flat=True)
        )

        while parents:
            p = parents[0]
            current_level_parent = common.recalculate_bom_cost(p)
            next_level_parent = (
                Recipe_Line.objects.filter(sku_id=current_level_parent)
                .order_by("sku_parent_id")
                .distinct("sku_parent_id")
                .values_list("sku_parent_id", flat=True)
            )

            for n in next_level_parent:
                parents.append(n)

            parents.remove(p)

    # recalculate inventory weights
    if instance.original_unit_of_measure != instance.unit_of_measure:
        location_inventory = Inventory_Onhand.objects.filter(sku=instance)

        for i in location_inventory:
            converted_weight = common.convert_weight(
                from_measure=instance.original_unit_of_measure,
                to_measure=instance.unit_of_measure,
                weight=i.quantity_onhand,
            )
            i.quantity_onhand = converted_weight
            i.save()
