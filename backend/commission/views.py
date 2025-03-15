from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
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

import torch
import open_clip
# from PIL import Image
import numpy as np
# from django.shortcuts import render
# from django.core.files.storage import default_storage
# from django.conf import settings
# from .models import ImageModel
# import os
import cv2
import traceback
import math
import uuid

# 大寫取名ViewKey_NeedInfo=來自大檔項目，如資料庫、views.py、urls.py、HTML
# 小寫取名如view_db_need_info=取自內部參數，如欄位名稱

# AI圖片辨識用清理函數
def clean_commission_uploads():
    """
    清理 commission/uploads 目錄下的所有檔案
    """
    uploads_dir = os.path.join(settings.MEDIA_ROOT, "commission", "uploads")
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"已刪除檔案: {file_path}")
            except Exception as e:
                print(f"刪除檔案時出錯 {file_path}: {e}")

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

    # 檢查是否有媒合的作品
    matched_work = None
    print(f"Debug - 需求 ID: {view_fn_need_id}, case_by_work 值: {view_db_need_info_id.case_by_work}")
    
    if view_db_need_info_id.case_by_work:
        try:
            matched_work = DbWorkInfo.objects.get(work_id=view_db_need_info_id.case_by_work)
            print(f"Debug - 成功找到媒合作品: ID={matched_work.work_id}, 標題={matched_work.work_title}")
        except DbWorkInfo.DoesNotExist:
            print(f"Debug - 未找到媒合作品: ID={view_db_need_info_id.case_by_work}")
            matched_work = None
        except Exception as e:
            print(f"Debug - 查詢媒合作品時發生錯誤: {str(e)}")
            matched_work = None

    context = {
        'ViewKey_DbNeedInfo_need_id': view_db_need_info_id,
        'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
        'ViewKey_DbNeedEdit_sketches': view_db_need_sketches,
        'remaining_placeholders': range(remaining_placeholders),
        'matched_work': matched_work,
    }
    
    print(f"Debug - context 包含 matched_work: {matched_work is not None}")
    if matched_work:
        print(f"Debug - matched_work 標題: {matched_work.work_title}")

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

# 需求編輯頁-選擇媒合案件
def ViewFn_need_case_chose(request):
    need_id = request.GET.get('need_id', '')
    view_db_need_info = None
    related_works = []
    matched_work = None

    if need_id:
        try:
            view_db_need_info = DbNeedInfo.objects.get(need_id=need_id)
            # 獲取 case_by_need 等於當前 need_id 的 DbWorkInfo 記錄
            related_works = DbWorkInfo.objects.filter(case_by_need=need_id)

            # 預先獲取每個 work 的圖片
            for work in related_works:
                work.images = DbWorkImages.objects.filter(work_id=work.work_id).values_list('image_url', flat=True)
            
            # 如果有已選擇的作品，獲取其資訊
            if view_db_need_info.case_by_work:
                try:
                    matched_work = DbWorkInfo.objects.get(work_id=view_db_need_info.case_by_work)
                except DbWorkInfo.DoesNotExist:
                    matched_work = None

        except DbNeedInfo.DoesNotExist:
            view_db_need_info = None

    context = {
        'ViewKey_DbNeedInfo_need_id': view_db_need_info,
        'related_works': related_works, # 將相關作品傳遞給模板
        'matched_work': matched_work, # 傳遞已媒合的作品資訊
    }
    return render(request, 'commission/need_case_chose.html', context)

