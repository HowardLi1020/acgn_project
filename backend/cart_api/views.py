from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.permissions import IsAuthenticatedWithCustomToken
from cart.models import ShoppingCartItems, Orders, OrderItems, PaymentTransactions
from products.models import Products
from cart_api.serializers import ShoppingCartItemsSerializer, OrdersSerializer, PaymentTransactionsSerializer
from django.db import transaction
#購物車功能
class ShoppingCartView(APIView):

    permission_classes = [IsAuthenticatedWithCustomToken]
    
    #獲取當前用戶購物車內容
    def get(self, request):
        cart_items = ShoppingCartItems.objects.filter( user = request.user )
        serializer = ShoppingCartItemsSerializer(cart_items, many=True, context={'request': request} )
        # print("Authorization Header:", request.headers.get("Authorization"))
        return Response(serializer.data)
    
    #在商店新增商品到購物車
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1 )
        product = get_object_or_404(Products, product_id = product_id)

        #檢查購物車內是否已有該商品，如果有直接做數量上的增加
        try:
            cart_item = ShoppingCartItems.objects.get(user=request.user, product=product)
            # 如果存在，直接更新數量
            cart_item.quantity += quantity
            cart_item.save()
            message = '商品數量已更新到購物車'
        except ShoppingCartItems.DoesNotExist:
            # 如果不存在，創建新的條目
            cart_item = ShoppingCartItems.objects.create(
            user=request.user, 
            product=product, 
            quantity=quantity
            )
            message = '商品已成功添加到購物車'
        return Response({'message':message}, status = status.HTTP_201_CREATED)

    #在購物車內更新商品的數量
    def put(self, request):
        product_id = request.data.get('product_id')
        action = request.data.get('action') # 'increment' 或 'decrement'
        cart_item = get_object_or_404(ShoppingCartItems, user = request.user , product_id = product_id )

        if action == 'increment':
            cart_item.quantity += 1
        if action == 'decrement':
            cart_item.quantity -= 1
        cart_item.save()

        return Response({'message':'商品數量已更新'}, status=status.HTTP_200_OK)
    
    #移除購物車內的商品
    def delete(self, request):
        product_id = request.data.get('product_id')
        cart_item = get_object_or_404(ShoppingCartItems, user = request.user, product_id = product_id )
        cart_item.delete()
        return Response({'message':'商品已從購物車移除'}, status=status.HTTP_200_OK)

#用戶端訂單功能
class UserOrdersView(APIView):

    permission_classes = [IsAuthenticatedWithCustomToken]

    #建立訂單
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # 接收前端提交的數據
        serializer = OrdersSerializer(data=request.data)
        if not serializer.is_valid():
            print("序列化器錯誤：", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 創建訂單，將前端提交的總金額存入 total_amount
        order = serializer.save(user=request.user)

        # 從購物車提取數據並重新計算總金額
        cart_items = ShoppingCartItems.objects.filter(user=request.user)
        if not cart_items.exists():
            # 刪除訂單並返回錯誤
            order.delete()
            return Response({"message": "購物車內沒有商品，無法創建訂單。"}, status=status.HTTP_400_BAD_REQUEST)

        backend_total_amount = 0
        for cart_item in cart_items:
            backend_total_amount += cart_item.product.price * cart_item.quantity

        # 比對前端提交的 total_amount 和後端計算的金額
        if order.total_amount != backend_total_amount:
            # 刪除訂單
            order.delete()
            return Response(
                {"message": "總金額錯誤，請重新創建訂單。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 金額一致，更新訂單總金額並保存訂單
        order.total_amount = backend_total_amount
        order.save()

        # 將購物車項目轉移到 OrderItems
        for cart_item in cart_items:
            OrderItems.objects.create(
                order=order,
                product=cart_item.product,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
                subtotal=cart_item.product.price * cart_item.quantity,
            )

        # 清空購物車
        cart_items.delete()

        return Response(
            {
                "message": "訂單建立成功",
                "order_id": order.order_id,
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    #刪除訂單
    def delete(self, request, order_id, *args, **kwargs):
        try:
            # 確保僅能刪除與當前用戶相關的訂單
            order = Orders.objects.get(order_id=order_id, user=request.user)
            order.delete()
            return Response(
                {
                    "message" : "訂單已刪除",
                },
                status= status.HTTP_204_NO_CONTENT
            )
        except Orders.DoesNotExist:
            return Response(
                {
                    "message" : "無此訂單",
                },
                status= status.HTTP_404_NOT_FOUND
            )
    
    #檢視訂單
    def get(self, request):
        user_orders = Orders.objects.filter(user=request.user).order_by('-created_at')
        order_list = []

        for order in user_orders:
            # 取得該訂單的最新付款交易
            transaction = PaymentTransactions.objects.filter(order=order).order_by('-payment_date').first()

            order_list.append({
                "order_id": order.order_id,
                "total_amount": order.total_amount,
                "order_status": order.order_status,
                "payment_method": transaction.payment_method if transaction else "未付款",
                "payment_status": transaction.payment_status if transaction else "Pending",
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Response({"orders": order_list}, status=status.HTTP_200_OK)