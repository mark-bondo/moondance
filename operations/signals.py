from .models import Materials_Management_Proxy, Inventory_Onhand
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


@receiver(post_save, sender=Inventory_Onhand)
def product_saved(sender, instance, created, **kwargs):
    pass
    # location_inventory = Inventory_Onhand.objects.filter(sku=instance.sku)
    # total_inventory_onhand = 0

    # print('hello')
    # for i in location_inventory:
    #     print(i.quantity_onhand)
    #     total_inventory_onhand += (i.quantity_onhand or 0)
    
    # totals = Materials_Management_Proxy.objects.get(pk=instance.sku_id)
    # totals.quantity_onhand = total_inventory_onhand
    # totals.save()