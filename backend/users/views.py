from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from users.models import MemberBasic, MemberVerify, MemberPrivacy, MemberPhotos, MemberLogin, MemberIndextype
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.timezone import now
from urllib.parse import unquote 
# Create your views here.

# 1. 後台-用戶管理首頁(總覽)   OKOK!!
def index(request):
    # 資料庫的操作    
    # 讀取會員所有資料
    members = MemberBasic.objects.all()

    # 修正圖片 URL
    for member in members:
        if member.user_avatar:
            # 解碼 URL
            decoded_avatar = unquote(member.user_avatar.url)

            if decoded_avatar.startswith('/media/https:/'):
                member.avatar_url = decoded_avatar.replace('/media/', '')
            else:
                member.avatar_url = decoded_avatar  # 不修改

    # return JsonResponse(members, safe=False)
    return render(request, "users/index.html", {"members":members} )

# 2. 後台-手動新增用戶資料(註冊)   OKOK!!
def register(request):
    return render(request, 'users/register.html', {"title": "會員註冊"})

# 3. 1.3 後台-修改用戶基本資料(修改)   OKOK!!
@transaction.atomic
def edit(request):
    id = request.GET.get('id')
    member = MemberBasic.objects.get(user_id=id)

    if member.user_avatar:
            # 解碼 URL
            decoded_avatar = unquote(member.user_avatar.url)

            if decoded_avatar.startswith('/media/https:/'):
                member.avatar_url = decoded_avatar.replace('/media/', '')
            else:
                member.avatar_url = decoded_avatar  # 不修改

    if request.method == "POST":
        # 接收使用者上傳的資料
        name = request.POST.get('username')
        phone = request.POST.get('userphone')
        email = request.POST.get("useremail")
        nickname = request.POST.get('usernickname')
        gender = request.POST.get('usergender', 'prefer_not_to_say')  # 預設值
        birth = request.POST.get('userbirth')
        vip_status = request.POST.get("vip_status", "0")

        # 接收上傳的檔案
        userphoto = request.FILES.get('userphoto')
        if userphoto:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'avatars'))
            upload_file = f"avatars/{fs.save(userphoto.name, userphoto)}"
        else:
            upload_file = member.user_avatar
        print(f"upload_file: {upload_file}")  # 記錄解碼後的 URL

        # 有效性檢查
        valid_genders = ['male', 'female', 'prefer_not_to_say']
        if gender not in valid_genders:
            messages.error(request, "性別值不正確。")
            return redirect('users:edit')

        if birth:
            try:
                parsed_date = parse_date(birth)
                if parsed_date is None:
                    raise ValidationError("日期格式錯誤")
            except ValidationError:
                messages.error(request, "日期格式錯誤。應該是 YYYY-MM-DD 格式。")
                return redirect('users:edit')
        else:
            birth = None    

        # 修改到資料庫
        member.user_name = name
        member.user_phone = phone
        member.user_email = email
        member.user_nickname = nickname
        member.user_gender = gender
        member.user_birth = birth
        member.vip_status = vip_status
        member.user_avatar = upload_file

        member.save()
        print(f"Updated user_avatar in database: {member.user_avatar}")

        # 刪除同一用戶的重複 MemberPhoto 紀錄，只保留最新的一條
        member_photos = MemberPhotos.objects.filter(user=member)
        if member_photos.exists():
            member_photos.exclude(pk=member_photos.first().pk).delete()  # 只保留一條紀錄，刪除其他紀錄

        # 更新 MemberPhoto 資料
        MemberPhotos.objects.update_or_create(
            user=member,  # 根據 member 關聯檢查
            defaults={
                "photo_url": member.user_avatar.url if member.user_avatar and member.user_avatar.name else None,
                "updated_at": now()
            },
        )

        messages.success(request, "會員資料更新成功！")
        return redirect('users:index')  #到同一页面
    
    return render(request, "users/edit.html", {"member": member})

# 4. 後台-刪除用戶所有資料(總覽)   OKOK!!
@transaction.atomic
def delete(request, id): 
    try:
        member = MemberBasic.objects.get(user_id=id)
        email = member.user_email

        # 刪除相關的 MemberPrivacy MemberVerify MemberLogin 記錄
        MemberPrivacy.objects.filter(user_id=id).delete()
        MemberVerify.objects.filter(user_id=id).delete()
        MemberLogin.objects.filter(user_id=id).delete()

        # 最後刪除 MemberBasic 記錄
        member.delete()

        messages.success(request, "用戶及其相關信息已成功刪除。")
    except MemberBasic.DoesNotExist:
        messages.error(request, "未找到指定的用戶。")
    except Exception as e:
        messages.error(request, f"刪除過程發生錯誤{str(e)}")

    return redirect('users:index')

# 5. 後台-手動發送驗證信(總覽)
def hand_verify(request):
    id = request.GET.get("id")
    member = None
    if id:
        member = MemberBasic.objects.filter(user_id=id).first()
    return render(request, "users/hand_verify.html", {"title": "手動發驗證碼", "member": member})

