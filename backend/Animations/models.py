# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Animations(models.Model):
    animation_id = models.AutoField(primary_key=True)
    animation_title = models.CharField(max_length=255)
    animation_description = models.TextField()
    episodes = models.IntegerField()
    release_date = models.DateField()
    animation_genre = models.CharField(max_length=100)
    animation_studio = models.CharField(max_length=100, blank=True, null=True)
    poster = models.CharField(max_length=255, blank=True, null=True)
    voice_actors = models.TextField(blank=True, null=True)  # 聲優

    class Meta:
        managed = False
        db_table = 'animations'
