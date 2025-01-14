from django.db import models


class Coupons(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    coupon_code = models.CharField(unique=True, max_length=50, verbose_name="優惠券代碼")
    discount_type = models.CharField(max_length=10, verbose_name="折扣類型")  # percentage 或 amount
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="折扣值")
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="最低消費金額")
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="最高折扣金額")
    start_date = models.DateField(verbose_name="開始日期")
    end_date = models.DateField(verbose_name="結束日期")
    is_active = models.BooleanField(default=True, verbose_name="是否啟用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'coupons'
        verbose_name = "優惠券"
        verbose_name_plural = "優惠券"

    def __str__(self):
        return self.coupon_code
