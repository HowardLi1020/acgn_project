from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
import os
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.cache import cache
from django.urls import reverse
from django.utils.timezone import now, timedelta
from users.models import MemberBasic, MemberVerify, MemberPrivacy, MemberPhotos
from django.utils.crypto import get_random_string
import random
from django.db.models import Q
import json
import re
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


# Create your views here.
# 後台會員管理首頁
# 1.  後台-用戶管理首頁(總覽)   OKOK!!
def index(request):
    # 讀取會員所有資料
    members = list(MemberBasic.objects.values())
    return JsonResponse(members, safe=False)

# 1.1 後台-用戶管理首頁(搜尋用戶名 手機 信箱)  OKOK!!
def search(request):
    search_value = request.GET.get("search", "").strip()
    result = []

    if search_value:
        members = MemberBasic.objects.filter(
            Q(user_name__icontains=search_value) |
            Q(user_phone__icontains=search_value) |
            Q(user_email__icontains=search_value)
        )
        result = list(members.values('user_id', 'user_name', 'user_phone', 'user_email'))

    return JsonResponse(result, safe=False)

# 1.2 後台-用戶個人資料頁面(總覽)  支付設定    not yet
def personal(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # 解析請求的 JSON
        id = data.get("id")
        password = data.get("userPassword")

        member = MemberBasic.objects.get(user_id=id)
        member.user_password = password  # 修改密碼
        member.updated_at = now()
        member.save()  # 保存到資料庫
            # return render(request, "users/personal.html", {"member": member})
        return JsonResponse({"success": True, "message": "修改成功"})
    return JsonResponse({"success": False, "message": "請求錯誤"})

# 1.4 後台-用戶個人資料頁面(更新用戶隱私設定)
def privacy_setting(request):
    try:
        if request.method == 'POST':
            user_id = request.POST.get('user')
            account_verify = request.POST.get('accountOn') == 'True'
            activity_checked = request.POST.get('activateOn') == 'True'

            # 更新資料庫中的隱私設定
            member_privacy, created = MemberPrivacy.objects.get_or_create(user_id=user_id)
            member_privacy.account_verify = account_verify
            member_privacy.activity_checked = activity_checked
            member_privacy.updated_at = now()
            member_privacy.save()

            # 獲取最新的 MemberBasic 對象
            member = MemberBasic.objects.get(user_id=user_id)

            return JsonResponse({
                'status': 'success',
                'verification_message': '啟動 / On' if account_verify else '關閉 / Off',
                'activation_message': '啟動 / On' if activity_checked else '關閉 / Off',
                'account_verify': account_verify,
                'activity_checked': activity_checked
            })
    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=500)
    return JsonResponse({"success": False, "message": "請求錯誤"}, status=400)

