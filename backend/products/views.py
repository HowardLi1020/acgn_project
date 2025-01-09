from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.models import Products, ProductBrands, ProductCategories, ProductSeries, ProductImages, ProductReviews,  ProductRecommendations, ProductComments
from users.models import ProductWishlist, MemberBasic
from cart.models import ProductMemberRatings
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer, SeriesSerializer, ReviewSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
from datetime import datetime, timedelta
import logging
from django.db.models import Subquery, OuterRef
import json
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views import View
import jwt 
from django.conf import settings


# 設置日誌
logger = logging.getLogger(__name__)
now = datetime.now()
# 刪除不需要的原始模板渲染邏輯（如 render, redirect 等）

# API 版本的視圖

@api_view(['GET'])
def index(request):
    products = Products.objects.all()
    products_data = [
        {
            'product_id': product.product_id,
            'product_name': product.product_name,
            'price': str(product.price),
            'stock': product.stock,
            'image_url': ProductImages.objects.filter(product=product).first().image_url if ProductImages.objects.filter(product=product).exists() else '',
            'brand_name': product.brand.brand_name if product.brand else '未指定',
            'category_name': product.category.category_name if product.category else '未指定',
            'series_name': product.series.series_name if product.series else '未指定'
        }
        for product in products
    ]
    return JsonResponse({'products': products_data})

