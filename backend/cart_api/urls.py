from django.urls import path
from cart_api import views

urlpatterns = [
    # 購物車相關操作
    path('cart/', views.ShoppingCartView.as_view(), name='cart-list'),  # 查看用戶購物車
    path('cart/add/', views.ShoppingCartView.as_view(), name='cart-add'),  # 添加商品到購物車
    path('cart/update/<int:cart_item_id>/', views.ShoppingCartView.as_view(), name='cart-update'),  # 更新購物車商品數量
    path('cart/delete/<int:cart_item_id>/', views.ShoppingCartView.as_view(), name='cart-delete'),  # 刪除購物車商品

    # 訂單相關操作
    path('orders/create/', views.OrderCreateView.as_view(), name='orders-create'),  # 提交新訂單
    path('orders/', views.UserOrdersView.as_view(), name='orders-list'),  # 查看用戶所有訂單
    path('orders/<int:order_id>/', views.OrderDetailView.as_view(), name='orders-detail'),  # 查看單個訂單詳細信息
]