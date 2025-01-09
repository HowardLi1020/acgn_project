# from django.urls import path
# from Discussion_board import views
# app_name='Discussion_board'
# # http://127.0.0.1:8000/Discussion_board/
# urlpatterns = [
#     path('', views.index, name='index'),
#     path('change_report/<int:post_id>/', views.change_report, name='change_report'),
#     path('delete/<int:post_id>/', views.delete_post, name='delete_post'),  # 確保名稱為 delete_post
# ]

from django.urls import path
from . import views

app_name = 'Discussion_board'

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('toggle_report/<int:post_id>/', views.toggle_report, name='toggle_report'),
]
