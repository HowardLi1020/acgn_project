from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Orders
from django.contrib import messages

#獲取訂單
def order_list(request):
    orders = Orders.objects.all()  # 獲取所有訂單
    return render(request, 'cart/orders_list.html', {'orders': orders})

#編輯訂單
# def edit_order(request, order_id):

#刪除訂單
# def delete_order(request, order_id):

