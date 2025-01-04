from rest_framework import serializers
from cart.models import Orders, OrderItems, ShoppingCartItems

# 購物車項目序列化器
class ShoppingCartItemsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ShoppingCartItems
        fields = ['cart_item_id', 'member', 'product', 'product_name', 'product_price', 'quantity', 'added_at']
        read_only_fields = ['cart_item_id', 'added_at']

    def validate(self, data):
        # 檢查是否已存在於購物車
        member = data['member']
        product = data['product']
        if ShoppingCartItems.objects.filter(member=member, product=product).exists():
            raise serializers.ValidationError("此商品已存在於購物車中，請更新數量而非重複添加。")

        # 檢查庫存
        if data['quantity'] > product.stock:
            raise serializers.ValidationError(f"商品庫存不足，當前庫存為 {product.stock}")

        return data

# 訂單細項序列化器
class OrderItemsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = OrderItems
        fields = ['order_item_id', 'order', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']
        read_only_fields = ['order_item_id', 'subtotal']

# 訂單序列化器
class OrdersSerializer(serializers.ModelSerializer):
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

    def validate(self, data):
        # 確認購物車有商品
        member = data['member']
        cart_items = ShoppingCartItems.objects.filter(member=member)
        if not cart_items.exists():
            raise serializers.ValidationError("購物車中沒有商品，無法提交訂單。")

        # 檢查商品是否仍可購買
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                raise serializers.ValidationError(
                    f"商品 {cart_item.product.product_name} 庫存不足，請更新購物車。"
                )

        return data
