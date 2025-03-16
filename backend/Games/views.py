from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Games
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

def index(request):
    query = request.GET.get('keyword', '').strip()
    game_list = Games.objects.all()

    # 搜尋條件
    if query:
        if query.isdigit() and len(query) == 4:  # 如果是年份
            game_list = game_list.filter(release_date__year=query)
        else:  # 關鍵字搜尋
            game_list = game_list.filter(
                Q(game_title__icontains=query) |
                Q(game_genre__icontains=query) |
                Q(developer__icontains=query)
            )

    game_list = game_list.order_by('release_date')
    paginator = Paginator(game_list, 5)  # 每頁顯示 5 筆資料
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 計算分頁範圍 (最多顯示 5 頁)
    max_pages = 5  
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start_page = max(1, current_page - 2)
    end_page = min(total_pages, start_page + max_pages - 1)

    if end_page - start_page < max_pages - 1:
        start_page = max(1, end_page - max_pages + 1)

    page_range = range(start_page, end_page + 1)

    return render(request, 'Games/index.html', {
        'page_obj': page_obj,
        'query': query,  
        'page_range': page_range,  
    })





def add_games(request):
    if request.method == 'POST':
        # 取得表單資料
        game_title = request.POST.get('game_title')
        release_date = request.POST.get('release_date')
        game_genre = request.POST.get('game_genre')
        game_platform = request.POST.get('game_platform')
        developer = request.POST.get('developer')
        game_description = request.POST.get('game_description')  # 新增遊戲描述欄位
        poster = request.FILES.get('poster')
        poster_url = request.POST.get('poster_url')  # 新增圖片網址處理

        # 優先檢查是否有上傳遊戲海報檔案
        if poster:
            fs = FileSystemStorage()
            poster_file = fs.save(poster.name, poster)
        elif poster_url:  # 如果沒有檔案，則使用圖片網址
            poster_file = poster_url
        else:
            poster_file = None

        # 將資料寫入資料庫
        Games.objects.create(
            game_title=game_title,
            release_date=release_date,
            game_genre=game_genre,
            game_platform=game_platform,
            developer=developer,
            game_description=game_description,  # 保存遊戲描述
            poster=poster_file  # 保存圖片檔案或網址
        )

        messages.success(request, '遊戲資料新增成功')
        return redirect('Games:index')  # 重定向到遊戲列表頁面

    return render(request, 'Games/add_game.html')

def edit(request, id):
    game = get_object_or_404(Games, game_id=id)

    if request.method == "POST":
        game.game_title = request.POST.get('game_title')
        game.release_date = request.POST.get('release_date')
        game.game_genre = request.POST.get('game_genre')
        game.game_platform = request.POST.get('game_platform')
        game.developer = request.POST.get('developer')
        game.game_description = request.POST.get('game_description')  # 更新遊戲描述

        poster = request.FILES.get('poster')
        poster_url = request.POST.get('poster_url')

        if poster:
            fs = FileSystemStorage()
            poster_file = fs.save(poster.name, poster)
            game.poster = poster_file
        elif poster_url:
            game.poster = poster_url

        game.save()

        messages.success(request, '遊戲資料修改成功')
        return redirect('Games:index')

    return render(request, "Games/edit.html", {"game": game})

def delete(request, id):
    game = Games.objects.get(game_id=id)
    game.delete()
    return redirect('Games:index')
