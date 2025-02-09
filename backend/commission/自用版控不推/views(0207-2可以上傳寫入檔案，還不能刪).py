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
from django.views.decorators.cache import never_cache
import time

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

@never_cache
@require_http_methods(["GET", "POST"])
def ViewFn_work_edit(request, view_fn_work_id):
    # 待修BUG：
    # ．分次加入圖檔時，只有最後一次加的圖才被寫入資料庫

    # ．(已解決)上傳未滿5張圖時，會重複上傳
    if request.method == 'POST':
        try:
            with transaction.atomic():
                view_db_work_info_id = get_object_or_404(DbWorkInfo, work_id=view_fn_work_id)
                
                # 新增：處理原始檔案上傳
                if 'original_files' in request.FILES:
                    # 建立儲存路徑
                    save_path = os.path.join('commission', 'workID_file', str(view_fn_work_id))
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)
                    
                    # 處理每個上傳的原始檔案
                    for file in request.FILES.getlist('original_files'):
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

                # 新增：處理刪除的原始檔案
                if 'deleted_original_files' in request.POST:
                    deleted_files = json.loads(request.POST['deleted_original_files'])
                    for filename in deleted_files:
                        # 刪除資料庫記錄
                        DbWorkOriginalFile.objects.filter(
                            work_id=view_fn_work_id,
                            original_file_url=filename
                        ).delete()
                        
                        # 刪除實際檔案
                        file_path = os.path.join('commission', 'workID_file', str(view_fn_work_id), filename)
                        if default_storage.exists(file_path):
                            default_storage.delete(file_path)

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
                            if index < 5:
                                # 找到要替換的圖片記錄
                                image_record = existing_images[index]
                                
                                # 刪除舊檔案
                                old_file_path = os.path.join('commission', 'workID_img', image_record.image_url)
                                if default_storage.exists(old_file_path):
                                    default_storage.delete(old_file_path)
                                

                                # 使用新文件的副檔名
                                new_extension = Path(file.name).suffix
                                new_filename = f"{view_fn_work_id}_sketch{image_record.step}{new_extension}"
                                

                                # 儲存新檔案
                                file_path = os.path.join('commission', 'workID_img', new_filename)
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
                            new_filename = f"{view_fn_work_id}_sketch{index}{new_extension}"
                            image_record = DbWorkImages(
                                work_id=view_db_work_info_id.work_id,
                                step=index,
                                image_url=new_filename
                            )

                            image_record.save()
                            
                            # 儲存新檔案
                            file_path = os.path.join('commission', 'workID_img', new_filename)
                            default_storage.save(file_path, file)


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

# 作品頁-投稿需求案選擇功能用API端點
def ViewFn_need_info_api(request):
    need_info = DbNeedInfo.objects.all().values(
        'need_id', 
        'need_title', 
        'need_category', 
        'need_original_from'
    )
    return JsonResponse(list(need_info), safe=False)


def ViewFn_work_delete(request, view_fn_work_id):
    view_db_work_info = get_object_or_404(DbWorkInfo, pk=view_fn_work_id)
    view_db_work_info.delete()
    
    return HttpResponseRedirect(reverse('commission:Urls_work_list'))


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
    
    # 獲取該用戶的需求列表，並預加載相關的圖片
    view_db_need_info = DbNeedInfo.objects.filter(
        needer_id=view_db_publiccard_info.member_basic_id
    ).prefetch_related(
        'dbneedimages_set'  # 預加載關聯的圖片
    ).order_by('-publish_time')  # 使用 publish_time 進行排序
    
    # 獲取該用戶的價目表資料
    view_db_publiccard_sell = DbPublicCardSell.objects.filter(user=view_db_publiccard_info)
    
    # 動態判斷模板路徑
    url_name = request.resolver_match.url_name
    if url_name != 'Urls_publiccard_edit':
        # 如果不是主編輯頁面，則使用測試目錄下的對應模板
        template_name = f'commission/publiccard_edit_test/{url_name}.html'
    else:
        template_name = 'commission/publiccard_edit.html'

    context = {
        'ViewKey_DbPublicCardInfo': view_db_publiccard_info,
        'ViewKey_DbNeedInfo': view_db_need_info,
        'ViewKey_DbPublicCardSell': view_db_publiccard_sell,
    }
    return render(request, template_name, context)


