from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import AuthViewSet, VerifyEmailView, UpdateUserInfoView, SendResetLinkView, ResetPasswordView

router = DefaultRouter()

# https://...../profile/
router.register('profile', views.MemberViewSet)
# https://...../favorite/
router.register('favorite', views.FavoriteViewSet)
# https://...../login/
# router.register('login', views.ThirdLoginViewSet)
# https://...../coupon/
router.register('coupon', views.CouponViewSet)
# https://...../thirdparty/
router.register('thirdparty', views.ThirdLoginViewSet)
# https://...../orderdetails/
router.register('orderdetails', views.OrderdetailsViewSet)
# https://...../privacy/
router.register('privacy', views.PrivacyViewSet)
# https://...../verify/
router.register('verify', views.VerifyViewSet)
# https://...../auth/
router.register(r'auth', views.AuthViewSet, basename='auth')


app_name = 'member_api'
urlpatterns = [
    path('', include(router.urls)),
    path('auth/protected_route/', views.ProtectedRouteView.as_view(), name='protected_route'),
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/update_info/<int:pk>/', UpdateUserInfoView.as_view(), name='update_user_info'),
    # path('auth/upload_avatar/', UploadAvatarView.as_view(), name='upload_avatar'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('reset/', SendResetLinkView.as_view(), name='send-reset-link'),
    path('reset/<int:code>/', ResetPasswordView.as_view(), name='reset_password'),
]