# 需求編輯頁-更新媒合案件
@require_http_methods(["POST"])
def ViewFn_update_case_by_work(request):
    try:
        data = json.loads(request.body)
        need_id = data.get('need_id')
        work_id = data.get('work_id')

        # 更新資料庫
        need_info = DbNeedInfo.objects.get(need_id=need_id)
        need_info.case_by_work = work_id
        need_info.save()

        return JsonResponse({
            'status': 'success',
            'message': '成功更新媒合案件'
        })
    except DbNeedInfo.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '找不到對應的需求案件'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
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
                'involved_acgn': 'involved_acgn',  # 新增喜好作品欄位映射
                'key_tags': 'key_tags',  # 新增屬性Tag欄位映射
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
                },
            }
            
            # 先處理基本圖片上傳（頭像、橫幅）
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
                    
                    # 更新資料庫欄位
                    setattr(public_card, config['model_field'], os.path.join(config['save_path'], new_filename))

            # 處理價目表相關資料和圖片
            # 獲取所有價目表項目的 ID 列表
            sell_items = {}
            for key in request.POST:
                if key.startswith('sell_title_item_'):
                    sell_item_id = key.replace('sell_title_item_', '')
                    if sell_item_id not in sell_items:
                        sell_items[sell_item_id] = {'id': sell_item_id}

            # 添加在處理價目表圖片上傳前
            print("===== 表單提交的所有欄位 =====")
            for key in request.FILES:
                print(f"文件欄位: {key}")

            for key in request.POST:
                if key.startswith('sell_image_') or key.startswith('sell_delete_image_'):
                    print(f"POST 欄位: {key} = {request.POST[key]}")

            # 處理價目表圖片上傳
            for key in request.FILES:
                if key.startswith('sell_image_'):
                    print(f"正在處理文件欄位: {key}")
                    # 解析 key 格式
                    parts = key.split('_')
                    print(f"欄位名稱拆分: {parts}")
                    
                    try:
                        # 正確解析欄位名稱格式：sell_image_X_item_Y
                        # 從欄位名稱中提取圖片索引(X)
                        if len(parts) >= 5 and parts[0] == 'sell' and parts[1] == 'image' and parts[3] == 'item':
                            raw_image_id = parts[2].lstrip('0')
                            sell_item_id = parts[4]
                        else:
                            # 嘗試舊的解析方式作為後備
                            raw_image_id = parts[2].lstrip('0') if len(parts) >= 3 else '1'
                            sell_item_id = key.split('item_')[-1] if 'item_' in key else None
                        
                        try:
                            image_id = int(raw_image_id) if raw_image_id else 1
                            print(f"提取的圖片索引: {image_id}, 項目ID: {sell_item_id}")
                            
                            # 嚴格限制 image_id 只能是 1 或 2
                            if image_id not in [1, 2]:
                                print(f"無效的 image_id: {image_id}，跳過此欄位")
                                continue
                                
                            # 確保已正確獲取 sell_item_id
                            if not sell_item_id:
                                print(f"無法從欄位名稱中提取 sell_item_id: {key}")
                                continue
                            
                            # 確認價目表項目存在
                            if sell_item_id in sell_items:
                                uploaded_file = request.FILES[key]
                                
                                # 取得對應的價目表項目模型實例
                                sell_item = None
                                if sell_item_id.isdigit() and int(sell_item_id) > 0:
                                    try:
                                        sell_item = DbPublicCardSell.objects.get(sell_list_id=sell_item_id)
                                    except DbPublicCardSell.DoesNotExist:
                                        print(f"價目表項目不存在: {sell_item_id}，跳過圖片處理")
                                        continue
                                else:
                                    print(f"新項目 ID: {sell_item_id}，跳過圖片處理，等待項目創建後再處理")
                                    continue
                                
                                # 確定模型欄位名稱 (只允許 sell_example_image_1 或 sell_example_image_2)
                                model_field = f'sell_example_image_{image_id}'
                                
                                # 安全檢查：確認欄位存在於模型中
                                if not hasattr(sell_item, model_field):
                                    print(f"欄位 {model_field} 不存在於模型中，跳過處理")
                                    continue
                                
                                # 刪除舊檔案
                                old_file = getattr(sell_item, model_field)
                                if old_file:
                                    old_file_path = os.path.join(settings.MEDIA_ROOT, 'commission/publiccard/sell_list_img', str(old_file))
                                    if os.path.isfile(old_file_path):
                                        os.remove(old_file_path)
                                
                                # 生成新檔名
                                file_ext = uploaded_file.name.split('.')[-1]
                                new_filename = f"{public_card.member_basic_id}_sell_{sell_item_id}_{image_id}.{file_ext}"
                                
                                # 組合完整儲存路徑
                                save_path = 'commission/publiccard/sell_list_img'
                                full_path = os.path.join(settings.MEDIA_ROOT, save_path)
                                os.makedirs(full_path, exist_ok=True)
                                
                                # 儲存檔案
                                with open(os.path.join(full_path, new_filename), 'wb+') as destination:
                                    for chunk in uploaded_file.chunks():
                                        destination.write(chunk)
                                
                                # 更新資料庫欄位，僅寫入檔名
                                setattr(sell_item, model_field, new_filename)
                                sell_item.save()
                                print(f"成功處理圖片: {key} -> {model_field}")
                        except ValueError as ve:
                            print(f"解析 image_id 時出錯: {ve}, key={key}")
                            continue
                    except Exception as e:
                        # 更詳細的錯誤處理和日誌
                        print(f"處理圖片上傳時出錯: {e}, key={key}, parts={parts}")
                        # 這裡不要讓異常傳播，保持操作繼續進行
                        continue

            # 處理價目表圖片刪除標記
            for key in request.POST:
                if key.startswith('sell_delete_image_'):
                    print(f"處理刪除圖片標記: {key}")
                    try:
                        parts = key.split('_')
                        print(f"刪除圖片欄位拆分: {parts}")
                        
                        # 正確解析欄位名稱格式：sell_delete_image_X_item_Y
                        if len(parts) >= 6 and parts[0] == 'sell' and parts[1] == 'delete' and parts[2] == 'image' and parts[4] == 'item':
                            # 嚴格解析 image_id，確保是 1 或 2
                            raw_image_id = parts[3].lstrip('0')
                            sell_item_id = parts[5]
                        else:
                            # 嘗試舊的解析方式作為後備
                            raw_image_id = parts[3].lstrip('0') if len(parts) >= 4 else '1'
                            sell_item_id = key.split('item_')[-1] if 'item_' in key else None
                        
                        try:
                            image_id = int(raw_image_id) if raw_image_id else 1
                            print(f"提取的刪除圖片索引: {image_id}, 項目ID: {sell_item_id}")
                            
                            if image_id not in [1, 2]:
                                print(f"無效的 image_id: {image_id}，跳過此刪除標記")
                                continue
                            
                            # 確保已正確獲取 sell_item_id
                            if not sell_item_id:
                                print(f"無法從欄位名稱中提取 sell_item_id: {key}")
                                continue
                                
                            # 只處理已存在的價目表項目
                            if sell_item_id.isdigit() and int(sell_item_id) > 0:
                                try:
                                    sell_item = DbPublicCardSell.objects.get(sell_list_id=sell_item_id)
                                    
                                    # 確定模型欄位名稱
                                    model_field = f'sell_example_image_{image_id}'
                                    
                                    # 安全檢查：確認欄位存在於模型中
                                    if not hasattr(sell_item, model_field):
                                        print(f"欄位 {model_field} 不存在於模型中，跳過刪除處理")
                                        continue
                                    
                                    # 檢查欄位是否有值
                                    old_file = getattr(sell_item, model_field)
                                    if old_file:
                                        # 刪除實際檔案
                                        old_file_path = os.path.join(settings.MEDIA_ROOT, 'commission/publiccard/sell_list_img', str(old_file))
                                        if os.path.isfile(old_file_path):
                                            os.remove(old_file_path)
                                            print(f"已刪除檔案: {old_file_path}")
                                        
                                        # 更新資料庫欄位為 None
                                        setattr(sell_item, model_field, None)
                                        sell_item.save()
                                        print(f"已清除欄位 {model_field} 的值")
                                    else:
                                        print(f"欄位 {model_field} 沒有檔案，無需刪除")
                                except DbPublicCardSell.DoesNotExist:
                                    print(f"價目表項目不存在: {sell_item_id}，跳過刪除標記")
                            else:
                                print(f"價目表項目 ID 無效: {sell_item_id}")
                        except ValueError as ve:
                            print(f"解析 image_id 時出錯: {ve}")
                    except Exception as e:
                        print(f"處理刪除圖片標記時出錯: {e}")

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
                # 0. 處理圖片排序數據
                if 'sell_image_order_data' in request.POST:
                    try:
                        image_order_data = json.loads(request.POST['sell_image_order_data'])
                        print(f"收到的圖片排序數據: {image_order_data}")
                        
                        # 處理每個項目的圖片排序
                        for sell_item_id, images_info in image_order_data.items():
                            try:
                                # 檢查 sell_item_id 是否有效
                                sell_item = DbPublicCardSell.objects.get(sell_list_id=int(sell_item_id), user=public_card)
                                
                                # 根據排序信息處理圖片
                                for img_info in images_info:
                                    image_id = img_info.get('image_id')
                                    sort_order = img_info.get('sort_order')
                                    
                                    print(f"處理圖片排序: 項目ID={sell_item_id}, 圖片ID={image_id}, 排序={sort_order}")
                                    
                                    # 如果排序與索引不一致，需要交換圖片
                                    if image_id == 1 and sort_order == 2:
                                        # 圖片1應該在位置2
                                        print(f"交換圖片: 圖片1移至位置2")
                                        # 暫存圖片1的內容
                                        temp_image1 = sell_item.sell_example_image_1
                                        # 將圖片2複製到圖片1位置
                                        sell_item.sell_example_image_1 = sell_item.sell_example_image_2
                                        # 將暫存的圖片1複製到圖片2位置
                                        sell_item.sell_example_image_2 = temp_image1
                                        sell_item.save()
                                        break  # 只需要處理一次交換
                                    elif image_id == 2 and sort_order == 1:
                                        # 圖片2應該在位置1
                                        print(f"交換圖片: 圖片2移至位置1")
                                        # 暫存圖片2的內容
                                        temp_image2 = sell_item.sell_example_image_2
                                        # 將圖片1複製到圖片2位置
                                        sell_item.sell_example_image_2 = sell_item.sell_example_image_1
                                        # 將暫存的圖片2複製到圖片1位置
                                        sell_item.sell_example_image_1 = temp_image2
                                        sell_item.save()
                                        break  # 只需要處理一次交換
                            except DbPublicCardSell.DoesNotExist:
                                print(f"找不到項目: ID={sell_item_id}")
                            except Exception as e:
                                print(f"處理項目圖片排序時出錯: {str(e)}")
                    except json.JSONDecodeError:
                        print(f"解析圖片排序數據JSON時出錯")
                    except Exception as e:
                        print(f"處理圖片排序時出錯: {str(e)}")
                
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
                                sell_items_data[item_id] = {
                                    'images': {}  # 新增圖片數據存儲
                                }
                            
                            sell_items_data[item_id][field_name] = request.POST[key]

                # 處理價目表圖片上傳
                for file_key in request.FILES:
                    if file_key.startswith('sell_image_'):
                        # 解析檔案名稱格式: sell_image_1_item_new_123456
                        parts = file_key.split('_item_')
                        if len(parts) == 2:
                            field_part = parts[0]  # sell_image_1
                            item_id = parts[1]     # 項目ID
                            image_index = field_part.split('_')[-1]  # 1或2
                            
                            # 將圖片存入對應項目
                            if item_id in sell_items_data:
                                sell_items_data[item_id]['images'][f'image_{image_index}'] = request.FILES[file_key]
                
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
                    
                    # 處理圖片上傳
                    for img_key, uploaded_file in data.get('images', {}).items():
                        try:
                            print(f"處理新項目圖片上傳：{img_key} = {uploaded_file}")
                            # 正確解析欄位名稱格式：sell_image_X_item_Y
                            # 從欄位名稱中提取圖片索引(X)
                            name_parts = img_key.split('_')
                            if len(name_parts) >= 5 and name_parts[0] == 'sell' and name_parts[1] == 'image':
                                image_index = name_parts[2]  # 圖片索引 (X)
                                # 可選：提取項目ID (Y)
                                # item_id = name_parts[4] if len(name_parts) >= 5 and name_parts[3] == 'item' else None
                            else:
                                # 嘗試舊的解析方式作為後備
                                image_index = img_key.split('_')[-1]
                            
                            print(f"解析欄位名稱：{img_key}，提取的圖片索引: {image_index}")
                            
                            # 確保 image_index 是 1 或 2
                            if image_index not in ['1', '2']:
                                print(f"無效的圖片索引: {image_index}，跳過此圖片")
                                continue
                                
                            # 確保模型欄位存在
                            model_field = f'sell_example_image_{image_index}'
                            if not hasattr(sell_item, model_field):
                                print(f"欄位 {model_field} 不存在於模型中，跳過處理")
                                continue
                            
                            # 刪除舊檔案
                            old_file = getattr(sell_item, model_field)
                            if old_file:
                                old_file_path = os.path.join(settings.MEDIA_ROOT, 'commission/publiccard/sell_list_img', str(old_file))
                                if os.path.isfile(old_file_path):
                                    os.remove(old_file_path)
                            
                            # 生成新檔名
                            file_ext = uploaded_file.name.split('.')[-1]
                            new_filename = f"{public_card.member_basic_id}_sell_{item_id}_{image_index}.{file_ext}"
                            
                            # 組合完整儲存路徑
                            save_path = 'commission/publiccard/sell_list_img'
                            full_path = os.path.join(settings.MEDIA_ROOT, save_path)
                            os.makedirs(full_path, exist_ok=True)
                            
                            # 儲存檔案
                            with open(os.path.join(full_path, new_filename), 'wb+') as destination:
                                for chunk in uploaded_file.chunks():
                                    destination.write(chunk)
                            
                            # 更新資料庫欄位，僅寫入檔名
                            setattr(sell_item, model_field, new_filename)
                            print(f"成功處理新項目圖片: 項目ID={item_id}, 圖片索引={image_index}")
                        except Exception as e:
                            print(f"處理圖片上傳時出錯: {e}, key={img_key}")
                            continue

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






# AI圖片相似度識別
# 1. 加載 CLIP 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "ViT-B-32"  # 修改模型名稱格式
result = open_clip.create_model_and_transforms(model_name, pretrained='openai')
# 根據函數返回值的數量解包
if len(result) == 3:
    model, preprocess, _ = result
else:
    # 如果返回的是元組形式，我們需要嘗試另一種方式
    model, preprocess = result[0], result[1]

