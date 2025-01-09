# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Games(models.Model):
    game_id = models.AutoField(primary_key=True)
    game_title = models.CharField(max_length=255)
    game_description = models.TextField()
    game_genre = models.CharField(max_length=100)
    release_date = models.DateField()
    game_platform = models.CharField(max_length=100)
    poster = models.CharField(max_length=255, blank=True, null=True)
    developer = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'games'
