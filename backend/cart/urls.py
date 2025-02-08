from django.urls import path
from . import views

app_name = 'cart'
#後臺管理端
urlpatterns = [
    path('', views.order_list, name='orders'),
]