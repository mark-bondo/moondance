# Generated by Django 3.1.5 on 2021-06-05 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='amazon_product',
            options={'ordering': ('product__sku', 'asin'), 'verbose_name': 'Amazon Product', 'verbose_name_plural': 'Amazon Products'},
        ),
        migrations.RemoveField(
            model_name='amazon_product',
            name='seller_sku',
        ),
        migrations.RemoveField(
            model_name='historicalamazon_product',
            name='seller_sku',
        ),
        migrations.AlterField(
            model_name='amazon_product',
            name='asin',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalamazon_product',
            name='asin',
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]