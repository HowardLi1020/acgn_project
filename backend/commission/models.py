# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from users.models import MemberBasic  # 確保這行在文件頂部


class DbNeedInfo(models.Model):
    needer_id = models.IntegerField()
    # needer_nickname = models.CharField(max_length=50)
    # needer_avatar = models.CharField(max_length=255, blank=True, null=True)
    # needer_introduction = models.CharField(max_length=300, blank=True, null=True)
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

class DbNeedImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    need = models.ForeignKey('DbNeedInfo', models.DO_NOTHING, blank=True, null=True)
    step = models.IntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_need_images'


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


class DbPublicCardInfo(models.Model):
    member_basic = models.OneToOneField(
        'users.MemberBasic',
        models.RESTRICT,
        db_column='user_id',
        primary_key=True
    )
    user_nickname = models.CharField(max_length=50)
    user_avatar = models.CharField(max_length=255)
    user_introduction = models.CharField(max_length=300, blank=True, null=True)
    card_banner = models.CharField(max_length=255, blank=True, null=True)
    card_status = models.CharField(max_length=3, blank=True, null=True)
    involved_works = models.TextField(blank=True, null=True)
    key_tags = models.CharField(max_length=255, blank=True, null=True)
    
    # 只保留基於 ID 的外鍵關聯
    work = models.ForeignKey(DbWorksInfo, models.DO_NOTHING, blank=True, null=True)
    need = models.ForeignKey(DbNeedInfo, models.DO_NOTHING, blank=True, null=True)
    
    deal_count = models.IntegerField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_public_card_info'


class DbPublicCardSell(models.Model):
    sell_list_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(DbPublicCardInfo, models.DO_NOTHING, blank=True, null=True)
    sell_title = models.TextField(blank=True, null=True)
    sell_description = models.TextField(blank=True, null=True)
    sell_price = models.IntegerField(blank=True, null=True)
    sell_example_image = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_public_card_sell'