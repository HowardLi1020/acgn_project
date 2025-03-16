from django.db import models

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)  # 文章 ID
    title = models.CharField(max_length=255)  # 文章標題
    body = models.TextField()  # 文章內容
    author_id = models.IntegerField()  # 作者 ID，對應 member_basic(user_id)
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 更新時間

    class Meta:
        managed = False  # 讓 Django 不去管理這張表
        db_table = 'Posts'  # 這裡要對應 MySQL 中的表名稱

class Reply(models.Model):
    reply_id = models.AutoField(primary_key=True)  # 回覆 ID
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # 文章 ID
    body = models.TextField()  # 回覆內容
    author_id = models.IntegerField()  # 作者 ID
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間
    updated_at = models.DateTimeField(auto_now=True)  # 更新時間

    class Meta:
        managed = False
        db_table = 'Replies'  # 這裡要對應 MySQL 中的表名稱

class Like(models.Model):
    like_id = models.AutoField(primary_key=True)  # 按讚 ID
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # 文章 ID
    user_id = models.IntegerField()  # 用戶 ID
    created_at = models.DateTimeField(auto_now_add=True)  # 按讚時間
    posts_report = models.BooleanField(default=False)  # 是否被檢舉

    class Meta:
        managed = False
        db_table = 'Likes'  # 這裡要對應 MySQL 中的表名稱
