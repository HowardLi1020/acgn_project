from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.core.cache import cache
from django.conf import settings
import jwt
from users.models import MemberBasic  # 確保這是您的用戶模型

class IsAuthenticatedWithCustomToken(BasePermission):
    """
    全局 JWT Token 驗證權限
    """
    def has_permission(self, request, view):
        # 從 Authorization Header 中提取 Token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationFailed('未提供授權憑證 (Authorization Header)')

        try:
            # 分離出 Bearer Token
            token = auth_header.split(' ')[1]
            # 使用密鑰與算法解析 Token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # 確認 payload 中是否包含 user_id
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token 無效，未包含用戶 ID')

            # 驗證用戶是否存在
            request.user = MemberBasic.objects.get(user_id=user_id)

            # 驗證 session_key 是否一致
            # session_key = f"user_session_{user_id}"
            # if cache.get(session_key) != user_id:
            #     raise AuthenticationFailed('Session 驗證失敗')

            return True

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token 已過期')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('無效的 Token')
        except MemberBasic.DoesNotExist:
            raise AuthenticationFailed('用戶不存在')

        return False
