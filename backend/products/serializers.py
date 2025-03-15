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
    user_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = ProductReviews
        fields = ['review_id', 'rating', 'review_text', 'review_date', 'user', 'user_name', 'is_owner']

    def get_user_name(self, obj):
        return obj.user.user_nickname or obj.user.user_name

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_id == request.user.id
        return False
    
class ProductDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.brand_name', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    series_name = serializers.CharField(source='series.series_name', read_only=True)
    images = ProductImageSerializer(many=True, source='productimages_set')
    
    class Meta:
        model = Products
        fields = [
            'product_id', 'product_name', 'description_text', 
            'brand', 'brand_name', 'series', 'series_name', 
            'category', 'category_name', 'price', 'stock',
            'images', 'created_at', 'updated_at'
        ]