from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Product, Recipe_Line, recalculate_bom_cost


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
