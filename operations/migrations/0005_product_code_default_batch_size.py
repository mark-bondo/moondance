# Generated by Django 3.1.12 on 2022-02-16 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0004_auto_20220213_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_code',
            name='default_batch_size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]