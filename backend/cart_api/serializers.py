from rest_framework import serializers
from cart.models import ShoppingCartItems, Orders, OrderItems, PaymentTransactions
from products.models import ProductImages

class ShoppingCartItemsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCartItems
        fields = ['cart_item_id', 'user_id', 'product_id', 'product_name', 'product_image', 'price', 'quantity', 'added_at']

    def get_product_image(self, obj):
        product_image = ProductImages.objects.filter(product=obj.product, is_main=True).first()
        request = self.context.get("request")
        if product_image and request:
            return request.build_absolute_uri(product_image.image_url.url)
        return None

class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = [
            'order_id', 'recipient', 'recipient_phone', 'city', 'region', 'detailed_address', 'postal_code', 'order_status', 'total_amount', 'created_at'
        ]

class OrderItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItems
        fields = [
            'product_id', 'product_name' , 'price', 'quantity', 'subtotal'
        ]
        read_only_fields = ['subtotal']

class PaymentTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransactions
        fields = [
            'payment_id', 'payment_method', 'payment_status', 'payment_date', 'payment_amount', 'transaction_id'
        ]