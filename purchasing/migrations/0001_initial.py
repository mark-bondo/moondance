# Generated by Django 3.1.5 on 2021-01-26 17:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('type', models.CharField(choices=[('Distributor', 'Distributor'), ('Manufacturer', 'Manufacturer')], default='Manufacturer', max_length=200)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('contact_name', models.CharField(blank=True, max_length=200, null=True)),
                ('contact_email', models.CharField(blank=True, max_length=200, null=True)),
                ('street_address', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('state', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.CharField(blank=True, default='United States', max_length=200, null=True)),
                ('supplier_website', models.URLField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
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
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('invoice', models.CharField(max_length=200)),
                ('order', models.CharField(blank=True, max_length=200, null=True)),
                ('date_invoiced', models.DateField(default=django.utils.timezone.now)),
                ('freight_charges', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Invoice_supplier_fk', to='purchasing.supplier', verbose_name='Invoicing Supplier')),
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
                'ordering': ('-date_invoiced', 'invoice'),
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
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], max_length=200)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_onhand_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_onhand_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Inventory_Onhand_sku_fk', to='operations.Raw_Material_Proxy')),
            ],
            options={
                'verbose_name': 'Inventory Onhand',
                'verbose_name_plural': 'Inventory Onhand',
                'ordering': ('sku', 'location'),
            },
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
                ('supplier_sku_link', models.URLField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sku', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.Raw_Material_Proxy')),
                ('supplier', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='purchasing.supplier')),
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
                ('type', models.CharField(choices=[('Distributor', 'Distributor'), ('Manufacturer', 'Manufacturer')], default='Manufacturer', max_length=200)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('contact_name', models.CharField(blank=True, max_length=200, null=True)),
                ('contact_email', models.CharField(blank=True, max_length=200, null=True)),
                ('street_address', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('state', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.CharField(blank=True, default='United States', max_length=200, null=True)),
                ('supplier_website', models.URLField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
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
            name='HistoricalInvoice_Line',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], max_length=200)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='purchasing.invoice')),
                ('manufacturer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='purchasing.supplier', verbose_name='Manufacturer')),
                ('sku', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.Raw_Material_Proxy', verbose_name='MoonDance SKU')),
            ],
            options={
                'verbose_name': 'historical Invoice Line',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalInvoice',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('invoice', models.CharField(max_length=200)),
                ('order', models.CharField(blank=True, max_length=200, null=True)),
                ('date_invoiced', models.DateField(default=django.utils.timezone.now)),
                ('freight_charges', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='purchasing.supplier', verbose_name='Invoicing Supplier')),
            ],
            options={
                'verbose_name': 'historical Invoice',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
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
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], max_length=200)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sku', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='operations.Raw_Material_Proxy')),
            ],
            options={
                'verbose_name': 'historical Inventory Onhand',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
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
                ('supplier_sku_link', models.URLField(blank=True, null=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_product_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_product_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Supplier_Product_product_fk', to='operations.Raw_Material_Proxy')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='supplier_product_supplier_fk', to='purchasing.supplier')),
            ],
            options={
                'verbose_name': 'Supplier Product',
                'verbose_name_plural': 'Supplier Products',
                'ordering': ('sku', 'supplier_sku'),
                'unique_together': {('supplier', 'supplier_sku')},
            },
        ),
        migrations.CreateModel(
            name='Invoice_Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('unit_of_measure', models.CharField(choices=[('grams', 'grams'), ('oz', 'oz'), ('lbs', 'lbs'), ('each', 'each')], max_length=200)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_line_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_line_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Invoice_Line_invoice_fk', to='purchasing.invoice')),
                ('manufacturer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Invoice_Manufacturer_fk', to='purchasing.supplier', verbose_name='Manufacturer')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Invoice_Line_sku_fk', to='operations.Raw_Material_Proxy', verbose_name='MoonDance SKU')),
            ],
            options={
                'verbose_name': 'Invoice Line',
                'verbose_name_plural': 'Invoice Lines',
                'ordering': ('sku',),
                'unique_together': {('sku', 'invoice')},
            },
        ),
        migrations.AddField(
            model_name='historicalinventory_onhand',
            name='to_location',
            field=models.CharField(blank=True, choices=[('Bondo - Garage', 'Bondo - Garage'), ('Bondo - 2nd Floor', 'Bondo - 2nd Floor'), ('MoonDance HQ - Workshop', 'MoonDance HQ - Workshop'), ('MoonDance HQ - Fulfillment Center', 'MoonDance HQ - Fulfillment Center')], max_length=200, null=True, verbose_name='Transfer To Location'),
        ),
        migrations.AddField(
            model_name='historicalinventory_onhand',
            name='transfer_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='inventory_onhand',
            name='to_location',
            field=models.CharField(blank=True, choices=[('Bondo - Garage', 'Bondo - Garage'), ('Bondo - 2nd Floor', 'Bondo - 2nd Floor'), ('MoonDance HQ - Workshop', 'MoonDance HQ - Workshop'), ('MoonDance HQ - Fulfillment Center', 'MoonDance HQ - Fulfillment Center')], max_length=200, null=True, verbose_name='Transfer To Location'),
        ),
        migrations.AddField(
            model_name='inventory_onhand',
            name='transfer_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='inventory_onhand',
            unique_together={('sku', 'location')},
        ),
    ]
