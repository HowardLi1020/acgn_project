# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DbNeedImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    need = models.ForeignKey('DbNeedInfo', models.DO_NOTHING, blank=True, null=True)
    step = models.IntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_need_images'


class DbNeedInfo(models.Model):
    needer_id = models.IntegerField()
    needer_nickname = models.CharField(max_length=50)
    needer_avatar = models.CharField(max_length=255, blank=True, null=True)
    needer_introduction = models.CharField(max_length=300, blank=True, null=True)
    need_id = models.AutoField(primary_key=True)
    need_title = models.CharField(max_length=50, blank=True, null=True)
    need_category = models.CharField(max_length=50, blank=True, null=True)
    need_original_from = models.CharField(max_length=150, blank=True, null=True)
    need_description = models.TextField(blank=True, null=True)
    need_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    need_status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_need_info'


class DbPublicCard(models.Model):
    user_id = models.IntegerField(primary_key=True)  # The composite primary key (user_id, user_nickname, user_avatar) found, that is not supported. The first column is selected.
    user_nickname = models.CharField(max_length=50)
    user_avatar = models.CharField(max_length=255)
    user_introduction = models.CharField(max_length=300, blank=True, null=True)
    involved_works = models.TextField(blank=True, null=True)
    key_tags = models.CharField(max_length=255, blank=True, null=True)
    price_list = models.TextField(blank=True, null=True)
    price_example_image = models.CharField(max_length=255, blank=True, null=True)
    work_id = models.IntegerField(blank=True, null=True)
    work_title = models.CharField(max_length=50, blank=True, null=True)
    work_original_from = models.CharField(max_length=150, blank=True, null=True)
    work_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    need_id = models.IntegerField(blank=True, null=True)
    need_title = models.CharField(max_length=50, blank=True, null=True)
    need_original_from = models.CharField(max_length=150, blank=True, null=True)
    need_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    reviewer_nickname = models.CharField(max_length=50, blank=True, null=True)
    review_content = models.TextField(blank=True, null=True)
    deal_count = models.IntegerField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_public_card'
        unique_together = (('user_id', 'user_nickname', 'user_avatar'),)


class DbWorksInfo(models.Model):
    author_id = models.IntegerField()
    author_nickname = models.CharField(max_length=50)
    author_avatar = models.CharField(max_length=255, blank=True, null=True)
    author_introduction = models.CharField(max_length=300, blank=True, null=True)
    work_id = models.AutoField(primary_key=True)
    work_title = models.CharField(max_length=50, blank=True, null=True)
    work_original_from = models.CharField(max_length=150, blank=True, null=True)
    work_description = models.TextField(blank=True, null=True)
    usage_restrictions = models.TextField(blank=True, null=True)
    sale_items = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True, null=True)
    work_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    original_file = models.CharField(max_length=255, blank=True, null=True)
    submission_history = models.TextField(blank=True, null=True)
    work_thumbnail = models.CharField(max_length=255, blank=True, null=True)
    work_preview = models.CharField(max_length=255, blank=True, null=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    work_status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_works_info'


class MemberBasic(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(unique=True, max_length=20)
    user_password = models.CharField(max_length=128)
    user_phone = models.CharField(unique=True, max_length=10)
    user_email = models.CharField(unique=True, max_length=120)
    user_nickname = models.CharField(max_length=20, blank=True, null=True)
    user_gender = models.CharField(max_length=10, blank=True, null=True)
    user_birth = models.DateField(blank=True, null=True)
    user_address = models.TextField(blank=True, null=True)
    vip_status = models.IntegerField(blank=True, null=True)
    user_avatar = models.CharField(max_length=50, blank=True, null=True)
    privacy_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_basic'


class MemberPrivacy(models.Model):
    privacy_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    user_email = models.CharField(max_length=120, blank=True, null=True)
    privacy_name = models.CharField(max_length=50, blank=True, null=True)
    privacy_value = models.IntegerField(blank=True, null=True)
    phone_change = models.CharField(max_length=10, blank=True, null=True)
    email_change = models.CharField(max_length=50, blank=True, null=True)
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
    user = models.ForeignKey(MemberBasic, models.DO_NOTHING, blank=True, null=True)
    user_email = models.CharField(max_length=50, blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_token = models.CharField(max_length=16, blank=True, null=True)
    code_used = models.IntegerField(blank=True, null=True)
    token_used = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'member_verify'
