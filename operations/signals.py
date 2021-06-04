from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Product, Recipe_Line
from .admin import convert_weight


def recalculate_bom_cost(p):
    bom = (
        Recipe_Line.objects.filter(sku_parent_id=p)
        .select_related("sku")
        .only(
            "quantity",
            "sku__unit_material_cost",
            "sku__unit_labor_cost",
            "sku__unit_of_measure",
        )
    )

    unit_material_cost = 0
    unit_labor_cost = 0

    for b in bom:
        converted_weight = convert_weight(
            to_measure=b.sku.unit_of_measure,
            from_measure=b.unit_of_measure,
            weight=(b.quantity or 0),
        )

        unit_material_cost += (b.sku.unit_material_cost or 0) * converted_weight
        unit_labor_cost += (b.sku.unit_labor_cost or 0) * converted_weight

    Product.objects.filter(id=p).update(
        unit_material_cost=unit_material_cost, unit_labor_cost=unit_labor_cost
    )

    return p


@receiver(post_save, sender=Product)
def post_save(sender, instance, created, **kwargs):
    if created:
        return

    # recalculate rolled BOM costs
    if (
        instance.original_unit_material_cost != instance.unit_material_cost
        or instance.original_unit_labor_cost != instance.unit_labor_cost
    ):
        parents = list(
            Recipe_Line.objects.filter(sku=instance)
            .order_by("sku_parent_id")
            .distinct("sku_parent_id")
            .values_list("sku_parent_id", flat=True)
        )
    else:
        parents = []

    parents.append(instance.id)

    while parents:
        p = parents[0]
        current_level_parent = recalculate_bom_cost(p)
        next_level_parent = (
            Recipe_Line.objects.filter(sku_id=current_level_parent)
            .order_by("sku_parent_id")
            .distinct("sku_parent_id")
            .values_list("sku_parent_id", flat=True)
        )

        for n in next_level_parent:
            parents.append(n)

        parents.remove(p)
