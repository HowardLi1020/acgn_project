from rest_framework import serializers
from .models import OrderItems, Orders, ShoppingCartItems, PaymentTransactions, ShippingDetails, ProductMemberRatings

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='order_items_set')

    class Meta:
        model = Orders
        fields = '__all__'

class ShoppingCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCartItems
        fields = '__all__'

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransactions
        fields = '__all__'

class ShippingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingDetails
        fields = '__all__'

class ProductMemberRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMemberRatings
        fields = '__all__'
