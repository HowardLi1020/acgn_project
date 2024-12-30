from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

app_name = 'products'

urlpatterns = [
    # 公開 API 端點
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('view_all_products/', views.view_all_products, name='view_all_products'),
    path('products/<int:product_id>/', views.ProductDetail.as_view(), name='product_detail'),
    path('my-products/', views.my_products, name='my_products'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    path('series/', views.SeriesListView.as_view(), name='series-list'),
    path('featured-products/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('new-arrivals/', views.NewArrivalsView.as_view(), name='new-arrivals'),

    path('products/<int:product_id>/reviews/', views.ProductReviewsView.as_view(), name='get_reviews'),
    path('recommendations/similar/<int:product_id>/', views.ProductRecommendationsView.as_view(), name='product-recommendations'),
    

    path('create_product/', views.create_product, name='create_product'),
    
    path('create_brand/', views.create_brand, name='create_brand'),
    path('create_category/', views.create_category, name='create_category'),
    path('create_series/', views.create_series, name='create_series'),

    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/check/<int:product_id>/', views.check_wishlist, name='check_wishlist'),
]

urlpatterns += router.urls