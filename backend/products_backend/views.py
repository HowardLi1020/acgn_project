from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from products.models import Products, ProductBrands, ProductSeries, ProductCategories, ProductImages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import logging
import traceback
import os
import json

logger = logging.getLogger(__name__)

def index(request):
    try:
        # 獲取篩選參數
        search_query = request.GET.get('search', '')
        category_id = request.GET.get('category')
        brand_id = request.GET.get('brand')
        series_id = request.GET.get('series')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort_order = request.GET.get('sort', 'newest')

        # 獲取所有分類、品牌和系列
        categories = ProductCategories.objects.all()
        brands = ProductBrands.objects.all()
        series = ProductSeries.objects.all()

        # 構建查詢集
        products = Products.objects.all().prefetch_related('productimages_set')

        # 應用搜索過濾
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        # 應用篩選條件
        if category_id:
            products = products.filter(category_id=category_id)
        if brand_id:
            products = products.filter(brand_id=brand_id)
        if series_id:
            products = products.filter(series_id=series_id)
        if min_price and min_price.isdigit():
            products = products.filter(price__gte=float(min_price))
        if max_price and max_price.isdigit():
            products = products.filter(price__lte=float(max_price))

        # 應用排序
        if sort_order == 'price_asc':
            products = products.order_by('price')
        elif sort_order == 'price_desc':
            products = products.order_by('-price')
        elif sort_order == 'newest':
            products = products.order_by('-created_at')

        # 準備返回的數據
        products_data = []
        for product in products:
            main_image = product.productimages_set.filter(is_main=1).first()
            image_url = main_image.image_url.url if main_image else ''
            products_data.append({
                'id': product.product_id,
                'product_name': product.product_name,
                'brand_name': product.brand.brand_name if product.brand else '未指定',
                'category_name': product.category.category_name if product.category else '未指定',
                'series_name': product.series.series_name if product.series else '未指定',
                'price': int(product.price),
                'stock': product.stock,
                'image_url': image_url,
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'products': products_data,
                'categories': list(categories.values('category_id', 'category_name')),
                'brands': list(brands.values('brand_id', 'brand_name')),
                'series': list(series.values('series_id', 'series_name'))
            })

        context = {
            'products_data': products_data,
            'categories': categories,
            'brands': brands,
            'series': series,
        }
        return render(request, 'products_backend/index.html', context)
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}", exc_info=True)
        return render(request, 'products_backend/index.html', {'error': str(e)})

def edit_product(request, product_id):
    try:
        product = get_object_or_404(Products, product_id=product_id)
        
        if request.method == 'GET':
            # 獲取商品相關數據
            product_images = ProductImages.objects.filter(product=product)
            main_image = product_images.filter(is_main=1).first()
            other_images = product_images.filter(is_main=0)
            
            # 計算剩餘的圖片槽位
            max_images = 5
            current_image_count = product_images.count()
            slot_range = range(max_images - current_image_count)  # 修改這裡
            
            context = {
                'product': product,
                'brands': ProductBrands.objects.all(),
                'categories': ProductCategories.objects.all(),
                'series': ProductSeries.objects.all(),
                'main_image': main_image,
                'other_images': other_images,
                'MEDIA_URL': settings.MEDIA_URL,
                'slot_range': slot_range  # 確保變量名稱與模板中一致
            }
            return render(request, 'products_backend/edit_product.html', context)
            
        elif request.method == 'POST':
            try:
                # 更新基本信息
                product.product_name = request.POST.get('product_name')
                product.description_text = request.POST.get('description_text')
                product.price = request.POST.get('price')
                product.stock = request.POST.get('stock')
                
                if request.POST.get('category'):
                    product.category_id = request.POST.get('category')
                if request.POST.get('brand'):
                    product.brand_id = request.POST.get('brand')
                if request.POST.get('series'):
                    product.series_id = request.POST.get('series')

                product.save()

                # 先處理刪除的圖片
                deleted_images_json = request.POST.get('deleted_images', '[]')
                try:
                    deleted_images = json.loads(deleted_images_json)
                    for image_path in deleted_images:
                        try:
                            image = ProductImages.objects.get(
                                product=product,
                                image_url=image_path
                            )
                            # 實際刪除檔案
                            file_path = os.path.join(settings.MEDIA_ROOT, str(image.image_url))
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            image.delete()
                        except Exception as e:
                            logger.error(f"刪除圖片出錯: {str(e)}")
                except json.JSONDecodeError:
                    logger.error("解析deleted_images JSON時出錯")
                
                # 處理新上傳的圖片
                files = request.FILES.getlist('image_url')
                existing_images_count = ProductImages.objects.filter(product=product).count()
                
                if files:
                    for index, file in enumerate(files):
                        try:
                            is_main = (index == 0 and existing_images_count == 0)  # 如果是第一張且沒有其他圖片，設為主圖
                            new_image = ProductImages(
                                product=product,
                                image_url=file,
                                is_main=is_main
                            )
                            new_image.save()
                        except Exception as e:
                            logger.error(f"保存新圖片時出錯: {str(e)}")

                # 確保至少有一張主圖
                all_images = ProductImages.objects.filter(product=product)
                if all_images.exists() and not all_images.filter(is_main=True).exists():
                    first_image = all_images.first()
                    first_image.is_main = True
                    first_image.save()

                return redirect('products_backend:index')

            except Exception as e:
                logger.error(f"更新商品時發生錯誤: {str(e)}")
                logger.error(traceback.format_exc())
                return redirect('products_backend:index')

        max_images = 5
        current_image_count = ProductImages.objects.filter(product=product).count()
        slot_range = range(max_images - current_image_count)
                
        # GET 請求處理
        context = {
            'product': product,
            'brands': ProductBrands.objects.all(),
            'categories': ProductCategories.objects.all(),
            'series': ProductSeries.objects.all(),
            'main_image': ProductImages.objects.filter(product=product, is_main=True).first(),
            'other_images': ProductImages.objects.filter(product=product, is_main=False),
            'MEDIA_URL': settings.MEDIA_URL,
            'slot_range': slot_range
        }
        return render(request, 'products_backend/edit_product.html', context)
                
    except Exception as e:
        logger.error(f"編輯商品時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        context = {
            'error_message': str(e),
            'product': product if 'product' in locals() else None,
            'brands': ProductBrands.objects.all(),
            'categories': ProductCategories.objects.all(),
            'series': ProductSeries.objects.all(),
            'MEDIA_URL': settings.MEDIA_URL
        }
        return render(request, 'products_backend/edit_product.html', context)

