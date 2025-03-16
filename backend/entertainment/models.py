from django.db import models

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
        managed = False  # 告訴 Django 不要嘗試創建或修改這張表
        db_table = 'Games'  # 對應 MySQL 中的表名


class Animation(models.Model):
    animation_id = models.AutoField(primary_key=True)
    animation_title = models.CharField(max_length=255)
    animation_description = models.TextField()
    episodes = models.IntegerField()
    release_date = models.DateField()
    animation_genre = models.CharField(max_length=100)
    animation_studio = models.CharField(max_length=100)
    poster = models.CharField(max_length=255, null=True, blank=True)
    voice_actors = models.TextField()

    class Meta:
        managed = False
        db_table = 'animations'  # 對應 MySQL 中的表名


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
        managed = False
        db_table = 'Movies'  # 對應 MySQL 中的表名
