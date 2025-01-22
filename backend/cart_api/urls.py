from django.urls import path
from .views import ShoppingCartView, UserOrdersView

urlpatterns = [
    #客戶端
    path('cart/', ShoppingCartView.as_view(), name='cart'),
    path('create_order/', UserOrdersView.as_view(), name='create_order'),
    path('delete_order/<int:order_id>/', UserOrdersView.as_view(), name='delete_order'),
    path('order_list/', UserOrdersView.as_view(), name='order_list'),
]