@api_view(['POST'])
def create_product(request):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'detail': '未授權訪問'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            # 解碼 JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return Response({
                    'detail': '無效的用戶信息'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 驗證用戶是否存在
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({
                    'detail': '用戶不存在'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except jwt.ExpiredSignatureError:
            return Response({
                'detail': 'token已過期'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({
                'detail': '無效的token'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 創建產品
        product = Products(
            product_name=request.data['product_name'],
            description_text=request.data.get('description_text', ''),
            price=request.data['price'],
            stock=request.data['stock'],
            user_id=user_id,  # 直接使用從 token 中獲取的 user_id
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 處理外鍵關係
        if request.data.get('category'):
            product.category_id = request.data['category']
        if request.data.get('brand'):
            product.brand_id = request.data['brand']
        if request.data.get('series'):
            product.series_id = request.data['series']

        product.save()

        # 處理圖片
        images = request.FILES.getlist('images')
        if images:
            for index, image in enumerate(images):
                ProductImages.objects.create(
                    product=product,
                    image_url=image,
                    is_main=1 if index == 0 else 0,
                    created_at=datetime.now()
                )

        return Response({
            'detail': '商品創建成功',
            'product_id': product.product_id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"創建商品時發生錯誤: {str(e)}")
        return Response({
            'detail': f'創建商品時發生錯誤: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'detail': '未授權訪問'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            # 解碼 JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return Response({
                    'detail': '無效的用戶信息'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 驗證用戶是否存在
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({
                    'detail': '用戶不存在'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # 獲取商品
            product = Products.objects.get(product_id=product_id)

            # 檢查是否為商品擁有者
            if product.user_id != user_id:
                return Response({
                    'detail': '您沒有權限刪除此商品'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 刪除相關圖片
            ProductImages.objects.filter(product=product).delete()
            # 刪除商品
            product.delete()
            
            return Response({
                'detail': '商品已成功刪除'
            }, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({
                'detail': 'token已過期'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({
                'detail': '無效的token'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Products.DoesNotExist:
        return Response({
            'detail': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def view_all_products(request):
    try:
        # 獲取查詢參數
        search_query = request.query_params.get('search', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        category_id = request.GET.get('category')
        brand_id = request.GET.get('brand')
        series_id = request.GET.get('series')
        sort = request.GET.get('sort', 'newest')  # 默认排序方式

        logger.debug(f"min_price: {min_price}, max_price: {max_price}")  # 打印 min_price 和 max_price

        # 基本查詢
        products = Products.objects.all().select_related('brand', 'category', 'series')

        # 應用搜索過濾
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        # 根据价格进行筛选
        if min_price and min_price.isdigit():  # 确保 min_price 是有效的数字
            products = products.filter(price__gte=float(min_price))
        if max_price and max_price.isdigit():  # 确保 max_price 是有效的数字
            products = products.filter(price__lte=float(max_price))

        # 根据分类、品牌和系列进行筛选
        if category_id:
            products = products.filter(category_id=category_id)
        if brand_id:
            products = products.filter(brand_id=brand_id)
        if series_id:
            products = products.filter(series_id=series_id)

        # 根据排序条件进行排序
        if sort == 'price_asc':
            products = products.order_by('price')  # 从低到高
        elif sort == 'price_desc':
            products = products.order_by('-price')  # 从高到低
        else:
            products = products.order_by('-created_at')  # 默认按最新上架排序

        # 构建返回的数据
        products_data = []
        for product in products:
            # 获取产品的主图片
            product_image = (ProductImages.objects.filter(product=product, is_main=1).first() or ProductImages.objects.filter(product=product).first())

            product_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'price': str(product.price),
                'stock': product.stock,
                'image_url': str(product_image.image_url) if product_image else '',  # 直接轉換為字符串
                'brand_name': product.brand.brand_name if product.brand else '未指定',
                'category_name': product.category.category_name if product.category else '未指定',
                'series_name': product.series.series_name if product.series else '未指定'
            }
            products_data.append(product_data)

        return JsonResponse({'products': products_data, 'total': len(products_data)}, status=200)
    except Exception as e:
        logger.error(f"处理请求时出错: {e}")  # 打印错误信息
        return JsonResponse({'error': 'An error occurred during the product loading'}, status=500)

@api_view(['GET', 'PUT'])
def edit_product(request, product_id):
    try:
        product = Products.objects.get(product_id=product_id)
        
        if request.method == 'GET':
            # 返回商品詳情
            product_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'description_text': product.description_text,
                'price': str(product.price),
                'stock': product.stock,
                'category': product.category_id,
                'brand': product.brand_id,
                'series': product.series_id,
                'images': [
                    {
                        'image_url': str(image.image_url),
                        'is_main': image.is_main
                    }
                    for image in ProductImages.objects.filter(product=product)
                ]
            }
            return Response(product_data)
            
        elif request.method == 'PUT':
            # 處理要刪除的圖片
            deleted_images = json.loads(request.data.get('deleted_images', '[]'))
            for image_url in deleted_images:
                # 從 URL 中提取圖片路徑
                image_path = image_url.split('/media/')[-1]
                ProductImages.objects.filter(
                    product=product,
                    image_url=image_path
                ).delete()

            # 更新商品信息
            product.product_name = request.data.get('product_name', product.product_name)
            product.description_text = request.data.get('description_text', product.description_text)
            product.price = request.data.get('price', product.price)
            product.stock = request.data.get('stock', product.stock)
            
            if 'category' in request.data:
                product.category_id = request.data['category']
            if 'brand' in request.data:
                product.brand_id = request.data['brand']
            if 'series' in request.data:
                product.series_id = request.data['series']
                
            product.save()
            
            # 處理新上傳的圖片
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    ProductImages.objects.create(
                        product=product,
                        image_url=image,
                        is_main=0
                    )
            
            return Response({'detail': '商品更新成功'})
            
    except Products.DoesNotExist:
        return Response({'detail': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def create_brand(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brand_name = data.get('name')
            # 添加輸入驗證
            if not brand_name:
                return JsonResponse({'message': '類別名稱不能為空'}, status=400)

            # 檢查是否已存在相同名稱的系列
            if ProductSeries.objects.filter(brand_name=brand_name).exists():
                return JsonResponse({'message': '該類別名稱已存在'}, status=400)
            
            brand = ProductBrands.objects.create(brand_name=brand_name)
            return JsonResponse({'message': '類別創建成功', 'category' : {
                'brand_id': brand.brand_id,
                'brand_name': brand.brand_name
            }}, status=201)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid method'}, status=405)

@csrf_exempt
def create_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('name')
            # 添加輸入驗證
            if not category_name:
                return JsonResponse({'message': '分類名稱不能為空'}, status=400)

            # 檢查是否已存在相同名稱的系列
            if ProductSeries.objects.filter(category_name=category_name).exists():
                return JsonResponse({'message': '該分類名稱已存在'}, status=400)

            category = ProductCategories.objects.create(category_name=category_name)
            return JsonResponse({'message': '分類創建成功', 'category': {
                'category_id': category.category_id,
                'category_name': category.category_name
            }}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': '無效的 JSON 數據'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    return JsonResponse({'message': 'Invalid method'}, status=405)

@csrf_exempt
def create_series(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            series_name = data.get('name')

            # 添加輸入驗證
            if not series_name:
                return JsonResponse({'message': '系列名稱不能為空'}, status=400)

            # 檢查是否已存在相同名稱的系列
            if ProductSeries.objects.filter(series_name=series_name).exists():
                return JsonResponse({'message': '該系列名稱已存在'}, status=400)
            
            series = ProductSeries.objects.create(series_name=series_name)
            return JsonResponse({
                'message': '系列創建成功',
                'series': {
                    'series_id': series.series_id,
                    'series_name': series.series_name
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'message': '無效的 JSON 數據'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'創建系列時發生錯誤: {str(e)}'}, status=500)
            
    return JsonResponse({'message': '不支持的請求方法'}, status=405)

# 替換 `render` 的部分
class CategoryListView(generics.ListAPIView):
    queryset = ProductCategories.objects.all().order_by('category_id')
    serializer_class = CategorySerializer

class BrandListView(generics.ListAPIView):
    queryset = ProductBrands.objects.all().order_by('brand_id')
    serializer_class = BrandSerializer

class SeriesListView(generics.ListAPIView):
    queryset = ProductSeries.objects.all().order_by('series_id')
    serializer_class = SeriesSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(APIView):
    def get(self, request, product_id):
        try:
            product = Products.objects.filter(product_id=product_id).first()
            if not product:
                return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

            # 使用 ProductSerializer
            serializer = ProductSerializer(product)
            product_data = serializer.data

            # 獲取品牌、分類和系列的 ID
            product_data.update({
                "brand": product.brand_id,
                "category": product.category_id,
                "series": product.series_id,
            })

            return Response(product_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return Response(
                {"detail": "An error occurred while getting product details."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class MyProductsView(View):
    def get(self, request):
        try:
            # 手動驗證 JWT token
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return JsonResponse({'detail': '未登入，請先登入'}, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 解碼 JWT token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                
                if not user_id:
                    return JsonResponse({'detail': '無效的 token'}, status=401)
                
                # 獲取用戶的產品
                products = Products.objects.filter(user_id=user_id).select_related('brand', 'category', 'series')
                
                # 構建產品數據
                products_data = []
                for product in products:
                    product_image = ProductImages.objects.filter(product=product).first()
                    
                    product_data = {
                        'product_id': product.product_id,
                        'product_name': product.product_name,
                        'price': str(product.price),
                        'stock': product.stock,
                        'image_url': str(product_image.image_url) if product_image else '',
                        'brand_name': product.brand.brand_name if product.brand else '未指定',
                        'category_name': product.category.category_name if product.category else '未指定',
                        'series_name': product.series.series_name if product.series else '未指定'
                    }
                    products_data.append(product_data)
                
                return JsonResponse({'products': products_data}, status=200)
                
            except jwt.ExpiredSignatureError:
                return JsonResponse({'detail': 'token 已過期'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'detail': '無效的 token'}, status=401)
                
        except Exception as e:
            logger.error(f"Error fetching user products: {e}")
            return JsonResponse({'detail': str(e)}, status=500)

@api_view(['POST'])
def toggle_wishlist(request, product_id):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': '請先登入'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            # 解碼 JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return Response({'detail': '無效的用戶信息'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 驗證用戶是否存在
            user = MemberBasic.objects.get(user_id=user_id)
            product = Products.objects.get(product_id=product_id)

            # 檢查是否已經收藏
            wishlist_item = ProductWishlist.objects.filter(user=user, product=product).first()

            if wishlist_item:
                wishlist_item.delete()
                is_in_wishlist = False
            else:
                ProductWishlist.objects.create(user=user, product=product)
                is_in_wishlist = True

            return Response({
                'is_in_wishlist': is_in_wishlist,
                'message': '已更新收藏狀態'
            })

        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)
        except (MemberBasic.DoesNotExist, Products.DoesNotExist):
            return Response({'detail': '用戶或商品不存在'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Toggle wishlist error: {str(e)}")
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def check_wishlist(request, product_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'is_in_wishlist': False})
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return Response({'is_in_wishlist': False})
            
            user = MemberBasic.objects.get(user_id=user_id)
            product = Products.objects.get(product_id=product_id)
            
            is_in_wishlist = ProductWishlist.objects.filter(
                user=user, 
                product=product
            ).exists()

            return Response({'is_in_wishlist': is_in_wishlist})

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return Response({'is_in_wishlist': False})
        except (MemberBasic.DoesNotExist, Products.DoesNotExist):
            return Response({'is_in_wishlist': False})

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeaturedProductsView(APIView):
    def get(self, request):
        featured_products = Products.objects.filter(is_featured=True)
        serializer = ProductSerializer(featured_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NewArrivalsView(APIView):
    def get(self, request):
        try:
            one_month_ago = datetime.now() - timedelta(days=30)
            new_arrivals = Products.objects.filter(date_added__gte=one_month_ago).order_by('-date_added')

            if not new_arrivals.exists():
                new_arrivals = Products.objects.all().order_by('-date_added')[:8]

            products_data = []
            for product in new_arrivals:
                # 獲取產品的第一張圖片
                product_image = ProductImages.objects.filter(product=product).first()
                
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'price': str(product.price),
                    'date_added': product.created_at,
                    'image_url': str(product_image.image_url) if product_image else ''
                }
                products_data.append(product_data)

            if not products_data:
                return JsonResponse({"error": "No new arrivals found."}, status=404)

            return JsonResponse({"products": products_data})

        except Exception as e:
            logger.error(f"Error while fetching new arrivals: {e}")
            return JsonResponse({"error": "載入商品時出現問題，請稍後再試。"}, status=500)

class ProductReviewsView(APIView):
    def get(self, request, product_id):
        product = Products.objects.filter(product_id=product_id).first()
        if not product:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        reviews = ProductReviews.objects.filter(product=product)
        review_data = [{"rating": review.rating, "comment": review.comment, "created_at": review.created_at} for review in reviews]
        return Response(review_data, status=status.HTTP_200_OK)
    
    def post(self, request, product_id):
        try:
            # 獲取請求數據
            data = request.data
            rating = data.get('rating')
            review_text = data.get('review_text')

            # 確保用戶已登入
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'detail': '請先登入'}, status=status.HTTP_401_UNAUTHORIZED)

            # 創建評論
            product = Products.objects.get(product_id=product_id)
            review = ProductReviews.objects.create(
                product=product,
                user_id=user_id,
                rating=rating,
                review_text=review_text
            )

            return Response({'message': '評論已提交'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_featured_products(request):
    featured_products = Products.objects.filter(is_featured=True)
    serialized_products = ProductSerializer(featured_products, many=True)
    return Response(serialized_products.data)

def get_new_arrivals(request):
    one_month_ago = now() - timedelta(days=30)

    # 嘗試獲取符合條件的新品
    new_arrivals = Products.objects.filter(date_added__gte=one_month_ago).order_by('-date_added')

    # 如果新品為空，返回最近的 10 個商品
    if not new_arrivals.exists():
        new_arrivals = Products.objects.all().order_by('-date_added')[:10]  # 限制返回最多 10 個

    # 返回 JSON 格式的數據
    return JsonResponse({
        "products": list(new_arrivals.values())
    })

class ProductRecommendationsView(APIView):
    def get(self, request, product_id):
        try:
            # 獲取當前商品
            product = Products.objects.filter(product_id=product_id).first()
            if not product:
                return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

            # 獲取相似商品，排除當前商品
            recommendations = Products.objects.filter(category=product.category).exclude(product_id=product_id)[:8]  # 限制數量

            # 構建推薦商品數據
            products_data = []
            for product in recommendations:
                product_image = ProductImages.objects.filter(product=product).first()
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'price': str(product.price),
                    'stock': product.stock,
                    'image_url': str(product_image.image_url) if product_image else '',
                    'brand_name': product.brand.brand_name if product.brand else '未指定',
                    'category_name': product.category.category_name if product.category else '未指定',
                    'series_name': product.series.series_name if product.series else '未指定'
                }
                products_data.append(product_data)
            
            return Response(products_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return Response({"detail": "An error occurred while getting recommendations."}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    