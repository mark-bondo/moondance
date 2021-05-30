# Generated by Django 3.1.5 on 2021-05-30 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('making', '0006_auto_20210530_1050'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalrecipe_proxy',
            old_name='labor_minutes',
            new_name='labor_amount',
        ),
        migrations.AlterField(
            model_name='historicalrecipe_proxy',
            name='labor_type',
            field=models.CharField(blank=True, choices=[('Soap Making', 'Soap Making'), ('Soap Wrapping', 'Soap Wrapping'), ('Soap Boxing', 'Soap Boxing')], max_length=100, null=True),
        ),
    ]
