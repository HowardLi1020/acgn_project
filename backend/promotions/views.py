from django.shortcuts import render, redirect, get_object_or_404
from .models import Coupons
from django.utils import timezone
from .form import CouponForm
from users.models import MemberBasic
from member_api.models import Usercoupons
from django.contrib import messages

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
            print("Form Errors:", form.errors)  # 排查表單錯誤
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'promotions/edit_coupon.html', {'form': form})


def delete_coupon(request, coupon_id):
    """刪除優惠券，並刪除相關的會員優惠券記錄"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)

    # 刪除關聯的會員優惠券記錄
    user_coupon_count = Usercoupons.objects.filter(coupon=coupon).delete()[0]  # 刪除並獲取刪除的記錄數

    # 刪除優惠券本身
    coupon.delete()

    # 添加提示訊息
    messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功刪除，並移除了 {user_coupon_count} 條會員優惠券記錄！")

    return redirect('promotions:coupon_list')

def assign_coupon(request, coupon_id):
    """分派優惠券"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)

    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')  # 獲取選中的會員 ID 列表
        members = MemberBasic.objects.filter(pk__in=member_ids)

        for member in members:
            # 確保不會重複分派
            if not Usercoupons.objects.filter(user=member, coupon=coupon).exists():
                Usercoupons.objects.create(user=member, coupon=coupon)

        # 添加提示訊息
        messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功分派給選中的會員！")

        # 重定向到優惠券列表頁
        return redirect('promotions:coupon_list')

    # GET 請求返回會員列表
    members = MemberBasic.objects.all()
    return render(request, 'promotions/assign_coupon.html', {
        'coupon': coupon,
        'members': members,
    })