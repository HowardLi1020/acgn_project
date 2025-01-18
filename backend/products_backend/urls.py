from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products_backend'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),

    path('add_brand/', views.add_brand, name='add_brand'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_series/', views.add_series, name='add_series'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)