# 2. 後台-手動新增用戶(註冊)  跟 前台-signup 類似   OKOK!!
def register(request):
    if request.method == "POST":
        name = request.POST.get("name","GUEST")
        phone = request.POST.get("phone","0911223344")
        email = request.POST.get("email","guest@gmail.com")
        password = request.POST.get("password")
        password1 = request.POST.get("password1")
        nickname = request.POST.get("nickname","nickname")
        gender = request.POST.get("gender","prefer_not_to_say")
        birth = request.POST.get("birth","2024-09-21")
        vip_status = request.POST.get("vip_status","0")
        uploaded_file = request.FILES.get("avatar")

        required_fields = [name, phone, email, password, password1, birth]
        if any(not field for field in required_fields):
            error_message = "請填寫所有帶有 *必填欄位"
            return JsonResponse({"success": False, "message": "請填寫所有帶有 *必填欄位"}, status=400)

        # 檢查用戶名是否存在
        if MemberBasic.objects.filter(user_name=name).exists():
            content = f"姓名已存在，請重新輸入。"
            return JsonResponse({"success": False, "message": f"姓名已存在，請重新輸入。"}, status=409)
        # 檢查電子郵件是否存在
        if MemberBasic.objects.filter(user_email=email).exists():
            content = f"請重新輸入電子郵箱。"
            return JsonResponse({"success": False, "message": f"請重新輸入電子郵箱。"}, status=409)
        
        # 檢查手機號是否存在
        if MemberBasic.objects.filter(user_phone=phone).exists():
            content = f"請重新輸入手機號。"
            return JsonResponse({"success": False, "message": f"請重新輸入手機號。"}, status=409)

        # 檢查密碼是否一致
        if password != password1:
            content = f"密碼不一致，請重新確認。"
            return JsonResponse({"success": False, "message": "密碼不一致，請重新確認。"}, status=400)

        # 如果沒有上傳文件，使用默認頭像
        if not uploaded_file:
            file_name = "avatars/default.png"   # 修改為 avatars 路徑
        else:
            # fs = FileSystemStorage()
            # file_name = fs.save(uploaded_file.name, uploaded_file)
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'avatars'))  # 儲存到 avatars 子目錄
            file_name = f"avatars/{fs.save(uploaded_file.name, uploaded_file)}"
            
            # 將表單傳過來的資料寫進資料庫
        try:
            member = MemberBasic.objects.create(
                user_name = name,
                user_phone = phone,
                user_email = email,
                user_password = make_password(password),
                user_nickname = nickname,
                user_gender = gender,
                user_birth = birth,
                user_avatar = file_name,
                vip_status = vip_status,
                created_at = now()
            )

            # 創建 pohtos進資料庫
            MemberPhotos.objects.create(
                user=member,  # 根據 member 關聯檢查
                created_at = now(),
                photo_url = member.user_avatar.url if member.user_avatar and member.user_avatar.name else None
            )

            # 產生隱私設定-預設為未驗證
            MemberPrivacy.objects.create(
                user=member,
                created_at=now(),
                email_verified=False,     # 郵箱驗證預設為未驗證
                account_verify=False      # 初始帳號預設為未驗證
            )

            # 產生驗證碼
            verification_token = get_random_string(16)
            MemberVerify.objects.create(
                user=member,
                change_value=email,
                verification_type='registration',
                verification_token=verification_token,
                created_at=now(),
                expires_at=now() + timedelta(days=1),
                token_used=False    # 初始驗證碼預設為未使用
            )

            # 發送驗證郵件
            verification_url = request.build_absolute_uri(
                reverse('users_api:verify_email', args=[verification_token])
            )
            send_mail(
                '驗證您的帳號',
                f'請點擊以下連結驗證您的帳號：{verification_url}',
                'forworkjayjay@gmail.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "註冊成功，提醒用戶查看郵箱，並點擊驗證連結以啟動帳號！~*"}, status=201)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"註冊失敗：{str(e)}"}, status=500)
        
    return JsonResponse({"success": False, "message": "不支持的請求方法"}, status=405)

# 2-1. 後台-手動新增用戶(檢查用戶姓名)
def checkname(request):
    name = request.GET.get("name","GUEST")
    result = {
        "name_exists": False,
    }
    # 檢用戶名是否存在
    if MemberBasic.objects.filter(user_name=name).exists():
        result["name_exists"] = True
    return JsonResponse(result, safe=False)

# 2-2. 後台-手動新增用戶(檢查用戶手機)
def checkphone(request):
    phone = request.GET.get("phone","0911223344")
    result = {
        "phone_exists": False,
    }
    # 檢查手機號是否存在
    if MemberBasic.objects.filter(user_phone=phone).exists():
        result["phone_exists"] = True
    return JsonResponse(result, safe=False)

# 2-3. 後台-手動新增用戶(檢查電子郵件)
def checkemail(request):
    email = request.GET.get("email","guest@gmail.com")
    result = {
        "email_exists": False,
    }
    # 檢查電子郵件是否存在
    if MemberBasic.objects.filter(user_email=email).exists():
        result["email_exists"] = True
    return JsonResponse(result, safe=False)

# 2-4. 後台-手動新增用戶(檢查用戶密碼是否一致)
def checkpassword(request):
    password = request.GET.get("password")
    result = {
        "password_match": False,
    }
    # 檢查密碼是否相符
    if MemberBasic.objects.filter(user_password=password).exists():
        result["password_match"] = True
    return JsonResponse(result, safe=False)


# 前後台-用戶忘記密碼 1.發驗證信  OKOK!!
def send_reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        userid = data.get('userid')

        if email and userid:
            try:
                with transaction.atomic():
                    member = MemberBasic.objects.get(user_id=userid)

                    # 驗證郵箱是否匹配
                    if member.user_email != email:
                        return JsonResponse({'status': 'error', 'message': '用戶ID與郵箱不匹配'})
                    
                    member.user_password = make_password(data.get('password'))
                    member.updated_at = now()
                    member.save()
                    
                    # 創建新的驗證記錄
                    verify_code = random.randint(100000, 999999)
                    expiration_time = now() + timedelta(hours=24)
                    
                    MemberVerify.objects.create(
                        user=member,
                        verification_type='password_change',
                        verification_code=verify_code,
                        change_value=email,
                        created_at=now(),
                        expires_at=expiration_time,
                        code_used=False
                    )
                    
                    send_verification_email(email, verify_code, userid)
                return JsonResponse({'status': 'success', 'message': '重置密碼-驗證信已發送，請提醒用戶留意郵箱。'})
            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在'})
        else:
            return JsonResponse({'status': 'error', 'message': '未提供電子郵件地址'})
    else:
        return JsonResponse({'status': 'error', 'message': '請使用 POST 方法發送請求'})

# 前後台-用戶忘記密碼 2.檢查email是否存在於資料庫
def request_verification(request):
    if request.method == 'POST':
        email_address = request.POST.get('email')
        user_id = request.POST.get('id')
        # user_id = request.POST.get('user')

        member = MemberBasic.objects.get(user_id=user_id)

       
        if MemberBasic.objects.filter(user_email=email_address).exists():
            # 刪除該信箱的所有舊驗證記錄
            MemberVerify.objects.filter(user_id=user_id).delete()
            
            # 創建新的驗證記錄
            verify_code = random.randint(100000, 999999)
            expiration_time = now() + timedelta(hours=24)
            
            MemberVerify.objects.create(
                user=member,
                verification_type='password_change',
                verification_code=verify_code,
                change_value=email_address,
                created_at=now(),
                expires_at=expiration_time,
                code_used=False
            )
            
            send_verification_email(email_address, verify_code)
            return JsonResponse({"message": "重置密碼-驗證信已發送，請留意註冊郵箱。"}, status=200)
        else:
            return JsonResponse({"message": "請確認信箱是否輸入正確"}, status=404)
        
    return JsonResponse({"message": "請使用 POST 方法發送請求！"}, status=405)

# 前後台-用戶忘記密碼 3.輸入email 發送隨機6位數驗證信  OKOK!!
def send_verification_email(email_address, verify_code, userid):
    msg = EmailMessage(
        '忘記密碼-驗證碼驗證',
        f'親愛的用戶您好，請您點擊以下連結進行安全驗證：http://127.0.0.1:8000/users_api/reset_confirm?code={verify_code}&id={userid}，如您已登入成功，請您忽略此消息即可，謝謝。',
        'forworkjayjay@gmail.com',
        [email_address]
    )
    msg.send()
    
    return verify_code

# 前後台-用戶忘記密碼 4.確認驗證碼存於資料庫 並跳轉重置密碼頁面  OKOK!!
def verify_code(request):
    if request.method == 'GET':
        try:
            code = request.GET.get('code')  # 提取查詢參數中的 `code`
            userid = request.GET.get('id')
            
            verification_entry = MemberVerify.objects.get(verification_code=code, user_id=userid)

            # 驗證碼是否過期
            if verification_entry.is_valid() and not verification_entry.code_used:
                verification_entry.code_used = True  # 設置為已使用
                verification_entry.save()  # 驗證成功後儲存驗證碼
                return JsonResponse({"code_exists": True}, status=200)

            return JsonResponse({"message": "驗證碼已過期"}, status=400)
        except MemberVerify.DoesNotExist:
            return JsonResponse({"message": "驗證碼無效"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"message": "請求格式錯誤"}, status=400)

    return JsonResponse({"message": "不支援的請求方法"}, status=405)

# 前後台-用戶忘記密碼 5.重置密碼並更新資料庫跳轉登入頁面
def reset_confirm(request):
    try:
        if request.method == 'GET':
            code = request.GET.get('code')  # 提取 code 查詢參數
            user_id = request.GET.get('id')  # 提取 id 查詢參數

            # 查找驗證記錄
            verification = MemberVerify.objects.filter(verification_code=code, user_id=user_id, code_used=False).first()
            
            if not verification:
                return render(request, 'users/reset.html', {
                    'error': '無效的驗證連結，或已經被使用。請重新申請重置密碼。',
                    'frontend_url': settings.FRONTEND_URL
                })
            
            # 渲染密碼重置頁面
            return render(request, 'users/reset_confirm.html', {
                'frontend_url': settings.FRONTEND_URL,
            })

        # POST 請求處理
        elif  request.method == 'POST':
            # 提取 JSON 數據
            body = json.loads(request.body)
            code = body.get('code')
            user_id = body.get('id')
            new_password = body.get('password')
            confirm_password = body.get('password1')

            # 查找驗證記錄
            try:
                verification = MemberVerify.objects.filter(verification_code=code, user_id=user_id, code_used=False).first()

                if not verification:
                    return JsonResponse({'status': 'error', 'message': '無效的驗證連結或已被使用。'})

                # 驗證密碼一致性
                if new_password != confirm_password:
                    return JsonResponse({'status': 'error', 'message': '密碼不一致，請重新輸入。'})

                # 更新密碼
                user = verification.user
                with transaction.atomic():
                    user.user_password = make_password(new_password)
                    user.updated_at = now()
                    user.save()
                    verification.code_used = True
                    verification.save()
            
                return JsonResponse({'status': 'success', 'message': '密碼已更新，稍後請使用新密碼登入。'})
            
            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在。'})
        context = {
            'frontend_url': settings.FRONTEND_URL,
            'code': code,
            'user_id': verification.user.user_id
        }
        return render(request, 'users/reset_confirm.html', context)
        
    except Exception as e:
        return render(request, 'users/reset.html', {
            'error': '發生錯誤，請稍後再試。',
            'frontend_url': settings.FRONTEND_URL,
        })


# 後台-用戶"修改信箱"  1.發送驗證信  OKOK!!
def reset_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            userid = data.get('userid')
            
            if not email:
                return JsonResponse({'status': 'error', 'message': '未提供電子郵件地址'}, status=400)

            try:
                member = MemberBasic.objects.get(user_id=userid)
            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在'}, status=404)

            # 生成驗證碼
            verification_token = get_random_string(length=16)
            expiration_time = now() + timedelta(hours=24)

            # 保存驗證碼(24H)
            MemberVerify.objects.create(
                user=member,
                verification_type='email_change',
                verification_token=verification_token,
                change_value=email,
                created_at=now(),
                expires_at=expiration_time,
                token_used=False
            )

            # 構建驗證 URL
            verification_url = request.build_absolute_uri(
                reverse('users_api:reconfirm_email', args=[verification_token])
            )

            # 發送郵件
            subject = '修改電子郵箱地址'
            message = f'請點擊以下連結來修改您的電子郵箱地址：\n\n{verification_url}\n\n如果您沒有請求修改電子郵箱，請忽略此郵件。'
            send_mail(subject, message, 'forworkjayjay@gmail.com', [email])

            return JsonResponse({'status': 'success', 'message': '修改信箱-驗證信已發送，請提醒用戶留意郵箱。'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '無效的 JSON 數據。'}, status=400)

    return JsonResponse({'status': 'error', 'message': '不支持的請求方法'}, status=405)

# 後台-用戶"修改信箱"  2.確認驗證碼存於資料庫 跳轉修改信箱頁面並輸入原始密碼  OKOK!!
def reconfirm_email(request, token=None):
    try:
        verification = MemberVerify.objects.get(verification_token=token, token_used=False)
        if now() > verification.expires_at:
            return render(request, 'users/email_reconfirm.html', {
                'error': '驗證連結已過期，請重新申請修改郵箱。',
                'frontend_url': settings.FRONTEND_URL
            })
        
        if request.method == 'POST':
            data = json.loads(request.body)
            new_email = data.get('newEmail')
            password = data.get('password')


            try:
                user = verification.user
                if not check_password(password, user.user_password):
                    return JsonResponse({'status': 'error', 'message': '密碼錯誤。'})

                if new_email == user.user_email:
                    return JsonResponse({'status': 'error', 'message': '新郵箱不能與原郵箱相同。'})

                with transaction.atomic():
                    # 更新 MemberBasic 的郵箱
                    user.user_email = new_email
                    user.updated_at = now()
                    user.save()

                    # 更新 MemberVerify 的 token_used email
                    verification.token_used = True
                    verification.change_value = new_email
                    verification.save()

                return JsonResponse({'status': 'success', 'message': '郵箱修改成功，3秒後跳轉登入頁面。'})
            
            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在。'})
        context = {
            'frontend_url': settings.FRONTEND_URL,
            'token': token,
            'old_email': verification.user.user_email
        }
        return render(request, 'users/email_reconfirm.html', context)           
    except MemberVerify.DoesNotExist:
        # 當驗證記錄不存在或已被使用
        context = {
            'frontend_url': settings.FRONTEND_URL,
            'error': '無效的驗證連結，請填寫以下資料，為您重新申請修改郵箱。',
            'token': ''
        }
        return render(request, 'users/email_change.html', context)
    

# 後台-用戶"修改手機"  1.發送驗證信  OKOK!!
def reset_phone(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            email = data.get('email')
    
            if not phone or not email:
                return JsonResponse({'status': 'error', 'message': '未提供手機號或電子郵件地址'}, status=400)

            try:
                member = MemberBasic.objects.get(user_phone=phone, user_email=email)
            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在或手機號與電子郵件不匹配'}, status=404)

            # 生成驗證碼
            verification_token = get_random_string(length=16)
            expiration_time = now() + timedelta(hours=24)

            # 保存驗證碼(24H)
            MemberVerify.objects.create(
                user=member,
                verification_type='phone_change',
                verification_token=verification_token,
                change_value=email,
                created_at=now(),
                expires_at=expiration_time,
                token_used=False
            )

            # 構建驗證 URL
            verification_url = request.build_absolute_uri(
                reverse('users_api:reconfirm_phone', args=[verification_token])
            )

            # 發送郵件
            subject = '修改手機號'
            message = f'請點擊以下連結來修改您的手機號：\n\n{verification_url}\n\n如果您沒有請求修改手機號，請忽略此郵件。'
            send_mail(subject, message, 'forworkjayjay@gmail.com', [email])

            return JsonResponse({'status': 'success', 'message': '修改手機-驗證信已發送，請提醒用戶留意郵箱。'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '無效的 JSON 數據。'}, status=400)

    return JsonResponse({'status': 'error', 'message': '不支持的請求方法'}, status=405)

# 後台-用戶"修改手機"  2.確認驗證碼存於資料庫 跳轉修改手機頁面並輸入原始密碼  OKOK!!
def reconfirm_phone(request, token=None):
    try:
        verification = MemberVerify.objects.get(verification_token=token, token_used=False)
        if now() > verification.expires_at:
            return render(request, 'users/phone_reconfirm.html', {
                'error': '驗證連結已過期，請重新申請修改手機。',
                'frontend_url': settings.FRONTEND_URL
            })
        
        if request.method == 'POST':
            # 支持多種提交格式
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'message': '請求格式不正確，應為 JSON。'})
            else:
                data = request.POST
            
            new_phone = data.get('newPhone')
            password = data.get('password')

            # 添加手機號碼格式驗證
            if not re.match(r'^09\d{8}$', new_phone):
                return JsonResponse({'status': 'error', 'message': '請輸入有效的手機號碼格式。'})
            
            # 添加新手機號是否已存在於資料庫中
            if MemberBasic.objects.filter(user_phone=new_phone).exists():
                return JsonResponse({'status': 'error', 'message': '新手機號已被其他用戶使用。'})

            try:
                user = verification.user
                if not check_password(password, user.user_password):
                    return JsonResponse({'status': 'error', 'message': '密碼錯誤。'})
            
                if new_phone == user.user_phone:
                    return JsonResponse({'status': 'error', 'message': '新手機號不能與原手機號相同。'})
                
                with transaction.atomic():
                    # 更新 MemberBasic 的手機
                    user.user_phone = new_phone
                    user.updated_at = now()
                    user.save()
                
                    verification.token_used = True
                    verification.save()
    
                return JsonResponse({'status': 'success', 'message': '手機號修改成功，3秒後跳轉登入頁面。'})
            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在。'})
        context = {
            'frontend_url': settings.FRONTEND_URL,
            'token': token,
            'old_phone': verification.user.user_phone
        }
        return render(request, 'users/phone_reconfirm.html', context)
    except MemberVerify.DoesNotExist:
        # 當驗證記錄不存在或已被使用
        context = {
            'frontend_url': settings.FRONTEND_URL,
            'error': '無效的驗證連結，請填寫以下資料，為您重新申請修改手機號。',
            'token': ''
        }
        return render(request, 'users/phone_change.html', context)


