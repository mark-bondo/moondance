# Generated by Django 3.1.5 on 2021-01-06 20:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0007_materials_management_proxy'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Inventory_Onhand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('location', models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Bondo - 2nd Floor', 'Bondo - 2nd Floor'), ('MoonDance HQ - Workshop', 'MoonDance HQ - Workshop'), ('MoonDance HQ - Fulfillment Center', 'MoonDance HQ - Fulfillment Center')], max_length=200)),
                ('quantity_onhand', models.DecimalField(decimal_places=2, max_digits=12)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_onhand_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_onhand_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Inventory_Onhand_sku_fk', to='operations.product')),
            ],
            options={
                'verbose_name': 'Inventory Onhand',
                'verbose_name_plural': 'Inventory Onhand',
                'ordering': ('sku', 'location'),
            },
        ),
    ]