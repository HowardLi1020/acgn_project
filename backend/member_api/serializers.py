from rest_framework import serializers
from users.models import MemberBasic, MemberIndextype, MemberLogin,  MemberPrivacy, MemberVerify
from member_api.models import Usercoupons
from cart.models import Orders
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken

# 1. 用戶資料序列化
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberBasic
        # fields = '__all__'
        fields = ['user_id', 'user_name', 'user_email', 'user_phone', 'user_nickname', 'user_gender', 'user_birth', 'user_address', 'vip_status', 'user_avatar']

    def validate_user_password(self, value):
        return make_password(value)

# 2. 登入資料序列化
class LoginSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)
    user_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    class Meta:
        model = MemberBasic
        fields = ['user_email', 'user_password']

    def validate(self, attrs):
        email = attrs.get("user_email")
        password = attrs.get("user_password")
        # remember_me = attrs.get("remember_me")

        if email and password:
            # 查詢用戶
            user = MemberBasic.objects.filter(user_email=email).first()

            if not user:
                raise serializers.ValidationError('該郵箱未註冊')
            
            # 密碼驗證
            password_valid = False
            if user.user_password.startswith('pbkdf2_sha256$') or user.user_password.startswith('bcrypt$'):
                password_valid = check_password(password, user.user_password)
            else:
                password_valid = (password == user.user_password)

            if not password_valid:
                raise serializers.ValidationError('密碼錯誤')

            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('必須提供email和密碼')

# 3. 註冊資料序列化
class RegisterSerializer(serializers.ModelSerializer):
    user_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = MemberBasic
        fields = ['user_name', 'user_email', 'user_phone', 'user_password']

    def validate(self, attrs):
        print("初始資料:", self.initial_data)  # 確認前端提交的原始數據
        print("處理後資料:", attrs)  # 確認處理後的資料
    
        # 確保 name 唯一性
        if MemberBasic.objects.filter(user_name=attrs['user_name']).exists():
            raise serializers.ValidationError({"name": "此姓名已被使用"})
        
        # 確保 email 唯一性
        if MemberBasic.objects.filter(user_email=attrs['user_email']).exists():
            raise serializers.ValidationError({"email": "此信箱已被使用"})
        
        # 確保 手機 唯一性
        if MemberBasic.objects.filter(user_phone=attrs['user_phone']).exists():
            raise serializers.ValidationError({"user_phone": "此手機號碼已被註冊"})

        return attrs
    
    def create(self, validated_data):
        # 設置預設值...
        vip_status = validated_data.pop('vip_status', '0')
        user_avatar = validated_data.pop('user_avatar', 'default.png')
        user_nickname = validated_data.pop("user_nickname","nickname")
        user_gender = validated_data.pop("user_gender","prefer_not_to_say")
        created_at = now()  # 自動生成 created_at

        # 加密密碼
        validated_data['user_password'] = make_password(validated_data.pop('user_password'))

        # # 建立使用者
        # return MemberBasic.objects.create(**validated_data)

        # 建立使用者
        user = MemberBasic.objects.create(
            user_name=validated_data['user_name'],
            user_email=validated_data['user_email'],
            user_phone=validated_data['user_phone'],
            user_password=validated_data['user_password'],
            user_avatar=user_avatar,
            vip_status=vip_status,
            user_nickname=user_nickname,
            user_gender=user_gender,
            created_at=created_at,
        )

        return user

# 4. 驗證資料序列化
class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberVerify
        fields = ['user', 'change_value', 'verification_code', 'verification_token', 'verification_type']
        # fields = '__all__'
    
    verification_type = serializers.ChoiceField(choices=[
        ('registration', 'registration'),
        ('two_factor', 'two_factor'),
        ('password_change', 'password_change'),
        ('phone_change', 'phone_change'),
        ('email_change', 'email_change'),
    ])

# 5. 使用者頭像資料序列化
class UploadAvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField(required=True)

# 6. 使用者網站個人喜好排序
class MemberIndextypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberIndextype
        fields = ['type_name', 'sort_order']

# 7. 空序列化器
class EmptySerializer(serializers.Serializer):
    pass

# 尚未使用 MemberPrivacy
class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPrivacy
        fields = '__all__'

# 尚未使用 第三方登入
class ThirdLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberLogin
        fields = '__all__'

# 尚未使用 Orderdetails
class OrderdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'