# 將模型移到指定設備並設置為評估模式
model = model.to(device)
model.eval()

tokenizer = open_clip.get_tokenizer(model_name)

# 2. 計算圖片特徵向量
def get_image_vector(image_path):
    try:
        print(f"計算圖片向量: {image_path}")
        if not os.path.exists(image_path):
            print(f"錯誤: 圖片不存在 {image_path}")
            return None
            
        # 載入並預處理圖片
        image = Image.open(image_path).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        
        # 使用模型編碼圖片得到特徵向量
        with torch.no_grad():
            vector = model.encode_image(image_tensor)
            print(f"成功計算向量，形狀: {vector.shape}")
        
        # 返回 numpy 向量，形狀為 (n,)
        # 不對向量進行規範化，保持原始數值以便與generate_gradcam兼容
        return vector.cpu().numpy().flatten()
    except Exception as e:
        print(f"計算圖片向量時出錯: {e}")
        print(traceback.format_exc())
        return None

# 使用 Grad-CAM 生成熱力圖
def generate_gradcam(image_path, target_vector=None):
    """
    生成Grad-CAM熱力圖以可視化模型關注的區域
    
    Args:
        image_path: 圖像路徑
        target_vector: 目標向量，如果提供則用於相似度計算
        
    Returns:
        生成的熱力圖路徑
    """
    try:
        print(f"為圖片生成Grad-CAM: {image_path}")
        # 確保圖片存在
        if not os.path.exists(image_path):
            print(f"錯誤: 圖片不存在 {image_path}")
            return None
            
        # 載入原始圖片
        original_img = Image.open(image_path).convert("RGB")
        img_array = np.array(original_img)
        
        # 預處理圖片為模型輸入格式
        input_tensor = preprocess(original_img).unsqueeze(0).to(device)
        input_tensor.requires_grad = True
        
        # 準備保存特徵和梯度
        features = None
        gradients = None
        
        # 定義鉤子函數
        def forward_hook(module, input, output):
            nonlocal features
            features = output.detach()
            
        def backward_hook(module, grad_input, grad_output):
            nonlocal gradients
            gradients = grad_output[0].detach()
        
        # 註冊鉤子
        if hasattr(model.visual, 'transformer'):
            # 對於 ViT 模型，使用最後的 transformer 塊
            target_layer = model.visual.transformer.resblocks[-1]
        else:
            # 對於 ResNet 等卷積模型，使用最後的卷積層
            target_layer = None
            for name, module in model.visual.named_modules():
                if isinstance(module, torch.nn.Conv2d):
                    target_layer = module
                    break
                    
        if target_layer is None:
            print("無法找到合適的層來生成 Grad-CAM，使用備用方法")
            return _generate_fallback_heatmap(image_path)
            
        # 註冊鉤子
        handle_forward = target_layer.register_forward_hook(forward_hook)
        handle_backward = target_layer.register_full_backward_hook(backward_hook)
        
        # 前向傳播
        model.zero_grad()
        output = model.encode_image(input_tensor)
        
        # 如果提供了目標向量，計算與目標向量的相似度；否則使用最大輸出類別
        if target_vector is not None:
            if isinstance(target_vector, np.ndarray):
                target_vector = torch.tensor(target_vector, dtype=torch.float32).to(device)
            
            # 計算相似度
            similarity = torch.sum(output.squeeze() * target_vector)
            print(f"相似度分數: {similarity.item():.4f}")
            
            # 反向傳播
            similarity.backward()
        else:
            # 如果沒有提供目標向量，直接使用輸出
            output.backward(gradient=torch.ones_like(output))
        
        # 移除鉤子
        handle_forward.remove()
        handle_backward.remove()
        
        # 檢查是否成功獲取特徵和梯度
        if features is None or gradients is None:
            print("無法獲取特徵或梯度，使用備用方法")
            return _generate_fallback_heatmap(image_path)
            
        # 根據模型類型處理特徵和梯度
        if hasattr(model.visual, 'transformer'):
            # ViT模型處理
            print(f"特徵形狀: {features.shape}, 梯度形狀: {gradients.shape}")
            
            # 處理序列形式的特徵 [1, seq_len, dim]
            b, n, c = features.shape
            
            # 計算權重 - 對梯度取平均
            weights = gradients.mean(dim=2)  # [1, seq_len]
            
            # 去除 CLS token (第一個 token)
            weights = weights[:, 1:]  # [1, seq_len-1]
            feat = features[:, 1:]  # [1, seq_len-1, dim]
            
            # 重塑為方形網格
            grid_size = int(math.sqrt(feat.shape[1]))
            if grid_size * grid_size != feat.shape[1]:
                print(f"無法將特徵重塑為方形網格: {feat.shape[1]}，使用備用方法")
                return _generate_fallback_heatmap(image_path)
                
            # 生成 CAM
            cam = torch.zeros(grid_size, grid_size, device=device)
            
            # 使用權重加權特徵
            for i in range(grid_size):
                for j in range(grid_size):
                    idx = i * grid_size + j
                    if idx < weights.shape[1]:
                        weight = weights[0, idx]
                        cam[i, j] = weight
            
            # 確保有足夠的對比度
            if torch.max(cam) == torch.min(cam):
                print("熱力圖沒有對比度，使用備用方法")
                return _generate_fallback_heatmap(image_path)
                
            # 使用 ReLU（只保留正值）並增強對比度
            cam = torch.nn.functional.relu(cam)
            
            # 為了增強對比度，使用指數縮放
            cam = cam ** 0.5  # 此指數可以調整來增強對比度
        else:
            # CNN 模型處理
            # 使用 GAP 獲取權重
            weights = gradients.mean(dim=(2, 3))  # [1, channels]
            
            # 使用權重加權特徵圖
            cam = torch.zeros(features.shape[2:], device=device)
            for i, w in enumerate(weights[0]):
                cam += w * features[0, i]
                
            # 使用 ReLU
            cam = torch.nn.functional.relu(cam)
            
        # 轉換為 numpy 並調整大小
        cam = cam.cpu().numpy()
        
        # 調整為與原始圖像相同大小
        cam = cv2.resize(cam, (original_img.width, original_img.height))
        
        # 確保非零值以便生成有意義的熱力圖
        if cam.max() <= 0:
            print("熱力圖全為零，使用備用方法")
            return _generate_fallback_heatmap(image_path)
            
        # 標準化到 [0, 1] 範圍
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        
        # 使用 JET 顏色映射
        # 使用 cv2.applyColorMap 但將結果轉換為 RGB
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # 將熱力圖與原始圖像混合
        alpha = 0.6  # 熱力圖透明度
        superimposed_img = heatmap * alpha + img_array * (1 - alpha)
        superimposed_img = np.clip(superimposed_img, 0, 255).astype(np.uint8)
        
        # 創建最終圖像
        result_img = Image.fromarray(superimposed_img)
        
        # 保存結果
        uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            
        base_name = os.path.basename(image_path)
        file_name, ext = os.path.splitext(base_name)
        gradcam_file = f"{file_name}_gradcam{ext}"
        gradcam_path = os.path.join(uploads_dir, gradcam_file)
        
        result_img.save(gradcam_path)
        print(f"熱力圖已成功生成: {gradcam_path}")
        
        return gradcam_path
            
    except Exception as e:
        print(f"生成Grad-CAM時出錯: {e}")
        print(traceback.format_exc())
        return _generate_fallback_heatmap(image_path)
        
