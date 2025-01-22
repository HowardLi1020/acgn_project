from django.shortcuts import render, redirect
from cart.models import Orders
from users.models import MemberBasic

def order_list(request):
    orders = Orders.objects.all()  # 獲取所有訂單
    return render(request, 'cart/orders_list.html', {'orders': orders})
