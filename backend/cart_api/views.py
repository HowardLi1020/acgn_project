from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from cart.models import Orders, OrderItems, ShoppingCartItems
from .serializers import (
    OrdersSerializer,
    OrderItemsSerializer,
    ShoppingCartItemsSerializer,
)
from .permissions import IsAuthenticatedWithCustomToken  # 自定義權限類


class ShoppingCartListView(APIView):
    """
    查看用戶購物車
    """
    permission_classes = [IsAuthenticatedWithCustomToken]

    def get(self, request):
        user = request.user
        cart_items = ShoppingCartItems.objects.filter(member=user)
        serializer = ShoppingCartItemsSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShoppingCartAddView(APIView):
    """
    添加商品到購物車
    """
    permission_classes = [IsAuthenticatedWithCustomToken]

    def post(self, request):
        print("Received Payload:", request.data)

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id or not isinstance(quantity, int) or quantity <= 0:
            return Response({"error": "商品ID或數量無效"}, status=status.HTTP_400_BAD_REQUEST)

        # 嘗試從數據庫獲取現有的購物車項目
        cart_item = ShoppingCartItems.objects.filter(member=request.user, product_id=product_id).first()

        if cart_item:
            # 如果該商品已存在購物車，則更新數量
            cart_item.quantity += quantity
            cart_item.save()
            return Response(
                {"message": "商品數量已更新", "cart_item_id": cart_item.cart_item_id, "new_quantity": cart_item.quantity},
                status=status.HTTP_200_OK,
            )
        else:
            # 如果該商品不存在購物車，則新增條目
            serializer = ShoppingCartItemsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(member=request.user)  # 綁定當前用戶到 member 字段
                return Response({"message": "商品已成功加入購物車"}, status=status.HTTP_201_CREATED)
            else:
                print("Serializer Errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ShoppingCartUpdateView(APIView):
    """
    更新購物車中的商品數量
    """
    permission_classes = [IsAuthenticatedWithCustomToken]

    def put(self, request, cart_item_id):
        try:
            # 確認當前用戶是否有效
            member = request.user
            if not member:
                return Response({"error": "用戶未授權"}, status=status.HTTP_401_UNAUTHORIZED)

            # 獲取購物車項目
            cart_item = ShoppingCartItems.objects.get(pk=cart_item_id, member=member)
            
            # 檢查請求數據是否包含 quantity
            new_quantity = request.data.get("quantity")
            if not new_quantity or int(new_quantity) <= 0:
                return Response({"error": "無效的數量值"}, status=status.HTTP_400_BAD_REQUEST)

            # 更新購物車項目數量
            cart_item.quantity = new_quantity
            cart_item.save()

            return Response({"message": "購物車更新成功"}, status=status.HTTP_200_OK)
        except ShoppingCartItems.DoesNotExist:
            return Response({"error": "購物車項目不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"發生錯誤：{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ShoppingCartDeleteView(APIView):
    """
    從購物車中移除商品
    """
    permission_classes = [IsAuthenticatedWithCustomToken]

    def delete(self, request, cart_item_id):
        try:
            # 確認當前用戶是否有效
            member = request.user
            if not member:
                return Response({"error": "用戶未授權"}, status=status.HTTP_401_UNAUTHORIZED)

            # 確認購物車項目是否屬於當前用戶
            cart_item = ShoppingCartItems.objects.get(pk=cart_item_id, member=member)
            cart_item.delete()

            return Response({"message": "商品已從購物車中移除"}, status=status.HTTP_200_OK)
        except ShoppingCartItems.DoesNotExist:
            return Response({"error": "購物車項目不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"發生錯誤：{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderCreateView(APIView):
    """
    用戶提交訂單
    """
    permission_classes = [IsAuthenticatedWithCustomToken]

    def post(self, request):
        serializer = OrdersSerializer(data=request.data)
        if serializer.is_valid():
            # 創建訂單
            order = serializer.save(member=request.user)  # 綁定用戶

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
    permission_classes = [IsAuthenticatedWithCustomToken]

    def get(self, request):
        user = request.user
        orders = Orders.objects.filter(member=user)
        serializer = OrdersSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):
    """
    查看單個訂單詳細信息（包含購物細項）
    """
    permission_classes = [IsAuthenticatedWithCustomToken]

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
