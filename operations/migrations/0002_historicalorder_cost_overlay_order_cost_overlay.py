# Generated by Django 3.1.5 on 2021-01-29 21:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Cost_Overlay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(auto_now_add=True, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(auto_now=True, verbose_name='Datetime Updated')),
                ('sales_channel', models.CharField(choices=[('Shopify Website', 'Shopify Website'), ('Amazon FBA', 'Amazon FBA'), ('Amazon FBM', 'Amazon FBM'), ('POS', 'POS')], max_length=200)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('type', models.CharField(choices=[('Fulfillment Labor', 'Fulfillment Labor'), ('Shipping Materials', 'Shipping Materials')], max_length=200)),
                ('apply_to', models.CharField(choices=[('Each Order', 'Each Order'), ('Each Order Line', 'Each Order Line')], max_length=200)),
                ('labor_hourly_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('labor_minutes', models.IntegerField(blank=True, null=True)),
                ('material_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True)),
                ('_created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='order_cost_overlay_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='order_cost_overlay_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
            ],
            options={
                'verbose_name': 'Order Cost Overlay',
                'verbose_name_plural': 'Order Cost Overlays',
                'ordering': ('sales_channel', 'name'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalOrder_Cost_Overlay',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('_created', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Created')),
                ('_last_updated', models.DateTimeField(blank=True, editable=False, verbose_name='Datetime Updated')),
                ('sales_channel', models.CharField(choices=[('Shopify Website', 'Shopify Website'), ('Amazon FBA', 'Amazon FBA'), ('Amazon FBM', 'Amazon FBM'), ('POS', 'POS')], max_length=200)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('type', models.CharField(choices=[('Fulfillment Labor', 'Fulfillment Labor'), ('Shipping Materials', 'Shipping Materials')], max_length=200)),
                ('apply_to', models.CharField(choices=[('Each Order', 'Each Order'), ('Each Order Line', 'Each Order Line')], max_length=200)),
                ('labor_hourly_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('labor_minutes', models.IntegerField(blank=True, null=True)),
                ('material_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('_created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('_last_updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Last Updated By')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Order Cost Overlay',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]