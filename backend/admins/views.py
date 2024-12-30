from django.shortcuts import render, redirect
from admins.models import AuthUser
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.cache import cache

# Create your views here.
# 後台-管理者 "註冊"並存入資料庫
def signup(request):
    return render(request, 'admins/signup.html', {"title": "管理者註冊頁面"})

# 後台-管理者 "重置密碼"並更新於資料庫
def reset(request):
    return render(request, 'admins/reset.html', {"title": "管理者重置密碼"})


# 後台-管理者 登入
def login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        remember_me = request.POST.get("remember_me")

        # 驗證用戶
        auth = AuthUser.objects.filter(superuser_name=name).first()
        if auth:

            # 檢查密碼是否已經哈希
            if auth.superuser_password.startswith('pbkdf2_sha256$') or auth.superuser_password.startswith('bcrypt$'):
                password_valid = check_password(password, auth.superuser_password)
            else:
                password_valid = (password == auth.superuser_password)

            if password_valid:
                # 後台登入成功
                # 生成一個唯一的session key
                session_key = f"user_session_{auth.superuser_id}"  # 管理者ID當作session key

                # 暫存用戶信息，有效期30分鐘
                cache.set(session_key, auth.superuser_id, 30 * 60)

                response = redirect('admins:index')

                # 設置cookie，包含session key
                if remember_me == "on":
                    max_age = 24 * 60 * 60  # 保留1天
                    response.set_cookie('user_session', session_key, max_age=max_age)
                else:
                    response.set_cookie('user_session', session_key)

                print(f"Login successful for user: {auth.superuser_id}")
                return response
            else:
                messages.error(request, "密碼錯誤，請重新輸入。")
        else:
            messages.error(request, "用戶信息未找到，請再次檢查或註冊新帳號。")

        return render(request, "admins/login.html", {"name": name})
        # return redirect('admins:login')

    return render(request, "admins/login.html")

# 後台-管理者 登出 OK 但sesion沒清除 x
def logout(request):
    # 獲取 session key
    session_key = request.COOKIES.get('user_session')
    
    # 清除緩存中的用户信息
    if session_key:
        cache.delete(session_key)
    
    # 清除 session 中的數據
    request.session.flush()

    # 創建響應對象
    response = redirect('admins:login')
    
    # 清除 cookie 中的數據
    response.delete_cookie("user_session")
    response.delete_cookie("superuser_email")
    response.delete_cookie("remember_me")

    messages.success(request, "您已成功登出。")
    
    return response

# 檢查用戶是否已登入
def check_auth(request):
    session_key = request.COOKIES.get('user_session')
    if session_key:
        superuser_id = cache.get(session_key)
        if superuser_id:
            # 用戶已登入
            return True
    return False

# 後台-管理者登入後的頁面
def index(request):
    if not check_auth(request):
        messages.warning(request, "您尚未登入或登入已過期，請重新登入。")
        return redirect('admins:login')
    
    # 獲取用戶信息
    session_key = request.COOKIES.get('user_session')
    print(f"Session Key: {session_key}")  # 新增調試信息
    superuser_id = cache.get(session_key)
    print(f"Superuser ID: {superuser_id}")  # 調試信息
    auth = AuthUser.objects.get(superuser_id=superuser_id)

    # 確保 auth 不為 None
    if auth is None:
        messages.warning(request, "用戶信息未找到，請重新登入。")
        return redirect('admins:login')
    
    # 傳遞用戶信息到前端
    return render(request, 'admins/index.html', {"auth": auth})