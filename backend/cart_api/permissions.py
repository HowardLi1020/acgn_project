from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from users.models import MemberBasic  # 修改為你的用戶模型
from django.core.cache import cache
class IsAuthenticatedWithCustomToken(BasePermission):
    """
    自訂義的 JWT Token 驗證權限
    """
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationFailed('未提供授權憑證 (Authorization Header)')

        try:
            # 從 Authorization Header 中提取 Token
            token = auth_header.split(' ')[1]
            # 使用和 AuthViewSet 相同的密鑰與算法解析 Token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # 從 payload 中提取 user_id
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token 無效，未包含用戶 ID')

            # 驗證該用戶是否存在
            request.user = MemberBasic.objects.get(user_id=user_id)

            # 驗證 session_key 是否一致
            session_key = f"user_session_{user_id}"
            if cache.get(session_key) != user_id:
                raise AuthenticationFailed('Session 驗證失敗')
            
            return True

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token 已過期')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('無效的 Token')
        except MemberBasic.DoesNotExist:
            raise AuthenticationFailed('用戶不存在')

        return False
