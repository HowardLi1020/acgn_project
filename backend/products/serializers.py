from rest_framework import serializers
from .models import Products, ProductBrands, ProductCategories, ProductSeries,ProductImages, ProductReviews

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrands
        fields = ['brand_id', 'brand_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = ['category_id', 'category_name']

class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSeries
        fields = ['series_id', 'series_name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['image_url', 'is_main']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, source='productimages_set')  # 使用反向關聯名稱
    
    class Meta:
        model = Products
        fields = [
            'product_id', 
            'product_name', 
            'description_text', 
            'price', 
            'stock',
            'images',
            'brand',
            'category',
            'series',
            'user'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviews
        fields = ['id', 'rating', 'comment', 'created_at', 'user']  # 根據需要調整字段