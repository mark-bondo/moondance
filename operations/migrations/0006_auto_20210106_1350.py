# Generated by Django 3.1.5 on 2021-01-06 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0005_auto_20210105_1602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='amazon_product',
            options={'ordering': ('asin',), 'verbose_name': 'Amazon Product', 'verbose_name_plural': 'Amazon Products'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('sku',), 'verbose_name': 'Product Master', 'verbose_name_plural': 'Product Master'},
        ),
        migrations.AlterModelOptions(
            name='supplier_product',
            options={'ordering': ('product', 'supplier_sku'), 'verbose_name': 'Supplier Product', 'verbose_name_plural': 'Supplier Products'},
        ),
        migrations.AddField(
            model_name='supplier_product',
            name='supplier_sku_description',
            field=models.CharField(default=None, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='unit_of_measure',
            field=models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], default='grams', max_length=200),
        ),
    ]