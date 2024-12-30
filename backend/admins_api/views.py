from django.shortcuts import render, redirect
from django.http import JsonResponse
from admins.models import AuthUser
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.cache import cache
import json

# Create your views here.
# 後台-管理者 註冊並存入資料庫
def signup(request):
    if request.method == 'POST':
        auth_username = request.POST.get('auth_username')
        auth_useremail = request.POST.get("auth_useremail")
        password = request.POST.get('password')
        confirm_password = request.POST.get("confirm_password")

        required_fields = [auth_username, auth_useremail, password, confirm_password]
        if any(not field for field in required_fields):
            return JsonResponse({"success": False, "message": "請填寫所有帶有 *必填欄位"}, status=400)

        if AuthUser.objects.filter(superuser_name=auth_username).exists():
            return JsonResponse({"success": False, "message": "姓名已存在，請重新輸入。"}, status=409)

        if AuthUser.objects.filter(superuser_email=auth_useremail).exists():
            return JsonResponse({"success": False, "message": "請重新輸入電子郵箱。"}, status=409)

        if password != confirm_password:
            return JsonResponse({"success": False, "message": "密碼不一致，請重新確認。"}, status=400)
        
        try:
            AuthUser.objects.create(
                superuser_name=auth_username,
                superuser_email=auth_useremail,
                superuser_password=make_password(password),
                created_at=timezone.now(),
            )
            return JsonResponse({'success': True, 'message': '管理者註冊成功！~將於5秒後跳轉登入頁面', 'redirect_url': '/'}, status=201)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"使用者註冊失敗：{str(e)}"}, status=500)
        
    return JsonResponse({"success": False, "message": "不支持的請求方法"}, status=405)



# 後台-管理者 重置密碼並更新於資料庫
def reset(request):
    if request.method == "POST":
        try:
            body_data = json.loads(request.body)
            new_password = body_data.get('password')
            confirm_password = body_data.get('password1')
            email = body_data.get('email')

            if new_password != confirm_password:
                return JsonResponse({"status": "error", "message": "密碼不一致，請重新輸入。"})
            
            authUser = AuthUser.objects.get(superuser_email=email)
            authUser.superuser_password = make_password(confirm_password)
            authUser.save()

            return JsonResponse({"status": "success", "message": "密碼更新完成，請使用新密碼登入。如3秒後沒有跳轉，請手動登入。"})

        except AuthUser.DoesNotExist:
            return JsonResponse({"status": "error", "message": "找不到用戶！"})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "無效的 JSON 數據。"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "不支持的請求方法"}, status=405)