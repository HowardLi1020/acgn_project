from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import  VerifyEmailView, UpdateUserInfoView, UpdateUserLikesView, SendResetLinkView, ResetPasswordView, SendPhoneLinkView, ResetPhoneView, SendEmailLinkView, ResetEmailView, LineLoginView
from member_api.views import AuthViewSet
from .web_api_chatbot_openai import ChatBotView

router = DefaultRouter()
# https://...../profile/
router.register('profile', views.MemberViewSet)
# https://...../thirdparty/
router.register('thirdparty', views.ThirdLoginViewSet)
# https://...../orderdetails/
router.register('orderdetails', views.OrderdetailsViewSet)
# https://...../privacy/
router.register('privacy', views.PrivacyViewSet)
# https://...../verify/
router.register('verify', views.VerifyViewSet)
# https://...../auth/
router.register(r'auth', AuthViewSet, basename='auth')

app_name = 'member_api'
urlpatterns = [
    path('', include(router.urls)),
    path('chat-bot/', ChatBotView.as_view(), name='chat_bot'),    # 聊天機器人
    path('auth/protected-route/', views.ProtectedRouteView.as_view(), name='protected_route'),
    path('auth/update-info/<int:pk>/', UpdateUserInfoView.as_view(), name='update_user_info'),
    path('auth/update-likes/<int:pk>/', UpdateUserLikesView.as_view(), name='update_user_likes'),
    path('auth/line-login/', LineLoginView.as_view(), name='line-login'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),   #註冊驗證連結
    path('reset/', SendResetLinkView.as_view(), name='send-reset-link'),                 #發送密碼重置驗證碼
    path('reset/<int:code>/', ResetPasswordView.as_view(), name='reset_password'),       #密碼重置驗證連結
    path('phone-change/', SendPhoneLinkView.as_view(), name='send-phone-link'),          #發送修改手機號驗證碼
    path('phone-change/<int:code>/', ResetPhoneView.as_view(), name='reset_phone'),      #修改手機號驗證連結
    path('email-change/', SendEmailLinkView.as_view(), name='send-email-link'),          #發送修改郵箱驗證碼
    path('email-change/<int:code>/', ResetEmailView.as_view(), name='reset_email'),      #修改郵箱驗證連結
]