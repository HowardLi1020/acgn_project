from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Orders, OrderItems, ShoppingCartItems, PaymentTransactions, ShippingDetails
from .serializers import OrderSerializer, ShoppingCartItemSerializer, PaymentTransactionSerializer, ShippingDetailSerializer


# 用戶端訂單相關
class UserOrderView(APIView):
    """
    用戶端 - 查看訂單列表 & 新增訂單
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """查看當前用戶的所有訂單"""
        user = request.user
        orders = Orders.objects.filter(member=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """新增訂單"""
        data = request.data
        data['member'] = request.user.id  # 將當前用戶設置為訂單擁有者
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrderDetailView(APIView):
    """
    用戶端 - 查看特定訂單詳情
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """查看用戶的特定訂單"""
        user = request.user
        try:
            order = Orders.objects.get(pk=pk, member=user)
        except Orders.DoesNotExist:
            return Response({'錯誤': '找不到該訂單'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 後端管理訂單相關
class AdminOrderView(APIView):
    """
    管理端 - 訂單管理
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """查看所有訂單（支持篩選和排序）"""
        orders = Orders.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """更新特定訂單狀態"""
        try:
            order = Orders.objects.get(pk=pk)
        except Orders.DoesNotExist:
            return Response({'錯誤': '找不到該訂單'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """刪除訂單"""
        try:
            order = Orders.objects.get(pk=pk)
            order.delete()
            return Response({'訊息': '訂單已刪除'}, status=status.HTTP_204_NO_CONTENT)
        except Orders.DoesNotExist:
            return Response({'錯誤': '找不到該訂單'}, status=status.HTTP_404_NOT_FOUND)


# 購物車相關
class ShoppingCartView(APIView):
    """
    用戶端 - 購物車功能
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """查看當前用戶的購物車"""
        user = request.user
        cart_items = ShoppingCartItems.objects.filter(member=user)
        serializer = ShoppingCartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """添加商品到購物車"""
        data = request.data
        data['member'] = request.user.id  # 將當前用戶設置為購物車擁有者
        serializer = ShoppingCartItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """從購物車中移除商品"""
        try:
            cart_item = ShoppingCartItems.objects.get(pk=pk, member=request.user)
            cart_item.delete()
            return Response({'訊息': '商品已移除'}, status=status.HTTP_204_NO_CONTENT)
        except ShoppingCartItems.DoesNotExist:
            return Response({'錯誤': '找不到該購物車商品'}, status=status.HTTP_404_NOT_FOUND)


# 付款交易相關
class PaymentTransactionView(APIView):
    """
    查看付款交易
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """查看特定訂單的付款記錄"""
        try:
            payment = PaymentTransactions.objects.get(order_id=pk)
            serializer = PaymentTransactionSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PaymentTransactions.DoesNotExist:
            return Response({'錯誤': '找不到該付款記錄'}, status=status.HTTP_404_NOT_FOUND)


# 配送詳情相關
class ShippingDetailView(APIView):
    """
    查看配送詳情
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """查看特定訂單的配送詳情"""
        try:
            shipping = ShippingDetails.objects.get(order_id=pk)
            serializer = ShippingDetailSerializer(shipping)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ShippingDetails.DoesNotExist:
            return Response({'錯誤': '找不到該配送詳情'}, status=status.HTTP_404_NOT_FOUND)
