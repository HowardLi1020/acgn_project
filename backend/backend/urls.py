from django.contrib import admin
from django.urls import path, include # 導入個人應用程式
from django.conf import settings
from django.conf.urls.static import static

from . import views  # 導入專案的 views.py(自己手動建的)

urlpatterns = [
    # http://127.0.0.1:8000/<str:template_name>.html 
    # 以確保操作index時其餘頁面都能正常連結到
    path('<str:template_name>.html', views.render_template, name='render_template'),


    # admin-APP (後台管理者)
    # http://127.0.0.1:8000/
    path('', include('admins.urls')), # 包含 admin 的 URL

    # http://127.0.0.1:8000/admins_api/
    path('admins_api/', include('admins_api.urls')), # 包含 admins_api 的 URL

    # Users-APP (後台會員)
    # http://127.0.0.1:8000/users/ 
    path('users/', include('users.urls')), # 包含 users 的 URL
    # http://127.0.0.1:8000/users_api/ 
    path('users_api/', include('users_api.urls')),  # 包含 users_api 的 URL

    # member-api APP (串前台vue會員)
    # http://127.0.0.1:8000/member_api/ 
    path('member_api/', include('member_api.urls')), # 包含 member_api 的 URL

    path('store/', include('products.urls')),
    path('store_backend/', include('products_backend.urls')),

    #http://127.0.0.1:8000/cart/ 
    path('cart/', include('cart.urls')),

    #http://127.0.0.1:8000/cart_api/ 
    path('cart_api/', include('cart_api.urls')),
    
    #http://127.0.0.1:8000/promotions/
    path('promotions/', include('promotions.urls')),

    # http://127.0.0.1:8000/commission/ 
    path('commission/', include('commission.urls')),
    
    path('Movies/', include('Movies.urls')),
    path('Games/', include('Games.urls')),
    path('Animations/', include('Animations.urls')),
    path('Discussion_board/', include('Discussion_board.urls')),
    path("api/", include("discussion.urls")),
    path('api/', include('entertainment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
