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
from promotions.models import Coupons
from cart.models import Orders
from .serializers import MemberSerializer, FavoriteSerializer, LoginSerializer, CouponSerializer, LoginSerializer, OrderdetailsSerializer, PhotoSerializer, RegisterSerializer, PrivacySerializer, VerifySerializer, ThirdLoginSerializer
from django.http import HttpResponseRedirect
import os
import random
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now, timedelta
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.mail import send_mail
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# Create your views here.
class MemberViewSet(viewsets.ModelViewSet):
    queryset = MemberBasic.objects.all()
    serializer_class = MemberSerializer

    def retrieve(self, request, pk=None):
        try:
            # 根據主鍵 ID 查找會員資料
            user = MemberBasic.objects.get(pk=pk)
            
            # 使用序列化器將會員資料轉換為 JSON 格式
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MemberBasic.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = MemberIndextype.objects.all()
    serializer_class = FavoriteSerializer

class PrivacyViewSet(viewsets.ModelViewSet):
    queryset = MemberPrivacy.objects.all()
    serializer_class = PrivacySerializer

class VerifyViewSet(viewsets.ModelViewSet):
    queryset = MemberVerify.objects.all()
    serializer_class = VerifySerializer

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupons.objects.all()
    serializer_class = CouponSerializer

class ThirdLoginViewSet(viewsets.ModelViewSet):
    queryset = MemberLogin.objects.all()
    serializer_class = ThirdLoginSerializer

class OrderdetailsViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderdetailsSerializer

class ProtectedRouteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Token 是有效的！"})


# 會員登入 與 註冊
class AuthViewSet(viewsets.GenericViewSet):
    queryset = MemberBasic.objects.all()
    permission_classes = [AllowAny]

    # 登入!!!
    @action(detail=False, methods=['POST'], serializer_class=LoginSerializer)
    def login(self, request):
        print("Received data:", request.data)    #  打印請求資料，確認請求參數是否正確
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
                # 登入成功
                try:
                    # 生成 JWT Token
                    refresh = RefreshToken.for_user(member)
                    tokens = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }

                    # 處理 session 和 cookie
                    session_key = f"user_session_{member.user_id}"
                    # 暫存用戶信息，有效期30分鐘
                    cache.set(session_key, member.user_id, 30 * 60)  # 30分鐘

                    # 準備響應
                    response_data = {
                        'message': '登入成功',
                        'user': MemberSerializer(member).data,
                        # 'tokens': tokens
                    }

                    # 如果選擇記住我
                    if remember_me :
                        # 設置長期 cookie
                        response = Response(response_data, status=status.HTTP_200_OK)
                        max_age = 30 * 24 * 60 * 60  # 30天
                        response.set_cookie('user_session', session_key, max_age=max_age)
                        return response
                    else:
                        # 設置臨時 cookie
                        response = Response(response_data, status=status.HTTP_200_OK)
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
            user = serializer.save()

            # 自動生成 Token
            refresh = RefreshToken.for_user(user)

            # 創建 MemberPrivacy 記錄
            MemberPrivacy.objects.create(
                user=user,
                created_at=now(),
                account_verify=False  # 預設帳號未驗證
            )

            # 生成驗證碼並創建 MemberVerify
            verification_token = get_random_string(16)  # 生成隨機驗證碼
            try:
                MemberVerify.objects.create(
                    user=user,
                    change_value=None,  # 如果不需要修改，可以設為 None
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
    @action(detail=False, methods=['POST'])
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
        
    # 更新 前台會員資料和喜好
    @action(detail=False, methods=['POST'], serializer_class=MemberSerializer, permission_classes=[AllowAny])
    def update_info(self, request):
        print("当前用户:", request.user)  # 打印当前用户信息
        user_id = request.data.get("user_id")  # 从请求中获取用户ID
        user = MemberBasic.objects.filter(user_id=user_id).first()  # 根据用户ID查找用户

        if not user:
            return Response({"error": "用户未找到"}, status=status.HTTP_404_NOT_FOUND)

        # 更新用户信息
        serializer = self.get_serializer(user, data=request.data, partial=True)  # 允许部分更新
        if serializer.is_valid():
            serializer.save()  # 保存更新
            
            # 处理会员喜好更新
            personal_like_data = request.data.get("personal_like", [])  # 从请求中获取personal_like 数据
            user.personal_like_set.all().delete()  # 清空現有數據

            for like in personal_like_data:
                favorite_serializer = FavoriteSerializer(data=like)
                if favorite_serializer.is_valid():
                    favorite_serializer.save(user=user)  # 联当前用户
                else:
                    return Response({
                        'error': favorite_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'message': '會員資料和喜好更新成功',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
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
            member_privacy.save()

            verification.token_used = True
            verification.save()

            # 重定向到前端驗證成功頁面
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}verify-email/{token}?status=success")

        except Exception as e:
            print("Error during verification:", str(e))
            return Response({"message": "驗證失敗", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 更新 前台會員中心資料
class UpdateUserInfoView(APIView):

    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            # 根據主鍵 ID 查找會員資料
            user = MemberBasic.objects.get(pk=pk)

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
        email = request.data.get("user_email")
        if not email:
            return Response({"message": "請提供有效的電子郵箱"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = MemberBasic.objects.filter(user_email=email).first()

        # 檢查是否存在未使用的相同請求
        existing_request = MemberVerify.objects.filter(
            user=user,
            verification_type='phone_change',
            change_value=email,
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
        email = request.data.get("user_email")
        oldphone = request.data.get("user_phone")
        newphone = request.data.get("new_phone")

        if not oldphone or not newphone or not email:
            return Response({"message": "請輸入有效的手機號和郵箱。"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not MemberBasic.objects.filter(user_phone=oldphone, user_email=email).exists():
            return Response({'message': '輸入的手機號和郵箱不匹配或不存在。'}, status=400)
        
        # 獲取對應用戶
        user = MemberBasic.objects.get(user_phone=oldphone, user_email=email)
        
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
        email = request.data.get("user_email")
        newemail = request.data.get("new_email")

        if not email or not newemail or not email:
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

        # if existing_request:
        #     return Response({'message': '已存在待驗證的修改郵箱請求，請勿重複提交'}, status=400)
        
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