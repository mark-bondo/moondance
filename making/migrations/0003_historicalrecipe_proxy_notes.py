# Generated by Django 3.1.5 on 2021-05-30 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('making', '0002_auto_20210530_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalrecipe_proxy',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
