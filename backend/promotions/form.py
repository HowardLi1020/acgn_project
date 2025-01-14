from django import forms
from .models import Coupons

DISCOUNT_TYPE_CHOICES = [
    ('percentage', '百分比折扣'),  # 資料庫設置為 percentage
    ('amount', '固定金額折扣'),      # 資料庫設置為 amount
]

class CouponForm(forms.ModelForm):
    discount_type = forms.ChoiceField(
        choices=DISCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="折扣類型"
    )
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="是否啟用"
    )

    class Meta:
        model = Coupons
        exclude = ['created_at', 'updated_at']  # 排除資料庫自動處理的欄位
        labels = {
            'coupon_code': '優惠券代碼',
            'discount_value': '折扣值',
            'min_purchase': '最低消費金額',
            'max_discount': '最高折扣金額',
            'start_date': '開始日期',
            'end_date': '結束日期',
            'is_active': '是否啟用',
        }
        widgets = {
            'coupon_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請輸入優惠券代碼'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '請輸入折扣值'}),
            'min_purchase': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '請輸入最低消費金額'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '請輸入最高折扣金額'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
