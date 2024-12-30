from django.urls import path
from . import views  # 導入視圖

app_name = "admins_api"
urlpatterns = [
    # http://127.0.0.1:8000/admins_api/signup
    path('signup/', views.signup, name="signup"),
    # http://127.0.0.1:8000/admins_api/reset
    path('reset/', views.reset, name="reset"),

]