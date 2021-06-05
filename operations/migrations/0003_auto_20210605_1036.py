# Generated by Django 3.1.5 on 2021-06-05 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0002_auto_20210531_1136'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe_line',
            options={'ordering': ('sku__product_code__family', 'sku__sku'), 'verbose_name': 'Recipe', 'verbose_name_plural': 'Recipe'},
        ),
        migrations.AddField(
            model_name='historicalproduct',
            name='unit_freight_cost',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='unit_freight_cost',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='unit_of_measure',
            field=models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('hours', 'hours'), ('minutes', 'minutes')], default='lbs', max_length=200),
        ),
        migrations.AlterField(
            model_name='historicalrecipe_line',
            name='unit_of_measure',
            field=models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('hours', 'hours'), ('minutes', 'minutes')], default='grams', max_length=200),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit_of_measure',
            field=models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('hours', 'hours'), ('minutes', 'minutes')], default='lbs', max_length=200),
        ),
        migrations.AlterField(
            model_name='product_code',
            name='freight_factor_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Percentage adder to material cost. Use whole numbers with 2 decimals maximum.', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='product_code',
            name='type',
            field=models.CharField(choices=[('Finished Goods', 'Finished Goods'), ('Raw Materials', 'Raw Materials'), ('Labor', 'Labor'), ('Labor Groups', 'Labor Groups'), ('Services', 'Services'), ('WIP', 'WIP')], max_length=200),
        ),
        migrations.AlterField(
            model_name='recipe_line',
            name='unit_of_measure',
            field=models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('hours', 'hours'), ('minutes', 'minutes')], default='grams', max_length=200),
        ),
    ]
