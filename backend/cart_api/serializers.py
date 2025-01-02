from rest_framework import serializers
from cart.models import Orders, OrderItems, ShoppingCartItems

class ShoppingCartItemsSerializer(serializers.ModelSerializer):
    """
    用戶端購物車項目序列化
    """
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ShoppingCartItems
        fields = ['cart_item_id', 'member', 'product', 'product_name', 'product_price', 'quantity', 'added_at']
        read_only_fields = ['cart_item_id', 'added_at']


class OrderItemsSerializer(serializers.ModelSerializer):
    """
    訂單細項序列化
    """
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = OrderItems
        fields = ['order_item_id', 'order', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']
        read_only_fields = ['order_item_id', 'subtotal']


class OrdersSerializer(serializers.ModelSerializer):
    """
    訂單序列化
    """
    order_items = OrderItemsSerializer(many=True, read_only=True, source='orderitems_set')

    class Meta:
        model = Orders
        fields = [
            'order_id', 'member', 'order_date', 'recipient', 'city', 'region', 
            'detailed_address', 'postal_code', 'total_amount', 'coupon_code', 
            'coupon_discount', 'payment_status', 'shipping_status', 
            'payment_method', 'order_status', 'created_at', 'updated_at', 'order_items'
        ]
        read_only_fields = ['order_id', 'order_date', 'created_at', 'updated_at']
