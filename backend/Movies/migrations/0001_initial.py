# Generated by Django 5.1.1 on 2024-09-12 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movies',
            fields=[
                ('movie_id', models.AutoField(primary_key=True, serialize=False)),
                ('movie_title', models.CharField(max_length=255)),
                ('movie_description', models.TextField()),
                ('release_date', models.DateField()),
                ('movie_genre', models.CharField(max_length=100)),
                ('director', models.CharField(max_length=100)),
                ('cast', models.TextField()),
                ('rating', models.DecimalField(decimal_places=2, max_digits=3)),
                ('poster', models.CharField(default='empty.jpg', max_length=100)),
            ],
            options={
                'db_table': 'Movies',
                'managed': False,
            },
        ),
    ]
