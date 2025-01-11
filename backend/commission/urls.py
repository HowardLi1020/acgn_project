from django.urls import path
from commission import views 


app_name='commission'
# http://127.0.0.1:8000/commission/
urlpatterns = [
    # path('', views.ViewFn_need_list, name='index'), # 只是方便nav連結所以取index，之後可以改nav時一樣改回ViewFn_need_list會比較好懂
    path('need_list/', views.ViewFn_need_list, name='Urls_need_list'),
    path('need_edit/', views.ViewFn_need_edit, name='Urls_need_edit'),
    path('need/edit/<int:view_fn_need_id>/', views.ViewFn_need_edit, name='Urls_need_edit'),
    path('need/delete/<int:view_fn_need_id>/', views.ViewFn_need_delete, name='Urls_need_delete'),
    path('publiccard_list/', views.ViewFn_publiccard_list, name='Urls_publiccard_list'),
    path('publiccard/edit/<int:view_fn_publiccard_id>/', views.ViewFn_publiccard_edit, name='Urls_publiccard_edit'),
    # path('usercard/edit/<int:view_fn_usercard_id>/', views.ViewFn_usercard_edit, name='Urls_usercard_edit'),
]