# 1.2 後台-用戶個人資料頁面(總覽)
def personal(request):
    try:
        id = request.GET.get("id", 1)
        member = MemberBasic.objects.get(user_id=id)
        
        # 處理頭像
        if member.user_avatar:
            decoded_avatar = unquote(member.user_avatar.url)
            if decoded_avatar.startswith('/media/https:/'):
                member.avatar_url = decoded_avatar.replace('/media/', '')
            else:
                member.avatar_url = decoded_avatar
        
        # 獲取個人喜好
        personal_likes = MemberIndextype.objects.filter(user=member).order_by('sort_order')
        
        # 獲取隱私設定
        account, created = MemberPrivacy.objects.get_or_create(user_id=id)
        
        # 打印調試信息
        print(f"用戶 ID: {id}")
        print(f"個人喜好數量: {personal_likes.count()}")
        for like in personal_likes:
            print(f"喜好: {like.type_name}, 排序: {like.sort_order}")
        
        context = {
            'member': member,
            'account': account,
            'personal_likes': personal_likes,
        }
        
        return render(request, "users/personal.html", context)
    except MemberBasic.DoesNotExist:
        return render(request, 'error.html', {'message': '用戶不存在'})

# 前台-用戶忘記密碼 1. 輸入電子郵箱
def reset(request):
    return render(request, "users/reset.html", {"title": "忘記密碼-輸入電子郵箱"})

# 前台-用戶忘記密碼 2. 發送驗證碼
def reset_confirm(request):
    return render(request, "users/reset_confirm.html", {"title": "忘記密碼-輸入驗證碼"})


# 前台-用戶修改郵箱 1. 輸入電子郵箱
def email_change(request):
    return render(request, "users/email_change.html", {"title": "修改郵箱-輸入電子郵箱"})

# 前台-用戶修改郵箱 2. 發送驗證碼
def email_change_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MemberBasic.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MemberBasic.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        return render(request, 'users/email_change_confirm.html', {'uidb64': uidb64, 'token': token})
    else:
        return render(request, 'users/email_change_confirm.html')

# 後台-用戶修改郵箱 1. 輸入電子郵箱，發送驗證碼
def email_reconfirm(request, token):
    return render(request, "users/email_reconfirm.html", {"title": "修改郵箱-發送驗證碼"})


# 前台-用戶修改手機 1. 輸入手機
def phone_change(request):
    return render(request, "users/phone_change.html", {"title": "修改手機-輸入手機"})

# 前台-用戶修改手機 2. 發送驗證碼
def phone_change_confirm(request, uidb64, token):
    return render(request, "users/phone_change_confirm.html", {"title": "修改手機-發送驗證碼"})

# 後台-用戶修改手機 1. 輸入手機，發送驗證碼
def phone_reconfirm(request, token):
    return render(request, "users/phone_reconfirm.html", {"title": "修改手機-發送驗證碼"})


# 前台-用戶註冊
def signup(request):
    return render(request, "users/signup.html")

# 前台-用戶登入
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        # 驗證用戶
        member = MemberBasic.objects.filter(user_email=email).first()
        if member:
            # 檢查密碼是否已經哈希
            if member.user_password.startswith('pbkdf2_sha256$') or member.user_password.startswith('bcrypt$'):
                # 密碼已哈希，使用 check_password
                password_valid = check_password(password, member.user_password)
            else:
                # 密碼未哈希，直接比較
                password_valid = (password == member.user_password)

            if password_valid:
                # 登入成功
                # 生成一個唯一的session key
                session_key = f"user_session_{member.user_id}"
                
                # 暫存用戶信息，有效期30分鐘
                cache.set(session_key, member.user_id, 30 * 60)
                
                response = redirect('users:dashboard')
                
                # 設置cookie，包含session key
                if remember_me == "on":
                    max_age = 30 * 24 * 60 * 60  # 30天
                    response.set_cookie('user_session', session_key, max_age=max_age)
                else:
                    response.set_cookie('user_session', session_key)
                
                return response
            else:
                messages.error(request, "密碼錯誤，請重新輸入。")
        else:
            messages.error(request, "該郵箱未註冊，請檢查郵箱或註冊新帳號。")

        return render(request, "users/login.html", {"email": email})

    return render(request, "users/login.html")

# 前台-用戶登出
def logout(request):
    # 獲取 session key
    session_key = request.COOKIES.get('user_session')
    
    # 清除緩存中的用户信息
    if session_key:
        cache.delete(session_key)
    
    # 清除 session 中的數據
    request.session.flush()
    
    # 創建響應對象
    response = redirect('users:login')
    
    # 清除 cookie 中的數據
    response.delete_cookie("user_session")
    response.delete_cookie("user_email")
    response.delete_cookie("remember_me")
    
    messages.success(request, "您已成功登出。")
    
    return response

# 檢查用戶是否已登入
def check_auth(request):
    session_key = request.COOKIES.get('user_session')
    if session_key:
        user_id = cache.get(session_key)
        if user_id:
            # 用戶已登入
            return True
    return False

# 前台-用戶登入後的頁面 (簡易版)
def dashboard(request):
    if not check_auth(request):
        messages.warning(request, "您尚未登入或登入已過期，請重新登入。")
        return redirect('users:login')
    
    # 獲取用戶信息
    session_key = request.COOKIES.get('user_session')
    user_id = cache.get(session_key)
    user = MemberBasic.objects.get(user_id=user_id)
    
    # 傳遞用戶信息到前端
    return render(request, "users/dashboard.html", {"user": user})

# 前台-404頁面
def page404(request):
    return render(request, 'users/404.html', {"title": "找不到頁面"})