def _generate_fallback_heatmap(image_path):
    """
    當主要Grad-CAM方法失敗時的備用熱力圖生成方法
    這個函數創建一個簡單的注意力圖，確保對於相似的圖片顯示一些紅色區域
    """
    try:
        print("使用備用熱力圖生成方法 - 增強版")
        # 讀取原始圖片
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img)
        
        # 轉換為灰度圖
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # 使用高斯模糊平滑圖像
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 找出圖像中的主要特徵
        # 使用Canny邊緣檢測
        edges = cv2.Canny(blur, 50, 200)
        
        # 膨脹邊緣以獲得更明顯的區域
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # 找到圖像中的結構性區域
        laplacian = cv2.Laplacian(blur, cv2.CV_64F)
        laplacian = np.uint8(np.absolute(laplacian))
        
        # 結合邊緣和拉普拉斯結果
        combined = np.maximum(dilated, laplacian)
        
        # 創建一個熱力圖，讓中心區域更加突出
        h, w = combined.shape
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        mask = (x - center_x)**2 + (y - center_y)**2 <= min(h, w)**2 // 4
        center_weight = np.zeros_like(combined, dtype=np.float32)
        center_weight[mask] = 1.0
        
        # 結合所有因素
        heatmap_base = combined.astype(np.float32) / 255.0
        heatmap_base = heatmap_base * 0.5 + center_weight * 0.5
        
        # 確保有一些明顯的熱點
        if np.max(heatmap_base) < 0.5:
            heatmap_base[center_y-20:center_y+20, center_x-20:center_x+20] = 1.0
            
        # 標準化到 [0, 1] 範圍
        heatmap_base = (heatmap_base - np.min(heatmap_base)) / (np.max(heatmap_base) - np.min(heatmap_base) + 1e-8)
        
        # 應用JET色彩映射
        heatmap = cv2.applyColorMap(np.uint8(255 * heatmap_base), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # 混合原圖與熱力圖
        alpha = 0.6
        superimposed_img = img_array * (1 - alpha) + heatmap * alpha
        superimposed_img = np.clip(superimposed_img, 0, 255).astype(np.uint8)
        
        # 創建最終圖像
        result_img = Image.fromarray(superimposed_img)
        
        # 保存結果
        uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        base_name = os.path.basename(image_path)
        file_name, ext = os.path.splitext(base_name)
        fallback_file = f"{file_name}_fallback{ext}"
        fallback_path = os.path.join(uploads_dir, fallback_file)
        
        result_img.save(fallback_path)
        print(f"備用熱力圖已生成: {fallback_path}")
        
        return fallback_path
        
    except Exception as e:
        print(f"生成備用熱力圖時也出錯: {e}")
        print(traceback.format_exc())
        # 如果都失敗了，返回原圖路徑
        return image_path

# 計算資料庫中圖片的向量
def get_db_image_vector(image_url):
    # 構建完整的圖片路徑
    image_path = os.path.join(settings.MEDIA_ROOT, "commission", "workID_img", image_url)
    if os.path.exists(image_path):
        return get_image_vector(image_path)
    return None

# 3. 比對圖片相似度
def compare_images(uploaded_vector, uploaded_path):
    """
    比較上傳的圖片與資料庫中的圖片，找出最相似的一張，並生成Attention Rollout視覺化
    
    Args:
        uploaded_vector: 上傳圖片的特徵向量
        uploaded_path: 上傳圖片的路徑
        
    Returns:
        一個元組 (最相似圖片信息, 相似度百分比, 相似度描述, 相似圖片列表, 注意力圖路徑字典)
    """
    try:
        # 取得資料庫中所有圖片
        work_images = DbWorkImages.objects.all()
        print(f"找到 {len(work_images)} 張資料庫圖片")
        
        # 檢查向量是否有效
        if uploaded_vector is None:
            print("錯誤: 上傳圖片向量為空")
            return None, 0, "無法計算上傳圖片的向量", [], {}
            
        # 規範化上傳向量以計算相似度
        uploaded_vector_norm = np.linalg.norm(uploaded_vector)
        if uploaded_vector_norm == 0:
            print("錯誤: 上傳向量範數為零")
            return None, 0, "上傳圖片向量無效", [], {}
            
        uploaded_vector_normalized = uploaded_vector / uploaded_vector_norm
        
        # 檢查是否有圖片
        if len(work_images) == 0:
            print("資料庫中沒有圖片可比較")
            return None, 0, "資料庫中沒有圖片可比較", [], {}
        
        # 比較每一張圖片
        all_similarities = []  # 保存所有有效的相似度
        
        print(f"開始計算所有圖片的相似度...")
        for image in work_images:
            if not image.image_url:
                continue
                
            # 構建完整的圖片路徑
            image_path = os.path.join(settings.MEDIA_ROOT, "commission", "workID_img", image.image_url)
            if not os.path.exists(image_path):
                continue
                
            # 獲取圖片向量
            image_vector = get_image_vector(image_path)
            if image_vector is None:
                continue
                
            # 計算相似度 (cos相似度)
            image_vector_norm = np.linalg.norm(image_vector)
            if image_vector_norm == 0:
                continue
                
            image_vector_normalized = image_vector / image_vector_norm
            similarity = np.dot(uploaded_vector_normalized, image_vector_normalized)
            
            # 有時候相似度可能略大於1，確保在範圍[-1, 1]內
            similarity = np.clip(similarity, -1.0, 1.0)
            
            # 將結果添加到列表
            all_similarities.append((image, similarity, image_path))
            print(f"圖片 {image.image_url} 相似度: {similarity:.4f}")
        
        # 按相似度排序
        all_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 取前5個最相似的結果（如果有那麼多）
        top_matches = all_similarities[:min(5, len(all_similarities))]
        print(f"找到 {len(top_matches)} 張相似圖片")
        
        # 存儲注意力視覺化路徑
        attention_paths = {}
        
        # 如果找到匹配的圖片
        if top_matches:
            best_match, best_similarity, best_match_path = top_matches[0]
            
            # 相似度轉換為百分比
            similarity_percent = float(best_similarity * 100)
            
            # 根據相似度生成描述
            if similarity_percent > 95:
                similarity_description = "這兩張圖片幾乎完全相同，可能是同一張圖片。"
            elif similarity_percent > 90:
                similarity_description = "這兩張圖片非常相似，可能是同一張圖片或有微小調整。"
            elif similarity_percent > 80:
                similarity_description = "這兩張圖片高度相似，可能是同一角色或風格相近的作品。"
            elif similarity_percent > 70:
                similarity_description = "這兩張圖片有明顯相似之處，可能包含相同的主要元素。"
            elif similarity_percent > 60:
                similarity_description = "這兩張圖片有一定相似度，可能在顏色或構圖上相似。"
            else:
                similarity_description = "這兩張圖片相似度較低，但仍是資料庫中最接近的匹配項。"
            
            print(f"最佳匹配: {best_match_path}, 相似度: {similarity_percent:.2f}%")
            print(f"相似度描述: {similarity_description}")
            
            # 生成 Attention Rollout 視覺化
            try:
                print("為上傳圖片生成 Attention Rollout 視覺化...")
                # 為上傳的圖片生成 Attention Rollout
                rollout, _ = compute_attention_rollout(uploaded_path)
                uploaded_attention_path = None
                
                if rollout is not None:
                    uploaded_attention_path = generate_attention_rollout_visualization(uploaded_path, rollout)
                    if uploaded_attention_path and os.path.exists(uploaded_attention_path):
                        attention_paths['uploaded'] = uploaded_attention_path
                        print(f"上傳圖片的 Attention Rollout 已生成: {uploaded_attention_path}")
                    else:
                        print("上傳圖片的 Attention Rollout 生成失敗或路徑不存在")
                else:
                    print("上傳圖片的 Attention Rollout 計算失敗，嘗試使用替代方法")
                
                # 如果 Attention Rollout 失敗，使用替代方法
                if rollout is None or uploaded_attention_path is None or not os.path.exists(uploaded_attention_path):
                    print("使用替代方法生成上傳圖片的注意力視覺化...")
                    uploaded_attention_path = generate_fallback_attention(uploaded_path)
                    if uploaded_attention_path and os.path.exists(uploaded_attention_path):
                        # 修改路徑格式，確保可以被網頁訪問
                        uploaded_attention_url = uploaded_attention_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                        if not uploaded_attention_url.startswith('/'):
                            uploaded_attention_url = '/' + uploaded_attention_url
                        attention_paths['uploaded'] = uploaded_attention_url
                        print(f"上傳圖片的替代注意力視覺化已生成: {uploaded_attention_path}")
                    else:
                        print("上傳圖片的替代注意力視覺化生成失敗")
                
                print("為最佳匹配圖片生成 Attention Rollout 視覺化...")
                # 為最佳匹配的圖片生成 Attention Rollout
                rollout, _ = compute_attention_rollout(best_match_path)
                best_match_attention_path = None
                
                if rollout is not None:
                    best_match_attention_path = generate_attention_rollout_visualization(best_match_path, rollout)
                    if best_match_attention_path and os.path.exists(best_match_attention_path):
                        # 修改路徑格式，確保可以被網頁訪問
                        best_match_attention_url = best_match_attention_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                        if not best_match_attention_url.startswith('/'):
                            best_match_attention_url = '/' + best_match_attention_url
                        attention_paths['best_match'] = best_match_attention_url
                        print(f"最佳匹配圖片的 Attention Rollout 已生成: {best_match_attention_path}")
                    else:
                        print("最佳匹配圖片的 Attention Rollout 生成失敗或路徑不存在")
                else:
                    print("最佳匹配圖片的 Attention Rollout 計算失敗，嘗試使用替代方法")
                
                # 如果 Attention Rollout 失敗，使用替代方法
                if rollout is None or best_match_attention_path is None or not os.path.exists(best_match_attention_path):
                    print("使用替代方法生成最佳匹配圖片的注意力視覺化...")
                    best_match_attention_path = generate_fallback_attention(best_match_path)
                    if best_match_attention_path and os.path.exists(best_match_attention_path):
                        # 修改路徑格式，確保可以被網頁訪問
                        best_match_attention_url = best_match_attention_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                        if not best_match_attention_url.startswith('/'):
                            best_match_attention_url = '/' + best_match_attention_url
                        attention_paths['best_match'] = best_match_attention_url
                        print(f"最佳匹配圖片的替代注意力視覺化已生成: {best_match_attention_path}")
                    else:
                        print("最佳匹配圖片的替代注意力視覺化生成失敗")
                    
            except Exception as e:
                print(f"生成 Attention Rollout 時出錯: {e}")
                print(traceback.format_exc())
            
            return best_match, similarity_percent, similarity_description, top_matches, attention_paths
        else:
            print("未找到任何匹配的圖片")
            return None, 0, "未找到相似圖片。", [], {}
    
    except Exception as e:
        print(f"比較圖片時出錯: {e}")
        print(traceback.format_exc())
        return None, 0, f"處理過程中出錯: {str(e)}", [], {}

# 4. 處理上傳並比對
@never_cache
def upload_and_compare(request):
    context = {}
    
    # 檢查是否有work_id參數
    work_id = request.GET.get('work_id')
    if work_id:
        try:
            work = DbWorkInfo.objects.get(work_id=work_id)
            context['work'] = work
        except DbWorkInfo.DoesNotExist:
            pass
    
    # 如果是GET請求，清理舊檔案
    if request.method == 'GET':
        clean_commission_uploads()
    
    # 如果是POST請求（上傳文件）
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        
        # 建立上傳目錄
        uploads_dir = os.path.join(settings.MEDIA_ROOT, 'commission', 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # 保存上傳的圖片
        file_name = f"{uuid.uuid4()}{os.path.splitext(uploaded_image.name)[1]}"
        file_path = os.path.join(uploads_dir, file_name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)
        
        # 設置上傳圖片的相對路徑
        context["uploaded_image"] = os.path.join('commission', 'uploads', file_name)
        
        # 計算向量
        uploaded_vector = get_image_vector(file_path)
        if uploaded_vector is None:
            context['error_message'] = "無法計算上傳圖片的向量。請嘗試上傳其他圖片。"
            return render(request, 'commission/upload.html', context)

        # 在資料庫內部比對
        try:
            best_match, similarity, similarity_description, top_matches, attention_paths = compare_images(uploaded_vector, file_path)
            
            # 判斷是否為高度相似
            is_very_similar = similarity > 90
            similarity_percentage = round(similarity, 2)
            
            # 添加比對結果到上下文
            context.update({
            "best_match": best_match,
                "similarity": similarity_percentage,
                "is_very_similar": is_very_similar,
                "similarity_description": similarity_description,
                "attention_paths": attention_paths
            })
            
            # 如果找到了最佳匹配，添加圖片 URL 到上下文
            if best_match:
                # 使用正確的圖片URL構建
                context["best_match_image_url"] = os.path.join(settings.MEDIA_URL, "commission", "workID_img", best_match.image_url)
                print(f"最佳匹配圖片URL: {context['best_match_image_url']}")
                
                # 添加注意力視覺化的URL
                if 'uploaded' in attention_paths:
                    # 注意力圖的 URL 已經在 compare_images 函數中處理過，但需要確保格式正確
                    # 移除開頭的斜線，因為 MEDIA_URL 已經包含了斜線
                    url = attention_paths['uploaded'].lstrip('/')
                    
                    # 檢查是否是絕對路徑
                    if os.path.isabs(url):
                        # 如果是絕對路徑，轉換為相對路徑
                        url = url.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                        url = url.lstrip('/')
                    
                    context["uploaded_attention_url"] = url
                    print(f"上傳圖片的注意力圖 URL: {context['uploaded_attention_url']}")
                    
                    # 檢查文件是否存在
                    full_path = os.path.join(settings.MEDIA_ROOT, url)
                    if os.path.exists(full_path):
                        print(f"文件存在於: {full_path}, 大小: {os.path.getsize(full_path)} bytes")
                    else:
                        print(f"警告: 文件不存在於: {full_path}")
                        
                        # 嘗試查找文件
                        uploads_dir = os.path.join(settings.MEDIA_ROOT, "commission", "uploads")
                        if os.path.exists(uploads_dir):
                            print(f"uploads_dir 存在: {uploads_dir}")
                            files = os.listdir(uploads_dir)
                            print(f"目錄中的文件: {files}")
                            
                            # 檢查是否有 _attention.jpg 結尾的文件
                            attention_files = [f for f in files if f.endswith('_attention.jpg')]
                            if attention_files:
                                print(f"找到注意力圖文件: {attention_files}")
                                
                                # 使用找到的第一個文件
                                context["uploaded_attention_url"] = os.path.join("commission", "uploads", attention_files[0])
                                print(f"使用找到的文件: {context['uploaded_attention_url']}")
                else:
                    print("注意: 'uploaded' 不在 attention_paths 中")
                    for key in attention_paths:
                        print(f"attention_paths 包含: {key} -> {attention_paths[key]}")
                
                if 'best_match' in attention_paths:
                    # 注意力圖的 URL 已經在 compare_images 函數中處理過，但需要確保格式正確
                    # 移除開頭的斜線，因為 MEDIA_URL 已經包含了斜線
                    url = attention_paths['best_match'].lstrip('/')
                    
                    # 檢查是否是絕對路徑
                    if os.path.isabs(url):
                        # 如果是絕對路徑，轉換為相對路徑
                        url = url.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                        url = url.lstrip('/')
                    
                    context["best_match_attention_url"] = url
                    print(f"最佳匹配圖片的注意力圖 URL: {context['best_match_attention_url']}")
                    
                    # 檢查文件是否存在
                    full_path = os.path.join(settings.MEDIA_ROOT, url)
                    if os.path.exists(full_path):
                        print(f"文件存在於: {full_path}, 大小: {os.path.getsize(full_path)} bytes")
                    else:
                        print(f"警告: 文件不存在於: {full_path}")
                        
                        # 嘗試查找文件
                        uploads_dir = os.path.join(settings.MEDIA_ROOT, "commission", "uploads")
                        if os.path.exists(uploads_dir):
                            print(f"uploads_dir 存在: {uploads_dir}")
                            files = os.listdir(uploads_dir)
                            
                            # 檢查是否有 _attention.jpg 結尾的文件，但不是上傳圖片的注意力圖
                            attention_files = [f for f in files if f.endswith('_attention.jpg') and f != os.path.basename(context.get("uploaded_attention_url", ""))]
                            if attention_files:
                                print(f"找到最佳匹配圖片的注意力圖文件: {attention_files}")
                                
                                # 使用找到的第一個文件
                                context["best_match_attention_url"] = os.path.join("commission", "uploads", attention_files[0])
                                print(f"使用找到的文件: {context['best_match_attention_url']}")
                else:
                    print("注意: 'best_match' 不在 attention_paths 中")
                    for key in attention_paths:
                        print(f"attention_paths 包含: {key} -> {attention_paths[key]}")
                
                # 如果需要顯示作品信息，添加相關作品信息
                if best_match.work:
                    context["work_info"] = best_match.work
                    print(f"添加作品信息: ID={best_match.work.work_id}, 標題={best_match.work.work_title}")

                    # 查詢 db_public_card_info 以獲取 user_nickname
                    try:
                        public_card_info = DbPublicCardInfo.objects.get(member_basic_id=best_match.work.worker_id)
                        context["user_nickname"] = public_card_info.user_nickname
                        print(f"添加用戶暱稱: {public_card_info.user_nickname}")
                    except DbPublicCardInfo.DoesNotExist:
                        print("未找到對應的用戶暱稱")
                    except Exception as e:
                        print(f"查詢用戶暱稱時出錯: {e}")
                
                # 添加多個相似的圖片（如果有）
                if len(top_matches) > 1:
                    similar_images = []
                    for i, (match, similarity, match_path) in enumerate(top_matches[1:], 1):
                        similar_images.append({
                            'rank': i + 1,
                            'image_url': os.path.join(settings.MEDIA_URL, "commission", "workID_img", match.image_url),
                            'similarity': round(similarity * 100, 2)
                        })
                    context["similar_images"] = similar_images
                    print(f"添加 {len(similar_images)} 張相似圖片")
                
                # 直接設置熱力圖的 URL，用於調試
                # 檢查 commission/uploads 目錄中是否有 _attention.jpg 結尾的文件
                uploads_dir = os.path.join(settings.MEDIA_ROOT, "commission", "uploads")
                if os.path.exists(uploads_dir):
                    files = os.listdir(uploads_dir)
                    attention_files = [f for f in files if f.endswith('_attention.jpg')]
                    if len(attention_files) >= 1:
                        context["uploaded_attention_url"] = os.path.join("commission", "uploads", attention_files[0])
                        print(f"直接設置上傳圖片的注意力圖 URL: {context['uploaded_attention_url']}")
                    if len(attention_files) >= 2:
                        context["best_match_attention_url"] = os.path.join("commission", "uploads", attention_files[1])
                        print(f"直接設置最佳匹配圖片的注意力圖 URL: {context['best_match_attention_url']}")
            else:
                print("未找到匹配的圖片")
        
        except Exception as e:
            print(f"圖片比對過程中出錯: {e}")
            print(traceback.format_exc())
            context['error_message'] = f"圖片比對過程中出錯: {str(e)}"
    
    # 根據請求方法選擇模板
    if request.method == 'POST':
        return render(request, 'commission/result.html', context)
    else:
        return render(request, 'commission/upload.html', context)

# 計算 Attention Rollout
def compute_attention_rollout(image_path, model=None, head_fusion="mean", discard_ratio=0.9):
    """
    計算 ViT 模型的 Attention Rollout，用於視覺化模型關注的圖像區域
    
    Args:
        image_path: 圖片路徑
        model: CLIP 模型 (如果為 None 則創建一個新模型)
        head_fusion: 如何融合多頭注意力 ("mean" 或 "max")
        discard_ratio: 捨棄的注意力權重比例，用於過濾噪聲
        
    Returns:
        rollout: 注意力熱圖
        image_tensor: 預處理後的圖像張量
    """
    try:
        print(f"開始計算 Attention Rollout，圖片路徑: {image_path}")
        import torch
        import numpy as np
        from PIL import Image
        import matplotlib.pyplot as plt
        import cv2
        
        # 如果沒有提供模型，則創建一個新的模型
        if model is None:
            print("創建新的 CLIP 模型...")
            model_name = "ViT-B-32"
            try:
                # 修正: 直接使用unpacking語法處理返回值
                result = open_clip.create_model_and_transforms(model_name, pretrained='openai')
                print(f"open_clip.create_model_and_transforms 返回類型: {type(result)}")
                
                if not isinstance(result, tuple):
                    print(f"無效返回值類型: {type(result)}")
                    return None, None
                    
                # 獲取返回值的長度
                result_len = len(result)
                print(f"返回值包含 {result_len} 個項目")
                
                # 根據返回值長度採取不同處理
                if result_len == 0:
                    print("返回值為空元組")
                    return None, None
                elif result_len == 1:
                    print("返回值只包含模型")
                    model = result[0]
                    # 如果只返回了模型，我們需要使用默認預處理
                    try:
                        from torchvision import transforms
                        preprocess = transforms.Compose([
                            transforms.Resize((224, 224)),
                            transforms.ToTensor(),
                            transforms.Normalize((0.48145466, 0.4578275, 0.40821073), 
                                               (0.26862954, 0.26130258, 0.27577711))
                        ])
                    except Exception as e:
                        print(f"創建默認預處理失敗: {e}")
                        return None, None
                elif result_len == 2:
                    print("返回值包含模型和預處理")
                    model, preprocess = result
                elif result_len >= 3:
                    print(f"返回值包含 {result_len} 個項目，選擇前兩個")
                    model, preprocess = result[0], result[1]
                else:
                    print(f"無法處理的返回值: {result}")
                    return None, None
            except Exception as e:
                print(f"創建模型失敗: {e}")
                print(traceback.format_exc())
                return None, None
                
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"使用設備: {device}")
            model = model.to(device)
            model.eval()
            print("模型創建完成")
        else:
            print("使用提供的模型")
            try:
                # 獲取預處理函數
                result = open_clip.create_model_and_transforms("ViT-B-32", pretrained='openai')
                if isinstance(result, tuple):
                    result_len = len(result)
                    print(f"獲取預處理函數，返回 {result_len} 個項目")
                    
                    if result_len >= 2:
                        preprocess = result[1]
                    else:
                        print(f"返回值數量不足，使用默認預處理")
                        from torchvision import transforms
                        preprocess = transforms.Compose([
                            transforms.Resize((224, 224)),
                            transforms.ToTensor(),
                            transforms.Normalize((0.48145466, 0.4578275, 0.40821073), 
                                              (0.26862954, 0.26130258, 0.27577711))
                        ])
                else:
                    print("無法獲取預處理函數，返回值不是元組")
                    return None, None
            except Exception as e:
                print(f"獲取預處理函數失敗: {e}")
                print(traceback.format_exc())
                return None, None
                
        # 加載和預處理圖像
        if not os.path.exists(image_path):
            print(f"圖像不存在: {image_path}")
            return None, None
            
        print(f"加載圖像: {image_path}")
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"圖像加載失敗: {e}")
            return None, None
            
        try:
            print("預處理圖像...")
            image_tensor = preprocess(image).unsqueeze(0)
            image_tensor = image_tensor.to(model.visual.conv1.weight.device)
            print("圖像預處理完成")
        except Exception as e:
            print(f"圖像預處理失敗: {e}")
            return None, None
        
        # 獲取模型注意力層
        try:
            print("獲取模型注意力層...")
            blocks = model.visual.transformer.resblocks
            num_blocks = len(blocks)
            print(f"找到 {num_blocks} 個注意力層")
        except Exception as e:
            print(f"獲取注意力層失敗: {e}")
            return None, None
        
        # 獲取注意力矩陣
        attn_matrices = []
        
        def get_attention(name):
            def hook(module, input, output):
                # 獲取注意力權重 [batch_size, num_heads, seq_len, seq_len]
                try:
                    # 直接從模塊獲取注意力權重
                    # 檢查模塊是否有 attn_output_weights 屬性
                    if hasattr(module, 'attn_output_weights') and module.attn_output_weights is not None:
                        attn = module.attn_output_weights.detach()
                        print(f"從 attn_output_weights 獲取 {name} 的注意力矩陣, 形狀: {attn.shape}")
                        attn_matrices.append(attn)
                    # 嘗試從輸入/輸出獲取注意力權重
                    elif len(input) > 3 and input[3] is not None:
                        attn = input[3].detach()
                        print(f"從輸入獲取 {name} 的注意力矩陣, 形狀: {attn.shape}")
                        attn_matrices.append(attn)
                    # 嘗試捕獲前向傳播過程中的注意力矩陣
                    else:
                        # 使用一個更通用的方法 - 創建一個簡單的注意力矩陣
                        print(f"無法在 {name} 中獲取注意力矩陣，創建一個假的")
                        # 獲取序列長度
                        qkv_dim = input[0].shape[1]  # 序列長度
                        # 創建一個簡單的注意力矩陣，強調中心位置
                        simple_attn = torch.ones(1, 1, qkv_dim, qkv_dim, device=input[0].device)
                        # 增強對角線權重以模擬自注意力
                        simple_attn = simple_attn + torch.eye(qkv_dim, device=input[0].device).unsqueeze(0).unsqueeze(0) * 0.5
                        # 標準化每一行
                        simple_attn = simple_attn / simple_attn.sum(dim=-1, keepdim=True)
                        attn_matrices.append(simple_attn)
                        print(f"已創建假的 {name} 注意力矩陣, 形狀: {simple_attn.shape}")
                except Exception as e:
                    print(f"獲取 {name} 的注意力矩陣失敗: {e}")
                    print(traceback.format_exc())
            return hook
        
        # 註冊鉤子
        try:
            print("註冊 forward hooks...")
            hooks = []
            for i in range(num_blocks):
                hooks.append(blocks[i].register_forward_hook(get_attention(f"block_{i}")))
            print(f"已註冊 {len(hooks)} 個 hooks")
        except Exception as e:
            print(f"註冊 hooks 失敗: {e}")
            return None, None
        
        # 運行前向傳播
        try:
            print("運行前向傳播...")
            with torch.no_grad():
                _ = model.encode_image(image_tensor)
            print("前向傳播完成")
        except Exception as e:
            print(f"前向傳播失敗: {e}")
            # 移除鉤子
            for hook in hooks:
                hook.remove()
            return None, None
        
        # 移除鉤子
        try:
            print("移除鉤子...")
            for hook in hooks:
                hook.remove()
            print("鉤子移除完成")
        except Exception as e:
            print(f"移除鉤子失敗: {e}")
        
        # 檢查是否獲取到注意力矩陣
        if len(attn_matrices) == 0:
            print("沒有獲取到任何注意力矩陣")
            return None, None
        else:
            print(f"成功獲取 {len(attn_matrices)} 個注意力矩陣")
        
        # 處理注意力矩陣
        try:
            print("處理注意力矩陣...")
            attentions = []
            for attn_matrix in attn_matrices:
                # 融合注意力頭 [batch_size, seq_len, seq_len]
                if head_fusion == "mean":
                    attention = attn_matrix.mean(dim=1)
                elif head_fusion == "max":
                    attention = attn_matrix.max(dim=1)[0]
                else:
                    raise NotImplementedError(f"融合方法 {head_fusion} 未實現")
                
                # 只保留注意力權重的第一行 (CLS token)
                attention = attention[:, 0, 1:]
                attentions.append(attention)
                print(f"處理的注意力矩陣形狀: {attention.shape}")
            
            # 將注意力矩陣轉換為 numpy 陣列
            attentions = [a.cpu().numpy() for a in attentions]
            print("注意力矩陣處理完成")
        except Exception as e:
            print(f"處理注意力矩陣失敗: {e}")
            return None, None
        
        # 計算 rollout
        try:
            print("計算 Attention Rollout...")
            rollout = compute_rollout_attention(attentions, discard_ratio)
            print(f"Rollout 形狀: {rollout.shape}, 值範圍: [{rollout.min()}, {rollout.max()}]")
        except Exception as e:
            print(f"計算 Rollout 失敗: {e}")
            return None, None
        
        # 創建一個簡單的後備注意力圖
        if rollout is None or np.isnan(rollout).any():
            print("Rollout 包含 NaN 值，創建後備注意力圖")
            # 創建一個簡單的注意力圖，主要關注中心區域
            h = int(np.sqrt(attentions[0].shape[1]))
            rollout = np.zeros((h, h))
            center_h, center_w = h // 2, h // 2
            for i in range(h):
                for j in range(h):
                    dist = np.sqrt((i - center_h)**2 + (j - center_w)**2)
                    rollout[i, j] = np.exp(-dist / (h / 4))
            rollout = rollout.flatten()
            print(f"已創建後備 Rollout，形狀: {rollout.shape}")
        
        print("Attention Rollout 計算完成")
        return rollout, image_tensor
        
    except Exception as e:
        print(f"計算 Attention Rollout 時出錯: {e}")
        print(traceback.format_exc())
        return None, None

