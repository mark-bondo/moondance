# Generated by Django 3.1.5 on 2021-05-30 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0005_auto_20210530_1442'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='finished_goods_proxy',
            options={'ordering': ('sku',), 'verbose_name': 'Product Finished Good', 'verbose_name_plural': 'Product Finished Goods'},
        ),
        migrations.AlterModelOptions(
            name='historicalfinished_goods_proxy',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Product Finished Good'},
        ),
        migrations.AlterModelOptions(
            name='historicallabor_proxy',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Labor Items'},
        ),
        migrations.AlterModelOptions(
            name='historicalraw_material_proxy',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Product Raw Material'},
        ),
        migrations.AlterModelOptions(
            name='labor_code',
            options={'verbose_name': 'Labor Category', 'verbose_name_plural': 'Labor Categories'},
        ),
        migrations.AlterModelOptions(
            name='labor_proxy',
            options={'ordering': ('sku',), 'verbose_name': 'Labor Items', 'verbose_name_plural': 'Labor Items'},
        ),
        migrations.AlterModelOptions(
            name='product_code',
            options={'ordering': ('type', 'family', 'category'), 'verbose_name': 'Product Category', 'verbose_name_plural': 'Product Categories'},
        ),
        migrations.AlterModelOptions(
            name='raw_material_proxy',
            options={'ordering': ('sku',), 'verbose_name': 'Product Raw Material', 'verbose_name_plural': 'Product Raw Materials'},
        ),
        migrations.RemoveField(
            model_name='historicalfinished_goods_proxy',
            name='labor_amount',
        ),
        migrations.RemoveField(
            model_name='historicalfinished_goods_proxy',
            name='labor_type',
        ),
        migrations.RemoveField(
            model_name='historicalfinished_goods_proxy',
            name='product_type',
        ),
        migrations.RemoveField(
            model_name='historicallabor_proxy',
            name='labor_amount',
        ),
        migrations.RemoveField(
            model_name='historicallabor_proxy',
            name='labor_type',
        ),
        migrations.RemoveField(
            model_name='historicallabor_proxy',
            name='product_type',
        ),
        migrations.RemoveField(
            model_name='historicallabor_rate',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='historicalproduct',
            name='labor_amount',
        ),
        migrations.RemoveField(
            model_name='historicalproduct',
            name='labor_type',
        ),
        migrations.RemoveField(
            model_name='historicalproduct',
            name='product_type',
        ),
        migrations.RemoveField(
            model_name='historicalraw_material_proxy',
            name='labor_amount',
        ),
        migrations.RemoveField(
            model_name='historicalraw_material_proxy',
            name='labor_type',
        ),
        migrations.RemoveField(
            model_name='historicalraw_material_proxy',
            name='product_type',
        ),
        migrations.RemoveField(
            model_name='labor_rate',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='product',
            name='labor_amount',
        ),
        migrations.RemoveField(
            model_name='product',
            name='labor_type',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_type',
        ),
    ]
