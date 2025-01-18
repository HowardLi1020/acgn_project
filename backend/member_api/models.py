from django.db import models

class Usercoupons(models.Model):
    user_coupon_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.MemberBasic', on_delete=models.CASCADE, verbose_name="會員")
    coupon = models.ForeignKey('promotions.Coupons', on_delete=models.CASCADE, verbose_name="優惠券")
    usage_limit = models.IntegerField(default=1, verbose_name="使用次數限制")  # 每位會員的使用次數限制
    usage_count = models.IntegerField(default=0, verbose_name="已使用次數")  # 已使用次數
    used_in_order = models.ForeignKey('cart.Orders', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="使用的訂單")
    used_at = models.DateTimeField(blank=True, null=True, verbose_name="最後使用時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'usercoupons'
        verbose_name = "會員優惠券"
        verbose_name_plural = "會員優惠券"

    def __str__(self):
        return f"{self.user} - {self.coupon} ({self.usage_count}/{self.usage_limit})"
