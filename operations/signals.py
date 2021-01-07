from .models import Materials_Management_Proxy, Inventory_Onhand
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
