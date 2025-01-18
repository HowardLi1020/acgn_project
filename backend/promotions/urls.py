from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.coupon_list, name='coupon_list'),
    path('add/', views.add_coupon, name='add_coupon'),
    path('edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    path('assign/<int:coupon_id>/', views.assign_coupon, name='assign_coupon'),
]
