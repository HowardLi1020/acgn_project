from django.urls import path
from .views import ShoppingCartView

urlpatterns = [
    path('cart/', ShoppingCartView.as_view(), name='cart'),
]
