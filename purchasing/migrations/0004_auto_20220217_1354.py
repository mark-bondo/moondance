# Generated by Django 3.1.12 on 2022-02-17 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0003_auto_20220213_1159'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invoice_line',
            unique_together=set(),
        ),
    ]