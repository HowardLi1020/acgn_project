from django.urls import path
from .views import ShoppingCartView, UserOrdersView
from .payment import ECPayPaymentView, ECPayCallbackView

urlpatterns = [
    # 購物車
    path('cart/', ShoppingCartView.as_view(), name='cart'),
    
    # 訂單管理
    path('create_order/', UserOrdersView.as_view(), name='create_order'),
    path('delete_order/<int:order_id>/', UserOrdersView.as_view(), name='delete_order'),
    path('order_list/', UserOrdersView.as_view(), name='order_list'),
    
    # ECPay 付款
    path('ecpay/<int:order_id>/', ECPayPaymentView.as_view(), name='ecpay_payment'),
    path('ecpay/callback/', ECPayCallbackView.as_view(), name='ecpay_callback'),
]
