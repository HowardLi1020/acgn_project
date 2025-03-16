from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from .models import Posts, Categories
from datetime import datetime  # ← **這行是關鍵！一定要加上！**

def index(request):
    # 取得搜尋關鍵字與篩選條件
    query = request.GET.get('keyword', '').strip()
    reported_filter = request.GET.get('reported_filter', '')
    category_filter = request.GET.get('category', '')

    # 查詢貼文，並統計檢舉數量
    posts = Posts.objects.annotate(
        reported_count=Count('likes', filter=Q(likes__posts_report=True))
    ).select_related('author', 'category')

    # **搜尋功能：根據標題、內容、作者名稱、創建日期**
    if query:
        try:
            # 嘗試將 `query` 轉換為 `YYYY-MM-DD` 日期格式
            query_date = datetime.strptime(query, "%Y-%m-%d").date()
            posts = posts.filter(created_at__date=query_date)
        except ValueError:
            # 不是日期時，搜尋 `title`、`body`、`author.user_name`
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(body__icontains=query) |
                Q(author__user_name__icontains=query)
            )

    # **篩選功能：依據檢舉狀態篩選**
    if reported_filter == '1':  # 被檢舉
        posts = posts.filter(reported_count__gt=0)
    elif reported_filter == '0':  # 未被檢舉
        posts = posts.filter(reported_count=0)

    # **分類篩選：根據 `category_id` 過濾**
    if category_filter:
        posts = posts.filter(category__category_id=category_filter)

    # **排序貼文，按照創建時間倒序排列**
    posts = posts.order_by('-created_at')

    # **分頁功能，每頁顯示 5 篇文章**
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # **計算分頁範圍 (最多顯示 5 頁)**
    max_pages = 5  
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start_page = max(1, current_page - 2)
    end_page = min(total_pages, start_page + max_pages - 1)

    if end_page - start_page < max_pages - 1:
        start_page = max(1, end_page - max_pages + 1)

    page_range = range(start_page, end_page + 1)

    # **取得所有分類**
    categories = Categories.objects.all()

    # **渲染模板並返回結果**
    return render(request, 'Discussion_board/index.html', {
        'page_obj': page_obj,
        'query': query,
        'reported_filter': reported_filter,
        'category_filter': category_filter,
        'categories': categories,
        'page_range': page_range,
    })

def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Posts, post_id=post_id)
        post.delete()
        return redirect('Discussion_board:index')
    return HttpResponse(status=405)

def toggle_report(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Posts, post_id=post_id)
        current_reported = post.likes.filter(posts_report=True).exists()
        if current_reported:
            post.likes.update(posts_report=False)
        else:
            post.likes.update(posts_report=True)
        return redirect('Discussion_board:index')
    return HttpResponse(status=405)