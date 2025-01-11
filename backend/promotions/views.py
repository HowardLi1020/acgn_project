from django.shortcuts import render, redirect, get_object_or_404
from .models import Coupons
from django.utils import timezone
from .form import CouponForm


def coupon_list(request):
    """顯示所有優惠券"""
    coupons = Coupons.objects.all()  # 即使為空，這裡也會返回空的 QuerySet
    return render(request, 'promotions/coupon_list.html', {'coupons': coupons})



def add_coupon(request):
    """新增優惠券"""
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_at = timezone.now()  # 設置創建時間
            coupon.updated_at = timezone.now()  # 設置更新時間
            coupon.save()
            return redirect('promotions:coupon_list')
        else:
            print("Form Errors:", form.errors)
    else:
        form = CouponForm()

    return render(request, 'promotions/add_coupon.html', {'form': form})


def edit_coupon(request, coupon_id):
    """編輯優惠券"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)  # 確保加載了正確的實例
        if form.is_valid():
            updated_coupon = form.save(commit=False)
            updated_coupon.created_at = coupon.created_at  # 保留原始創建日期
            updated_coupon.updated_at = timezone.now()     # 更新編輯日期
            updated_coupon.save()
            return redirect('promotions:coupon_list')
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'promotions/edit_coupon.html', {'form': form})


def delete_coupon(request, coupon_id):
    """刪除優惠券"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)
    coupon.delete()
    return redirect('promotions:coupon_list')
