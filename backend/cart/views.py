from django.shortcuts import render
from cart.models import Orders, PaymentTransactions

def order_list(request):
    orders = Orders.objects.all().prefetch_related('payments')  # 預先載入付款資料
    return render(request, 'cart/orders_list.html', {'orders': orders})