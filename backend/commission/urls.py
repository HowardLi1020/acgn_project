from django.urls import path
from commission import views 


app_name='commission'
# http://127.0.0.1:8000/commission/
urlpatterns = [
    # path('', views.ViewFn_need_list, name='index'), # 只是方便nav連結所以取index，之後可以改nav時一樣改回ViewFn_need_list會比較好懂

    # 需求頁
    path('need_list/', views.ViewFn_need_list, name='Urls_need_list'),
    # path('need_edit/', views.ViewFn_need_edit, name='Urls_need_edit'),
    path('need/edit/<int:view_fn_need_id>/', views.ViewFn_need_edit, name='Urls_need_edit'),
    path('need/delete/<int:view_fn_need_id>/', views.ViewFn_need_delete, name='Urls_need_delete'),
    path('need/case_chose/', views.ViewFn_need_case_chose, name='Urls_need_case_chose'),
    path('update_case_by_work/', views.ViewFn_update_case_by_work, name='Urls_update_case_by_work'), # 更新媒合案件

    # 接案頁
    path('work_list/', views.ViewFn_work_list, name='Urls_work_list'),
    # path('work/edit/', views.ViewFn_work_edit, name='Urls_work_edit'),
    path('work/edit/<int:view_fn_work_id>/', views.ViewFn_work_edit, name='Urls_work_edit'),
    path('work/delete/<int:view_fn_work_id>/', views.ViewFn_work_delete, name='Urls_work_delete'),
    path('api/image-info/', views.ViewFn_image_info_api, name='Urls_image_info_api'), # 原始檔圖片DPI資訊API端點
    path('api/archive-info/', views.ViewFn_archive_info_api, name='Urls_archive_info_api'), # 壓縮檔資訊API端點
    path('api/need-info/', views.ViewFn_need_info_api, name='Urls_need_info_api'), # 選擇投稿需求案id之API端點
    path("upload/", views.upload_and_compare, name="Urls_upload_compare"), # [測試]上傳圖片並比對

    # 名片頁
    path('publiccard_list/', views.ViewFn_publiccard_list, name='Urls_publiccard_list'),
    path('publiccard/edit/<int:view_fn_publiccard_id>/', views.ViewFn_publiccard_edit, name='Urls_publiccard_edit'),
    path('api/filter-items/', views.ViewFn_filter_items, name='Urls_filter_items'), # 卡片篩選器API端點
    
    # 名片剝皮測試用待註解
    # path('publiccard/edit/<int:view_fn_publiccard_id>/[all]publiccard_edit/', views.ViewFn_publiccard_edit, name='[all]publiccard_edit'), #[測試用]名片編輯-剝皮主頁
    # path('publiccard/edit/<int:view_fn_publiccard_id>/banner/', views.ViewFn_publiccard_edit, name='banner'), #[測試用]名片編輯-橫幅
    # path('publiccard/edit/<int:view_fn_publiccard_id>/avatar/', views.ViewFn_publiccard_edit, name='avatar'), #[測試用]名片編輯-頭像
    # path('publiccard/edit/<int:view_fn_publiccard_id>/user_info/', views.ViewFn_publiccard_edit, name='user_info'), #[測試用]名片編輯-個人資訊
    # path('publiccard/edit/<int:view_fn_publiccard_id>/favorite_and_tag/', views.ViewFn_publiccard_edit, name='favorite_and_tag'), #[測試用]名片編輯-喜好作品&屬性Tag
    # path('publiccard/edit/<int:view_fn_publiccard_id>/sell_list/', views.ViewFn_publiccard_edit, name='sell_list'), #[測試用]名片編輯-價目表
    # path('publiccard/edit/<int:view_fn_publiccard_id>/work_sellnow/', views.ViewFn_publiccard_edit, name='work_sellnow'), #[測試用]名片編輯-公開販售作品
    # path('publiccard/edit/<int:view_fn_publiccard_id>/work_sellnow/', views.ViewFn_publiccard_edit, name='work_sellnow'), #[測試用]名片編輯-公開販售作品
    # path('publiccard/edit/<int:view_fn_publiccard_id>/work_done/', views.ViewFn_publiccard_edit, name='work_done'), #[測試用]名片編輯-已成交作品
    # path('publiccard/edit/<int:view_fn_publiccard_id>/need/', views.ViewFn_publiccard_edit, name='need'), #[測試用]名片編輯-需求小卡
    # path('usercard/edit/<int:view_fn_usercard_id>/', views.ViewFn_usercard_edit, name='Urls_usercard_edit'),

]
