# Generated by Django 3.1.12 on 2022-02-13 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0002_auto_20220212_1058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice_line',
            options={'ordering': ('-invoice__date_invoiced',), 'verbose_name': 'Receipt Line', 'verbose_name_plural': 'Receipt Lines'},
        ),
    ]