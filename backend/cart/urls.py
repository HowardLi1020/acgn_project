from django.urls import path
from . import views
from .payment import create_ecpay_payment, ecpay_callback

app_name = 'cart'

urlpatterns = [
    path('', views.order_list, name='orders'),
    path('ecpay/<int:order_id>/', create_ecpay_payment, name='ecpay_payment'),
    path('ecpay/callback/', ecpay_callback, name='ecpay_callback'),
]