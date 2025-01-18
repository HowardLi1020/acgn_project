from django.urls import path
from .views import ShoppingCartView, OrdersView

urlpatterns = [
    path('cart/', ShoppingCartView.as_view(), name='cart'),
    path('create_order/', OrdersView.as_view(), name='create_order'),
    path('delete_order/<int:order_id>/', OrdersView.as_view(), name='delete_order'),
]
