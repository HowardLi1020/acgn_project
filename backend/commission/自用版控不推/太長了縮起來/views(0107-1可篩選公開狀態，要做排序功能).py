from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
import os
from pathlib import Path
import json
from django.conf import settings

# 大寫取名ViewKey_NeedInfo=來自大檔項目，如資料庫、views.py、urls.py、HTML
# 小寫取名如view_db_need_info=取自內部參數，如欄位名稱

# def index(request):
#     view_db_need_info = DbNeedInfo.objects.all()
#     return render(request, 'commission/need_list.html', {'ViewKey_DbNeedInfo': view_db_need_info})

def ViewFn_need_list(request):
    # 資料提取與顯示
    view_db_need_info = DbNeedInfo.objects.all()
    
    # 搜尋功能
    search_term = request.GET.get('search', '')
    search_column = request.GET.get('column', 'option-1')
    status_filter = request.GET.get('status', 'all')
    
    # 排序功能
    sort_column = request.GET.get('sort', 'id')  # 預設為 ID
    sort_order = request.GET.get('order', 'desc')  # 預設為降序
    
    # 映射前端欄位名稱到資料庫欄位名稱
    column_map = {
        'id': 'need_id',
        'title': 'need_title',
        'category': 'need_category',
        'description': 'need_description',
        'needer': 'needer_nickname',
        'originalFrom': 'need_original_from',
        'price': 'need_price',
        'publishTime': 'publish_time',
        'deadline': 'deadline',
        'status': 'need_status',
        'lastUpdate': 'last_update'
    }
    
    # 應用排序
    sort_field = column_map.get(sort_column, 'need_id')  # 使用 need_id 作為默認
    if sort_order == 'asc':
        view_db_need_info = view_db_need_info.order_by(sort_field)
    else:
        view_db_need_info = view_db_need_info.order_by(f'-{sort_field}')
    
    # 搜尋邏輯
    if search_term:
        if search_column == 'option-1':
            # 搜尋所有欄位
            view_db_need_info = view_db_need_info.filter(
                Q(need_title__icontains=search_term) |
                Q(need_category__icontains=search_term) |
                Q(need_description__icontains=search_term) |
                Q(needer_nickname__icontains=search_term) |
                Q(need_original_from__icontains=search_term) |
                Q(need_price__icontains=search_term) |
                Q(publish_time__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(need_status__icontains=search_term) |
                Q(last_update__icontains=search_term)
            )
        else:
            # 搜尋特定欄位
            column = column_map.get(search_column.replace('option-', ''))
            if column:
                view_db_need_info = view_db_need_info.filter(**{f"{column}__icontains": search_term})

    # 篩選功能
    if status_filter != 'all':
        view_db_need_info = view_db_need_info.filter(need_status=status_filter)

    paginator = Paginator(view_db_need_info, 7)  # 每頁顯示7條記錄
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_term': search_term,
        'search_column': search_column,
        'status_filter': status_filter,
        'sort_column': sort_column,
        'sort_order': sort_order,
        'is_sorted': 'sort' in request.GET
    }
    
    return render(request, 'commission/need_list.html', context)

