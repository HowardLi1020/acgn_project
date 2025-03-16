from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ReplyViewSet, LikeViewSet

# 註冊 REST API 路由
router = DefaultRouter()
router.register(r'posts', PostViewSet)  # /api/posts/
router.register(r'replies', ReplyViewSet)  # /api/replies/
router.register(r'likes', LikeViewSet)  # /api/likes/

urlpatterns = [
    path("", include(router.urls)),  # ✅ 讓 Django 使用自動生成的 REST API 路由
]