# 前台-首次註冊
def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        vip_status = request.POST.get("vip_status","0")
        uploaded_file = request.FILES.get("avatar")

        required_fields = [name, email, phone, password, confirm_password]
        if any(not field for field in required_fields):
            return JsonResponse({"success": False, "message": "請填寫所有帶有 *必填欄位"}, status=400)

        if MemberBasic.objects.filter(user_name=name).exists():
            return JsonResponse({"success": False, "message": "姓名已存在，請重新輸入。"}, status=409)

        if MemberBasic.objects.filter(user_email=email).exists():
            return JsonResponse({"success": False, "message": "請重新輸入電子郵箱。"}, status=409)

        if MemberBasic.objects.filter(user_phone=phone).exists():
            return JsonResponse({"success": False, "message": "請重新輸入手機號。"}, status=409)

        if password != confirm_password:
            return JsonResponse({"success": False, "message": "密碼不一致，請重新確認。"}, status=400)
        
        # 如果沒有上傳文件，使用默認頭像
        if not uploaded_file:
            file_name = "avatars/default.png"   # 修改為 avatars 路徑
        else:
            # fs = FileSystemStorage()
            # file_name = fs.save(uploaded_file.name, uploaded_file)
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'avatars'))  # 儲存到 avatars 子目錄
            file_name = f"avatars/{fs.save(uploaded_file.name, uploaded_file)}"

        try:
            member = MemberBasic.objects.create(
                user_name=name,
                user_email=email,
                user_phone=phone,
                user_password=make_password(password),
                user_avatar = file_name,
                vip_status = vip_status,
                created_at=now(),
            )

            MemberPrivacy.objects.create(
                user=member,
                created_at=now(),
                email_verified=False,     # 郵箱驗證預設為未驗證
                account_verify=False      # 初始帳號預設為未驗證
            )

            # 產生驗證碼
            verification_token = get_random_string(16)
            MemberVerify.objects.create(
                user=member,
                verification_type='registration',
                change_value=email,
                verification_token=verification_token,
                created_at=now(),
                expires_at=now() + timedelta(days=1),
                token_used=False # 初始驗證碼預設為未使用
            )

            # 發送驗證郵件
            verification_url = request.build_absolute_uri(
                reverse('users_api:verify_email', args=[verification_token])
            )
            send_mail(
                '驗證您的帳號',
                f'請點擊以下連結驗證您的帳號：{verification_url}',
                'forworkjayjay@gmail.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "註冊成功，請查看您的郵箱並點擊驗證連結以啟動帳號！~*"}, status=201)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"註冊失敗：{str(e)}"}, status=500)
        
    return JsonResponse({"success": False, "message": "不支持的請求方法"}, status=405)

# 前後台-首次註冊(驗證帳號郵箱)
def verify_email(request, token):
    try:
        verification = MemberVerify.objects.filter(verification_token=token, token_used=False).first()
        if not verification :
            # 無效的驗證碼，重定向到前端
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=invalid")
        
        if now() > verification.expires_at:
            # 過期 刪除用戶及相關資料
            member = verification.user
            member.delete()
            verification.delete()  # 刪除驗證記錄

            # 驗證連結過期，重定向到前端註冊頁面
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=expired")
        else:
            member = verification.user
            member_privacy = MemberPrivacy.objects.get(user=member)
            member_privacy.account_verify = True
            member_privacy.email_verified = True
            member_privacy.updated_at = now()
            member_privacy.save()

            verification.token_used = True
            verification.save()

            return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=success")
    except MemberVerify.DoesNotExist:
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=invalid")

# 前後台-首次註冊(重新發送驗證郵件)  not yet
def resend_verify_email(request):
    if request.method == 'POST':
        try:
            # 解析請求的 JSON 資料
            data = json.loads(request.body)
            user_email = data.get('user_email')

            # 驗證 email 是否提供
            if not user_email:
                return JsonResponse({"message": "未提供電子郵件。", "type": "error"}, status=400)

            # 確認用戶是否存在
            try:
                user = MemberBasic.objects.get(user_email=user_email)
            except MemberBasic.DoesNotExist:
                return JsonResponse({"message": "用戶不存在。", "type": "error"}, status=404)

            # 建立新的驗證記錄
            verification = MemberVerify.objects.create(
                user=user,
                verification_token=get_random_string(32),
                created_at=now(),
                expires_at=now() + timedelta(hours=24),  # 新的有效期限
                token_used=False,
            )

            # 發送驗證信
            send_mail(
                '重新驗證您的帳號',
                f"請點擊以下連結完成驗證：{settings.FRONTEND_URL}/verify-email/{verification.verification_token}/",
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
            )

            return JsonResponse({"message": "驗證信已重新發送。", "type": "success"})
        except json.JSONDecodeError:
            return JsonResponse({"message": "無效的請求格式。", "type": "error"}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"發送驗證信時發生錯誤：{str(e)}", "type": "error"}, status=500)
    else:
        return JsonResponse({"message": "僅支持 POST 請求。", "type": "error"}, status=405)


