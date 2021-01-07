# Generated by Django 3.1.5 on 2021-01-07 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0013_auto_20210107_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_code',
            name='freight_factor_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Percentage adder to material cost. Use whole numbers with 2 decimals maximum.'),
        ),
        migrations.DeleteModel(
            name='HistoricalMaterials_Management_Proxy',
        ),
    ]
