from django.db import models


class MemberBasic(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=20, unique=True)  # 用戶名，唯一
    user_password = models.CharField(max_length=128)  # 密碼
    user_phone = models.CharField(max_length=10, unique=True)  # 手機號，唯一
    user_email = models.EmailField(max_length=120, unique=True)  # 電子郵件，唯一
    user_nickname = models.CharField(max_length=20, null=True, blank=True)  # 暱稱
    user_gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('prefer_not_to_say', 'Prefer not to say')
        ],
        default='prefer_not_to_say'
    )  # 性別
    user_birth = models.DateField(null=True, blank=True)  # 出生日期
    user_address = models.TextField(null=True, blank=True)  # 地址
    vip_status = models.BooleanField(default=False)  # VIP 狀態
    user_avatar = models.CharField(max_length=255, default='default.png')  # 用戶頭像
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 更新時間

    class Meta:
        db_table = 'member_basic'
        verbose_name = "會員"
        verbose_name_plural = "會員"
        indexes = [
            models.Index(fields=['user_email', 'user_phone'], name='idx_user_email_phone'),  # 複合索引
        ]

    def __str__(self):
        return self.user_name


class Posts(models.Model):
    post_id = models.AutoField(primary_key=True)  # 文章 ID
    title = models.CharField(max_length=255)  # 標題
    body = models.TextField()  # 內容
    author = models.ForeignKey(
        MemberBasic, 
        on_delete=models.CASCADE, 
        related_name='posts'  # 關聯到 MemberBasic
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 更新時間

    class Meta:
        db_table = 'Posts'
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return self.title


class Replies(models.Model):
    reply_id = models.AutoField(primary_key=True)  # 回覆 ID
    post = models.ForeignKey(
        Posts, 
        on_delete=models.CASCADE, 
        related_name='replies'  # 關聯到 Posts
    )
    body = models.TextField()  # 回覆內容
    author = models.ForeignKey(
        MemberBasic, 
        on_delete=models.CASCADE, 
        related_name='replies'  # 關聯到 MemberBasic
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 更新時間

    class Meta:
        db_table = 'Replies'
        verbose_name = "回覆"
        verbose_name_plural = "回覆"

    def __str__(self):
        return f"Reply to {self.post.title} by {self.author.user_name}"


class Likes(models.Model):
    like_id = models.AutoField(primary_key=True)  # 按讚 ID
    post = models.ForeignKey(
        Posts, 
        on_delete=models.CASCADE, 
        related_name='likes'  # 關聯到 Posts
    )
    user = models.ForeignKey(
        MemberBasic, 
        on_delete=models.CASCADE, 
        related_name='likes'  # 關聯到 MemberBasic
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 按讚時間
    posts_report = models.BooleanField(default=False)  # 是否被檢舉

    class Meta:
        db_table = 'Likes'
        verbose_name = "按讚"
        verbose_name_plural = "按讚"

    def __str__(self):
        return f"Like by {self.user.user_name} on {self.post.title}"