# 前台-用戶"修改信箱" 1.發送驗證信
def email_change(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': '無效的 JSON 數據。'}, status=400)
        
        old_email = data.get('old_email')
        new_email = data.get('new_email')
        
        if not new_email or not old_email:
            return JsonResponse({'message': '請輸入有效的電子郵箱地址。'}, status=400)
        
        # 驗證新郵箱格式
        try:
            validate_email(new_email)
        except ValidationError:
            return JsonResponse({'message': '新電子郵箱地址格式無效。'}, status=400)
        
        if MemberBasic.objects.filter(user_email=old_email).exists():
            member = MemberBasic.objects.get(user_email=old_email)
        else:
            return JsonResponse({'message': '舊電子郵箱地址不存在。'}, status=400)
        
        if MemberBasic.objects.filter(user_email=new_email).exists():
            return JsonResponse({'message': '該電子郵箱地址已被使用。'}, status=400)
        
        # 生成隨機6位數驗證碼
        verification_code = random.randint(100000, 999999)
        
        # 生成驗證連結的token
        verification_token = get_random_string(length=16)
        
        # 保存驗證信息
        MemberVerify.objects.create(
            user=member,
            change_value=new_email,
            verification_type='email_change',
            verification_token=verification_token,
            verification_code=verification_code,  # 保存驗證碼
            created_at=now(),
            expires_at=now() + timedelta(hours=24),
            token_used=False,
            code_used=False
        )
        
        # 構建驗證 URL
        verification_url = request.build_absolute_uri(
            reverse('users_api:email_change_confirm', args=[verification_token])
        )
        
        # 發送郵件
        subject = '修改電子郵箱地址'
        message = f'請點擊以下連結來修改您的電子郵箱地址：\n\n{verification_url}\n\n如果您沒有請求修改電子郵箱，請忽略此郵件。\n\n您的驗證碼是：{verification_code}'
        send_mail(subject, message, 'forworkjayjay@gmail.com', [new_email])
        
        return JsonResponse({'status': 'success','message': '驗證信已發送到您的新郵箱，請查收。'}, status=200)
    
    return JsonResponse({'status': 'error', 'message': '不支援的請求方法。'}, status=405)

# 前台-用戶"修改信箱" 2.用戶輸入驗證碼 進入修改郵箱頁面
def email_change_confirm(request, token):
    try:
        verification = MemberVerify.objects.get(verification_token=token, token_used=False)

        if now() > verification.expires_at:
            return render(request, 'member/email_change_confirm.html', {'error': '驗證連結已過期，請重新申請修改郵箱。'})
            # return JsonResponse({
            #     'status': 'error',
            #     'message': '驗證連結已過期，請重新申請修改郵箱。',
            #     'redirect_url': f"{settings.FRONTEND_URL}email-change"
            # })
        
        if request.method == 'GET':
            # 返回驗證頁面的前端 URL 和相關信息
            return render(request, 'users/email_change_confirm.html', {'token': token})
            # return JsonResponse({
            #     'status': 'success',
            #     'message': '驗證連結有效，請輸入驗證碼。',
            #     'redirect_url': f"{settings.FRONTEND_URL}email-verify?token={token}"
            # })

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': '請求格式無效。'}, status=400)
            
            verification_code = data.get('verification_code')  # 接收用戶輸入的驗證碼
            
            # 檢查驗證碼是否正確
            if verification_code != verification.verification_code:
                return JsonResponse({'status': 'error', 'message': '驗證碼錯誤。'})
                # return JsonResponse({
                #     'status': 'error', 
                #     'message': '驗證碼錯誤,請再次確認。',
                #     'stay_on_page': True  # 停留在當前頁面
                #     }, status=400)
            
            # 驗證碼正確，返回修改信箱的頁面 URL
            return JsonResponse({
                'status': 'success',
                'message': '驗證碼正確，即將進入修改郵箱頁面。',
                'redirect_url': reverse('users_api:email_change_form', args=[verification.verification_code])  # 返回修改信箱的 URL
                # 'redirect_url': f"{settings.FRONTEND_URL}email-reset"
            })
        
        # 非 POST 請求的處理
        return JsonResponse({'status': 'error', 'message': '不支援的請求方法。'}, status=405)
    
    except MemberVerify.DoesNotExist:
        # 當驗證記錄不存在或已被使用
        return JsonResponse({'status': 'error', 'message': '無效的驗證連結。'})
        # return JsonResponse({
        #     'status': 'error',
        #     'message': '無效的驗證連結，請重新申請修改郵箱。',
        #     'redirect_url': f"{settings.FRONTEND_URL}email-change"
        # }, status=404)

# 前台-用戶"修改信箱" 3.更新驗證碼狀態 並於輸入新郵箱.密碼 更新資料庫
def email_change_form(request, code):
    try:
        verification = MemberVerify.objects.get(verification_code=code, code_used=False)
        if now() > verification.expires_at:
            return render(request, 'member/email_change_confirm.html', {'error': '驗證連結已過期，請重新申請修改郵箱。'})
            # return JsonResponse({
            #     'status': 'error',
            #     'message': '驗證連結已過期，請重新申請修改郵箱。',
            #     'redirect_url': f"{settings.FRONTEND_URL}email-change"
            # })
        
        user_id = verification.user.user_id

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': '請求格式無效。'}, status=400)
            
            new_email = data.get('email')
            password = data.get('password')
            verification_code = data.get('verification_code')  # 接收用戶輸入的驗證碼
            
            # 檢查驗證碼是否正確
            if verification_code != verification.verification_code:
                return JsonResponse({
                    'status': 'error', 
                    'message': '驗證碼錯誤,請再次確認。',
                    'stay_on_page': True  # 停留在當前頁面
                    }, status=400)
            
            # 檢查新郵箱是否已被使用
            if new_email != verification.change_value:
                return JsonResponse({
                    'status': 'error', 
                    'message': '新郵箱與輸入不相符，請再次確認。',
                    'stay_on_page': True  # 停留在當前頁面
                    }, status=400)
            
            try:
                user = MemberBasic.objects.get(user_id=user_id)
                if not check_password(password, user.user_password):
                    return JsonResponse({'status': 'error', 'message': '密碼錯誤。'}, status=401)
                
                # 更新用戶郵箱
                user.user_email = new_email
                user.updated_at = now()
                user.save()
                                
                # 設置驗證碼為已使用
                verification.code_used = True
                verification.token_used = True
                verification.save()  # 保存到資料庫
                
                return JsonResponse({
                'status': 'success',
                'message': '郵箱修改成功。',
                'redirect_url': f"{settings.FRONTEND_URL}login"
            })
            
            except MemberBasic.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': '用戶不存在，請重新註冊或再次確認信息。',
                    'redirect_url': f"{settings.FRONTEND_URL}signup"
                    }, status=404)
        

        # 如果是 GET 請求，渲染修改郵箱的表單
        if request.method == 'GET':
            return render(request, 'users/email_change_form.html', {
                'user_id': user_id, 
                'code': code, 
                'verification_code': verification.verification_code
                })
        
        # 其他不支持的請求方法
        return JsonResponse({'status': 'error', 'message': '不支援的請求方法。'}, status=405)

    except MemberVerify.DoesNotExist:
        # 當驗證記錄不存在或已被使用
        return JsonResponse({'status': 'error', 'message': '無效的驗證碼。'})
        # return JsonResponse({
        #     'status': 'error',
        #     'message': '無效的驗證連結，請重新申請修改郵箱。',
        #     'redirect_url': f"{settings.FRONTEND_URL}email-change"
        # }, status=404)

