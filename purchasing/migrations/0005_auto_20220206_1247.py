# Generated by Django 3.1.12 on 2022-02-06 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0004_auto_20220206_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalinvoice',
            name='invoice_attachment',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_attachment',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='historicalinventory_onhand',
            name='location',
            field=models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Workshop', 'Workshop'), ('Fulfillment Area', 'Fulfillment Area'), ('DFM Staging', 'DFM Staging'), ('Curing Room', 'Curing Room'), ('WomanCraft', 'WomanCraft'), ('FBA', 'FBA'), ('Offsite Wrapping', 'Offsite Wrapping')], max_length=200, verbose_name='Current Location'),
        ),
        migrations.AlterField(
            model_name='historicalinventory_onhand',
            name='to_location',
            field=models.CharField(blank=True, choices=[('Bondo - Garage', 'Bondo - Garage'), ('Workshop', 'Workshop'), ('Fulfillment Area', 'Fulfillment Area'), ('DFM Staging', 'DFM Staging'), ('Curing Room', 'Curing Room'), ('WomanCraft', 'WomanCraft'), ('FBA', 'FBA'), ('Offsite Wrapping', 'Offsite Wrapping')], max_length=200, null=True, verbose_name='Transfer To Location'),
        ),
        migrations.AlterField(
            model_name='historicalitem_transaction_history',
            name='location',
            field=models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Workshop', 'Workshop'), ('Fulfillment Area', 'Fulfillment Area'), ('DFM Staging', 'DFM Staging'), ('Curing Room', 'Curing Room'), ('WomanCraft', 'WomanCraft'), ('FBA', 'FBA'), ('Offsite Wrapping', 'Offsite Wrapping')], max_length=200),
        ),
        migrations.AlterField(
            model_name='inventory_onhand',
            name='location',
            field=models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Workshop', 'Workshop'), ('Fulfillment Area', 'Fulfillment Area'), ('DFM Staging', 'DFM Staging'), ('Curing Room', 'Curing Room'), ('WomanCraft', 'WomanCraft'), ('FBA', 'FBA'), ('Offsite Wrapping', 'Offsite Wrapping')], max_length=200, verbose_name='Current Location'),
        ),
        migrations.AlterField(
            model_name='inventory_onhand',
            name='to_location',
            field=models.CharField(blank=True, choices=[('Bondo - Garage', 'Bondo - Garage'), ('Workshop', 'Workshop'), ('Fulfillment Area', 'Fulfillment Area'), ('DFM Staging', 'DFM Staging'), ('Curing Room', 'Curing Room'), ('WomanCraft', 'WomanCraft'), ('FBA', 'FBA'), ('Offsite Wrapping', 'Offsite Wrapping')], max_length=200, null=True, verbose_name='Transfer To Location'),
        ),
        migrations.AlterField(
            model_name='item_transaction_history',
            name='location',
            field=models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Workshop', 'Workshop'), ('Fulfillment Area', 'Fulfillment Area'), ('DFM Staging', 'DFM Staging'), ('Curing Room', 'Curing Room'), ('WomanCraft', 'WomanCraft'), ('FBA', 'FBA'), ('Offsite Wrapping', 'Offsite Wrapping')], max_length=200),
        ),
    ]
