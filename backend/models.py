# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class MemberBasic(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(unique=True, max_length=20)
    user_password = models.CharField(max_length=128)
    user_phone = models.CharField(unique=True, max_length=10)
    user_email = models.CharField(unique=True, max_length=120)
    user_nickname = models.CharField(max_length=20, blank=True, null=True)
    user_gender = models.CharField(max_length=17, blank=True, null=True)
    user_birth = models.DateField(blank=True, null=True)
    user_address = models.TextField(blank=True, null=True)
    vip_status = models.IntegerField(blank=True, null=True)
    user_avatar = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_basic'

class MemberFavorites(models.Model):
    favorite_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING, blank=True, null=True)
    brand = models.ForeignKey('ProductBrands', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_favorites'

class MemberPhotos(models.Model):
    photo_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    photo_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_photos'

class MemberPrivacy(models.Model):
    privacy_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    phone_verified = models.IntegerField(blank=True, null=True)
    email_verified = models.IntegerField(blank=True, null=True)
    account_verify = models.IntegerField(blank=True, null=True)
    activity_checked = models.IntegerField(blank=True, null=True)
    double_verify = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_privacy'

class MemberVerify(models.Model):
    verify_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    change_value = models.CharField(max_length=255, blank=True, null=True)
    verification_code = models.CharField(max_length=6)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    verification_type = models.CharField(max_length=15)
    code_used = models.IntegerField(blank=True, null=True)
    token_used = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_verify'

class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_items'

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    order_date = models.DateTimeField(blank=True, null=True)
    recipient = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    detailed_address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(max_length=9, blank=True, null=True)
    shipping_status = models.CharField(max_length=10, blank=True, null=True)
    payment_method = models.CharField(max_length=16)
    order_status = models.CharField(max_length=9)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'

class ProductBrands(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_brands'

class ProductCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_categories'

class ProductComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    content = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_comments'

class ProductImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    image_url = models.CharField(max_length=255)
    is_main = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_images'

class ProductMemberRatings(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    rated_by_user = models.ForeignKey(MemberBasic, models.DO_NOTHING, related_name='productmemberratings_rated_by_user_set')
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    rating = models.IntegerField()
    rating_type = models.CharField(max_length=6)
    rating_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_member_ratings'

class ProductRecommendations(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    recommended_product = models.ForeignKey('Products', models.DO_NOTHING, related_name='productrecommendations_recommended_product_set')
    recommendation_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_recommendations'

class ProductReviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    rating = models.IntegerField()
    review_text = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_reviews'

class ProductSeries(models.Model):
    series_id = models.AutoField(primary_key=True)
    series_name = models.CharField(unique=True, max_length=255)
    brand = models.ForeignKey(ProductBrands, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_series'

class ProductWishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    added_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_wishlist'

class PaymentTransactions(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    payment_method = models.CharField(max_length=16)
    payment_status = models.CharField(max_length=9)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_transactions'

class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    description_text = models.TextField(blank=True, null=True)
    brand = models.ForeignKey(ProductBrands, models.DO_NOTHING, blank=True, null=True)
    series = models.ForeignKey(ProductSeries, models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(ProductCategories, models.DO_NOTHING, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    date_added = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'

class ShippingDetails(models.Model):
    shipping_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    shipping_status = models.CharField(max_length=10)
    carrier_name = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shipping_details'

class ShoppingCartItems(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    quantity = models.IntegerField()
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shopping_cart_items'

class Coupons(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    coupon_code = models.CharField(unique=True, max_length=50)
    discount_type = models.CharField(max_length=10)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    usage_limit = models.IntegerField(blank=True, null=True)
    used_count = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'coupons'

class Usercoupons(models.Model):
    user_coupon_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    coupon = models.ForeignKey(Coupons, models.DO_NOTHING)
    is_used = models.IntegerField(blank=True, null=True)
    used_in_order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usercoupons'
