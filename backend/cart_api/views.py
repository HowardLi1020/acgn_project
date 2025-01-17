from django.shortcuts import  get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.permissions import IsAuthenticatedWithCustomToken
from cart.models import ShoppingCartItems
from products.models import Products
from cart_api.serializers import ShoppingCartItemsSerializer

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
    