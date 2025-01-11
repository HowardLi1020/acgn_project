from django.db import models


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
