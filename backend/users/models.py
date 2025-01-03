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
    # user_avatar = models.CharField(max_length=255, blank=True, null=True)
    user_avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_basic'


class MemberLogin(models.Model):
    login_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    provider = models.CharField(max_length=50, blank=True, null=True)
    provider_id_google = models.CharField(unique=True, max_length=50, blank=True, null=True)
    provider_id_line = models.CharField(unique=True, max_length=50, blank=True, null=True)
    provider_id_fb = models.CharField(unique=True, max_length=50, blank=True, null=True)
    access_token = models.CharField(unique=True, max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_login'


class MemberIndextype(models.Model):
    type_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    type_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_indextype'


class MemberPhotos(models.Model):
    photo_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    photo_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_photos'


class MemberPrivacy(models.Model):
    privacy_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
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
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
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


class ProductWishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    product = models.ForeignKey('products.Products', models.DO_NOTHING)
    added_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_wishlist'


class Usercoupons(models.Model):
    user_coupon_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    coupon = models.ForeignKey('promotions.Coupons', models.DO_NOTHING)
    is_used = models.IntegerField(blank=True, null=True)
    used_in_order = models.ForeignKey('cart.Orders', models.DO_NOTHING, blank=True, null=True)
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usercoupons'
