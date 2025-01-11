# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from users.models import MemberBasic  # 確保這行在文件頂部
# Unable to inspect table 'shopping'
# The error was: (1146, "Table 'shopping.shopping' doesn't exist")

# class MemberBasic(models.Model):
#     user_id = models.AutoField(primary_key=True)
    
#     class Meta:
#         managed = False
#         db_table = 'member_basic'


class DbNeedInfo(models.Model):
    needer = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    needer_nickname = models.ForeignKey('DbPublicCardInfo', models.DO_NOTHING, db_column='needer_nickname', blank=True, null=True)
    needer_avatar = models.ForeignKey('DbPublicCardInfo', models.DO_NOTHING, db_column='needer_avatar', related_name='dbneedinfo_needer_avatar_set', blank=True, null=True)
    needer_introduction = models.ForeignKey('DbPublicCardInfo', models.DO_NOTHING, db_column='needer_introduction', related_name='dbneedinfo_needer_introduction_set', blank=True, null=True)
    need_id = models.AutoField(primary_key=True)
    need_title = models.CharField(max_length=50, blank=True, null=True, unique=True)
    need_category = models.CharField(max_length=50, blank=True, null=True)
    need_original_from = models.CharField(max_length=150, blank=True, null=True, unique=True)
    need_description = models.TextField(blank=True, null=True)
    need_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, unique=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    need_status = models.CharField(max_length=10, blank=True, null=True)
    reviewer_id = models.IntegerField(blank=True, null=True)
    reviewer_nickname = models.CharField(max_length=50, blank=True, null=True)
    reviewer_avatar = models.CharField(max_length=255, blank=True, null=True)
    reviewer_star = models.IntegerField(blank=True, null=True)
    review_content = models.TextField(blank=True, null=True)
    review_time = models.DateTimeField(blank=True, null=True)
    review_status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_need_info'


class DbNeedImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    need = models.ForeignKey(DbNeedInfo, models.DO_NOTHING, blank=True, null=True)
    step = models.IntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_need_images'


class DbWorksInfo(models.Model):
    author = models.ForeignKey(MemberBasic, models.DO_NOTHING)
    author_nickname = models.ForeignKey('DbPublicCardInfo', models.DO_NOTHING, db_column='author_nickname', blank=True, null=True)
    author_avatar = models.ForeignKey('DbPublicCardInfo', models.DO_NOTHING, db_column='author_avatar', related_name='dbworksinfo_author_avatar_set', blank=True, null=True)
    author_introduction = models.ForeignKey('DbPublicCardInfo', models.DO_NOTHING, db_column='author_introduction', related_name='dbworksinfo_author_introduction_set', blank=True, null=True)
    work_id = models.AutoField(primary_key=True)
    work_title = models.CharField(max_length=50, blank=True, null=True, unique=True)
    work_original_from = models.CharField(max_length=150, blank=True, null=True, unique=True)
    work_description = models.TextField(blank=True, null=True)
    usage_restrictions = models.TextField(blank=True, null=True)
    sale_items = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True, null=True)
    work_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, unique=True)
    original_file = models.CharField(max_length=255, blank=True, null=True)
    submission_history = models.TextField(blank=True, null=True)
    work_thumbnail = models.CharField(max_length=255, blank=True, null=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    work_status = models.CharField(max_length=10, blank=True, null=True)
    reviewer_id = models.IntegerField(blank=True, null=True)
    reviewer_nickname = models.CharField(max_length=50, blank=True, null=True)
    reviewer_avatar = models.CharField(max_length=255, blank=True, null=True)
    reviewer_star = models.IntegerField(blank=True, null=True)
    review_content = models.TextField(blank=True, null=True)
    review_time = models.DateTimeField(blank=True, null=True)
    review_status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'db_works_info'
# Unable to inspect table 'works_preview'
# The error was: (1146, "Table 'shopping.works_preview' doesn't exist")


class DbPublicCardInfo(models.Model):
    member_basic = models.OneToOneField(
        'users.MemberBasic',
        models.RESTRICT,
        db_column='user_id',
        primary_key=True  # 將 user_id 設為主鍵
    )
    user_nickname = models.CharField(max_length=50)
    user_avatar = models.CharField(max_length=255)
    user_introduction = models.CharField(max_length=300, blank=True, null=True)
    card_banner = models.CharField(max_length=255, blank=True, null=True)
    involved_works = models.TextField(blank=True, null=True)
    key_tags = models.CharField(max_length=255, blank=True, null=True)
    work = models.ForeignKey(DbWorksInfo, models.DO_NOTHING, blank=True, null=True)
    work_title = models.ForeignKey(DbWorksInfo, models.DO_NOTHING, db_column='work_title', to_field='work_title', related_name='dbpubliccardinfo_work_title_set', blank=True, null=True)
    work_original_from = models.ForeignKey(DbWorksInfo, models.DO_NOTHING, db_column='work_original_from', to_field='work_original_from', related_name='dbpubliccardinfo_work_original_from_set', blank=True, null=True)
    work_price = models.ForeignKey(DbWorksInfo, models.DO_NOTHING, db_column='work_price', to_field='work_price', related_name='dbpubliccardinfo_work_price_set', blank=True, null=True)
    need = models.ForeignKey(DbNeedInfo, models.DO_NOTHING, blank=True, null=True)
    need_title = models.ForeignKey(DbNeedInfo, models.DO_NOTHING, db_column='need_title', to_field='need_title', related_name='dbpubliccardinfo_need_title_set', blank=True, null=True)
    need_original_from = models.ForeignKey(DbNeedInfo, models.DO_NOTHING, db_column='need_original_from', to_field='need_original_from', related_name='dbpubliccardinfo_need_original_from_set', blank=True, null=True)
    need_price = models.ForeignKey(DbNeedInfo, models.DO_NOTHING, db_column='need_price', to_field='need_price', related_name='dbpubliccardinfo_need_price_set', blank=True, null=True)
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
