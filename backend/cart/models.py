from django.db import models
from django.utils.timezone import now


class Orders(models.Model):
    ORDER_STATUS = [
        ('PENDING', '待付款'),
        ('PROCESSING', '付款中'),
        ('COMPLETED', '已付款'),
        ('CANCELLED', '已取消'),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=now)
    recipient = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    detailed_address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_status = models.CharField(max_length=15, choices=ORDER_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('cart.Orders', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Products', on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    class Meta:
        db_table = 'order_items'
        unique_together = ('order', 'product')  # 確保訂單內每個商品唯一

class ShoppingCartItems(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Products', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shopping_cart_items'

class PaymentTransactions(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=9, choices=PAYMENT_STATUS_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        db_table = 'payment_transactions'


class ShippingDetails(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    ]

    shipping_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('cart.Orders', on_delete=models.CASCADE, related_name='shipping_details')
    shipping_status = models.CharField(max_length=10, choices=SHIPPING_STATUS_CHOICES)
    carrier_name = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'shipping_details'

class ProductMemberRatings(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    rated_by_user = models.ForeignKey(
        'users.MemberBasic',
        models.DO_NOTHING,
        related_name='productmemberratings_rated_by_user_set'
    )
    order = models.ForeignKey('cart.Orders', models.DO_NOTHING)
    rating = models.IntegerField()
    rating_type = models.CharField(max_length=6)
    rating_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_member_ratings'
