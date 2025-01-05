from django.urls import path
from . import views  # 導入視圖

app_name = "users_api"
urlpatterns = [
    # http://127.0.0.1:8000/admin/users_api/
    path('', views.index, name="index"),


    # http://127.0.0.1:8000/users_api/register
    path('register/', views.register),
    # http://127.0.0.1:8000/users_api/checkname/
    path('checkname/', views.checkname ),
    # http://127.0.0.1:8000/users_api/checkphone/
    path('checkphone/', views.checkphone ),
    # http://127.0.0.1:8000/users_api/checkemail/
    path('checkemail/', views.checkemail ),
    # http://127.0.0.1:8000/users_api/checkpassword/
    path('checkpassword/', views.checkpassword ),
    # http://127.0.0.1:8000/users_api/search/
    path('search/', views.search, name='search' ),
    # http://127.0.0.1:8000/users_api/signup
    path('signup/', views.signup, name='signup'),
        # http://127.0.0.1:8000/users_api/personal/
    path('personal/', views.personal ),
    # http://127.0.0.1:8000/users_api/privacy_setting/
    path('privacy_setting/', views.privacy_setting, name="privacy_setting" ),


    # http://127.0.0.1:8000/users_api/send_reset_password/
    path('send_reset_password/', views.send_reset_password, name='send_reset_password'),
    # http://127.0.0.1:8000/users_api/request-verification/
    path('request-verification/', views.request_verification, name='request_verification'),
    # http://127.0.0.1:8000/users_api/send_verification_email/
    path('send_verification_email/', views.send_verification_email, name='send_verification_email'),
    # http://127.0.0.1:8000/users_api/verify_code/
    path('verify_code/', views.verify_code, name='verify_code'),
    # http://127.0.0.1:8000/users_api/reset_confirm
    path('reset_confirm/', views.reset_confirm, name='reset_confirm'),
    # http://127.0.0.1:8000/users_api/email_change/
    path('email_change/', views.email_change, name='email_change'),
    # http://127.0.0.1:8000/users_api/email_change_confirm/<str:token>/
    path('email_change_confirm/<str:token>/', views.email_change_confirm, name='email_change_confirm'),
    # http://127.0.0.1:8000/users_api/email_change_form/
    path('email_change_form/<str:code>/', views.email_change_form, name='email_change_form'),

    
    # http://127.0.0.1:8000/users_api/verify-email/
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    # http://127.0.0.1:8000/users_api/resend-verify-email/
    path('resend-verify-email/', views.resend_verify_email, name='resend_verify_email'),

    
    # http://127.0.0.1:8000/users_api/reset_email/
    path('reset_email/', views.reset_email, name='reset_email'),
    # http://127.0.0.1:8000/users_api/reconfirm_email/<str:token>/
    path('reconfirm_email/<str:token>/', views.reconfirm_email, name='reconfirm_email'),
    # http://127.0.0.1:8000/users_api/reset_phone/
    path('reset_phone/', views.reset_phone, name='reset_phone'),
    # http://127.0.0.1:8000/users_api/reconfirm_phone/<str:token>/
    path('reconfirm_phone/<str:token>/', views.reconfirm_phone, name='reconfirm_phone'),


    # http://127.0.0.1:8000/users_api/phone_change/
    path('phone_change/', views.phone_change, name='phone_change'),
    # http://127.0.0.1:8000/users_api/phone_change_confirm/<str:token>/
    path('phone_change_confirm/<str:token>/', views.phone_change_confirm, name='phone_change_confirm'),
    # http://127.0.0.1:8000/users_api/phone_change_form/<str:code>/
    path('phone_change_form/<str:code>/', views.phone_change_form, name='phone_change_form'),
]