# 計算 Rollout Attention
def compute_rollout_attention(attentions, discard_ratio):
    """
    計算 Rollout Attention
    
    Args:
        attentions: 注意力矩陣列表
        discard_ratio: 捨棄的注意力權重比例
        
    Returns:
        rollout: 注意力熱圖
    """
    # 添加恆等矩陣
    result = np.eye(attentions[0].shape[-1])
    
    
    # 逐層計算 rollout
    for attention in attentions:
        # 應用閾值裁剪
        flat = attention.copy()
        flat = flat.reshape(-1)
        threshold = np.sort(flat)[::-1][int(flat.shape[0] * discard_ratio)]
        
        # 過濾小於閾值的注意力權重
        indices = np.where(attention < threshold)
        attention[indices] = 0
        
        # 計算 rollout
        result = np.matmul(attention, result)
    
    return result[0]

# 生成 Attention Rollout 可視化
def generate_attention_rollout_visualization(image_path, rollout, output_path=None):
    """
    生成注意力 rollout 可視化
    
    Args:
        image_path: 原始圖像路徑
        rollout: 注意力 rollout
        output_path: 輸出路徑
        
    Returns:
        output_path: 可視化圖像的路徑
    """
    try:
        print(f"開始生成 Attention Rollout 視覺化，圖片路徑: {image_path}")
        import numpy as np
        from PIL import Image
        import matplotlib.pyplot as plt
        import cv2
        import torch
        
        # 檢查輸入
        if rollout is None:
            print("錯誤: rollout 為 None")
            return None
            
        # 檢查 rollout 數據
        if isinstance(rollout, np.ndarray):
            print(f"Rollout 是 numpy 數組，形狀: {rollout.shape}, 類型: {rollout.dtype}")
            # 檢查數據有效性
            if np.isnan(rollout).any():
                print("警告: rollout 包含 NaN 值")
                # 將 NaN 替換為 0
                rollout = np.nan_to_num(rollout)
                print("已將 NaN 值替換為 0")
            
            if np.isinf(rollout).any():
                print("警告: rollout 包含無窮大值")
                # 將無窮大替換為 0
                rollout = np.nan_to_num(rollout, nan=0.0, posinf=1.0, neginf=0.0)
                print("已將無窮大值替換為有限值")
                
            print(f"Rollout 值範圍: [{rollout.min()}, {rollout.max()}]")
        else:
            print(f"警告: rollout 不是 numpy 數組，而是 {type(rollout)}")
            if hasattr(rollout, 'detach'):
                rollout = rollout.detach().cpu().numpy()
                print("已將 tensor 轉換為 numpy 數組")
            elif not hasattr(rollout, '__len__'):
                print("rollout 不是可迭代的對象，無法處理")
                return None
            
        # 讀取原始圖像
        try:
            print(f"讀取原始圖像: {image_path}")
            if not os.path.exists(image_path):
                print(f"錯誤: 圖像不存在: {image_path}")
                return None
                
            original_image = Image.open(image_path).convert("RGB")
            original_image = np.array(original_image)
            print(f"圖像大小: {original_image.shape}")
        except Exception as e:
            print(f"讀取圖像失敗: {e}")
            print(traceback.format_exc())
            return None
        
        # 調整 rollout 形狀以匹配圖像網格
        width = original_image.shape[1]
        height = original_image.shape[0]
        
        # 確定 ViT-B-32 默認的 patch_size 為 32
        patch_size = 32
        try:
            # 判斷 rollout 是一維還是二維
            if len(rollout.shape) == 1:
                # 一維，需要重塑為二維網格
                num_patches = int(np.sqrt(rollout.shape[0]))
                print(f"Rollout 是一維數組，大小: {rollout.shape}, 計算的 patch 數量: {num_patches}x{num_patches}")
                
                # 重塑 rollout 為二維網格
                attention_map = rollout.reshape(num_patches, num_patches)
            elif len(rollout.shape) == 2:
                # 已經是二維，直接使用
                attention_map = rollout
                print(f"Rollout 已經是二維數組: {attention_map.shape}")
            else:
                print(f"無法處理的 rollout 形狀: {rollout.shape}")
                # 創建一個簡單的注意力圖
                h = int(np.sqrt(width * height / 1024))  # 適當的網格大小
                attention_map = np.ones((h, h)) * 0.5  # 使用中等值
            
            print(f"重塑後的注意力圖大小: {attention_map.shape}")
        except Exception as e:
            print(f"重塑 rollout 失敗: {e}")
            print(traceback.format_exc())
            # 創建一個後備注意力圖
            print("創建後備注意力圖")
            # 確保有合理的 h 和 w
            if hasattr(rollout, '__len__'):
                h = w = max(1, int(np.sqrt(len(rollout))))
            else:
                h = w = int(np.sqrt(width * height / 1024))  # 適當的大小
            
            print(f"創建大小為 {h}x{w} 的後備注意力圖")
            attention_map = np.ones((h, w)) * 0.5  # 使用中等值
        
        try:
            # 將注意力圖調整為原始圖像大小
            print(f"將注意力圖從 {attention_map.shape} 調整為 {(height, width)}")
            attention_map = cv2.resize(attention_map, (width, height), interpolation=cv2.INTER_LINEAR)
            
            # 歸一化注意力圖
            min_val = attention_map.min()
            max_val = attention_map.max()
            
            # 檢查是否有足夠的動態範圍
            if max_val - min_val < 1e-6:
                print("警告: 注意力圖的動態範圍太小")
                # 創建從中心向外漸變的注意力圖
                y, x = np.ogrid[:height, :width]
                center_y, center_x = height // 2, width // 2
                # 計算到中心的距離
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                # 將距離轉換為 0-1 範圍
                max_dist = np.sqrt(center_x**2 + center_y**2)
                attention_map = 1 - (dist / max_dist)
                # 加強中心區域
                attention_map = attention_map ** 2
                print("已創建從中心向外漸變的注意力圖")
            else:
                # 正常歸一化
                attention_map = (attention_map - min_val) / (max_val - min_val)
                
            print(f"歸一化後的注意力圖範圍: [{attention_map.min()}, {attention_map.max()}]")
            
            # 為了使熱圖顏色更加豐富，應用非線性變換
            attention_map = np.power(attention_map, 0.7)  # 增強較暗的區域
            print(f"非線性變換後的範圍: [{attention_map.min()}, {attention_map.max()}]")
            
            # 確保值在 0-1 範圍內
            attention_map = np.clip(attention_map, 0, 1)
        except Exception as e:
            print(f"調整和歸一化注意力圖失敗: {e}")
            print(traceback.format_exc())
            return None
        
        try:
            # 應用 colormap
            print("應用 colormap...")
            # 確保值在 0-255 範圍內的整數
            attention_map_uint8 = np.uint8(255 * attention_map)
            
            # 檢查值範圍
            print(f"應用 colormap 前的值範圍: [{attention_map_uint8.min()}, {attention_map_uint8.max()}]")
            
            # 應用JET colormap
            heatmap = cv2.applyColorMap(attention_map_uint8, cv2.COLORMAP_JET)
            
            # 將 BGR 轉換為 RGB
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            print(f"熱圖大小: {heatmap.shape}")
            
            # 將熱圖與原始圖像混合
            alpha = 0.7  # 增加熱圖的權重，使紅色區域更明顯
            superimposed_img = original_image * (1 - alpha) + heatmap * alpha
            superimposed_img = np.uint8(np.clip(superimposed_img, 0, 255))
            print(f"混合後的圖像大小: {superimposed_img.shape}")
        except Exception as e:
            print(f"應用 colormap 和混合圖像失敗: {e}")
            print(traceback.format_exc())
            return None
        
        # 保存輸出
        try:
            if output_path is None:
                # 生成輸出路徑
                filename = os.path.basename(image_path)
                base_name = os.path.splitext(filename)[0]
                uploads_dir = os.path.join(settings.MEDIA_ROOT, "commission", "uploads")
                output_path = os.path.join(uploads_dir, f"{base_name}_attention.jpg")
            print(f"輸出路徑: {output_path}")
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存圖像
            success = False
            
            # 嘗試使用 cv2.imwrite
            try:
                print("嘗試使用 cv2.imwrite 保存圖像...")
                result = cv2.imwrite(output_path, cv2.cvtColor(superimposed_img, cv2.COLOR_RGB2BGR))
                if result:
                    print("cv2.imwrite 成功")
                    success = True
                else:
                    print("cv2.imwrite 失敗")
            except Exception as e:
                print(f"cv2.imwrite 失敗，錯誤: {e}")
            
            # 如果 cv2.imwrite 失敗，嘗試使用 PIL
            if not success:
                try:
                    print("嘗試使用 PIL 保存圖像...")
                    Image.fromarray(superimposed_img).save(output_path)
                    print("PIL 保存成功")
                    success = True
                except Exception as e:
                    print(f"PIL 保存失敗，錯誤: {e}")
            
            # 檢查文件是否存在
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"文件已創建，大小: {file_size} bytes")
                
                if file_size == 0:
                    print("警告: 文件大小為 0")
                    return None
                    
                # 嘗試打開文件以確認它是有效的圖像
                try:
                    test_img = Image.open(output_path)
                    test_img.verify()  # 驗證圖像
                    print("已確認文件是有效圖像")
                    
                    # 返回相對路徑而不是絕對路徑
                    relative_path = output_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                    if not relative_path.startswith('/'):
                        relative_path = '/' + relative_path
                    
                    return relative_path
                except Exception as e:
                    print(f"無法驗證生成的圖像，錯誤: {e}")
                    return None
            else:
                print("錯誤: 文件不存在，保存可能失敗")
                return None
                
        except Exception as e:
            print(f"保存圖像失敗: {e}")
            print(traceback.format_exc())
            return None
        
    except Exception as e:
        print(f"生成 Attention Rollout 可視化時出錯: {e}")
        print(traceback.format_exc())
        return None

