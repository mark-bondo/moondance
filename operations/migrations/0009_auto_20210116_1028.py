# Generated by Django 3.1.5 on 2021-01-16 15:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0008_auto_20210116_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsupplier',
            name='type',
            field=models.CharField(choices=[('distributor', 'distributor'), ('manufacturer', 'manufacturer')], db_index=True, default='manufacturer', max_length=200),
        ),
        migrations.AddField(
            model_name='supplier',
            name='type',
            field=models.CharField(choices=[('distributor', 'distributor'), ('manufacturer', 'manufacturer')], default='manufacturer', max_length=200),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='date_invoiced',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date_invoiced',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
