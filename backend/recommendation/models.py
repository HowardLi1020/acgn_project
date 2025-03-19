from django.db import models

# Create your models here.
# recommendation/models.py
from django.db import models

# 現有資料庫模型（用於參考，實際使用時可能需要透過inspectdb自動生成）
class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'Categories'
        managed = False  # 表示這個模型對應的表已存在，Django不需要創建
    
    def __str__(self):
        return self.category_name

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    game_title = models.CharField(max_length=255)
    game_description = models.TextField()
    game_genre = models.CharField(max_length=100)
    release_date = models.DateField()
    game_platform = models.CharField(max_length=100)
    poster = models.CharField(max_length=255, null=True, blank=True)
    developer = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'Games'
        managed = False
    
    def __str__(self):
        return self.game_title

class Animation(models.Model):
    animation_id = models.AutoField(primary_key=True)
    animation_title = models.CharField(max_length=255)
    animation_description = models.TextField()
    episodes = models.IntegerField()
    release_date = models.DateField()
    animation_genre = models.CharField(max_length=100)
    animation_studio = models.CharField(max_length=100)
    poster = models.CharField(max_length=255, null=True, blank=True)
    voice_actors = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'animations'
        managed = False
    
    def __str__(self):
        return self.animation_title

class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255)
    movie_description = models.TextField()
    release_date = models.DateField()
    movie_genre = models.CharField(max_length=255)
    director = models.CharField(max_length=100)
    cast = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    poster = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'Movies'
        managed = False
    
    def __str__(self):
        return self.movie_title

# 向量搜索模型（新增，用於存儲向量）
class ContentVector(models.Model):
    """統一存儲所有內容類型的向量表示"""
    id = models.AutoField(primary_key=True)
    
    # 內容類型和ID
    content_type = models.CharField(max_length=20)  # 'movie', 'game', 'animation'
    content_id = models.IntegerField()
    
    # 向量數據 (二進制格式)
    vector_binary = models.BinaryField()
    
    # 建立唯一索引確保每個內容只有一個向量
    class Meta:
        managed = False  # 添加這一行
        db_table = 'recommendation_contentvector'  # 確保表名與創建的表一致
        unique_together = ('content_type', 'content_id')
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
        ]
    
    def __str__(self):
        return f"{self.content_type}_{self.content_id}"

# 搜索記錄 (可選，用於分析和改進)
class SearchLog(models.Model):
    """記錄用戶的搜索查詢和結果"""
    id = models.AutoField(primary_key=True)
    query_text = models.TextField()
    content_type_filter = models.CharField(max_length=20, null=True, blank=True)
    genre_filter = models.CharField(max_length=100, null=True, blank=True)
    results_count = models.IntegerField()
    user_id = models.IntegerField(null=True, blank=True)  # 如果有用戶系統
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.query_text} ({self.results_count} results)"