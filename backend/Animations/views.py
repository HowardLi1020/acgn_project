from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Animations
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

def index(request):
    query = request.GET.get('keyword', '').strip()
    animation_list = Animations.objects.all()

    # 搜尋條件
    if query:
        if query.isdigit() and len(query) == 4:  # 如果是年份
            animation_list = animation_list.filter(release_date__year=query)
        else:  # 關鍵字搜尋
            animation_list = animation_list.filter(
                Q(animation_title__icontains=query) |
                Q(animation_genre__icontains=query) |
                Q(animation_studio__icontains=query)
            )

    animation_list = animation_list.order_by('release_date')
    paginator = Paginator(animation_list, 5)  # 每頁顯示 5 筆資料
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

    return render(request, 'Animations/index.html', {
        'page_obj': page_obj,
        'query': query,  
        'page_range': page_range,  
    })

def add_animations(request):
    if request.method == 'POST':
        animation_title = request.POST.get('animation_title')
        animation_description = request.POST.get('animation_description')
        episodes = request.POST.get('episodes')
        release_date = request.POST.get('release_date')
        animation_genre = request.POST.get('animation_genre')
        animation_studio = request.POST.get('animation_studio')
        voice_actors = request.POST.get('voice_actors')
        poster = request.FILES.get('poster')
        poster_url = request.POST.get('poster_url')

        # 判斷是使用本地圖片還是網路圖片
        if poster:
            fs = FileSystemStorage()
            poster_file = fs.save(poster.name, poster)
            poster_path = poster_file
        elif poster_url:
            poster_path = poster_url  # 儲存網路圖片 URL
        else:
            poster_path = None  # 如果都沒有提供

        # 儲存到資料庫
        Animations.objects.create(
            animation_title=animation_title,
            animation_description=animation_description,
            episodes=episodes,
            release_date=release_date,
            animation_genre=animation_genre,
            animation_studio=animation_studio,
            voice_actors=voice_actors,
            poster=poster_path  # 保存圖片路徑或 URL
        )

        messages.success(request, '動畫資料新增成功')
        return redirect('Animations:index')

    return render(request, 'Animations/add_animation.html')


def edit(request, id):
    animation = get_object_or_404(Animations, animation_id=id)

    if request.method == "POST":
        animation.animation_title = request.POST.get('animation_title')
        animation.release_date = request.POST.get('release_date')
        animation.animation_genre = request.POST.get('animation_genre')
        animation.animation_studio = request.POST.get('animation_studio')
        animation.episodes = request.POST.get('episodes')
        animation.animation_description = request.POST.get('animation_description')
        animation.voice_actors = request.POST.get('voice_actors')

        # 處理本地圖片和網路圖片
        poster = request.FILES.get('poster')
        poster_url = request.POST.get('poster_url')

        if poster:
            fs = FileSystemStorage()
            poster_file = fs.save(poster.name, poster)
            animation.poster = poster_file
        elif poster_url:
            animation.poster = poster_url

        animation.save()

        messages.success(request, '動畫資料修改成功')
        return redirect('Animations:index')

    return render(request, "Animations/edit.html", {"animation": animation})

def delete(request, id):
    animation = Animations.objects.get(animation_id=id)
    animation.delete()
    return redirect('Animations:index')