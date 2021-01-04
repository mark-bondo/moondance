# Generated by Django 3.1.5 on 2021-01-04 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0002_auto_20210104_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('Finished Goods', 'Finished Goods'), ('WIP', 'WIP'), ('Raw Materials', 'Raw Materials')], default='Finished Goods', max_length=200),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Product_Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('family', models.CharField(max_length=200)),
                ('category', models.CharField(max_length=200, unique=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_code_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_code_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Product Hierarchy',
                'verbose_name_plural': 'Product Hierarchy',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Product_product_code_fk', to='operations.product_code'),
            preserve_default=False,
        ),
    ]
