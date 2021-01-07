# Generated by Django 3.1.5 on 2021-01-07 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('product_type', models.CharField(choices=[('Finished Goods', 'Finished Goods'), ('WIP', 'WIP'), ('Raw Materials', 'Raw Materials')], max_length=200)),
                ('sku', models.CharField(max_length=200, unique=True, verbose_name='SKU')),
                ('description', models.CharField(max_length=200)),
                ('upc', models.CharField(blank=True, max_length=200, null=True, verbose_name='UPC')),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], default='grams', max_length=200, verbose_name='Default Unit of Measure')),
                ('total_quantity_onhand', models.DecimalField(blank=True, decimal_places=2, help_text='Total inventory across all locations.  Updates to quantites to should be done using the Inventory Onhand form below.', max_digits=12, null=True, verbose_name='Total Onhand Quantity')),
                ('total_freight_cost', models.DecimalField(blank=True, decimal_places=2, help_text='Calculated using a percentage adder to account for inbound freight based upon type of material.', max_digits=12, null=True)),
                ('total_material_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_sales_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_material_cost', models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True)),
                ('freight_factor_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Product Master',
                'verbose_name_plural': 'Product Master',
                'ordering': ('sku',),
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('contact_name', models.CharField(blank=True, max_length=200, null=True)),
                ('contact_email', models.CharField(blank=True, max_length=200, null=True)),
                ('street_address', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('state', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.CharField(blank=True, default='United States', max_length=200, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Supplier',
                'verbose_name_plural': 'Suppliers',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Shopify_Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('shopify_product_id', models.CharField(max_length=200, unique=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='shopify_product_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='shopify_product_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shopify_product_sku_fk', to='operations.product')),
            ],
            options={
                'verbose_name': 'Shopify Product',
                'verbose_name_plural': 'Shopify Products',
            },
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
                ('freight_factor_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Percentage adder to material cost. Use whole numbers with 2 decimals maximum.')),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_code_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_code_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Product - Category',
                'verbose_name_plural': 'Product - Categories',
                'ordering': ('family', 'category'),
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Product_product_code_fk', to='operations.product_code'),
        ),
        migrations.CreateModel(
            name='HistoricalSupplier_Product',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('supplier_sku', models.CharField(max_length=200)),
                ('supplier_sku_description', models.CharField(max_length=200)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.product')),
                ('supplier', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.supplier')),
            ],
            options={
                'verbose_name': 'historical Supplier Product',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSupplier',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('contact_name', models.CharField(blank=True, max_length=200, null=True)),
                ('contact_email', models.CharField(blank=True, max_length=200, null=True)),
                ('street_address', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('state', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.CharField(blank=True, default='United States', max_length=200, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Supplier',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProduct',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('product_type', models.CharField(choices=[('Finished Goods', 'Finished Goods'), ('WIP', 'WIP'), ('Raw Materials', 'Raw Materials')], max_length=200)),
                ('sku', models.CharField(db_index=True, max_length=200, verbose_name='SKU')),
                ('description', models.CharField(max_length=200)),
                ('upc', models.CharField(blank=True, max_length=200, null=True, verbose_name='UPC')),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], default='grams', max_length=200, verbose_name='Default Unit of Measure')),
                ('total_quantity_onhand', models.DecimalField(blank=True, decimal_places=2, help_text='Total inventory across all locations.  Updates to quantites to should be done using the Inventory Onhand form below.', max_digits=12, null=True, verbose_name='Total Onhand Quantity')),
                ('total_freight_cost', models.DecimalField(blank=True, decimal_places=2, help_text='Calculated using a percentage adder to account for inbound freight based upon type of material.', max_digits=12, null=True)),
                ('total_material_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_sales_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit_material_cost', models.DecimalField(blank=True, decimal_places=5, max_digits=12, null=True)),
                ('freight_factor_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
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
                'verbose_name': 'historical Product Master',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Amazon_Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('asin', models.CharField(max_length=200, unique=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='amazon_product_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='amazon_product_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='amazon_product_product_fk', to='operations.product')),
            ],
            options={
                'verbose_name': 'Amazon Product',
                'verbose_name_plural': 'Amazon Products',
                'ordering': ('asin',),
            },
        ),
        migrations.CreateModel(
            name='Materials_Management_Proxy',
            fields=[
            ],
            options={
                'verbose_name': 'Product - Raw Material',
                'verbose_name_plural': 'Product - Raw Materials',
                'ordering': ('sku',),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('operations.product',),
        ),
        migrations.CreateModel(
            name='Supplier_Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('supplier_sku', models.CharField(max_length=200)),
                ('supplier_sku_description', models.CharField(max_length=200)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_product_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_product_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Supplier_Product_product_fk', to='operations.product')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='supplier_product_supplier_fk', to='operations.supplier')),
            ],
            options={
                'verbose_name': 'Supplier Product',
                'verbose_name_plural': 'Supplier Products',
                'ordering': ('product', 'supplier_sku'),
                'unique_together': {('product', 'supplier_sku')},
            },
        ),
        migrations.CreateModel(
            name='Inventory_Onhand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('location', models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Bondo - 2nd Floor', 'Bondo - 2nd Floor'), ('MoonDance HQ - Workshop', 'MoonDance HQ - Workshop'), ('MoonDance HQ - Fulfillment Center', 'MoonDance HQ - Fulfillment Center')], max_length=200)),
                ('quantity_onhand', models.DecimalField(decimal_places=2, max_digits=12)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_onhand_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_onhand_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Inventory_Onhand_sku_fk', to='operations.materials_management_proxy')),
            ],
            options={
                'verbose_name': 'Inventory Onhand',
                'verbose_name_plural': 'Inventory Onhand',
                'ordering': ('sku', 'location'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalInventory_Onhand',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('location', models.CharField(choices=[('Bondo - Garage', 'Bondo - Garage'), ('Bondo - 2nd Floor', 'Bondo - 2nd Floor'), ('MoonDance HQ - Workshop', 'MoonDance HQ - Workshop'), ('MoonDance HQ - Fulfillment Center', 'MoonDance HQ - Fulfillment Center')], max_length=200)),
                ('quantity_onhand', models.DecimalField(decimal_places=2, max_digits=12)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sku', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.materials_management_proxy')),
            ],
            options={
                'verbose_name': 'historical Inventory Onhand',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
