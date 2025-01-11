from rest_framework import serializers
from cart.models import Orders, OrderItems, ShoppingCartItems
from rest_framework import serializers
from cart.models import ShoppingCartItems
from products.models import Products, ProductImages


class ShoppingCartItemsSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)  # 接收 product_id 作為輸入
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCartItems
        fields = ['cart_item_id', 'product_id', 'product_name', 'product_price', 'product_image', 'quantity', 'added_at']
        read_only_fields = ['cart_item_id', 'added_at']

    def get_product_image(self, obj):
        # 獲取商品主圖片（is_main = 1）或第一張圖片
        main_image = obj.product.productimages_set.filter(is_main=1).first()
        if main_image:
            return main_image.image_url.url
        first_image = obj.product.productimages_set.first()
        return first_image.image_url.url if first_image else None

    def validate(self, data):
        # 確保 product_id 對應的商品存在
        product_id = data.get('product_id')
        if not Products.objects.filter(pk=product_id).exists():
            raise serializers.ValidationError({"product": "該商品不存在"})

        # 確保數量合法
        product = Products.objects.get(pk=product_id)
        if data['quantity'] > product.stock:
            raise serializers.ValidationError({"quantity": f"商品庫存不足，當前庫存為 {product.stock}"})

        return data

    def create(self, validated_data):
        # 將 product_id 替換為 product 實例
        product_id = validated_data.pop('product_id')
        validated_data['product'] = Products.objects.get(pk=product_id)
        # member 由視圖中傳入，因此直接使用
        return ShoppingCartItems.objects.create(**validated_data)
        # 繼續創建購物車項目
        return super().create(validated_data)


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
