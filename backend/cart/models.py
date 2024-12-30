# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('cart.Orders', models.DO_NOTHING)
    product = models.ForeignKey('products.Products', models.DO_NOTHING)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_items'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    order_date = models.DateTimeField(blank=True, null=True)
    recipient = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    detailed_address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(max_length=9, blank=True, null=True)
    shipping_status = models.CharField(max_length=10, blank=True, null=True)
    payment_method = models.CharField(max_length=16)
    order_status = models.CharField(max_length=9)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class ShoppingCartItems(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    product = models.ForeignKey('products.Products', models.DO_NOTHING)
    quantity = models.IntegerField()
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shopping_cart_items'


class PaymentTransactions(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    payment_method = models.CharField(max_length=16)
    payment_status = models.CharField(max_length=9)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_transactions'


class ShippingDetails(models.Model):
    shipping_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    shipping_status = models.CharField(max_length=10)
    carrier_name = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shipping_details'


class ProductMemberRatings(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    rated_by_user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING, related_name='productmemberratings_rated_by_user_set')
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    rating = models.IntegerField()
    rating_type = models.CharField(max_length=6)
    rating_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_member_ratings'
