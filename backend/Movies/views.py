from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movies
from django.db.models import Q
from django.core.files.storage import FileSystemStorage, default_storage
from django.contrib import messages
import os
from django.conf import settings
from datetime import datetime


def index(request):
    query = request.GET.get('keyword', '').strip()
    movie_list = Movies.objects.all()

    # 搜尋條件
    if query:
        if query.isdigit() and len(query) == 4:  # 如果是年份
            movie_list = movie_list.filter(release_date__year=query)
        else:  # 關鍵字搜尋
            movie_list = movie_list.filter(
                Q(movie_title__icontains=query) |
                Q(movie_genre__icontains=query) |
                Q(director__icontains=query) |
                Q(cast__icontains=query)
            )

    movie_list = movie_list.order_by('release_date')
    paginator = Paginator(movie_list, 5)  # 每頁顯示 5 筆資料
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 計算分頁範圍 (顯示當前頁前後最多 5 頁)
    max_pages = 5  
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start_page = max(1, current_page - 2)
    end_page = min(total_pages, start_page + max_pages - 1)

    if end_page - start_page < max_pages - 1:
        start_page = max(1, end_page - max_pages + 1)

    page_range = range(start_page, end_page + 1)

    return render(request, 'Movies/index.html', {
        'page_obj': page_obj,
        'query': query,  
        'page_range': page_range,  
    })


def add_movie(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title')
        release_date = request.POST.get('release_date')
        movie_genre = request.POST.get('movie_genre')
        director = request.POST.get('director')
        movie_description = request.POST.get('movie_description', "描述尚未提供")
        cast = request.POST.get('cast', "未知演員")  # 提供默認值
        poster_option = request.POST.get('poster-option')
        poster = None

        # 驗證必填字段
        if not movie_title or not release_date or not movie_genre or not director:
            messages.error(request, "所有字段均為必填")
            return render(request, 'Movies/add_movie.html')

        # 處理海報
        if poster_option == 'upload':
            poster_file = request.FILES.get('poster_file')
            if poster_file:
                file_path = os.path.join('posters', poster_file.name)
                poster = default_storage.save(file_path, poster_file)
        elif poster_option == 'url':
            poster = request.POST.get('poster_url')

        # 如果海報未提供，使用預設海報
        if not poster:
            poster = 'posters/default.jpg'

        # 創建電影
        movie = Movies(
            movie_title=movie_title,
            release_date=release_date,
            movie_genre=movie_genre,
            director=director,
            movie_description=movie_description,
            cast=cast,
            poster=poster,
        )
        movie.save()
        messages.success(request, "電影已新增")
        return redirect('/Movies/')

    return render(request, 'Movies/add_movie.html')


def edit(request, id):
    movie = get_object_or_404(Movies, movie_id=id)

    if request.method == "POST":
        movie.movie_title = request.POST.get('movie_title')
        movie.release_date = request.POST.get('release_date')
        movie.movie_genre = request.POST.get('movie_genre')
        movie.director = request.POST.get('director')
        movie.movie_description = request.POST.get('movie_description', movie.movie_description)
        movie.cast = request.POST.get('cast', movie.cast)

        # 處理海報
        poster_option = request.POST.get('poster-option')
        if poster_option == 'upload':
            poster_file = request.FILES.get('poster_file')
            if poster_file:
                # 刪除舊的圖片檔案
                if movie.poster and movie.poster != 'posters/default.jpg':
                    old_poster_path = os.path.join(settings.MEDIA_ROOT, movie.poster)
                    if os.path.exists(old_poster_path):
                        os.remove(old_poster_path)
                # 上傳新的圖片
                file_path = os.path.join('posters', poster_file.name)
                movie.poster = default_storage.save(file_path, poster_file)
        elif poster_option == 'url':
            movie.poster = request.POST.get('poster_url')

        movie.save()
        messages.success(request, '電影資料修改成功')
        return redirect('Movies:index')

    return render(request, "Movies/edit.html", {"movie": movie})


def delete(request, id):
    movie = get_object_or_404(Movies, movie_id=id)

    # 刪除圖片檔案
    if movie.poster and movie.poster != 'posters/default.jpg':
        poster_path = os.path.join(settings.MEDIA_ROOT, movie.poster)
        if os.path.exists(poster_path):
            os.remove(poster_path)

    # 刪除電影記錄
    movie.delete()
    messages.success(request, '電影資料已刪除')
    return redirect('Movies:index')