# 前台-用戶"修改手機" 1.發送驗證信
def phone_change(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': '無效的 JSON 數據。'}, status=400)
        
        old_phone = data.get('old_phone')
        new_phone = data.get('new_phone')
        email = data.get('email')

        if not old_phone or not new_phone or not email:
            return JsonResponse({'message': '請輸入有效的手機號和郵箱。'}, status=400)
        
        if not MemberBasic.objects.filter(user_phone=old_phone, user_email=email).exists():
            return JsonResponse({'message': '輸入的手機號和郵箱不匹配或不存在。'}, status=400)
        
        # 獲取對應用戶
        member = MemberBasic.objects.get(user_phone=old_phone, user_email=email)
        
        if MemberBasic.objects.filter(user_phone=new_phone).exists():
            return JsonResponse({'message': '新手機號已被使用，請更換手機號。'}, status=400)
        
        # 生成隨機6位數驗證碼
        verification_code = random.randint(100000, 999999)
        
        # 生成驗證連結的token
        verification_token = get_random_string(length=16)
        
        # 保存驗證信息
        MemberVerify.objects.create(
            user=member,
            verification_type='phone_change',
            change_value=new_phone,
            verification_token=verification_token,
            verification_code=verification_code,  # 保存驗證碼
            created_at=now(),
            expires_at=now() + timedelta(hours=24),
            token_used=False,
            code_used=False
        )
        
        # 構建驗證 URL
        # verification_url = f"{settings.FRONTEND_URL}phone-verify/{verification_token}"
        verification_url = request.build_absolute_uri(
            reverse('users_api:phone_change_confirm', args=[verification_token])
        )
        
        # 發送郵件
        subject = '修改手機號碼'
        message = f'請點擊以下連結來修改您的手機號碼：\n\n{verification_url}\n\n如果您沒有請求修改手機號碼，請忽略此郵件。\n\n您的驗證碼是：{verification_code}'
        send_mail(subject, message, 'forworkjayjay@gmail.com', [member.user_email])
        
        return JsonResponse({'message': '驗證信已發送到您的郵箱，請查收。'}, status=200)
        # return JsonResponse({
        #         'status': 'success',
        #         'message': '驗證信已發送到您的郵箱，請查收。',
        #         'redirect_url': f"{settings.FRONTEND_URL}phone-verify/{verification_token}"
        #     })
    
    return JsonResponse({'message': '不支援的請求方法'}, status=405)

# 前台-用戶"修改手機" 2.用戶輸入驗證碼 進入修改手機頁面
def phone_change_confirm(request, token):
    try:
        verification = MemberVerify.objects.get(verification_token=token, token_used=False)
        if now() > verification.expires_at:
            return render(request, 'users/phone_change_confirm.html', {'error': '驗證連結已過期，請重新申請修改手機號碼。'})
        
        if request.method == 'POST':
            data = json.loads(request.body)
            verification_code = data.get('verification_code')  # 接收用戶輸入的驗證碼
            
            # 檢查驗證碼是否正確
            if not verification_code:
                return JsonResponse({'status': 'error', 'message': '驗證碼為必填項。'})
            
            # 檢查驗證碼是否正確
            if verification_code != verification.verification_code:
                return JsonResponse({'status': 'error', 'message': '驗證碼錯誤。'})
            
            # 驗證碼正確，標記驗證成功並返回修改手機頁面的 URL
            verification.token_used = True
            verification.save()

            # 驗證碼正確，返回修改手機的頁面 URL
            return JsonResponse({
                'status': 'success',
                'message': '驗證碼正確，請進入修改手機頁面。',
                'redirect_url': reverse('users_api:phone_change_form', args=[verification.verification_code])  # 返回修改手機的 URL
                # 'redirect_url': f"{settings.FRONTEND_URL}phone-reset"
            })
        return render(request, 'users/phone_change_confirm.html', {'token': token})
    
    except MemberVerify.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '無效的驗證連結。'})

