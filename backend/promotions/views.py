from django.shortcuts import render, redirect, get_object_or_404
from .form import CouponForm
from promotions.models import Coupons
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
    """分派優惠券，檢查會員是否已經擁有該優惠券"""
    coupon = get_object_or_404(Coupons, pk=coupon_id)

    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')
        usage_limit = int(request.POST.get('usage_limit', 1))  # 默認每位會員可使用 1 次

        members = MemberBasic.objects.filter(pk__in=member_ids)
        assigned_count = 0
        already_has_coupon = []  # 用於存放已擁有優惠券的會員清單

        for member in members:
            # 檢查會員是否已擁有該優惠券
            if Usercoupons.objects.filter(user=member, coupon=coupon).exists():
                already_has_coupon.append(member.user_name)  # 保存會員名稱
                continue  # 跳過此會員

            # 如果會員未擁有，則新增記錄
            Usercoupons.objects.create(
                user=member,
                coupon=coupon,
                usage_limit=usage_limit,
                usage_count=0
            )
            assigned_count += 1

        # 顯示提示訊息
        if assigned_count > 0:
            messages.success(request, f"優惠券 '{coupon.coupon_code}' 已成功分派給 {assigned_count} 位會員，每位會員可使用 {usage_limit} 次！")
        if already_has_coupon:
            messages.warning(request, f"以下會員已擁有優惠券 '{coupon.coupon_code}'：{', '.join(already_has_coupon)}")

        return redirect('promotions:coupon_list')

    members = MemberBasic.objects.all()
    return render(request, 'promotions/assign_coupon.html', {
        'coupon': coupon,
        'members': members,
    })

