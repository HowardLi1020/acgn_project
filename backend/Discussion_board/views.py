from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from .models import Posts

def index(request):
    # 取得搜尋關鍵字與篩選條件
    query = request.GET.get('keyword', '')
    reported_filter = request.GET.get('reported_filter', '')

    # 查詢貼文，並註解檢舉數量
    posts = Posts.objects.annotate(
        reported_count=Count('likes', filter=Q(likes__posts_report=True))
    ).select_related('author')

    # 搜尋功能：根據關鍵字篩選
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(author__user_name__icontains=query)
        )

    # 篩選功能：依據檢舉狀態篩選
    if reported_filter == '1':  # 被檢舉
        posts = posts.filter(reported_count__gt=0)
    elif reported_filter == '0':  # 未被檢舉
        posts = posts.filter(reported_count=0)

    # 排序貼文，按照創建時間倒序排列
    posts = posts.order_by('-created_at')

    # 分頁功能，每頁顯示 5 篇文章
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 渲染模板並返回結果
    return render(request, 'Discussion_board/index.html', {
        'page_obj': page_obj,
        'query': query,
        'reported_filter': reported_filter,
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
