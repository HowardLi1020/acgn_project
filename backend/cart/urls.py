from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.order_list, name='orders'),
    # path('<int:order_id>/edit/', views.edit_order, name='edit_order'),
    # path('<int:order_id>/delete/', views.delete_order, name='delete_order'),
]