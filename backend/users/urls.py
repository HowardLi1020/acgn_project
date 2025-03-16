from django.contrib import admin
from django.urls import path
from . import views



app_name = 'users'
urlpatterns = [
    # http://127.0.0.1:8000/admin/users/
    path('', views.index, name="index" ),
    # http://127.0.0.1:8000/admin/users/404
    path('404/', views.page404, name="404" ),

    # http://127.0.0.1:8000/users/register
    path('register/', views.register, name="create" ),
    # http://127.0.0.1:8000/users/edit/
    path('edit/', views.edit, name="edit" ),
    # http://127.0.0.1:8000/users/delete/
    path('delete/<int:id>', views.delete, name="delete" ),
    
    # http://127.0.0.1:8000/users/hand_verify/
    path('hand_verify/', views.hand_verify, name="hand_verify" ),
    # http://127.0.0.1:8000/users/login/
    path('login/', views.login, name='login'),
    # http://127.0.0.1:8000/users/logout/
    path('logout/', views.logout, name='logout'),
    # http://127.0.0.1:8000/users/signup/
    path('signup/', views.signup, name="signup"),


    # http://127.0.0.1:8000/users/reset/
    path('reset/', views.reset, name="reset"),
    # http://127.0.0.1:8000/users/reset_confirm/
    path('reset_confirm/', views.reset_confirm, name="reset_confirm"),

    
    # http://127.0.0.1:8000/users/email_change/
    path('email_change/', views.email_change, name="email_change"),
    # http://127.0.0.1:8000/users/email_change_confirm/
    path('email_change_confirm/<str:uidb64>/<str:token>/', views.email_change_confirm, name='email_change_confirm'),
    # http://127.0.0.1:8000/users/email_reconfirm/
    path('email_reconfirm/<str:token>/', views.email_reconfirm, name='email_reconfirm'),
    # http://127.0.0.1:8000/users/phone_change/
    path('phone_change/', views.phone_change, name="phone_change"),
    # http://127.0.0.1:8000/users/phone_change_confirm/
    path('phone_change_confirm/<str:uidb64>/<str:token>/', views.phone_change_confirm, name='phone_change_confirm'),
    # http://127.0.0.1:8000/users/phone_reconfirm/
    path('phone_reconfirm/<str:token>/', views.phone_reconfirm, name='phone_reconfirm'),

    # http://127.0.0.1:8000/users/personal/
    path('personal/', views.personal, name='personal'),
    
    # # http://127.0.0.1:8000/users/verify-code/
    # path('verify-code/', views.verify_code, name='verify_code'),

    # http://127.0.0.1:8000/users/dashboard/
    path('dashboard/', views.dashboard, name='dashboard'),
]