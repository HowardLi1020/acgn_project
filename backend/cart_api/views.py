from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cart.models import Orders, OrderItems, ShoppingCartItems
from .serializers import (
    OrdersSerializer,
    OrderItemsSerializer,
    ShoppingCartItemsSerializer,
)

class ShoppingCartView(APIView):
    """
    用戶查看和管理購物車
    """
    def get(self, request):
        user = request.user
        cart_items = ShoppingCartItems.objects.filter(member=user)
        serializer = ShoppingCartItemsSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 添加商品到購物車
        serializer = ShoppingCartItemsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "商品已成功加入購物車"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, cart_item_id):
        # 更新購物車中的商品數量
        try:
            cart_item = ShoppingCartItems.objects.get(pk=cart_item_id)
            serializer = ShoppingCartItemsSerializer(cart_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "購物車更新成功"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ShoppingCartItems.DoesNotExist:
            return Response({"error": "購物車項目不存在"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, cart_item_id):
        # 從購物車中移除商品
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
    def post(self, request):
        # 提交訂單
        serializer = OrdersSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response({
                "message": "訂單提交成功",
                "order_id": order.order_id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserOrdersView(APIView):
    """
    用戶查看自己的所有訂單
    """
    def get(self, request):
        user = request.user
        orders = Orders.objects.filter(member=user)
        serializer = OrdersSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    """
    查看單個訂單詳細信息（包含購物細項）
    """
    def get(self, request, order_id):
        try:
            order = Orders.objects.get(pk=order_id)
            order_serializer = OrdersSerializer(order)

            # 獲取訂單細項
            order_items = OrderItems.objects.filter(order=order)
            order_items_serializer = OrderItemsSerializer(order_items, many=True)

            return Response({
                "order": order_serializer.data,
                "order_items": order_items_serializer.data
            }, status=status.HTTP_200_OK)
        except Orders.DoesNotExist:
            return Response({"error": "訂單不存在"}, status=status.HTTP_404_NOT_FOUND)
