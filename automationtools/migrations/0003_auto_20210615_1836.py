# Generated by Django 3.1.5 on 2021-06-15 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automationtools', '0002_auto_20210615_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboard',
            name='charts',
            field=models.ManyToManyField(null=True, to='automationtools.Chart'),
        ),
    ]
