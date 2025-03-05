from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
import os
from pathlib import Path
import json
from django.conf import settings
from django.views.decorators.cache import never_cache
import time
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import zipfile
import py7zr
import rarfile
import tempfile
from django.views.decorators.csrf import csrf_exempt
import tempfile
import re

# 大寫取名ViewKey_NeedInfo=來自大檔項目，如資料庫、views.py、urls.py、HTML
# 小寫取名如view_db_need_info=取自內部參數，如欄位名稱

# def index(request):
#     view_db_need_info = DbNeedInfo.objects.all()
#     return render(request, 'commission/need_list.html', {'ViewKey_DbNeedInfo': view_db_need_info})

def ViewFn_need_list(request):
    # 資料提取與顯示
    view_db_need_info = DbNeedInfo.objects.all()  # 保持為 QuerySet
    
    # 獲取所有需要的 public card 資訊
    public_cards = {
        card.member_basic_id: card 
        for card in DbPublicCardInfo.objects.all()
    }
    
    # 排序功能
    sort_column = request.GET.get('sort', 'id')  # 預設為 ID
    sort_order = request.GET.get('order', 'desc')  # 預設為降序
    
    # 映射前端欄位名稱到資料庫欄位名稱
    column_map = {
        'id': 'need_id',
        'title': 'need_title',
        'category': 'need_category',
        'description': 'need_description',
        'needer': 'needer_id', 
        'originalFrom': 'need_original_from',
        'price': 'need_price',
        'publishTime': 'publish_time',
        'deadline': 'deadline',
        'status': 'need_status',
        'lastUpdate': 'last_update'
    }
    
    # 應用排序
    sort_field = column_map.get(sort_column, 'need_id')
    if sort_order == 'asc':
        view_db_need_info = view_db_need_info.order_by(sort_field)
    else:
        view_db_need_info = view_db_need_info.order_by(f'-{sort_field}')
    
    # 搜尋功能
    search_term = request.GET.get('search', '')
    search_column = request.GET.get('column', 'option-1')
    status_filter = request.GET.get('status', 'all')
    
    # 搜尋邏輯
    if search_term:
        if search_column == 'option-1':
            # 先找出符合用戶暱稱的 needer_ids
            matching_needer_ids = [
                card.member_basic_id 
                for card in public_cards.values() 
                if search_term.lower() in card.user_nickname.lower()
            ]
            
            # 修改搜尋條件，加入對 needer_id 的檢查
            view_db_need_info = view_db_need_info.filter(
                Q(need_title__icontains=search_term) |
                Q(need_category__icontains=search_term) |
                Q(need_description__icontains=search_term) |
                Q(need_original_from__icontains=search_term) |
                Q(need_price__icontains=search_term) |
                Q(publish_time__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(need_status__icontains=search_term) |
                Q(last_update__icontains=search_term) |
                Q(needer_id__in=matching_needer_ids)  # 加入這行
            )
        elif search_column == 'needer':  # 如果特別選擇搜尋委託人
            matching_needer_ids = [
                card.member_basic_id 
                for card in public_cards.values() 
                if search_term.lower() in card.user_nickname.lower()
            ]
            view_db_need_info = view_db_need_info.filter(needer_id__in=matching_needer_ids)
        else:
            column = column_map.get(search_column.replace('option-', ''))
            if column:
                view_db_need_info = view_db_need_info.filter(**{f"{column}__icontains": search_term})

    # 篩選功能
    if status_filter != 'all':
        view_db_need_info = view_db_need_info.filter(need_status=status_filter)

    # 在這裡轉換為列表並添加 public_card
    view_db_need_info = list(view_db_need_info)
    for need in view_db_need_info:
        need.public_card = public_cards.get(need.needer_id)

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
    # ．(已解決)上傳未滿5張圖時，會重複上傳
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
                # 調試輸出
                # print("POST data:", request.POST)
                # print("Original status:", view_db_need_info_id.need_status)
                
                if 'need_status' in request.POST:
                    # 獲取 need_status 的第一個值（因為 radio 按鈕應該只有一個值），不知道什麼原因 'need_status'會接收到多個值
                    view_db_need_info_id.need_status = request.POST.getlist('need_status')[0].strip()
                    # view_db_need_info_id.need_status = request.POST['need_status']                    

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
                    print("New status:", request.POST['need_status'])
                # 更新 last_update
                view_db_need_info_id.last_update = timezone.now()
                view_db_need_info_id.save()
                
                # 驗證保存後的狀態
                updated_need = DbNeedInfo.objects.get(need_id=view_fn_need_id)
                print("Saved status:", updated_need.need_status)
                
                return JsonResponse({
                    'status': 'success',
                    'message': '更新成功',
                    'last_update': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'need_status': updated_need.need_status  # 在回應中也包含更新後的狀態
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    # GET 請求的處理
    view_db_need_info_id = get_object_or_404(DbNeedInfo, need_id=view_fn_need_id)
    
    # 獲取對應的 PublicCardInfo
    view_db_publiccard_info = get_object_or_404(DbPublicCardInfo, member_basic_id=view_db_need_info_id.needer_id)
    
    # 將截止時間轉換為當前時區
    if view_db_need_info_id.deadline:
        view_db_need_info_id.deadline = timezone.localtime(view_db_need_info_id.deadline)
    
    view_db_need_sketches = DbNeedImages.objects.filter(need_id=view_fn_need_id).order_by('step')
    
    # 計算剩餘的灰色加號DIV數量
    remaining_placeholders = max(0, 5 - view_db_need_sketches.count())

    context = {
        'ViewKey_DbNeedInfo_need_id': view_db_need_info_id,
        'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
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

def ViewFn_work_list(request):
    # 資料提取與顯示
    view_db_work_info = DbWorkInfo.objects.all()  # 保持為 QuerySet
    
    # 獲取所有需要的 public card 資訊
    public_cards = {
        card.member_basic_id: card 
        for card in DbPublicCardInfo.objects.all()
    }
    
    # 排序功能
    sort_column = request.GET.get('sort', 'id')  # 預設為 ID
    sort_order = request.GET.get('order', 'desc')  # 預設為降序
    
    # 映射前端欄位名稱到資料庫欄位名稱
    column_map = {
        'id': 'work_id',
        'title': 'work_title',
        'category': 'work_category',
        'description': 'work_description',
        'worker': 'worker_id', 
        'originalFrom': 'work_original_from',
        'price': 'work_price',
        'publishTime': 'publish_time',
        'deadline': 'deadline',
        'status': 'work_status',
        'lastUpdate': 'last_update'
    }
    
    # 應用排序
    sort_field = column_map.get(sort_column, 'work_id')
    if sort_order == 'asc':
        view_db_work_info = view_db_work_info.order_by(sort_field)
    else:
        view_db_work_info = view_db_work_info.order_by(f'-{sort_field}')
    
    # 搜尋功能
    search_term = request.GET.get('search', '')
    search_column = request.GET.get('column', 'option-1')
    status_filter = request.GET.get('status', 'all')
    
    # 搜尋邏輯
    if search_term:
        if search_column == 'option-1':
            # 先找出符合用戶暱稱的 worker_ids
            matching_worker_ids = [
                card.member_basic_id 
                for card in public_cards.values() 
                if search_term.lower() in card.user_nickname.lower()
            ]
            
            # 修改搜尋條件，加入對 worker_id 的檢查
            view_db_work_info = view_db_work_info.filter(
                Q(work_title__icontains=search_term) |
                Q(work_category__icontains=search_term) |
                Q(work_description__icontains=search_term) |
                Q(work_original_from__icontains=search_term) |
                Q(work_price__icontains=search_term) |
                Q(publish_time__icontains=search_term) |
                Q(deadline__icontains=search_term) |
                Q(work_status__icontains=search_term) |
                Q(last_update__icontains=search_term) |
                Q(worker_id__in=matching_worker_ids)  # 加入這行
            )
        elif search_column == 'worker':  # 如果特別選擇搜尋委託人
            matching_worker_ids = [
                card.member_basic_id 
                for card in public_cards.values() 
                if search_term.lower() in card.user_nickname.lower()
            ]
            view_db_work_info = view_db_work_info.filter(worker_id__in=matching_worker_ids)
        else:
            column = column_map.get(search_column.replace('option-', ''))
            if column:
                view_db_work_info = view_db_work_info.filter(**{f"{column}__icontains": search_term})

    # 篩選功能
    if status_filter != 'all':
        view_db_work_info = view_db_work_info.filter(work_status=status_filter)

    # 在這裡轉換為列表並添加 public_card
    view_db_work_info = list(view_db_work_info)
    for work in view_db_work_info:
        work.public_card = public_cards.get(work.worker_id)

    paginator = Paginator(view_db_work_info, 7)  # 每頁顯示7條記錄
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
    
    return render(request, 'commission/work_list.html', context)

def ViewFn_work_delete(request, view_fn_work_id):
    view_db_work_info = get_object_or_404(DbWorkInfo, pk=view_fn_work_id)
    view_db_work_info.delete()
    
    return HttpResponseRedirect(reverse('commission:Urls_work_list'))

@never_cache
@require_http_methods(["GET", "POST"])
def ViewFn_work_edit(request, view_fn_work_id):
    # 待修BUG：
    # ．分次加入圖檔時，只有最後一次加的圖才被寫入資料庫
    # ．從原始檔上傳的圖片還無法於模板控制刪除或替換再傳入views
    # ．(已解決)上傳未滿5張圖時，會重複上傳
    if request.method == 'POST':
        try:
            with transaction.atomic():
                view_db_work_info_id = get_object_or_404(DbWorkInfo, work_id=view_fn_work_id)
                
                # 用於追蹤已處理的檔案
                processed_files = set()

                # 處理重命名的檔案
                renamed_files = request.POST.get('renamed_files', '')
                if renamed_files:
                    try:
                        renamed_files_list = json.loads(renamed_files)
                        for old_name, new_name in renamed_files_list:
                            # 檢查是否為已存在的檔案
                            existing_file = DbWorkOriginalFile.objects.filter(
                                work=view_db_work_info_id,
                                original_file_url=old_name
                            ).first()
                            
                            if existing_file:
                                # 處理已存在檔案的重命名
                                old_path = os.path.join('commission', 'workID_file', str(view_fn_work_id), old_name)
                                new_path = os.path.join('commission', 'workID_file', str(view_fn_work_id), new_name)
                                
                                if default_storage.exists(old_path):
                                    # 讀取舊檔案內容
                                    with default_storage.open(old_path, 'rb') as old_file:
                                        # 儲存為新檔案
                                        default_storage.save(new_path, old_file)
                                    # 刪除舊檔案
                                    default_storage.delete(old_path)
                                    
                                    # 更新資料庫記錄
                                    existing_file.original_file_url = new_name
                                    existing_file.save()
                            else:
                                # 處理新上傳檔案的重命名
                                for file in request.FILES.getlist('original_files'):
                                    if file.name == old_name:
                                        # 使用新檔名保存檔案
                                        save_path = os.path.join('commission', 'workID_file', str(view_fn_work_id))
                                        os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)
                                        
                                        full_path = os.path.join(save_path, new_name)
                                        default_storage.save(full_path, file)
                                        
                                        # 寫入資料庫
                                        DbWorkOriginalFile.objects.create(
                                            work=view_db_work_info_id,
                                            original_file_url=new_name
                                        )
                                        # 將檔案標記為已處理
                                        processed_files.add(file.name)
                                        break
                                
                    except json.JSONDecodeError:
                        # 如果JSON解析失敗，忽略重命名操作
                        pass

                # 處理未重命名的新上傳檔案
                if 'original_files' in request.FILES:
                    # 建立儲存路徑
                    save_path = os.path.join('commission', 'workID_file', str(view_fn_work_id))
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)
                    
                    # 處理每個上傳的原始檔案
                    for file in request.FILES.getlist('original_files'):
                        # 跳過已處理的檔案
                        if file.name in processed_files:
                            continue
                            
                        # 生成唯一檔名
                        filename = file.name
                        unique_name = f"{int(time.time())}_{filename}"
                        
                        # 儲存檔案
                        full_path = os.path.join(save_path, unique_name)
                        default_storage.save(full_path, file)
                        
                        # 寫入資料庫
                        DbWorkOriginalFile.objects.create(
                            work=view_db_work_info_id,
                            original_file_url=unique_name
                        )

                # 處理刪除的原始檔案
                deleted_files = request.POST.get('deleted_original_files', '')
                if deleted_files:
                    try:
                        deleted_files_list = json.loads(deleted_files)
                        for filename in deleted_files_list:
                            # 刪除資料庫記錄
                            DbWorkOriginalFile.objects.filter(
                                work=view_db_work_info_id,
                                original_file_url=filename
                            ).delete()
                            
                            # 刪除實際檔案
                            file_path = os.path.join('commission', 'workID_file', str
                            (view_fn_work_id), filename)
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                    except json.JSONDecodeError:
                        # 如果 JSON 解析失敗，忽略刪除操作
                        pass
                
                # 處理刪除圖片
                if 'deleted_images' in request.POST:
                    deleted_images = json.loads(request.POST['deleted_images'])

                    for image_name in deleted_images:
                        # 刪除資料庫記錄
                        DbWorkImages.objects.filter(
                            work_id=view_fn_work_id,
                            image_url=image_name
                        ).delete()

                        

                        # 刪除實際檔案
                        file_path = os.path.join('commission', 'workID_img', image_name)
                        if default_storage.exists(file_path):
                            default_storage.delete(file_path)
                    

                    # 重新排序剩餘圖片
                    remaining_images = DbWorkImages.objects.filter(
                        work_id=view_fn_work_id
                    ).order_by('step')
                    

                    # 更新每張圖片的序號和檔名
                    for new_step, image in enumerate(remaining_images, 1):
                        # 取得舊檔名的副檔名
                        old_extension = Path(image.image_url).suffix
                        # 產生新檔名
                        new_filename = f"{view_fn_work_id}_sketch{new_step}{old_extension}"
                        

                        # 如果檔名需要更改
                        if image.image_url != new_filename:
                            # 重命名實際檔案
                            old_path = os.path.join('commission', 'workID_img', image.image_url)
                            new_path = os.path.join('commission', 'workID_img', new_filename)
                            

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
                if 'work_title' in request.POST:
                    view_db_work_info_id.work_title = request.POST['work_title']
                if 'work_category' in request.POST:
                    view_db_work_info_id.work_category = request.POST['work_category']

                if 'work_description' in request.POST:
                    view_db_work_info_id.work_description = request.POST['work_description']
                if 'work_original_from' in request.POST:
                    view_db_work_info_id.work_original_from = request.POST['work_original_from']
                if 'work_price' in request.POST:

                    view_db_work_info_id.work_price = request.POST['work_price']
                if 'deadline' in request.POST:
                    view_db_work_info_id.deadline = request.POST['deadline']
                # 調試輸出

                # print("POST data:", request.POST)
                # print("Original status:", view_db_work_info_id.work_status)
                

                if 'work_status' in request.POST:
                    # 獲取 work_status 的第一個值（因為 radio 按鈕應該只有一個值），不知道什麼原因 'work_status'會接收到多個值


                    view_db_work_info_id.work_status = request.POST.getlist('work_status')[0].strip()
                    # view_db_work_info_id.work_status = request.POST['work_status']                    

                # 更新 case_by_need 欄位
                if 'case_by_need' in request.POST:
                    # 檢查輸入的需求案ID是否存在
                    need_id = request.POST['case_by_need']
                    if need_id:  # 如果有輸入值
                        try:
                            # 嘗試查找對應的需求案
                            need_exists = DbNeedInfo.objects.filter(need_id=need_id).exists()
                            if need_exists:
                                view_db_work_info_id.case_by_need = need_id
                            else:
                                view_db_work_info_id.case_by_need = None
                        except ValueError:
                            # 如果輸入的不是有效的數字，設為 None
                            view_db_work_info_id.case_by_need = None
                    else:
                        # 如果輸入為空，設為 None
                        view_db_work_info_id.case_by_need = None

                # 處理圖片上傳
                if 'work_ex_image' in request.FILES:
                    uploaded_files = request.FILES.getlist('work_ex_image')

                    # 獲取現有的圖片記錄
                    existing_images = DbWorkImages.objects.filter(work_id=view_fn_work_id).order_by('step')
                    current_step = existing_images.count()

                    if current_step >= 5:
                        # 當已有5張圖片時，依序替換
                        for index, file in enumerate(uploaded_files):
                            if index < 5 and file.content_type.startswith('image/'):  # 確認是圖片檔案
                                # 找到要替換的圖片記錄
                                image_record = existing_images[index]
                                
                                # 刪除舊檔案
                                old_file_path = os.path.join('commission', 'workID_img', image_record.image_url)
                                if default_storage.exists(old_file_path):
                                    default_storage.delete(old_file_path)
                                
                                # 加上浮水印
                                watermarked_file = add_watermark(file)

                                # 使用新文件的副檔名
                                new_extension = Path(file.name).suffix
                                new_filename = f"{view_fn_work_id}_sketch{image_record.step}{new_extension}"
                                
                                # 儲存新檔案
                                file_path = os.path.join('commission', 'workID_img', new_filename)
                                default_storage.save(file_path, watermarked_file)
                                
                                # 更新資料庫記錄
                                image_record.image_url = new_filename
                                image_record.save()
                    else:
                        # 只處理前5張上傳的文件
                        files_to_process = [f for f in uploaded_files[:5 - current_step] if f.content_type.startswith('image/')]

                        # 處理新上傳的檔案
                        for index, file in enumerate(files_to_process, start=current_step + 1):
                            # 加上浮水印
                            watermarked_file = add_watermark(file)
                        
                            # 取得檔案副檔名
                            new_extension = Path(file.name).suffix
                        
                            # 生成新檔名
                            new_filename = f"{view_fn_work_id}_sketch{index}{new_extension}"
                        
                            # 儲存新檔案
                            file_path = os.path.join('commission', 'workID_img', new_filename)
                            default_storage.save(file_path, watermarked_file)
                        
                            # 更新資料庫
                            image_record = DbWorkImages.objects.create(
                                work_id=view_db_work_info_id.work_id,
                                step=index,
                                image_url=new_filename
                            )

                            image_record.save()


                # 處理替換的圖片
                if 'replaced_images' in request.POST:
                    replaced_images = json.loads(request.POST['replaced_images'])
                    for replacement in replaced_images:
                        original_filename = replacement['original']
                        new_file = request.FILES[f'replacement_file_{replacement["index"]}']
                        
                        # 找到要替換的圖片記錄
                        image_record = DbWorkImages.objects.get(
                            work_id=view_fn_work_id,
                            image_url=original_filename
                        )
                        

                        # 刪除舊檔案
                        old_file_path = os.path.join('commission', 'workID_img', original_filename)
                        if default_storage.exists(old_file_path):
                            default_storage.delete(old_file_path)
                        

                        # 使用新文件的副檔名
                        new_extension = Path(new_file.name).suffix
                        new_filename = f"{view_fn_work_id}_sketch{image_record.step}{new_extension}"
                        

                        # 儲存新檔案
                        file_path = os.path.join('commission', 'workID_img', new_filename)
                        default_storage.save(file_path, new_file)
                        

                        # 更新資料庫記錄
                        image_record.image_url = new_filename
                        image_record.save()
                    print("New status:", request.POST['work_status'])
                # 更新 last_update
                view_db_work_info_id.last_update = timezone.now()
                view_db_work_info_id.save()
                

                # 驗證保存後的狀態
                updated_work = DbWorkInfo.objects.get(work_id=view_fn_work_id)
                print("Saved status:", updated_work.work_status)
                

                return JsonResponse({
                    'status': 'success',
                    'message': '更新成功',
                    'last_update': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'work_status': updated_work.work_status,  # 在回應中也包含更新後的狀態
                    'case_by_need': view_db_work_info_id.case_by_need  # 在回應中包含更新後的需求案ID
                })
            

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    # GET 請求的處理
    view_db_work_info_id = get_object_or_404(DbWorkInfo, work_id=view_fn_work_id)
    

    # 獲取對應的 PublicCardInfo
    view_db_publiccard_info = get_object_or_404(DbPublicCardInfo, member_basic_id=view_db_work_info_id.worker_id)
    

    # 將截止時間轉換為當前時區
    if view_db_work_info_id.deadline:
        view_db_work_info_id.deadline = timezone.localtime(view_db_work_info_id.deadline)
    

    view_db_work_sketches = DbWorkImages.objects.filter(work_id=view_fn_work_id).order_by('step')
    

    # 查詢原始檔案
    original_files = DbWorkOriginalFile.objects.filter(work_id=view_fn_work_id).values('work_id', 'original_file_url')

    # 將 original_files 轉換為 JSON 格式
    original_files_json = json.dumps(list(original_files))

    # 計算剩餘的灰色加號DIV數量
    remaining_placeholders = max(0, 5 - view_db_work_sketches.count())

    context = {
        'ViewKey_DbWorkInfo_work_id': view_db_work_info_id,
        'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
        'ViewKey_DbWorkEdit_sketches': view_db_work_sketches,
        'remaining_placeholders': range(remaining_placeholders),
        'original_files_json': original_files_json,
    }


    return render(request, 'commission/work_edit.html', context)

# 接案編輯頁-原始檔圖片DPI資訊API端點
def ViewFn_image_info_api(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        try:
            # 使用PIL開啟圖片
            img = Image.open(image_file)
            
            # 獲取DPI資訊並進行更詳細的處理
            dpi = img.info.get('dpi')
            
            # 如果找不到dpi，嘗試其他可能的metadata key
            if dpi is None:
                # 某些圖片可能使用不同的key儲存DPI資訊
                resolution = img.info.get('resolution', (72, 72))
                dpi = resolution
            
            # 確保dpi是tuple且包含兩個數值
            if not isinstance(dpi, tuple) or len(dpi) != 2:
                dpi = (72, 72)
            
            # 確保數值是整數
            dpi_x = int(round(dpi[0]))
            dpi_y = int(round(dpi[1]))
            
            # 輸出除錯資訊到伺服器日誌
            # print(f"Image info - Size: {img.size}, DPI: {dpi}, Format: {img.format}")
            # print(f"Image metadata: {img.info}")
            
            response_data = {
                'width': img.width,
                'height': img.height,
                'dpi_x': dpi_x,
                'dpi_y': dpi_y,
                'format': img.format,
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")  # 輸出錯誤到伺服器日誌
            return JsonResponse({
                'error': str(e),
                'message': '無法讀取圖片DPI資訊'
            }, status=400)
            
    return JsonResponse({'error': '無效的請求'}, status=400)

# 接案編輯頁-壓縮檔資訊API端點
@csrf_exempt  # 如果你想要跳過 CSRF 驗證（不建議用在生產環境）
def ViewFn_archive_info_api(request):
    if request.method == 'POST' and request.FILES:
        archive_file = request.FILES.get('archive')
        if not archive_file:
            return JsonResponse({
                'success': False,
                'error': '未找到上傳的檔案'
            })
            
        file_list = []
        
        try:
            # 根據檔案類型使用不同的處理方法
            if archive_file.name.lower().endswith('.zip'):
                with zipfile.ZipFile(archive_file) as zf:
                    file_list = [f for f in zf.namelist() if not f.endswith('/')]
            
            elif archive_file.name.lower().endswith('.7z'):
                # 需要先將檔案寫入臨時檔案
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    for chunk in archive_file.chunks():
                        tmp_file.write(chunk)
                    tmp_file.flush()
                    
                try:
                    with py7zr.SevenZipFile(tmp_file.name, 'r') as sz:
                        file_list = [f for f in sz.getnames() if not f.endswith('/')]
                finally:
                    # 確保清理臨時檔案
                    os.unlink(tmp_file.name)
            
            elif archive_file.name.lower().endswith('.rar'):
                # 需要先將檔案寫入臨時檔案
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    for chunk in archive_file.chunks():
                        tmp_file.write(chunk)
                    tmp_file.flush()
                    
                try:
                    with rarfile.RarFile(tmp_file.name) as rf:
                        file_list = [f for f in rf.namelist() if not f.endswith('/')]
                finally:
                    # 確保清理臨時檔案
                    os.unlink(tmp_file.name)
            
            return JsonResponse({
                'success': True,
                'files': file_list
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': '無效的請求'
    }, status=400)

# 接案編輯頁-選擇投稿需求案id之API端點
def ViewFn_need_info_api(request):
    need_info = DbNeedInfo.objects.all().values(
        'need_id', 
        'need_title', 
        'need_category', 
        'need_original_from'
    )
    return JsonResponse(list(need_info), safe=False)

# 接案編輯頁-浮水印處理函式
def add_watermark(image_file, watermark_text="UPLOAD IN\nACGN PROJECT", position=(10, 10), vertical_stretch=2.0):
    """
    watermark_text 使用 \n 來分行
    vertical_stretch 如果需要垂直拉伸，調整此參數(預設1.0為不拉伸)
    """
    with Image.open(image_file) as image:
        image = image.convert("RGBA")

        # 建立浮水印圖層
        watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)

        # 先初始化 default_font，避免cannot access local variable 'default_font' where it is not associated with a value未定義的問題
        default_font = None
        # 設定字型與大小
        try:
            # 嘗試載入支援粗體的字型
            font_path = os.path.join(settings.BASE_DIR, "media", "commission", "workID_img", "COLONNA.TTF")
            font = ImageFont.truetype(font_path, 100)
        except Exception as e:
            print(f"無法載入指定字型，使用預設字型: {str(e)}")
            default_font = ImageFont.load_default()
            
            try:
                font = ImageFont.truetype("arial", 60)
            except Exception:
                font = default_font

        # 計算文字尺寸 (若有換行使用 multiline_textbbox)
        if "\n" in watermark_text:
            spacing = 10  # 可調整行間距
            text_box = draw.multiline_textbbox((0, 0), watermark_text, font=font, spacing=spacing)
        else:
            spacing = 0
            text_box = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]

        # 依 vertical_stretch 拉伸文字遮罩 (只影響高度)
        stretched_height = int(text_height * vertical_stretch)

        # 建立文字遮罩 (灰階)
        text_mask = Image.new("L", (text_width, text_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        if "\n" in watermark_text:
            # 使用 align="center" 使每一行文字在遮罩內水平置中對齊
            mask_draw.multiline_text((0, 0), watermark_text, fill=255, font=font, spacing=spacing, align="center")
        else:
            mask_draw.text((0, 0), watermark_text, fill=255, font=font)

        # 垂直拉伸文字遮罩
        if vertical_stretch != 1: # 避免不必要的縮放
            text_mask = text_mask.resize((text_width, stretched_height), Image.Resampling.NEAREST) # 使用 NEAREST 保持銳利

        # 計算放置位置，使文字遮罩置中於影像中
        x = (image.size[0] - text_width) // 2
        y = (image.size[1] - (stretched_height if vertical_stretch != 1 else text_height)) // 2

        # 建立顏色圖層 (可調整顏色與透明度)
        color_layer = Image.new("RGBA", text_mask.size, (0, 0, 0, 50))
        # 將顏色圖層貼到浮水印圖層，使用文字遮罩作為透明度蒙版
        watermark.paste(color_layer, (x, y), mask=text_mask)


        # 可加旋轉或其他效果（例如45度旋轉）
        watermark = watermark.rotate(45, expand=True)
        watermark = watermark.resize(image.size)

        # 合併原始圖片與浮水印圖層
        watermarked_image = Image.alpha_composite(image, watermark)

        # 輸出處理後的圖片內容
        output = io.BytesIO()
        watermarked_image.convert("RGB").save(output, format="JPEG", quality=95)
        return ContentFile(output.getvalue())

def ViewFn_publiccard_list(request):
    view_db_publiccard_info = DbPublicCardInfo.objects.all()
    

    # 獲取排序參數
    sort_by = request.GET.get('sort', 'last_update')  # 預設按最後更新排序
    sort_direction = request.GET.get('direction', 'desc')  # 預設降序
    
    # 搜尋功能
    search_term = request.GET.get('searchorders', '')
    search_column = request.GET.get('column', 'option-1')
    
    if search_term:
        if search_column == 'option-1':  # 全部
            # 使用 CAST 將 user_id 轉換為字符串進行比對
            view_db_publiccard_info = view_db_publiccard_info.filter(
                Q(member_basic__user_id__contains=search_term) |  # ID部分匹配
                Q(user_nickname__icontains=search_term) |         # 名片暱稱模糊匹配
                Q(user_introduction__icontains=search_term)       # 簡介模糊匹配
            )
        elif search_column == 'title':  # 使用者ID
            # 只進行 ID 的部分匹配
            view_db_publiccard_info = view_db_publiccard_info.filter(
                member_basic__user_id__contains=search_term
            )
        elif search_column == 'category':  # 名片暱稱
            view_db_publiccard_info = view_db_publiccard_info.filter(
                user_nickname__icontains=search_term
            )
        elif search_column == 'description':  # 簡介
            view_db_publiccard_info = view_db_publiccard_info.filter(
                user_introduction__icontains=search_term
            )

    # 應用排序
    if sort_by == 'last_update':
        order_field = '-last_update' if sort_direction == 'desc' else 'last_update'
    else:  # user_id
        order_field = '-member_basic_id' if sort_direction == 'desc' else 'member_basic_id'
    
    view_db_publiccard_info = view_db_publiccard_info.order_by(order_field)
    
    # 根據狀態篩選
    view_fn_status = request.GET.get('status')
    if view_fn_status and view_fn_status != 'all':
        view_db_publiccard_info = view_db_publiccard_info.filter(card_status=view_fn_status)

    # 分頁
    paginator = Paginator(view_db_publiccard_info, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'sort_by': sort_by,
        'sort_direction': sort_direction,
        'search_term': search_term,
        'search_column': search_column
    }
    return render(request, 'commission/publiccard_list.html', context)

@never_cache
def ViewFn_publiccard_edit(request, view_fn_publiccard_id):
    view_db_publiccard_info = get_object_or_404(DbPublicCardInfo, pk=view_fn_publiccard_id)

    # === 初始化顯示相關 ===
    # 獲取該用戶的價目表資料
    view_db_publiccard_sell = DbPublicCardSell.objects.filter(user=view_db_publiccard_info).order_by('sell_step')
    
    # 預處理價目表數據，確保圖片欄位為None時轉換為空列表
    for item in view_db_publiccard_sell:
        item.sell_example_image_1 = item.sell_example_image_1 or ""
        item.sell_example_image_2 = item.sell_example_image_2 or ""
    
    # 獲取該用戶的作品列表，並預加載相關的圖片
    view_db_work_info = DbWorkInfo.objects.filter(
        worker_id=view_db_publiccard_info.member_basic_id
    ).prefetch_related(
        'dbworkimages_set'  # 預加載關聯的圖片
    ).order_by('-publish_time')  # 使用 publish_time 進行排序
        
    # 獲取該用戶的需求列表，並預加載相關的圖片
    view_db_need_info = DbNeedInfo.objects.filter(
        needer_id=view_db_publiccard_info.member_basic_id
    ).prefetch_related(
        'dbneedimages_set'  # 預加載關聯的圖片
    ).order_by('-publish_time')  # 使用 publish_time 進行排序
    
    # 動態判斷模板路徑
    url_name = request.resolver_match.url_name
    if url_name != 'Urls_publiccard_edit':
        # 如果不是主編輯頁面，則使用測試目錄下的對應模板
        template_name = f'commission/publiccard_edit_test/{url_name}.html'
    else:
        template_name = 'commission/publiccard_edit.html'

    # === 資料寫入相關 ===
    if request.method == 'POST':
        try:
            # 取得主要資料物件
            public_card = DbPublicCardInfo.objects.get(pk=view_fn_publiccard_id)
            
            # === 一般資料寫入 ===
            # 通用欄位處理
            field_mapping = {
                'ViewKey_bd_public_card_info_user_nickname': 'user_nickname',
                'ViewKey_bd_public_card_info_user_introduction': 'user_introduction',
                'ViewKey_bd_public_card_info_card_status': 'card_status', # 提交表單-公開/非公開
                # 添加其他需要處理的欄位...
            }
            
            # 通用開關處理(新增部分)
            # 對應template的<input>開關name屬性
            switch_mapping = {
                'ViewKey_bd_public_card_info_use_default_avatar': 'use_default_avatar',
                'ViewKey_bd_public_card_info_use_default_banner': 'use_default_banner',
                'ViewKey_bd_public_card_info_switch-sell': 'sell_public_status',
                'ViewKey_bd_public_card_info_switch-work-sellnow': 'work_sellnow_list_public_status',
                'ViewKey_bd_public_card_info_switch-work-done': 'work_done_list_public_status',
                'ViewKey_bd_public_card_info_switch-need-list': 'need_list_public_status'
            }
            
            # 處理普通文字欄位
            for form_field, model_field in field_mapping.items():
                if form_field in request.POST:
                    setattr(public_card, model_field, request.POST[form_field])
            
            # 處理開關欄位
            for form_field, model_field in switch_mapping.items():
                # 對於頭像與橫幅的開關，反向處理
                if form_field in ['ViewKey_bd_public_card_info_use_default_avatar', 'ViewKey_bd_public_card_info_use_default_banner']:
                    switch_state = form_field not in request.POST  # 反向處理
                else:
                    switch_state = form_field in request.POST  # 正常處理

                setattr(public_card, model_field, switch_state)  # 設置狀態

            # === 圖檔寫入 ===
            # 通用檔案處理邏輯
            file_field_mapping = {
                # 以template的隱藏文件輸入元素<input type="file">的name屬性為key
                'avatar': {
                    'model_field': 'user_avatar',
                    'save_path': 'commission/publiccard/avatar',
                    'filename_pattern': f'{public_card.member_basic_id}_avatar'
                },
                'banner': {
                    'model_field': 'card_banner',
                    'save_path': 'commission/publiccard/banner',
                    'filename_pattern': f'{public_card.member_basic_id}_banner'
                }
            }
            
            for file_field, config in file_field_mapping.items():
                if file_field in request.FILES:
                    uploaded_file = request.FILES[file_field]
                    
                    # 刪除舊檔案
                    old_file = getattr(public_card, config['model_field'])
                    if old_file:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, str(old_file))
                        if os.path.isfile(old_file_path):
                            os.remove(old_file_path)
                    
                    # 生成新檔名
                    file_ext = uploaded_file.name.split('.')[-1]
                    new_filename = f"{config['filename_pattern']}.{file_ext}"
                    
                    # 組合完整儲存路徑
                    full_path = os.path.join(settings.MEDIA_ROOT, config['save_path'])
                    os.makedirs(full_path, exist_ok=True)
                    
                    # 儲存檔案
                    with open(os.path.join(full_path, new_filename), 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    
                    # 更新資料庫欄位(修改部分)
                    setattr(public_card, config['model_field'], new_filename)  # 只儲存檔名

            # === 小卡公開狀態處理 ===
            # 通用狀態處理邏輯（可擴展到不同類型）
            status_patterns = {
                'need': ('needStatus', DbNeedInfo, 'needer_id'),
                'work': ('workStatus', DbWorkInfo, 'worker_id')  
            }
            
            for prefix, model, user_field in status_patterns.values():
                # 過濾出符合前綴的POST參數
                status_fields = [k for k in request.POST if k.startswith(prefix)]
                for field in status_fields:
                    item_id = field.replace(prefix, '')
                    try:
                        # 驗證資料所屬權限
                        instance = model.objects.get(
                            **{f"{model._meta.pk.name}": item_id},
                            **{f"{user_field}": public_card.member_basic_id}
                        )
                        new_status = request.POST[field] == 'public'
                        if instance.public_status != new_status:
                            instance.public_status = new_status
                            instance.save(update_fields=['public_status'])
                    except (ValueError, model.DoesNotExist):
                        pass
                    
            # === 提交表單按鈕-名片公開/非公開的設定 ===
            card_status = request.POST.get('card_status', '非公開')  # 默認值
            public_card.card_status = card_status

            # 加入最後更新時間
            public_card.last_update = timezone.now()

            # 保存變更
            public_card.save()
            
            # === 新增價目表處理部分 ===
            # 處理價目表資料
            try:
                # 1. 獲取提交的所有價目表項目
                sell_items_data = {}
                for key in request.POST:
                    if key.startswith('sell_') and '_item_' in key:
                        parts = key.split('_item_')
                        if len(parts) == 2:
                            field_prefix = parts[0]
                            item_id = parts[1]
                            
                            # 過濾掉臨時ID中的特殊字符
                            item_id = re.sub(r'[^a-zA-Z0-9_]', '', item_id)
                            
                            field_name = field_prefix.replace('sell_', '')
                            
                            if item_id not in sell_items_data:
                                sell_items_data[item_id] = {}
                            
                            sell_items_data[item_id][field_name] = request.POST[key]
                
                # 2. 處理現有的價目表項目
                existing_items = {str(item.sell_list_id): item for item in DbPublicCardSell.objects.filter(user=public_card)}
                
                # 3. 根據處理順序設置 step 值
                for step, (item_id, data) in enumerate(sell_items_data.items(), 1):
                    if 'title' not in data or not data['title'].strip():
                        continue
                    
                    # 判斷是否為新項目
                    is_new_item = item_id.startswith('new')
                    if not is_new_item and item_id in existing_items:
                        # 更新現有項目
                        sell_item = existing_items[item_id]
                    else:
                        # 創建新項目
                        sell_item = DbPublicCardSell(user=public_card)
                    
                    # 設置步驟值
                    sell_item.sell_step = step
                    
                    # 設置其他字段
                    sell_item.sell_title = data.get('title', '')
                    sell_item.sell_description = data.get('description', '')
                    
                    try:
                        sell_item.sell_price = int(data.get('price', 0))
                    except (ValueError, TypeError):
                        sell_item.sell_price = 0
                    
                    # 保存項目
                    sell_item.save()
                
                # 4. 處理要刪除的項目
                submitted_ids = {k for k in sell_items_data.keys() if not k.startswith('new')}
                items_to_delete = set(existing_items.keys()) - submitted_ids
                for item_id in items_to_delete:
                    existing_items[item_id].delete()

            except Exception as e:
                print(f"Error processing sell items: {str(e)}")  # 調試信息
            
            # 根據請求類型返回不同回應
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': '儲存成功'})
            else:
                return redirect(reverse('commission:Urls_publiccard_edit', args=[view_fn_publiccard_id]))
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            else:
                # 處理非AJAX請求的錯誤顯示
                context = {
                    'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
                    'ViewKey_DbPublicCardSell': view_db_publiccard_sell,
                    'ViewKey_DbWorkInfo': view_db_work_info,
                    'ViewKey_DbNeedInfo': view_db_need_info,
                    'error_message': str(e)
                }
                return render(request, template_name, context)
    
    # GET請求保持原有邏輯...
    # ... 保持原有context設定和render部分不變 ...
    context = {
        'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
        'ViewKey_DbPublicCardSell': view_db_publiccard_sell,
        'ViewKey_DbWorkInfo': view_db_work_info,
        'ViewKey_DbNeedInfo': view_db_need_info,
    }
    return render(request, template_name, context)

# 名片頁-公開案件(公開販售作品、已成交作品、發起過的需求)篩選器的通用API端點
@require_POST
def ViewFn_filter_items(request):
    data = json.loads(request.body)
    search_term = data.get('searchTerm', '') # 用來存儲用戶在搜尋欄中輸入的關鍵字。是用來過濾資料的主要依據
    table_type = data.get('tableType', '') # 用來指定要過濾的資料表類型，例如 "need" 或 "work"
    id_field = data.get('idField', '') # 用來指定要返回的 ID 欄位名稱。對於需求資料表來說，這通常是 need_id，而對於作品資料表則是 work_id
    search_fields = data.get('searchFields', []) # 對應模板的data-search-fields="資料庫欄位名稱,資料庫欄位名稱,..."，要擴大搜尋範圍直接從template新增前者欄位就好，不用修改views
    user_id = data.get('userId', '')  # 用戶ID參數
    
    # print(f"Search parameters: term='{search_term}', table='{table_type}', user_id='{user_id}'")
    
    model_map = {
        'need': DbNeedInfo,
        'work': DbWorkInfo
    }
    
    model = model_map.get(table_type)
    if not model:
        return JsonResponse({'error': 'Invalid table type'}, status=400)
    
    # 構建基本查詢，限制只查詢當前用戶的數據
    base_query = {
        'need': lambda uid: Q(needer_id=uid),
        'work': lambda uid: Q(worker_id=uid)
    }
    
    # 先過濾用戶的數據
    query = base_query[table_type](user_id)
    
    # 再加入搜索條件
    if search_term:
        search_query = Q()
        for field in search_fields:
            search_query |= Q(**{f"{field}__icontains": search_term})
        query &= search_query
    
    # 執行查詢
    matching_ids = list(model.objects.filter(query).values_list(id_field, flat=True))
    # print(f"Found matching IDs for user {user_id}: {matching_ids}")
    
    return JsonResponse(matching_ids, safe=False)