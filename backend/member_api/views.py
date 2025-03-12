from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import MemberBasic,  MemberIndextype, MemberLogin, MemberPhotos, MemberPrivacy, MemberVerify
from cart.models import Orders
from member_api.models import Usercoupons
from .serializers import MemberSerializer, LoginSerializer, OrderdetailsSerializer, RegisterSerializer, PrivacySerializer, VerifySerializer, ThirdLoginSerializer, MemberIndextypeSerializer, EmptySerializer
from django.http import HttpResponseRedirect
import os
import random
from django.conf import settings
from django.utils.timezone import now, timedelta
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.mail import send_mail
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.db import transaction
import requests
import requests.exceptions 
import hashlib

# Create your views here.
# 自訂 Token 驗證方法!!
def verify_jwt_token(request):
    """
    驗證 JWT Token 的有效性，包括檢查過期時間。
    """
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationFailed("缺少或無效的 Authorization 標頭")

    token = auth_header.split(' ')[1]  # 提取 Token

    try:
        # 驗證並解析 Token
        decoded_token = AccessToken(token)
        return decoded_token
    except TokenError as e:
        # 檢查是否為 Token 過期錯誤或其他錯誤
        if 'token_not_valid' in str(e):
            raise AuthenticationFailed("Token 已過期，請重新登入")
        raise AuthenticationFailed(f"無效的 Token: {str(e)}")
    
