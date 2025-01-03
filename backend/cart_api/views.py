from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cart.models import Orders, OrderItems, ShoppingCartItems
from .serializers import (
    OrdersSerializer,
    OrderItemsSerializer,
    ShoppingCartItemsSerializer,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cart.models import ShoppingCartItems
from .serializers import ShoppingCartItemsSerializer
from rest_framework.permissions import IsAuthenticated


class ShoppingCartListView(APIView):
    """
    查看用戶購物車
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        cart_items = ShoppingCartItems.objects.filter(member=user)
        serializer = ShoppingCartItemsSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShoppingCartAddView(APIView):
    """
    添加商品到購物車
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ShoppingCartItemsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "商品已成功加入購物車"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartUpdateView(APIView):
    """
    更新購物車中的商品數量
    """
    permission_classes = [IsAuthenticated]
    def put(self, request, cart_item_id):
        try:
            cart_item = ShoppingCartItems.objects.get(pk=cart_item_id)
            serializer = ShoppingCartItemsSerializer(cart_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "購物車更新成功"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ShoppingCartItems.DoesNotExist:
            return Response({"error": "購物車項目不存在"}, status=status.HTTP_404_NOT_FOUND)


class ShoppingCartDeleteView(APIView):
    """
    從購物車中移除商品
    """
    permission_classes = [IsAuthenticated]
    def delete(self, request, cart_item_id):
        try:
            cart_item = ShoppingCartItems.objects.get(pk=cart_item_id)
            cart_item.delete()
            return Response({"message": "商品已從購物車中移除"}, status=status.HTTP_204_NO_CONTENT)
        except ShoppingCartItems.DoesNotExist:
            return Response({"error": "購物車項目不存在"}, status=status.HTTP_404_NOT_FOUND)


class OrderCreateView(APIView):
    """
    用戶提交訂單
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = OrdersSerializer(data=request.data)
        if serializer.is_valid():
            # 創建訂單
            order = serializer.save()

            # 從購物車生成 OrderItems
            cart_items = ShoppingCartItems.objects.filter(member=request.user)
            for cart_item in cart_items:
                OrderItems.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    subtotal=cart_item.quantity * cart_item.product.price,
                )

            # 清空購物車
            cart_items.delete()

            return Response({
                "message": "訂單提交成功",
                "order_id": order.order_id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrdersView(APIView):
    """
    用戶查看自己的所有訂單
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        orders = Orders.objects.filter(member=user)
        serializer = OrdersSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    """
    查看單個訂單詳細信息（包含購物細項）
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            # 使用 select_related 和 prefetch_related 提高效能
            order = Orders.objects.select_related('member').prefetch_related(
                'orderitems_set__product'
            ).get(pk=order_id)

            # 使用統一的 OrdersSerializer，包括訂單細項
            order_serializer = OrdersSerializer(order)

            return Response({
                "status": "success",
                "message": "訂單詳情獲取成功",
                "data": order_serializer.data
            }, status=status.HTTP_200_OK)
        except Orders.DoesNotExist:
            return Response({
                "status": "error",
                "message": "訂單不存在"
            }, status=status.HTTP_404_NOT_FOUND)
