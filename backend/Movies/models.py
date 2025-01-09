from django.db import models

class Movies(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255, verbose_name="電影名稱")
    movie_description = models.TextField(blank=True, null=True, verbose_name="電影描述")
    release_date = models.DateField(verbose_name="上映日期")
    movie_genre = models.CharField(max_length=100, verbose_name="電影類型")
    director = models.CharField(max_length=100, verbose_name="導演")
    cast = models.TextField(blank=True, null=True, default="未知演員", verbose_name="主要演員")  # 新增欄位
    poster = models.CharField(max_length=500, blank=True, null=True, verbose_name="電影海報")

    class Meta:
        db_table = 'Movies'
