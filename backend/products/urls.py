from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 商品
    path('', views.index, name='index'),
    # 編輯
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    # 刪除
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # 詳細商品
    path('products/<int:product_id>/', views.ProductDetail.as_view(), name='product_detail'),
    # 商品評論
    path('products/<int:product_id>/reviews/', views.ProductReviewsView.as_view(), name='product_reviews'),
    path('products/<int:product_id>/can-review/', views.check_can_review, name='check_can_review'),
    path('products/<int:product_id>/reviews/<int:review_id>/', views.ProductReviewsView.as_view(), name='update_review'),
    # 已購商品
    path('purchased-products/', views.get_purchased_products, name='purchased-products'),
    # 我的商品
    path('my-products/', views.MyProductsView.as_view(), name='my_products'),
    # 分類
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    #品牌
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    #系列
    path('series/', views.SeriesListView.as_view(), name='series-list'),
    # 推薦商品
    path('recommendations/similar/<int:product_id>/', views.ProductRecommendationsView.as_view(), name='product-recommendations'),
    # 創建商品
    path('create_product/', views.create_product, name='create_product'),
    # 創建品牌
    path('create_brand/', views.create_brand, name='create_brand'),
    # 創建分類
    path('create_category/', views.create_category, name='create_category'),
    # 創建系列
    path('create_series/', views.create_series, name='create_series'),
    # 收藏
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/check/<int:product_id>/', views.check_wishlist, name='check_wishlist'),
    path('wishlist/list/', views.get_wishlist, name='get_wishlist'),
]