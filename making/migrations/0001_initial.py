# Generated by Django 3.1.5 on 2021-05-30 15:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product_Bundle_Header',
            fields=[
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('bundle', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='Product_Bundle_product_bundle_fk', serialize=False, to='operations.finished_goods_proxy')),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_bundle_header_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_bundle_header_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Product Bundle',
                'verbose_name_plural': 'Product Bundles',
                'ordering': ('bundle__sku',),
            },
        ),
        migrations.CreateModel(
            name='Weight_Conversions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('minutes', 'minutes')], max_length=200)),
                ('to_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('minutes', 'minutes')], max_length=200)),
                ('conversion_rate', models.DecimalField(decimal_places=6, max_digits=16)),
            ],
            options={
                'verbose_name': 'Weight Conversion',
                'verbose_name_plural': 'Weight Conversions',
            },
        ),
        migrations.CreateModel(
            name='Recipe_Proxy',
            fields=[
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'ordering': ('sku',),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('operations.product',),
        ),
        migrations.CreateModel(
            name='Product_Bundle_Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('quantity', models.IntegerField()),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_bundle_line_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_bundle_line_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Product_Bundle_product_bundle_fk', to='making.product_bundle_header')),
                ('product_used', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Product_Bundle_product_used_fk', to='operations.finished_goods_proxy')),
            ],
            options={
                'verbose_name': 'Bundled Product',
                'verbose_name_plural': 'Bundled Products',
                'ordering': ('bundle', 'product_used__sku'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalRecipe_Proxy',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('product_type', models.CharField(choices=[('Finished Goods', 'Finished Goods'), ('WIP', 'WIP'), ('Raw Materials', 'Raw Materials'), ('Labor', 'Labor')], max_length=200)),
                ('sku', models.CharField(db_index=True, max_length=200, verbose_name='SKU')),
                ('description', models.CharField(max_length=200)),
                ('upc', models.CharField(blank=True, max_length=200, null=True, verbose_name='UPC')),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('minutes', 'minutes')], default='lbs', max_length=200)),
                ('unit_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_sales_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_material_cost', models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True)),
                ('unit_labor_cost', models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True)),
                ('unit_freight_cost', models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True)),
                ('product_notes', models.TextField(blank=True, null=True, verbose_name='Product Notes')),
                ('labor_amount', models.IntegerField(blank=True, null=True)),
                ('labor_type', models.CharField(blank=True, choices=[('Soap Making', 'Soap Making'), ('Soap Wrapping', 'Soap Wrapping'), ('Soap Boxing', 'Soap Boxing')], max_length=100, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('product_code', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.product_code')),
            ],
            options={
                'verbose_name': 'historical Recipe',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRecipe_Line',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('quantity', models.DecimalField(decimal_places=5, max_digits=12)),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('minutes', 'minutes')], default='grams', max_length=200)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sku', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.raw_material_proxy')),
                ('sku_parent', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.product')),
            ],
            options={
                'verbose_name': 'historical Recipe Line',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProduct_Bundle_Line',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('quantity', models.IntegerField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('bundle', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='making.product_bundle_header')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('product_used', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.finished_goods_proxy')),
            ],
            options={
                'verbose_name': 'historical Bundled Product',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
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
                ('bundle', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.finished_goods_proxy')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Product Bundle',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Recipe_Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('quantity', models.DecimalField(decimal_places=5, max_digits=12)),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each'), ('minutes', 'minutes')], default='grams', max_length=200)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipe_line_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipe_line_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Recipe_sku_fk', to='operations.raw_material_proxy')),
                ('sku_parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Recipe_sku_parent_fk', to='operations.product')),
            ],
            options={
                'verbose_name': 'Recipe Line',
                'verbose_name_plural': 'Recipe Lines',
                'ordering': ('sku_parent', 'sku'),
                'unique_together': {('sku', 'sku_parent')},
            },
        ),
    ]
