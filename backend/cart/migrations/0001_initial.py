# Generated by Django 5.1.4 on 2024-12-26 14:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_date', models.DateTimeField(blank=True, null=True)),
                ('recipient', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
                ('detailed_address', models.CharField(max_length=255)),
                ('postal_code', models.CharField(max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('coupon_code', models.CharField(blank=True, max_length=50, null=True)),
                ('coupon_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_status', models.CharField(blank=True, max_length=9, null=True)),
                ('shipping_status', models.CharField(blank=True, max_length=10, null=True)),
                ('payment_method', models.CharField(max_length=16)),
                ('order_status', models.CharField(max_length=9)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.memberbasic')),
            ],
            options={
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('order_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('subtotal', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='products.products')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cart.orders')),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
        migrations.CreateModel(
            name='PaymentTransactions',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_method', models.CharField(max_length=16)),
                ('payment_status', models.CharField(max_length=9)),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cart.orders')),
            ],
            options={
                'db_table': 'payment_transactions',
            },
        ),
        migrations.CreateModel(
            name='ProductMemberRatings',
            fields=[
                ('rating_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.IntegerField()),
                ('rating_type', models.CharField(max_length=6)),
                ('rating_date', models.DateTimeField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cart.orders')),
                ('rated_by_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='productmemberratings_rated_by_user_set', to='users.memberbasic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.memberbasic')),
            ],
            options={
                'db_table': 'product_member_ratings',
            },
        ),
        migrations.CreateModel(
            name='ShippingDetails',
            fields=[
                ('shipping_id', models.AutoField(primary_key=True, serialize=False)),
                ('shipping_status', models.CharField(max_length=10)),
                ('carrier_name', models.CharField(blank=True, max_length=100, null=True)),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('shipping_date', models.DateTimeField(blank=True, null=True)),
                ('estimated_delivery_date', models.DateField(blank=True, null=True)),
                ('actual_delivery_date', models.DateField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cart.orders')),
            ],
            options={
                'db_table': 'shipping_details',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCartItems',
            fields=[
                ('cart_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('added_at', models.DateTimeField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.memberbasic')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='products.products')),
            ],
            options={
                'db_table': 'shopping_cart_items',
            },
        ),
    ]