def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = Products.objects.get(product_id=product_id)
            product_name = product.product_name
            product.delete()
            return JsonResponse({'status': 'success', 'message': f'產品 "{product_name}" 已成功刪除。'})
        except Products.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '找不到指定的產品。'}, status=404)
        except Exception as e:
            error_message = f"刪除產品時發生錯誤: {str(e)}"
            print(error_message)
            print(traceback.format_exc())  # 這會打印完整的錯誤堆棧跟踪
            return JsonResponse({'status': 'error', 'message': error_message}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': '僅支持 POST 請求。'}, status=405)

def search(request):
    try:
        query = request.GET.get('query', '')
        logger.info(f"Received search query: {query}")

        if query:
            products = Products.objects.filter(
                product_name__icontains=query
            ).select_related('brand', 'category', 'series').prefetch_related('productimages_set')
        else:
            products = Products.objects.all().select_related(
                'brand', 'category', 'series'
            ).prefetch_related('productimages_set')

        products_data = []
        for product in products:
            # 獲取主圖片
            main_image = product.productimages_set.filter(is_main=1).first()
            image_url = main_image.image_url.url if main_image else ''

            products_data.append({
                'id': product.product_id,
                'product_name': product.product_name,
                'price': int(product.price),
                'stock': product.stock,
                'image_url': image_url,
                'brand_name': product.brand.brand_name if product.brand else '未指定',
                'category_name': product.category.category_name if product.category else '未指定',
                'series_name': product.series.series_name if product.series else '未指定'
            })

        logger.info(f"Returning {len(products_data)} products")
        return JsonResponse({'products': products_data})
    except Exception as e:
        logger.error(f"Error in search view: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred during the search'}, status=500)
    
def add_brand(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brand_name = data.get('brand_name')
            if brand_name:
                try:
                    brand = ProductBrands(brand_name=brand_name)
                    brand.save()
                    return JsonResponse({'status': 'success', 'brand_id': brand.brand_id})
                except Exception as e:
                    logger.error(f"新增品牌時發生錯誤: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': '新增品牌失敗，請稍後再試。'}, status=500)
            return JsonResponse({'status': 'error', 'message': '品牌名稱不能為空！'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '僅支持 POST 請求。'}, status=405)

def add_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('category_name')
            if category_name:
                try:
                    category = ProductCategories(category_name=category_name)
                    category.save()
                    return JsonResponse({'status': 'success', 'category_id': category.category_id})
                except Exception as e:
                    logger.error(f"新增分類時發生錯誤: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': '新增分類失敗，請稍後再試。'}, status=500)
            return JsonResponse({'status': 'error', 'message': '分類名稱不能為空！'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '僅支持 POST 請求。'}, status=405)

def add_series(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            series_name = data.get('series_name')
            if series_name:
                try:
                    series = ProductSeries(series_name=series_name)
                    series.save()
                    return JsonResponse({'status': 'success', 'series_id': series.series_id})
                except Exception as e:
                    logger.error(f"新增系列時發生錯誤: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': '新增系列失敗，請稍後再試。'}, status=500)
            return JsonResponse({'status': 'error', 'message': '系列名稱不能為空！'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '僅支持 POST 請求。'}, status=405)