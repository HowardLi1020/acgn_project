from django.db import models

class Usercoupons(models.Model):
    user_coupon_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', models.DO_NOTHING)
    coupon = models.ForeignKey('promotions.Coupons', models.DO_NOTHING)
    is_used = models.IntegerField(blank=True, null=True)
    usage_count = models.IntegerField(default=0, blank=True, null=True)  # 新增字段
    used_in_order = models.ForeignKey('cart.Orders', models.DO_NOTHING, blank=True, null=True)
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usercoupons'