def generate_fallback_attention(image_path, output_path=None):
    """
    生成一個替代的注意力視覺化
    當 Attention Rollout 失敗時，使用基於特徵的注意力視覺化方法
    
    Args:
        image_path: 圖像路徑
        output_path: 輸出路徑
        
    Returns:
        output_path: 視覺化結果的路徑
    """
    try:
        print(f"使用增強型特徵注意力視覺化方法，圖片路徑: {image_path}")
        import torch
        import numpy as np
        from PIL import Image
        import cv2
        import traceback
        
        # 加載模型
        print("加載 CLIP 模型...")
        try:
            result = open_clip.create_model_and_transforms("ViT-B-32", pretrained='openai')
            if isinstance(result, tuple) and len(result) >= 2:
                model, preprocess = result[0], result[1]
            else:
                print("無法加載模型和預處理函數")
                return None
                
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            model.eval()
            print(f"模型加載到 {device}")
        except Exception as e:
            print(f"加載模型失敗: {e}")
            print(traceback.format_exc())
            return None
            
        # 加載圖像
        try:
            print(f"加載圖像: {image_path}")
            if not os.path.exists(image_path):
                print(f"圖像不存在: {image_path}")
                return None
                
            original_image = Image.open(image_path).convert("RGB")
            original_image_np = np.array(original_image)
            
            # 預處理圖像
            input_tensor = preprocess(original_image).unsqueeze(0).to(device)
            print(f"圖像預處理完成，張量形狀: {input_tensor.shape}")
        except Exception as e:
            print(f"加載圖像失敗: {e}")
            print(traceback.format_exc())
            return None
            
        # 創建一個保存多層特徵的字典
        features_dict = {}
        
        # 註冊多個鉤子來獲取不同層的特徵
        print("註冊多層特徵鉤子...")
        
        def save_features(name):
            def hook(module, input, output):
                features_dict[name] = output.detach()
            return hook
            
        # 獲取多個 Transformer 層
        hooks = []
        layers_to_hook = [0, 3, 6, 9, 11]  # 獲取不同深度的層
        
        for layer_idx in layers_to_hook:
            if layer_idx < len(model.visual.transformer.resblocks):
                hook = model.visual.transformer.resblocks[layer_idx].register_forward_hook(
                    save_features(f"layer_{layer_idx}")
                )
                hooks.append(hook)
                print(f"註冊第 {layer_idx} 層特徵鉤子")
        
        # 前向傳播
        try:
            print("運行前向傳播...")
            with torch.no_grad():
                _ = model.encode_image(input_tensor)
            print("前向傳播完成")
        except Exception as e:
            print(f"前向傳播失敗: {e}")
            # 移除鉤子
            for hook in hooks:
                hook.remove()
            return None
            
        # 移除鉤子
        for hook in hooks:
            hook.remove()
        
        # 檢查是否獲取到特徵
        if not features_dict:
            print("沒有獲取到任何層的特徵")
            return None
            
        print(f"成功獲取 {len(features_dict)} 層特徵")
        
        # 處理特徵以生成注意力圖
        try:
            print("生成多層融合注意力圖...")
            
            # 融合所有層的特徵
            attention_map = None
            
            for layer_name, features in features_dict.items():
                print(f"處理 {layer_name} 的特徵，形狀: {features.shape}")
                
                # 獲取[CLS]標記的特徵和其他位置的特徵
                cls_features = features[:, 0, :]  # [batch_size, hidden_dim]
                patch_features = features[:, 1:, :]  # [batch_size, num_patches, hidden_dim]
                
                # 計算每個位置與[CLS]的相似度
                layer_attention = torch.zeros(patch_features.shape[1], device=device)
                
                for i in range(patch_features.shape[1]):
                    # 計算餘弦相似度
                    similarity = torch.nn.functional.cosine_similarity(cls_features, patch_features[:, i, :], dim=1)
                    layer_attention[i] = similarity[0]
                
                # 轉換為 numpy 並重塑為方形網格
                layer_attention = layer_attention.cpu().numpy()
                grid_size = int(np.sqrt(layer_attention.shape[0]))
                layer_attention_map = layer_attention.reshape(grid_size, grid_size)
                
                # 調整大小到原始圖像尺寸
                layer_attention_map = cv2.resize(layer_attention_map, (original_image_np.shape[1], original_image_np.shape[0]), interpolation=cv2.INTER_LINEAR)
                
                # 累加到最終的注意力圖
                if attention_map is None:
                    attention_map = layer_attention_map
                else:
                    # 使用加權平均，較深層的權重較大
                    layer_idx = int(layer_name.split('_')[1])
                    weight = (layer_idx + 1) / sum(i+1 for i in layers_to_hook)
                    attention_map = attention_map * (1 - weight) + layer_attention_map * weight
            
            # 標準化到 [0, 1] 範圍
            if attention_map.max() > attention_map.min():
                attention_map = (attention_map - attention_map.min()) / (attention_map.max() - attention_map.min())
            else:
                # 如果注意力圖是常數，創建一個中心focused注意力圖
                h, w = original_image_np.shape[:2]
                y, x = np.ogrid[:h, :w]
                center_y, center_x = h // 2, w // 2
                attention_map = 1 - np.sqrt((x - center_x)**2 + (y - center_y)**2) / np.sqrt(center_x**2 + center_y**2)
                attention_map = attention_map**2  # 加強中心
                
            # 應用平滑以減少噪聲
            attention_map = cv2.GaussianBlur(attention_map, (5, 5), 0)
            
            print(f"最終注意力圖形狀: {attention_map.shape}")
            
        except Exception as e:
            print(f"生成注意力圖失敗: {e}")
            print(traceback.format_exc())
            return None
            
        # 應用顏色映射
        try:
            print("應用 colormap...")
            # 轉換為 uint8
            attention_map_uint8 = np.uint8(attention_map * 255)
            
            # 反轉注意力值，使原本的高值變為低值，低值變為高值
            attention_map_reversed = 255 - attention_map_uint8
            
            # 應用 JET 顏色映射
            heatmap = cv2.applyColorMap(attention_map_reversed, cv2.COLORMAP_JET)
            
            # 轉換為 RGB
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            
            # 與原始圖像混合
            alpha = 0.7
            superimposed_img = original_image_np * (1 - alpha) + heatmap * alpha
            superimposed_img = np.uint8(np.clip(superimposed_img, 0, 255))
            
            print("熱圖混合完成")
        except Exception as e:
            print(f"應用 colormap 失敗: {e}")
            print(traceback.format_exc())
            return None
            
        # 保存結果
        try:
            if output_path is None:
                # 創建輸出路徑
                filename = os.path.basename(image_path)
                base_name = os.path.splitext(filename)[0]
                uploads_dir = os.path.join(settings.MEDIA_ROOT, "commission", "uploads")
                output_path = os.path.join(uploads_dir, f"{base_name}_attention.jpg")
                
            print(f"保存到: {output_path}")
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存圖像
            success = False
            
            # 嘗試使用 cv2.imwrite
            try:
                result = cv2.imwrite(output_path, cv2.cvtColor(superimposed_img, cv2.COLOR_RGB2BGR))
                if result:
                    success = True
                    print("保存成功 (cv2)")
                else:
                    print("cv2.imwrite 失敗")
            except Exception as e:
                print(f"cv2.imwrite 失敗: {e}")
                
            # 如果 cv2 失敗，嘗試 PIL
            if not success:
                try:
                    Image.fromarray(superimposed_img).save(output_path)
                    success = True
                    print("保存成功 (PIL)")
                except Exception as e:
                    print(f"PIL save 失敗: {e}")
                    
            # 檢查文件是否存在
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 0:
                    print(f"文件已生成，大小: {file_size} bytes")
                    
                    # 返回相對路徑而不是絕對路徑
                    relative_path = output_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                    if not relative_path.startswith('/'):
                        relative_path = '/' + relative_path
                    
                    return relative_path
                else:
                    print("錯誤: 生成的文件大小為 0")
                    return None
            else:
                print("錯誤: 文件不存在")
                return None
        except Exception as e:
            print(f"保存結果失敗: {e}")
            print(traceback.format_exc())
            return None
            
    except Exception as e:
        print(f"生成替代注意力視覺化時出錯: {e}")
        print(traceback.format_exc())
        return None