class MemberViewSet(viewsets.ModelViewSet):
    queryset = MemberBasic.objects.all()
    serializer_class = MemberSerializer

    def retrieve(self, request, pk=None):
        try:
            # 驗證 Token
            decoded_token = verify_jwt_token(request)
            print(f"Decoded Token: {decoded_token}")

            # 解析 Token 中的用戶 ID
            user_id = decoded_token.get('user_id', None)
            if not user_id:
                raise AuthenticationFailed("Token 中缺少用戶 ID")

            # 根據主鍵 ID 查找會員資料
            user = MemberBasic.objects.get(user_id=pk)
            if user.user_id != user_id:
                raise AuthenticationFailed("無權限查看該用戶的資料")
            
            # 使用序列化器將會員資料轉換為 JSON 格式
            serializer = self.get_serializer(user)
            print(f"User: {serializer.data}")
            print(f"Authorization Header: {request.headers.get('Authorization')}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MemberBasic.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except AuthenticationFailed as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class PrivacyViewSet(viewsets.ModelViewSet):
    queryset = MemberPrivacy.objects.all()
    serializer_class = PrivacySerializer

class VerifyViewSet(viewsets.ModelViewSet):
    queryset = MemberVerify.objects.all()
    serializer_class = VerifySerializer

class ThirdLoginViewSet(viewsets.ModelViewSet):
    queryset = MemberLogin.objects.all()
    serializer_class = ThirdLoginSerializer

class OrderdetailsViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderdetailsSerializer

class ProtectedRouteView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        token = request.data.get('token')  # 或者 headers.get 或 GET.get
        print(f"Received token: {token}")
        if not token:
            return Response({"detail": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 驗證 Token
            decoded_token = verify_jwt_token(request)
            print(f"User ID from Token: {decoded_token['user_id']}")
            return Response({"message": "您已成功驗證 Token！"}, status=status.HTTP_200_OK)
        
        except AuthenticationFailed as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


# 會員登入 與 註冊
class AuthViewSet(viewsets.GenericViewSet):
    queryset = MemberBasic.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=['POST'], serializer_class=LoginSerializer)
    def login(self, request):
        print("Received data:", request.data)  # 打印請求資料，確認請求參數是否正確
        email = request.data.get("user_email")
        password = request.data.get("user_password")
        remember_me = request.data.get("remember_me", False)

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
                try:
                    # 生成 JWT Token
                    refresh = RefreshToken.for_user(member)
                    tokens = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                    print(f"Generated Tokens: {tokens}")  # 打印 tokens

                    # 處理 session 和 cookie
                    session_key = f"user_session_{member.user_id}"
                    # 暫存用戶信息，有效期30分鐘
                    cache.set(session_key, member.user_id, 30 * 60)  # 30分鐘

                    # 準備響應
                    response_data = {
                        'message': '登入成功',
                        'user': MemberSerializer(member).data,
                        'tokens': tokens  # 添加 tokens 到返回數據中
                    }
                    print(f"Response Data: {response_data}")

                    # 如果選擇記住我
                    response = Response(response_data, status=status.HTTP_200_OK)
                    if remember_me:
                        max_age = 30 * 24 * 60 * 60  # 30天
                        response.set_cookie('user_session', session_key, max_age=max_age)
                    else:
                        response.set_cookie('user_session', session_key)

                    return response
                
                except Exception as e:
                    return Response({
                        'error': f'Token生成失敗: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            else:
                return Response({
                    'error': '帳號或密碼錯誤'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'error': '該郵箱未註冊，請再次確認郵箱或註冊新帳號。'
            }, status=status.HTTP_401_UNAUTHORIZED)
                
    # 註冊 1. 送出註冊
    @action(detail=False, methods=['POST'], serializer_class=RegisterSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)  # 驗證數據

            with transaction.atomic():  # 開啟數據庫事務

                user = serializer.save()

                # 自動生成 Token
                refresh = RefreshToken.for_user(user)

                # 創建 MemberPrivacy 記錄
                MemberPrivacy.objects.create(
                    user=user,
                    created_at=now(),
                    account_verify=False,  # 預設帳號未驗證
                    email_verified=False  # 預設郵箱未驗證
                )

                # 生成驗證碼並創建 MemberVerify
                verification_token = get_random_string(16)  # 生成隨機驗證碼
                try:
                    MemberVerify.objects.create(
                        user=user,
                        change_value=user.user_email,  # 記錄用戶註冊時使用的郵箱
                        verification_token=verification_token,
                        verification_type='registration',
                        created_at=now(),
                        expires_at=now() + timedelta(days=1),  # 設置驗證碼過期時間
                        token_used=False  # 初始設定為未使用
                    )

                    # 構建驗證連結
                    verification_url = request.build_absolute_uri(
                        reverse('member_api:verify_email', args=[verification_token])
                    )

                    # 發送驗證郵件
                    send_mail(
                        subject='驗證您的帳號',
                        message=f'請點擊以下連結驗證您的帳號：{verification_url}',
                        from_email='forworkjayjay@gmail.com',
                        recipient_list=[user.user_email],
                        fail_silently=False,
                    )

                except Exception as e:
                    return Response({
                        'error': f'創建驗證記錄或發送郵件失敗: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': '註冊成功，系統將發送驗證信以啟動帳號。請您留意查收',
                'user': MemberSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("註冊錯誤:", serializer.errors)  # 打印序列化錯誤
            return Response({
                'error': str(e)  # 返回錯誤訊息
            }, status=status.HTTP_400_BAD_REQUEST)

    # 刷新 Token
    @action(detail=False, methods=['POST'], serializer_class=EmptySerializer)
    def refresh_token(self, request):
        refresh_token = request.data.get('refresh')
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response({
                'access': access_token
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': '無效的刷新令牌'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
# 註冊 2. 發送帳號驗證信 並跳轉到登入頁面
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            # 驗證碼查詢
            verification = MemberVerify.objects.filter(verification_token=token, token_used=False).first()
            if not verification:
                print("Invalid or used token:", token)
                return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=invalid")

            # 驗證碼過期檢查
            if now() > verification.expires_at:
                print("Token expired. Expires at:", verification.expires_at)
                return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=expired")

            # 更新用戶隱私資料並標記驗證碼已使用
            member = verification.user
            member_privacy = MemberPrivacy.objects.filter(user=member).first()
            if not member_privacy:
                print("Member privacy not found for user:", member)
                return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=error")
            
            member_privacy.account_verify = True
            member_privacy.email_verified = True
            member_privacy.updated_at = now()
            member_privacy.save()

            verification.token_used = True
            verification.save()

            # 重定向到前端驗證成功頁面
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=success")

        except Exception as e:
            print("Error during verification:", str(e))
            return Response({"message": "驗證失敗", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 第三方串接登入-Line
class LineLoginView(APIView):
    def post(self, request):
        """
        處理 LINE Login 回應，交換 Access Token 並取得用戶資訊。
        """
        # 從請求中獲取授權碼
        code = request.data.get("code")
        state = request.data.get("state")
        print("接收到的 code state :", code, state)  # 日誌

        if not code or not state:
            return Response(
                {"error": "缺少授權碼或狀態參數"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 用於交換 Access Token 的 LINE API URL
        token_url = "https://api.line.me/oauth2/v2.1/token"

        try:
            # 使用授權碼交換 Access Token
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINE_REDIRECT_URI,
                "client_id": settings.LINE_CLIENT_ID,
                "client_secret": settings.LINE_CLIENT_SECRET,
            }
            token_response = requests.post(
                token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if token_response.status_code != 200:
                return Response(
                    {"error": f"無法交換 Access Token: {token_response.json().get('error_description')}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token_info = token_response.json()
            access_token = token_info.get("access_token")
            id_token = token_info.get("id_token")
            print("獲取的 Token_info:", token_info)

            if not access_token:
                return Response(
                    {"error": "無法獲取 Access Token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


            # 用於交換 ID Token 的 LINE API URL
            verify_idtoken = "https://api.line.me/oauth2/v2.1/verify"

            # 使用授權碼交換 Access Token
            id_data = {
                "id_token": id_token,
                "client_id": settings.LINE_CLIENT_ID,
            }
            id_response = requests.post(
                verify_idtoken,
                data=id_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print("ID Token 請求內容:", id_response.text)
            if id_response.status_code != 200:
                return Response(
                    {"error": f"無法驗證 ID Token: {id_response.json().get('error_description')}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            id_info = id_response.json()
            email = id_info.get("email")
            if not email:
                return Response(
                    {"error": "無法獲取用戶 Email，請確認 LINE 應用是否啟用了 Email 權限"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 使用 Access Token 獲取用戶資訊
            profile_url = "https://api.line.me/v2/profile"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_url, headers=headers)

            if profile_response.status_code != 200:
                return Response(
                    {"error": "無法獲取用戶資訊"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            profile_info = profile_response.json()
            line_user_id = profile_info.get("userId")
            display_name = profile_info.get("displayName")
            picture_url = profile_info.get("pictureUrl")

            if not line_user_id or not display_name or not picture_url:
                return Response(
                    {"error": "無法獲取完整的用戶資訊"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 將 access_token 進行哈希處理
            hashed_access_token = hashlib.sha256(access_token.encode()).hexdigest()

            # 將 line_password line_phone 進行隨機處理
            line_password = make_password(get_random_string(8))
            line_phone = "09" + str(random.randint(10000000, 99999999))

            # 開始資料庫事務
            with transaction.atomic():
                # 查找或創建會員資料
                user, created = MemberBasic.objects.get_or_create(
                    user_email=email,
                    defaults={
                        "user_name": display_name,
                        "user_avatar": picture_url,
                        "vip_status": "0",
                        "user_password": line_password,
                        "user_phone": line_phone,
                        "user_gender": "prefer_not_to_say",
                        "created_at": now(),
                    },
                )

                # 如果是現有用戶，更新資料
                if not created:
                    user.user_name = display_name
                    user.user_avatar = picture_url
                    user.updated_at = now()
                    user.save()

                # 更新 MemberLogin 資料
                MemberLogin.objects.update_or_create(
                    user=user,  # 根據 user 關聯檢查
                    provider="Line",
                    defaults={
                        "line_user_id": line_user_id,
                        "access_token": hashed_access_token,
                        "created_at": now(),
                        "updated_at": now()
                    },
                )

                # 更新 MemberPrivacy 資料
                MemberPrivacy.objects.update_or_create(
                    user=user,  # 根據 user 關聯檢查
                    defaults={
                        "email_verified": 1,
                        "account_verify": 1,
                        "created_at": now(),
                        "updated_at": now()
                    },
                )

            # 返回用戶資料及登入 Token
            serializer = MemberSerializer(user)

            # 生成 JWT Token
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            return Response(
                {
                    "user": serializer.data,
                    "tokens": tokens,
                },
                status=status.HTTP_200_OK,
            )

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"LINE API 通訊錯誤: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"伺服器錯誤: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# 更新 前台會員中心資料
class UpdateUserInfoView(APIView):

    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            # 驗證 JWT Token
            decoded_token = verify_jwt_token(request)
            print(f"Decoded Token: {decoded_token}")

            # 從 Token 中獲取用戶 ID 並檢查是否與請求的用戶一致
            token_user_id = decoded_token.get("user_id", None)
            if not token_user_id or str(token_user_id) != str(pk):
                return Response(
                    {"error": "無權限操作其他用戶的數據"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # 根據主鍵 ID 查找會員資料
            user = MemberBasic.objects.get(user_id=pk)

            # 更新用戶其他資料
            user.user_email = request.data.get("user_email", user.user_email)
            user.user_nickname = request.data.get("user_nickname", user.user_nickname)
            user.user_gender = request.data.get("user_gender", user.user_gender)
            user.updated_at = now()  # 自動生成 updated_at

            # 確認並處理生日數據
            user_birth = request.data.get("user_birth", None)
            if user_birth:
                # 確保生日數據格式正確
                try:
                    user.user_birth = datetime.strptime(user_birth, "%Y-%m-%d").date()
                except ValueError:
                    return Response(
                        {"error": "生日格式無效，必须为 YYYY-MM-DD 格式。"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                # 如果沒設定生日，預設為 None
                user.user_birth = None


            # 更新頭像
            user_avatar = request.FILES.get("user_avatar", None)

            if user_avatar:
                user.user_avatar = user_avatar
            else:
                # 如果未上傳圖片，設置默認圖片（注意，這僅適用於模型已支持默認圖片的情況）
                user.user_avatar = 'avatars/default.jpg'

            # 更新性別
            allowed_genders = ['male', 'female', 'prefer_not_to_say']
            user_gender = request.data.get('user_gender')

            if user_gender not in allowed_genders:
                return Response(
                    {"error": "Invalid gender value. Allowed values are: 'male', 'female', 'prefer_not_to_say'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.user_gender = user_gender

            user.save()  # 保存用户數據

            # 刪除同一用戶的重複 MemberPhoto 紀錄，只保留最新的一條
            member_photos = MemberPhotos.objects.filter(user=user)
            if member_photos.exists():
                member_photos.exclude(pk=member_photos.first().pk).delete()  # 只保留一條紀錄，刪除其他紀錄

            # 更新 MemberPhoto 資料
            MemberPhotos.objects.update_or_create (
                user=user,  # 根據 user 關聯檢查
                defaults={
                    # "photo_url": user.user_avatar.url if user.user_avatar else None,
                    "photo_url": user.user_avatar.url if user.user_avatar and user.user_avatar.name else None,
                    "updated_at" : now()
                },
            )
            return Response(
                {"message": "更新成功",},
                status=status.HTTP_200_OK,
            )
        except MemberBasic.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        except AuthenticationFailed as e:  # 處理驗證失敗的異常
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 更新 前台會員進階設定資料
class UpdateUserLikesView(APIView):
    def get(self, request, pk):
        try:
            # 驗證 JWT Token
            decoded_token = verify_jwt_token(request)

            # 檢查 Token 中的 user_id 是否匹配
            if str(decoded_token["user_id"]) != str(pk):
                return Response({"error": "用戶 ID 與 Token 不匹配"}, status=status.HTTP_403_FORBIDDEN)

            # 獲取用戶
            user = MemberBasic.objects.get(user_id=pk)

            # 獲取並排序用戶喜好資料
            personal_likes = MemberIndextype.objects.filter(user=user).order_by('sort_order')  # 使用模型進行查詢

            # 使用序列化器格式化數據
            personal_likes_data = MemberIndextypeSerializer(personal_likes, many=True).data
            
            return Response({
                "user_id": user.user_id,
                "personal_likes": personal_likes_data
            }, status=status.HTTP_200_OK)

        except MemberBasic.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        try:
            # 手動驗證 JWT Token
            decoded_token = verify_jwt_token(request)

            # 檢查 Token 中的 user_id 是否匹配
            if str(decoded_token["user_id"]) != str(pk):
                return Response({"error": "用戶 ID 與 Token 不匹配"}, status=status.HTTP_403_FORBIDDEN)
            
            # 獲取用戶
            user = MemberBasic.objects.get(user_id=pk)
            
            # 獲取請求數據
            personal_likes = request.data.get("personal_likes", [])
            user_address = request.data.get("user_address")  # 獲取新地址
            
            # 使用事務確保數據一致性
            with transaction.atomic():
                # 更新地址
                if user_address is not None:
                    user.user_address = user_address
                    user.save()

                # 處理個人喜好數據
                MemberIndextype.objects.filter(user=user).delete()
                for item in personal_likes:
                    if isinstance(item, dict) and 'type_name' in item and 'sort_order' in item:
                        MemberIndextype.objects.create(
                            user=user,
                            type_name=item['type_name'],
                            sort_order=item['sort_order'],
                            created_at=now(),
                            updated_at=now()
                        )

            # 查詢並返回更新後的數據
            updated_likes = MemberIndextype.objects.filter(user=user).order_by('sort_order')
            updated_likes_data = MemberIndextypeSerializer(updated_likes, many=True).data

            return Response({
                "user_id": user.user_id,
                "personal_likes": updated_likes_data,
                "user_address": user.user_address,  # 返回更新後的地址
                "message": "資料更新成功"
            }, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except MemberBasic.DoesNotExist:
            return Response({"error": "用戶不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 會員忘記密碼 1. 發送驗證信
class SendResetLinkView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "不支持的請求方法，請使用 POST"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def post(self, request):
        try:
            # 驗證 JWT Token，檢查用戶是否已登入
            try:
                decoded_token = verify_jwt_token(request)
                print(f"Decoded Token: {decoded_token}")
                # 如果登入，用戶 ID 直接從 Token 提取
                user_id = decoded_token.get("user_id")
                user = MemberBasic.objects.filter(user_id=user_id).first()
                if not user:
                    return Response(
                        {"message": "無效的用戶，請重新登入"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                # 直接使用用戶的電子郵件
                email = user.user_email
                print(f"User is logged in, using email: {email}")

            except AuthenticationFailed:
                # 未登入，檢查請求中是否提供了電子郵箱
                email = request.data.get("user_email")
                if not email:
                    return Response(
                        {"message": "請提供有效的電子郵箱"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user = MemberBasic.objects.filter(user_email=email).first()
                print(f"User is not logged in, email provided: {email}")

            # 檢查是否存在未使用的相同請求
            existing_request = MemberVerify.objects.filter(
                user=user,
                verification_type='phone_change',
                change_value=email,
                code_used=False,
                expires_at__gte=now()
            ).first()

            if existing_request:
                return Response({'message': '已存在待處理的密碼重置請求，請勿重複提交'}, status=400)
        
            if user:
                # 生成6位數驗證碼並創建新的驗證記錄
                code = random.randint(100000, 999999)
                MemberVerify.objects.create(
                    user=user,
                    verification_type='password_change',
                    verification_code=code,
                    change_value=email,  # 記錄用戶請求重置密碼時使用的郵箱
                    code_used=False,
                    created_at=now(),
                    expires_at=now() + timedelta(days=1),   # 設置驗證碼過期時間
                )

                # 構建驗證連結
                reset_link = request.build_absolute_uri(
                    reverse('member_api:reset_password', args=[code])
                )
                print(f"Generated reset link: {reset_link}")

                # 發送驗證郵件
                send_mail(
                    subject='密碼重置請求',
                    message=f'請您點擊以下連結進行密碼重置：{reset_link}',
                    from_email='forworkjayjay@gmail.com',
                    recipient_list=[user.user_email],
                    fail_silently=False,
                )

            return Response(
                {"message": "如果電子郵箱存在，我們會發送重置連結~!"},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# 會員忘記密碼 2. 按下驗證連結後跳轉重置密碼
class ResetPasswordView(APIView):
    def get(self, request, code):
        # 驗證碼查詢邏輯
        verify_code = MemberVerify.objects.filter(verification_code=code, code_used=False).first()
        if not verify_code :
            # 無效的驗證碼，重定向到前端
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}reset-verify/{code}?status=invalid")
        
        # 驗證碼過期檢查
        if now() > verify_code.expires_at:
                # 驗證碼已過期，重定向到前端
                return HttpResponseRedirect(f"{settings.FRONTEND_URL}reset-verify/{code}?status=expired")

        # 成功狀態
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}reset-verify/{code}?status=success")
    
    def post(self, request, code):
        new_password = request.data.get("new_password")
        verify_code = MemberVerify.objects.filter(verification_code=code, code_used=False).first()

        if not verify_code:
            return Response({"message": "無效的驗證碼"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = verify_code.user

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 更新密碼
        user.user_password = make_password(new_password)
        user.updated_at = now()
        user.save()

        # 標記驗證碼為已使用
        verify_code.code_used = True
        verify_code.save()

        # 密碼重置成功，重定向到前端登入頁面
        return Response({"message": "密碼已成功重置，請重新登入"}, status=status.HTTP_200_OK)

# 會員欲修改手機 1. 發送驗證信
class SendPhoneLinkView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "不支持的請求方法，請使用 POST"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    def post(self, request):
        # 驗證 JWT Token
        decoded_token = verify_jwt_token(request)  # 解碼 JWT Token
        print(f"手機驗證Token: {decoded_token}")

        if decoded_token:  # 如果用戶已登入
            user_id = decoded_token.get('user_id')
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({"message": "無效的用戶，請重新登入。"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 從用戶資料中獲取 email 和 oldphone
            email = user.user_email
            oldphone = user.user_phone

            # 僅需要用戶提供新手機號
            newphone = request.data.get("new_phone")
            if not newphone:
                return Response({"message": "請提供新手機號。"}, status=status.HTTP_400_BAD_REQUEST)
            

            
        else:  # 如果用戶未登入
            email = request.data.get("user_email")
            oldphone = request.data.get("user_phone")
            newphone = request.data.get("new_phone")

            if not oldphone or not newphone or not email:
                return Response({"message": "請輸入有效的手機號和郵箱。"}, status=status.HTTP_400_BAD_REQUEST)

            if not MemberBasic.objects.filter(user_phone=oldphone, user_email=email).exists():
                return Response({'message': '輸入的手機號和郵箱不匹配或不存在。'}, status=400)

            user = MemberBasic.objects.get(user_phone=oldphone, user_email=email)

        # 檢查新手機號是否已被使用
        if MemberBasic.objects.filter(user_phone=newphone).exists():
            return Response({'message': '新手機號已被使用，請更換手機號。'}, status=400)
            

        # 檢查是否存在未使用的相同請求
        existing_request = MemberVerify.objects.filter(
            user=user,
            verification_type='phone_change',
            change_value=newphone,
            code_used=False,
            expires_at__gte=now()
        ).first()

        if existing_request:
            return Response({'message': '已存在待驗證的修改手機號請求，請勿重複提交'}, status=400)

        if user:
             # 生成6位數驗證碼並創建新的驗證記錄
            code = random.randint(100000, 999999)
            MemberVerify.objects.create(
                user=user,
                verification_type='phone_change',
                verification_code=code,
                change_value=newphone,  # 記錄用戶請求修改手機時輸入的新手機號
                code_used=False,
                created_at=now(),
                expires_at=now() + timedelta(days=1),   # 設置驗證碼過期時間
            )

            # 構建驗證連結
            reset_link = request.build_absolute_uri(
                reverse('member_api:reset_phone', args=[code])
            )
            print(f"Generated reset link: {reset_link}")

            # 發送驗證郵件
            send_mail(
                subject='請求修改手機號',
                message=f'請您點擊以下連結進行操作修改手機號：{reset_link}',
                from_email='forworkjayjay@gmail.com',
                recipient_list=[user.user_email],
                fail_silently=False,
            )

        return Response(
            {"message": "如果電子郵箱存在，您將會收到修改手機號連結~!"},
            status=status.HTTP_200_OK
        )
    
# 會員欲修改手機 2. 按下驗證連結後跳轉修改手機
class ResetPhoneView(APIView):
    def get(self, request, code):
        # 驗證碼查詢邏輯
        verify_code = MemberVerify.objects.filter(verification_code=code, code_used=False).first()
        if not verify_code :
            # 無效的驗證碼，重定向到前端
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}phone-verify/{code}?status=invalid")
        
        # 驗證碼過期檢查
        if now() > verify_code.expires_at:
                # 驗證碼已過期，重定向到前端
                return HttpResponseRedirect(f"{settings.FRONTEND_URL}phone-verify/{code}?status=expired")

        # 成功狀態
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}phone-verify/{code}?status=success")
     
    def post(self, request, code):
        new_phone = request.data.get("new_phone")
        verify_code = MemberVerify.objects.filter(verification_code=code, code_used=False).first()

        if not verify_code:
            return Response({"message": "無效的驗證碼"}, status=status.HTTP_400_BAD_REQUEST)
        
        if verify_code.change_value != new_phone:
            return Response({'message': '新手機號與記錄不匹配。'}, status=400)
        
        if MemberBasic.objects.filter(user_phone=new_phone).exists():
            return Response({'message': '該手機號已被註冊使用。'}, status=400)
        
        user = verify_code.user

        # 更新手機號
        user.user_phone = new_phone
        user.updated_at = now()
        user.save()

        # 標記驗證碼為已使用
        verify_code.code_used = True
        verify_code.save()

        # 手機號修改成功，重定向到前端登入頁面
        return Response({"message": "手機號已成功修改，請重新登入"}, status=status.HTTP_200_OK)

# 會員欲修改郵箱 1. 發送驗證信
class SendEmailLinkView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "不支持的請求方法，請使用 POST"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def post(self, request):
        # 驗證 JWT Token
        decoded_token = verify_jwt_token(request)  # 解碼 JWT Token
        print(f"郵箱驗證Token: {decoded_token}")

        if decoded_token:  # 如果用戶已登入
            user_id = decoded_token.get('user_id')
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({"message": "無效的用戶，請重新登入。"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 從用戶資料中獲取 email 和 oldphone
            email = user.user_email

            # 僅需要用戶提供新手機號
            newemail = request.data.get("new_email")
            if not newemail:
                return Response({"message": "請提供新郵箱。"}, status=status.HTTP_400_BAD_REQUEST)
            

            
        else:  # 如果用戶未登入
            email = request.data.get("user_email")
            newemail = request.data.get("new_email")

            if not email or not newemail :
                return Response({"message": "請提供有效的電子郵箱。"}, status=status.HTTP_400_BAD_REQUEST)
            
            if MemberBasic.objects.filter(user_email=newemail).exists():
                return Response({'message': '該電子郵箱地址已被使用。'}, status=400)

            # 獲取對應用戶
            user = MemberBasic.objects.filter(user_email=email).first()
    

        # 檢查是否存在未使用的相同請求
        existing_request = MemberVerify.objects.filter(
            user=user,
            verification_type='email_change',
            change_value=newemail,
            code_used=False,
            expires_at__gte=now()
        ).first()

        if existing_request:
            return Response({'message': '已存在待驗證的修改郵箱請求，請勿重複提交'}, status=400)
        
        if user:
             # 生成6位數驗證碼並創建新的驗證記錄
            code = random.randint(100000, 999999)
            verification = MemberVerify.objects.create(
                user=user,
                verification_type='email_change',
                verification_code=code,
                change_value=newemail,  # 記錄用戶請求修改郵箱時輸入的新郵箱
                code_used=False,
                created_at=now(),
                expires_at=now() + timedelta(days=1),   # 設置驗證碼過期時間
            )

            # 構建驗證連結
            reset_link = request.build_absolute_uri(
                reverse('member_api:reset_email', args=[code])
            )
            print(f"Generated reset link: {reset_link}")

            # 發送驗證郵件
            send_mail(
                subject='請求修改電子郵箱',
                message=f'請您點擊以下連結進行操作修改電子郵箱：{reset_link}',
                from_email='forworkjayjay@gmail.com',
                recipient_list=[verification.change_value],
                fail_silently=False,
            )

        return Response(
            {"message": "如果新郵箱存在，您將會收到修改連接~!"},
            status=status.HTTP_200_OK
        )
    
# 會員欲修改郵箱2. 按下驗證連結後跳轉修改郵箱
class ResetEmailView(APIView):
    def get(self, request, code):
        # 驗證碼查詢邏輯
        verify_code = MemberVerify.objects.filter(verification_code=code, code_used=False).first()
        if not verify_code :
            # 無效的驗證碼，重定向到前端
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}email-verify/{code}?status=invalid")
        
        # 驗證碼過期檢查
        if now() > verify_code.expires_at:
                # 驗證碼已過期，重定向到前端
                return HttpResponseRedirect(f"{settings.FRONTEND_URL}email-verify/{code}?status=expired")

        # 成功狀態
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}email-verify/{code}?status=success")
    
    def post(self, request, code):
        new_email = request.data.get("new_email")
        verify_code = MemberVerify.objects.filter(verification_code=code, code_used=False).first()

        if not verify_code:
            return Response({"message": "無效的驗證碼"}, status=status.HTTP_400_BAD_REQUEST)
        
        if verify_code.change_value != new_email:
            return Response({'message': '新郵箱與記錄不匹配。'}, status=400)
        
        if MemberBasic.objects.filter(user_email=new_email).exists():
            return Response({'message': '該電子郵箱地址已被使用。'}, status=400)

        user = verify_code.user
        # 更新郵箱
        user.user_email = new_email
        user.updated_at = now()
        user.save()

        # 標記驗證碼為已使用
        verify_code.code_used = True
        verify_code.save()

        # 郵箱修改成功，重定向到前端登入頁面
        return Response({"message": "郵箱已成功修改，請重新登入"}, status=status.HTTP_200_OK)