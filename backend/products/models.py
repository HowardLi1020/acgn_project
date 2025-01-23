# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone

class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    description_text = models.TextField(blank=True, null=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING, blank=True, null=True)
    brand = models.ForeignKey('products.ProductBrands', models.DO_NOTHING, blank=True, null=True)
    series = models.ForeignKey('products.ProductSeries', models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey('products.ProductCategories', models.DO_NOTHING, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'products'

class ProductBrands(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_brands'

class ProductCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_categories'

class ProductSeries(models.Model):
    series_id = models.AutoField(primary_key=True)
    series_name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_series'

class ProductImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    image_url = models.ImageField(upload_to='products/')
    is_main = models.BooleanField(default=False) 
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_images'

class ProductComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_comments'

class ProductReviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    rating = models.IntegerField()
    review_text = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_reviews'

class ProductRecommendations(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    recommended_product = models.ForeignKey(Products, models.DO_NOTHING, related_name='productrecommendations_recommended_product_set')
    recommendation_date = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_recommendations'

class ProductWishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    product = models.ForeignKey('products.Products', models.DO_NOTHING)
    added_date = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_wishlist'