from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.models import Products, ProductBrands, ProductCategories, ProductSeries, ProductImages, ProductReviews, ProductWishlist
from users.models import  MemberBasic
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer, SeriesSerializer, ReviewSerializer, ProductDetailSerializer
from rest_framework import generics
from rest_framework.views import APIView
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import jwt 
from django.conf import settings
from cart.models import OrderItems
from django.db.models import F

# 設置日誌
logger = logging.getLogger(__name__)

@api_view(['GET'])
def index(request):
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
            user_id=user_id,
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

        if request.method == 'PUT':
            # 處理刪除圖片請求
            deleted_images = json.loads(request.data.get('deleted_images', '[]'))
            
            # 獲取當前商品的所有圖片
            current_images = ProductImages.objects.filter(product=product)
            
            # 處理要刪除的圖片
            for image_url in deleted_images:
                current_images.filter(image_url__endswith=image_url.split('/')[-1]).delete()

            # 更新商品信息
            product.product_name = request.data.get('product_name', product.product_name)
            product.description_text = request.data.get('description_text', product.description_text)
            product.price = request.data.get('price', product.price)
            product.stock = request.data.get('stock', product.stock)
            
            # 更新分類、品牌和系列
            if request.data.get('category'):
                product.category_id = request.data['category']
            if request.data.get('brand'):
                product.brand_id = request.data['brand']
            if request.data.get('series'):
                product.series_id = request.data['series']
                
            product.save()

            # 處理新上傳的圖片
            if 'image_url' in request.FILES:  # 注意這裡改成 image_url
                for image in request.FILES.getlist('image_url'):  # 這裡也改成 image_url
                    ProductImages.objects.create(
                        product=product,
                        image_url=image,
                        is_main=False,
                    )

            # 確保有一張圖片被標註為主圖
            if not ProductImages.objects.filter(product=product, is_main=True).exists():
                first_image = ProductImages.objects.filter(product=product).first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()

            return Response({'detail': '商品更新成功'})

    except Products.DoesNotExist:
        return Response({'detail': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"更新商品時發生錯誤: {str(e)}")  # 添加日誌
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_brand(request):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': '未授權訪問'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # 解碼 JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                return Response({'detail': '無效的用戶信息'}, status=status.HTTP_401_UNAUTHORIZED)

            # 驗證用戶是否存在
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({'detail': '用戶不存在'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)

        # 創建品牌
        brand_name = request.data.get('name')
        if not brand_name:
            return Response({'detail': '品牌名稱不能為空'}, status=status.HTTP_400_BAD_REQUEST)

        # 檢查是否已存在相同名稱的品牌
        if ProductBrands.objects.filter(brand_name=brand_name).exists():
            return Response({'detail': '該品牌名稱已存在'}, status=status.HTTP_400_BAD_REQUEST)

        brand = ProductBrands.objects.create(brand_name=brand_name)
        return Response({'detail': '品牌創建成功', 'brand_id': brand.brand_id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"創建品牌時發生錯誤: {str(e)}")
        return Response({'detail': f'創建品牌時發生錯誤: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_category(request):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': '未授權訪問'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # 解碼 JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                return Response({'detail': '無效的用戶信息'}, status=status.HTTP_401_UNAUTHORIZED)

            # 驗證用戶是否存在
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({'detail': '用戶不存在'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)

        # 創建分類
        category_name = request.data.get('name')
        if not category_name:
            return Response({'detail': '分類名稱不能為空'}, status=status.HTTP_400_BAD_REQUEST)

        # 檢查是否已存在相同名稱的分類
        if ProductCategories.objects.filter(category_name=category_name).exists():
            return Response({'detail': '該分類名稱已存在'}, status=status.HTTP_400_BAD_REQUEST)

        category = ProductCategories.objects.create(category_name=category_name)
        return Response({'detail': '分類創建成功', 'category_id': category.category_id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"創建分類時發生錯誤: {str(e)}")
        return Response({'detail': f'創建分類時發生錯誤: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_series(request):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': '未授權訪問'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # 解碼 JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                return Response({'detail': '無效的用戶信息'}, status=status.HTTP_401_UNAUTHORIZED)

            # 驗證用戶是否存在
            user = MemberBasic.objects.filter(user_id=user_id).first()
            if not user:
                return Response({'detail': '用戶不存在'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)

        # 創建系列
        series_name = request.data.get('name')
        if not series_name:
            return Response({'detail': '系列名稱不能為空'}, status=status.HTTP_400_BAD_REQUEST)

        # 檢查是否已存在相同名稱的系列
        if ProductSeries.objects.filter(series_name=series_name).exists():
            return Response({'detail': '該系列名稱已存在'}, status=status.HTTP_400_BAD_REQUEST)

        series = ProductSeries.objects.create(series_name=series_name)
        return Response({'detail': '系列創建成功', 'series_id': series.series_id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"創建系列時發生錯誤: {str(e)}")
        return Response({'detail': f'創建系列時發生錯誤: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListView(generics.ListAPIView):
    queryset = ProductCategories.objects.all().order_by('category_id')
    serializer_class = CategorySerializer

class BrandListView(generics.ListAPIView):
    queryset = ProductBrands.objects.all().order_by('brand_id')
    serializer_class = BrandSerializer

class SeriesListView(generics.ListAPIView):
    queryset = ProductSeries.objects.all().order_by('series_id')
    serializer_class = SeriesSerializer

class ProductDetail(APIView):
    def get(self, request, product_id):
        try:
            product = Products.objects.select_related('brand', 'category', 'series').filter(product_id=product_id).first()
            if not product:
                return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

            # 使用 ProductDetailSerializer
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

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

class ProductReviewsView(APIView):
    def get(self, request, product_id):
        try:
            # 獲取當前用戶ID（如果已登入）
            current_user_id = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                try:
                    token = auth_header.split(' ')[1]
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    current_user_id = payload.get('user_id')
                except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                    pass

            # 獲取商品的所有評論
            reviews = ProductReviews.objects.filter(product_id=product_id)\
                .select_related('user')\
                .order_by('-review_date')
            
            # 使用序列化器
            serializer = ReviewSerializer(reviews, many=True)
            reviews_data = serializer.data
            
            # 添加額外的字段
            for review_data, review in zip(reviews_data, reviews):
                review_data['user_name'] = review.user.user_nickname or review.user.user_name
                review_data['is_owner'] = current_user_id == review.user.user_id
            
            return Response(reviews_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"獲取評論時發生錯誤: {str(e)}")
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    # 更新評論
    def put(self, request, product_id, review_id):
        try:
            # 驗證用戶身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'detail': '請先登入'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # 獲取評論
            try:
                review = ProductReviews.objects.get(
                    review_id=review_id,
                    product_id=product_id
                )
            except ProductReviews.DoesNotExist:
                return Response({'detail': '評論不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 確認是否為評論擁有者
            if review.user_id != user_id:
                return Response({'detail': '您沒有權限編輯此評論'}, status=status.HTTP_403_FORBIDDEN)
            
            # 更新評論
            rating = request.data.get('rating')
            review_text = request.data.get('review_text', '')
            
            if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return Response({'detail': '請提供有效的評分（1-5）'}, status=status.HTTP_400_BAD_REQUEST)
            
            review.rating = rating
            review.review_text = review_text
            review.save()
            
            return Response({'detail': '評論已更新'}, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"更新評論時發生錯誤: {str(e)}")
            return Response({'detail': '更新評論時發生錯誤'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request, product_id):
        try:
            # 驗證用戶身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'detail': '請先登入'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # 檢查用戶是否已購買商品
            has_purchased = OrderItems.objects.filter(
                order__user_id=user_id,
                product_id=product_id,
                order__order_status='COMPLETED'
            ).exists()
            
            if not has_purchased:
                return Response({'detail': '您尚未購買此商品，無法評論'}, status=status.HTTP_403_FORBIDDEN)
            
            # 檢查是否已經評論過
            has_reviewed = ProductReviews.objects.filter(
                user_id=user_id,
                product_id=product_id
            ).exists()
            
            if has_reviewed:
                return Response({'detail': '您已經評論過此商品'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 獲取評論數據
            rating = request.data.get('rating')
            review_text = request.data.get('review_text', '')
            
            if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return Response({'detail': '請提供有效的評分（1-5）'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 創建評論
            user = MemberBasic.objects.get(user_id=user_id)
            product = Products.objects.get(product_id=product_id)
            
            review = ProductReviews.objects.create(
                user=user,
                product=product,
                rating=rating,
                review_text=review_text
            )
            
            return Response({'detail': '評論已提交'}, status=status.HTTP_201_CREATED)
            
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"提交評論時發生錯誤: {str(e)}")
            return Response({'detail': '提交評論時發生錯誤'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, product_id, review_id):
        try:
            # 驗證用戶身份
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'detail': '請先登入'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # 獲取評論
            try:
                review = ProductReviews.objects.get(
                    review_id=review_id,
                    product_id=product_id
                )
            except ProductReviews.DoesNotExist:
                return Response({'detail': '評論不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 確認是否為評論擁有者
            if review.user_id != user_id:
                return Response({'detail': '您沒有權限刪除此評論'}, status=status.HTTP_403_FORBIDDEN)
            
            # 刪除評論
            review.delete()
            
            return Response({'detail': '評論已刪除'}, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"刪除評論時發生錯誤: {str(e)}")
            return Response({'detail': '刪除評論時發生錯誤'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def check_can_review(request, product_id):
    try:
        # 從 Authorization header 獲取 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'can_review': False}, status=status.HTTP_200_OK)
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if not user_id:
            return Response({'can_review': False}, status=status.HTTP_200_OK)
        
        # 檢查是否購買過且未評論
        has_purchased = OrderItems.objects.filter(
            order__user_id=user_id,
            product_id=product_id,
            order__order_status='COMPLETED'
        ).exists()
        
        has_reviewed = ProductReviews.objects.filter(
            user_id=user_id,
            product_id=product_id
        ).exists()
        
        can_review = has_purchased and not has_reviewed
        
        return Response({'can_review': can_review}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"檢查評論權限時發生錯誤: {str(e)}")
        return Response({'can_review': False}, status=status.HTTP_200_OK)

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
                    'price': int(product.price),
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
        
@api_view(['GET'])
def get_purchased_products(request):
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
            
            # 獲取用戶的所有已完成訂單中的商品
            purchased_items = OrderItems.objects.filter(
                order__user_id=user_id,
                order__order_status='COMPLETED'
            ).select_related('product', 'order').annotate(
                purchase_date=F('order__order_date')
            ).order_by('-order__order_date')

            
            # 構建響應數據
            products_data = []
            for item in purchased_items:
                product = item.product
                product_image = ProductImages.objects.filter(product=product, is_main=1).first()
                
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'price': float(item.product_price),  # 購買時的價格
                    'quantity': item.quantity,
                    'purchase_date': item.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'order_id': item.order.order_id,
                    'image_url': str(product_image.image_url) if product_image else '',
                    'can_review': not ProductReviews.objects.filter(
                        user_id=user_id,
                        product=product
                    ).exists()
                }
                products_data.append(product_data)
            
            return Response(products_data, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"獲取購買紀錄時發生錯誤: {str(e)}")
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_wishlist(request):
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
            
            # 獲取用戶的收藏商品
            wishlist_items = ProductWishlist.objects.filter(user_id=user_id).select_related('product')
            
            # 構建響應數據
            products_data = []
            for item in wishlist_items:
                product = item.product
                product_image = ProductImages.objects.filter(product=product, is_main=1).first() or ProductImages.objects.filter(product=product).first()
                
                product_data = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'price': float(product.price),
                    'stock': product.stock,
                    'image_url': str(product_image.image_url) if product_image else '',
                    'brand_name': product.brand.brand_name if product.brand else '未指定',
                    'category_name': product.category.category_name if product.category else '未指定',
                    'series_name': product.series.series_name if product.series else '未指定',
                    'added_date': item.added_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                products_data.append(product_data)
            
            return Response({'products': products_data}, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'token已過期'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail': '無效的token'}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"獲取收藏列表時發生錯誤: {str(e)}")
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)