# Generated by Django 3.1.5 on 2021-01-26 20:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0001_initial'),
        ('making', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product_bundle_line',
            options={'ordering': ('bundle', 'product_used__sku'), 'verbose_name': 'Bundled Product', 'verbose_name_plural': 'Bundled Products'},
        ),
        migrations.AlterField(
            model_name='historicalproduct_bundle_line',
            name='product_used',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.finished_goods_proxy'),
        ),
        migrations.AlterField(
            model_name='product_bundle_line',
            name='product_used',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Product_Bundle_product_used_fk', to='operations.finished_goods_proxy'),
        ),
        migrations.CreateModel(
            name='Product_Bundle_Header',
            fields=[
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('bundle', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='Product_Bundle_product_bundle_fk', serialize=False, to='making.product_bundle_proxy')),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_bundle_header_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_bundle_header_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Bundled Product',
                'verbose_name_plural': 'Bundled Products',
                'ordering': ('bundle__sku',),
            },
        ),
        migrations.CreateModel(
            name='HistoricalProduct_Bundle_Header',
            fields=[
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('bundle', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='making.product_bundle_proxy')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Bundled Product',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterField(
            model_name='historicalproduct_bundle_line',
            name='bundle',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='making.product_bundle_header'),
        ),
        migrations.AlterField(
            model_name='product_bundle_line',
            name='bundle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Product_Bundle_product_bundle_fk', to='making.product_bundle_header'),
        ),
    ]