# 前台-用戶"修改手機" 3.更新驗證碼狀態 並於輸入新手機.密碼 更新資料庫
def phone_change_form(request, code):
    try:
        verification = MemberVerify.objects.get(verification_code=code, code_used=False)
        if now() > verification.expires_at:
            return render(request, 'users/phone_change_form.html', {'error': '驗證連結已過期，請重新申請修改手機號碼。'})
        
        if request.method == 'POST':
            data = json.loads(request.body)
            new_phone = data.get('phone')
            password = data.get('password')
            verification_code = data.get('verification_code')  # 接收用戶輸入的驗證碼
            
            # 檢查驗證碼是否正確
            if verification_code != verification.verification_code:
                return JsonResponse({'status': 'error', 'message': '驗證碼錯誤。'})
            
            # 檢查新手機是否正確
            if new_phone != verification.change_value:
                return JsonResponse({'status': 'error', 'message': '新手機與輸入不相符，請再次確認。'})
            
            try:
                user = verification.user
                if not check_password(password, user.user_password):
                    return JsonResponse({'status': 'error', 'message': '密碼錯誤。'})
                
                # 更新用戶手機號碼
                user.user_phone = new_phone
                user.updated_at = now()
                user.save()
                
                # 設置驗證碼為已使用
                verification.code_used = True
                verification.token_used = True
                verification.save()  # 確保保存到資料庫

                return JsonResponse({'status': 'success', 'message': '手機號碼修改成功。'})


            #     return JsonResponse({
            #     'status': 'success',
            #     'message': '手機號碼修改成功。',
            #     'redirect_url': f"{settings.FRONTEND_URL}login"
            # })

            except MemberBasic.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用戶不存在。'})
        
        # 如果是 GET 請求，渲染修改手機的表單
        return render(request, 'users/phone_change_form.html', {'old_phone': verification.user.user_phone, 'code': code, 'verification_code': verification.verification_code})

    except MemberVerify.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '無效的驗證碼。'})