from django.shortcuts import render, redirect, get_object_or_404
from .models import Coupons
from .form import CouponForm
from users.models import MemberBasic
from member_api.models import Usercoupons
from django.contrib import messages


def coupon_list(request):
    """顯示所有優惠券"""
    coupons = Coupons.objects.all()
    return render(request, 'promotions/coupon_list.html', {'coupons': coupons})


def add_coupon(request):
    """新增優惠券"""
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功新增！")
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
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功更新！")
            return redirect('promotions:coupon_list')
        else:
            print("Form Errors:", form.errors)
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'promotions/edit_coupon.html', {'form': form})


def delete_coupon(request, coupon_id):
    """刪除優惠券，並刪除相關的會員優惠券記錄"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)

    # 刪除關聯的會員優惠券記錄
    user_coupon_count = Usercoupons.objects.filter(coupon=coupon).delete()[0]

    # 刪除優惠券本身
    coupon.delete()

    # 添加提示訊息
    messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功刪除，並移除了 {user_coupon_count} 條會員優惠券記錄！")

    return redirect('promotions:coupon_list')


def assign_coupon(request, coupon_id):
    """分派優惠券，並設定每位會員的使用次數限制"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)

    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')
        usage_limit = request.POST.get('usage_limit', 1)  # 默認每位會員可使用 1 次
        try:
            usage_limit = int(usage_limit)
            if usage_limit <= 0:
                raise ValueError("使用次數限制必須為正整數")
        except ValueError:
            messages.error(request, "請輸入有效的使用次數限制！")
            return redirect(request.path)

        members = MemberBasic.objects.filter(pk__in=member_ids)

        assigned_count = 0
        for member in members:
            if not Usercoupons.objects.filter(user=member, coupon=coupon).exists():
                Usercoupons.objects.create(
                    user=member,
                    coupon=coupon,
                    usage_limit=usage_limit,  # 設定使用次數限制
                    usage_count=0  # 初始化已使用次數
                )
                assigned_count += 1

        messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功分派給 {assigned_count} 位會員，每位會員可使用 {usage_limit} 次！")
        return redirect('promotions:coupon_list')

    members = MemberBasic.objects.all()
    return render(request, 'promotions/assign_coupon.html', {
        'coupon': coupon,
        'members': members,
    })