@require_http_methods(["GET", "POST"])
def ViewFn_need_edit(request, view_fn_need_id):
    # 待修BUG：
    # ．分次加入圖檔時，只有最後一次加的圖才被寫入資料庫
    # ．上傳未滿5張圖時，會重複上傳
    if request.method == 'POST':
        try:
            with transaction.atomic():
                view_db_need_info_id = get_object_or_404(DbNeedInfo, need_id=view_fn_need_id)
                
                # 處理刪除圖片
                if 'deleted_images' in request.POST:
                    deleted_images = json.loads(request.POST['deleted_images'])
                    for image_name in deleted_images:
                        # 刪除資料庫記錄
                        DbNeedImages.objects.filter(
                            need_id=view_fn_need_id,
                            image_url=image_name
                        ).delete()
                        
                        # 刪除實際檔案
                        file_path = os.path.join('commission', 'needID_img', image_name)
                        if default_storage.exists(file_path):
                            default_storage.delete(file_path)
                    
                    # 重新排序剩餘圖片
                    remaining_images = DbNeedImages.objects.filter(
                        need_id=view_fn_need_id
                    ).order_by('step')
                    
                    # 更新每張圖片的序號和檔名
                    for new_step, image in enumerate(remaining_images, 1):
                        # 取得舊檔名的副檔名
                        old_extension = Path(image.image_url).suffix
                        # 產生新檔名
                        new_filename = f"{view_fn_need_id}_sketch{new_step}{old_extension}"
                        
                        # 如果檔名需要更改
                        if image.image_url != new_filename:
                            # 重命名實際檔案
                            old_path = os.path.join('commission', 'needID_img', image.image_url)
                            new_path = os.path.join('commission', 'needID_img', new_filename)
                            
                            if default_storage.exists(old_path):
                                # 讀取舊檔案內容
                                with default_storage.open(old_path, 'rb') as old_file:
                                    # 儲存為新檔案
                                    default_storage.save(new_path, old_file)
                                # 刪除舊檔案
                                default_storage.delete(old_path)
                            
                            # 更新資料庫記錄
                            image.image_url = new_filename
                        
                        # 更新序號
                        image.step = new_step
                        image.save()

                # 更新文字欄位
                if 'need_title' in request.POST:
                    view_db_need_info_id.need_title = request.POST['need_title']
                if 'need_category' in request.POST:
                    view_db_need_info_id.need_category = request.POST['need_category']
                if 'need_description' in request.POST:
                    view_db_need_info_id.need_description = request.POST['need_description']
                if 'need_original_from' in request.POST:
                    view_db_need_info_id.need_original_from = request.POST['need_original_from']
                if 'need_price' in request.POST:
                    view_db_need_info_id.need_price = request.POST['need_price']
                if 'deadline' in request.POST:
                    view_db_need_info_id.deadline = request.POST['deadline']
                if 'need_status' in request.POST:
                    view_db_need_info_id.need_status = request.POST['need_status']

                # 處理圖片上傳
                if 'need_ex_image' in request.FILES:
                    uploaded_files = request.FILES.getlist('need_ex_image')
                    
                    # 獲取現有的圖片記錄
                    existing_images = DbNeedImages.objects.filter(need_id=view_fn_need_id).order_by('step')
                    current_step = existing_images.count()
                    
                    if current_step >= 5:
                        # 當已有5張圖片時，依序替換
                        for index, file in enumerate(uploaded_files):
                            if index < 5:
                                # 找到要替換的圖片記錄
                                image_record = existing_images[index]
                                
                                # 刪除舊檔案
                                old_file_path = os.path.join('commission', 'needID_img', image_record.image_url)
                                if default_storage.exists(old_file_path):
                                    default_storage.delete(old_file_path)
                                
                                # 使用新文件的副檔名
                                new_extension = Path(file.name).suffix
                                new_filename = f"{view_fn_need_id}_sketch{image_record.step}{new_extension}"
                                
                                # 儲存新檔案
                                file_path = os.path.join('commission', 'needID_img', new_filename)
                                default_storage.save(file_path, file)
                                
                                # 更新資料庫記錄
                                image_record.image_url = new_filename
                                image_record.save()
                    else:
                        # 只處理前5張上傳的文件
                        files_to_process = uploaded_files[:5 - current_step]

                        # 處理新上傳的檔案
                        for index, file in enumerate(files_to_process, start=current_step + 1):
                            # 新增圖片
                            new_extension = Path(file.name).suffix
                            new_filename = f"{view_fn_need_id}_sketch{index}{new_extension}"
                            image_record = DbNeedImages(
                                need_id=view_db_need_info_id.need_id,
                                step=index,
                                image_url=new_filename
                            )
                            image_record.save()
                            
                            # 儲存新檔案
                            file_path = os.path.join('commission', 'needID_img', new_filename)
                            default_storage.save(file_path, file)

                # 處理替換的圖片
                if 'replaced_images' in request.POST:
                    replaced_images = json.loads(request.POST['replaced_images'])
                    for replacement in replaced_images:
                        original_filename = replacement['original']
                        new_file = request.FILES[f'replacement_file_{replacement["index"]}']
                        
                        # 找到要替換的圖片記錄
                        image_record = DbNeedImages.objects.get(
                            need_id=view_fn_need_id,
                            image_url=original_filename
                        )
                        
                        # 刪除舊檔案
                        old_file_path = os.path.join('commission', 'needID_img', original_filename)
                        if default_storage.exists(old_file_path):
                            default_storage.delete(old_file_path)
                        
                        # 使用新文件的副檔名
                        new_extension = Path(new_file.name).suffix
                        new_filename = f"{view_fn_need_id}_sketch{image_record.step}{new_extension}"
                        
                        # 儲存新檔案
                        file_path = os.path.join('commission', 'needID_img', new_filename)
                        default_storage.save(file_path, new_file)
                        
                        # 更新資料庫記錄
                        image_record.image_url = new_filename
                        image_record.save()

                # 更新 last_update
                view_db_need_info_id.last_update = timezone.now()
                view_db_need_info_id.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': '更新成功',
                    'last_update': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    # GET 請求的處理保持不變
    view_db_need_info_id = get_object_or_404(DbNeedInfo, need_id=view_fn_need_id)
    
    # 將截止時間轉換為當前時區
    if view_db_need_info_id.deadline:
        view_db_need_info_id.deadline = timezone.localtime(view_db_need_info_id.deadline)
    
    view_db_need_sketches = DbNeedImages.objects.filter(need_id=view_fn_need_id).order_by('step')
    
    # 計算剩餘的灰色加號DIV數量
    remaining_placeholders = max(0, 5 - view_db_need_sketches.count())

    context = {
        'ViewKey_DbNeedInfo_need_id': view_db_need_info_id,
        'ViewKey_DbNeedEdit_sketches': view_db_need_sketches,
        'remaining_placeholders': range(remaining_placeholders),
    }

    return render(request, 'commission/need_edit.html', context)

def ViewFn_need_delete(request, view_fn_need_id):

    view_db_need_info_id = get_object_or_404(DbNeedInfo, pk=view_fn_need_id)
    view_db_need_info_id.delete()
    
    # 獲取當前的完整 URL
    referer_url = request.META.get('HTTP_REFERER')
    
    # 如果沒有 referer，則返回到需求列表頁面
    if not referer_url:
        referer_url = reverse('commission:Urls_need_list')
    
    return HttpResponseRedirect(referer_url)

def ViewFn_publiccard_list(request):
    # 獲取所有公開名片資料，並關聯到 MemberBasic
    view_db_publiccard_info = DbPublicCardInfo.objects.select_related('member_basic').all()
    
    # 根據狀態篩選
    view_fn_status = request.GET.get('status')
    if view_fn_status and view_fn_status != 'all':
        view_db_publiccard_info = view_db_publiccard_info.filter(card_status=view_fn_status)

    context = {
        'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
    }
    return render(request, 'commission/publiccard_list.html', context)