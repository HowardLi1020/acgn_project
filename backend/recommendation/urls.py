# recommendation/urls.py
from django.urls import path
from .views import RecommendationAPIView, SystemStatusView, get_content_types, get_genres

urlpatterns = [
    # 推薦API
    path('recommendations/', RecommendationAPIView.as_view(), name='recommendations'),
    
    # 系統狀態API
    path('system-status/', SystemStatusView.as_view(), name='system-status'),
    
    # 獲取內容類型
    path('content-types/', get_content_types, name='content-types'),
    
    # 獲取類型/風格
    path('genres/', get_genres, name='genres'),
]