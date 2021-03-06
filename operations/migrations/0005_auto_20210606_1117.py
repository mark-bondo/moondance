# Generated by Django 3.1.5 on 2021-06-06 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0004_auto_20210606_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalorder_cost_overlay',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='historicalorder_cost_overlay',
            name='sales_channel',
            field=models.CharField(choices=[('Shopify Website', 'Shopify Website'), ('Amazon FBA', 'Amazon FBA'), ('Amazon FBM', 'Amazon FBM'), ('Farmers Market - Wake Forest', 'Farmers Market - Wake Forest'), ('Farmers Market - Durham', 'Farmers Market - Durham')], max_length=200),
        ),
        migrations.AlterField(
            model_name='historicalorder_cost_overlay',
            name='type',
            field=models.CharField(choices=[('Fulfillment Labor', 'Fulfillment Labor'), ('Shipping Materials', 'Shipping Materials'), ('Sales Channel Fees', 'Sales Channel Fees')], max_length=200),
        ),
        migrations.AlterField(
            model_name='order_cost_overlay',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='order_cost_overlay',
            name='sales_channel',
            field=models.CharField(choices=[('Shopify Website', 'Shopify Website'), ('Amazon FBA', 'Amazon FBA'), ('Amazon FBM', 'Amazon FBM'), ('Farmers Market - Wake Forest', 'Farmers Market - Wake Forest'), ('Farmers Market - Durham', 'Farmers Market - Durham')], max_length=200),
        ),
        migrations.AlterField(
            model_name='order_cost_overlay',
            name='type',
            field=models.CharField(choices=[('Fulfillment Labor', 'Fulfillment Labor'), ('Shipping Materials', 'Shipping Materials'), ('Sales Channel Fees', 'Sales Channel Fees')], max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='order_cost_overlay',
            unique_together={('name', 'sales_channel')},
        ),
    ]
