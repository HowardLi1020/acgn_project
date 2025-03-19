# recommendation/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from collections import defaultdict

from .serializers import (
    RecommendationRequestSerializer,
    RecommendationResultSerializer
)
from .vector_service import vector_service
from .models import Movie, Animation, Game, Category

logger = logging.getLogger(__name__)

class RecommendationAPIView(APIView):
    """提供內容推薦的API視圖"""
    # 如果需要用戶認證，請取消下面的註釋
    # permission_classes = [IsAuthenticated]
    
    # 緩存相同的請求15分鐘（根據流量和更新頻率調整）
    @method_decorator(cache_page(60 * 15))
    def post(self, request, format=None):
        """根據用戶查詢提供內容推薦"""
        try:
            serializer = RecommendationRequestSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # 獲取請求參數
            query = serializer.validated_data['query']
            top_k = serializer.validated_data.get('top_k', 10)
            content_type = serializer.validated_data.get('content_type')
            genres = serializer.validated_data.get('genres', [])
            # 新增參數 - 使用GET參數更加靈活
            min_rating = request.data.get('min_rating', 0)
            try:
                min_rating = float(min_rating)
            except (ValueError, TypeError):
                min_rating = 0
                
            diversity_factor = request.data.get('diversity', 0.3)  # 多樣性因子，0-1之間
            try:
                diversity_factor = float(diversity_factor)
                # 確保值在合理範圍內
                diversity_factor = max(0, min(1, diversity_factor))
            except (ValueError, TypeError):
                diversity_factor = 0.3  # 預設值
            
            # 構建過濾條件
            filters = {}
            if content_type:
                filters['content_type'] = content_type
            if genres:
                filters['genres'] = genres
            if min_rating > 0:
                filters['min_rating'] = min_rating
            
            # 記錄請求
            logger.info(f"接收推薦請求: 查詢='{query}', 類型={content_type}, 類型/風格={genres}, 最低評分={min_rating}, 多樣性={diversity_factor}")
            
            # 檢查向量服務狀態
            try:
                model_loaded = vector_service.load_model()
                if not model_loaded:
                    logger.warning("模型未成功加載，返回空結果")
                    return Response({
                        "query": query,
                        "results_count": 0,
                        "recommendations": [],
                        "message": "推薦模型未準備就緒，返回空結果"
                    })
                
                try:
                    vectors_loaded = vector_service.load_vectors()
                    if not vectors_loaded:
                        logger.warning("向量數據未成功加載，嘗試生成測試向量數據")
                        # 如果是開發/測試環境，可以嘗試生成測試向量
                        test_env = getattr(settings, 'DEBUG', False)
                        if test_env:
                            try:
                                test_vectors_created = vector_service.generate_test_vectors(count_per_type=10)
                                if not test_vectors_created:
                                    logger.warning("無法生成測試向量數據")
                                    return Response({
                                        "query": query,
                                        "results_count": 0,
                                        "recommendations": [],
                                        "message": "向量數據未準備就緒，無法生成測試數據"
                                    })
                            except Exception as e:
                                logger.error(f"生成測試向量數據失敗: {str(e)}")
                                return Response({
                                    "query": query,
                                    "results_count": 0,
                                    "recommendations": [],
                                    "message": "向量數據未準備就緒，返回空結果"
                                })
                        else:
                            return Response({
                                "query": query,
                                "results_count": 0,
                                "recommendations": [],
                                "message": "向量數據未準備就緒，返回空結果"
                            })
                except Exception as e:
                    logger.error(f"載入向量數據失敗: {str(e)}")
                    return Response({
                        "query": query,
                        "results_count": 0,
                        "recommendations": [],
                        "message": "載入向量數據時出錯，返回空結果"
                    })
                
                # 執行搜索 - 請求更多結果以便處理多樣性
                initial_count = min(top_k * 3, 50)  # 最多獲取50個，避免過多
                recommendations = vector_service.search(query, top_k=initial_count, filters=filters)
                
                if not recommendations:
                    logger.warning(f"查詢 '{query}' 未找到匹配結果")
                    return Response({
                        "query": query,
                        "results_count": 0,
                        "recommendations": [],
                        "message": "未找到匹配的推薦內容"
                    })
                
                # 應用多樣性處理
                if len(recommendations) > top_k:
                    recommendations = self._diversify_results(recommendations, diversity_factor, top_k)
                else:
                    # 如果結果不足，直接返回所有結果
                    logger.info(f"結果數量不足 ({len(recommendations)} < {top_k})，跳過多樣性處理")
                
                # 序列化結果
                result_serializer = RecommendationResultSerializer(recommendations, many=True)
                
                # 返回結果
                response_data = {
                    "query": query,
                    "results_count": len(recommendations),
                    "recommendations": result_serializer.data
                }
                
                # 添加過濾信息
                if filters:
                    response_data["filters"] = filters
                
                return Response(response_data)
            
            except Exception as e:
                logger.error(f"推薦處理過程中出錯: {str(e)}")
                return Response({
                    "query": query,
                    "results_count": 0,
                    "recommendations": [],
                    "message": f"推薦處理過程中出錯: {str(e)}"
                })
        
        except Exception as e:
            logger.error(f"推薦API處理請求時發生未預期錯誤: {str(e)}")
            return Response({
                "results_count": 0,
                "recommendations": [],
                "message": "處理請求時發生錯誤，返回空結果"
            })
            
    def _diversify_results(self, recommendations, diversity_factor=0.3, target_count=10):
        """使用最大邊際相關性(MMR)增加推薦多樣性"""
        try:
            if not recommendations or len(recommendations) <= 1:
                return recommendations
            
            # 如果多樣性因子為0，則不進行多樣性處理
            if diversity_factor <= 0:
                return recommendations[:target_count]
            
            # 初始化已選結果列表和待選結果列表
            selected = [recommendations[0]]  # 首先選擇最相關的項目
            remaining = recommendations[1:]
            
            # 直到已選結果數量達到目標數量或沒有待選結果
            while remaining and len(selected) < target_count:
                # 初始化最大MMR分數和對應索引
                max_mmr_score = -float('inf')
                best_item_idx = -1
                
                # 計算每個待選結果的MMR分數
                for i, item in enumerate(remaining):
                    # 相關性分數（直接使用原始相似度）
                    relevance = item["similarity_score"]
                    
                    # 計算與已選結果的最大相似度（衡量冗餘度）
                    max_similarity = self._calculate_max_similarity(item, selected)
                    
                    # MMR計算：平衡相關性和多樣性
                    mmr_score = (1 - diversity_factor) * relevance - diversity_factor * max_similarity
                    
                    # 更新最大MMR分數和對應索引
                    if mmr_score > max_mmr_score:
                        max_mmr_score = mmr_score
                        best_item_idx = i
                
                # 將最佳項目添加到已選結果
                if best_item_idx >= 0:
                    selected.append(remaining[best_item_idx])
                    remaining.pop(best_item_idx)
                else:
                    # 理論上不應該發生，但為安全起見增加處理
                    break
            
            logger.info(f"多樣性處理: 原始結果 {len(recommendations)} -> 處理後 {len(selected)}")
            return selected
        except Exception as e:
            logger.error(f"多樣性處理失敗: {str(e)}")
            # 出錯時返回原始結果的前target_count個
            return recommendations[:target_count]
    
    def _calculate_max_similarity(self, item, selected_items):
        """計算一個項目與已選項目集合的最大相似度"""
        if not selected_items:
            return 0
        
        # 計算內容相似度的方法
        similarities = []
        
        for selected in selected_items:
            # 計算類型相似度（相同類型增加相似度）
            type_sim = 1.0 if item['type'] == selected['type'] else 0.0
            
            # 計算類型/風格相似度（共享類型/風格的比例）
            genre_sim = 0.0
            if item['genres'] and selected['genres']:
                common_genres = set(item['genres']).intersection(set(selected['genres']))
                all_genres = set(item['genres']).union(set(selected['genres']))
                if all_genres:
                    genre_sim = len(common_genres) / len(all_genres)
            
            # 組合相似度分數（可調整權重）
            sim_score = (0.4 * type_sim + 0.6 * genre_sim)
            similarities.append(sim_score)
        
        # 返回最大相似度
        return max(similarities) if similarities else 0


class SystemStatusView(APIView):
    """檢查推薦系統狀態的API"""
    def get(self, request, format=None):
        """返回系統狀態信息"""
        try:
            # 檢查模型和向量數據是否已加載
            model_loaded = vector_service.load_model()
            
            try:
                vectors_loaded = vector_service.load_vectors()
            except Exception as e:
                logger.error(f"載入向量數據失敗: {str(e)}")
                vectors_loaded = False
            
            status_data = {
                "status": "healthy" if model_loaded and vectors_loaded else "unhealthy",
                "details": {
                    "model_loaded": model_loaded,
                    "vectors_loaded": vectors_loaded
                }
            }
            
            # 如果向量數據已加載，添加向量信息
            if vectors_loaded and hasattr(vector_service, 'vectors') and vector_service.vectors is not None:
                try:
                    status_data["details"]["vectors_count"] = len(vector_service.vectors)
                    
                    # 添加更詳細的統計信息
                    content_types_count = defaultdict(int)
                    for _, (content_type, _) in vector_service.id_mapping.items():
                        content_types_count[content_type] += 1
                    
                    status_data["details"]["content_types_stats"] = dict(content_types_count)
                except Exception as e:
                    logger.error(f"獲取向量數據統計信息失敗: {str(e)}")
            
            return Response(status_data)
        
        except Exception as e:
            logger.error(f"檢查系統狀態時發生錯誤: {str(e)}")
            return Response({
                "status": "error",
                "message": f"檢查系統狀態時發生錯誤: {str(e)}"
            })


@api_view(['GET'])
def get_content_types(request):
    """獲取所有內容類型"""
    try:
        categories = Category.objects.all().order_by('category_id')
        return Response([
            {"id": cat.category_id, "name": cat.category_name}
            for cat in categories
        ])
    except Exception as e:
        logger.error(f"獲取內容類型時發生錯誤: {str(e)}")
        return Response([])


@api_view(['GET'])
def get_genres(request):
    """獲取所有類型/風格，按內容類型分組"""
    try:
        # 從資料庫獲取不同類型的風格
        movie_genres = set()
        animation_genres = set()
        game_genres = set()
        
        # 電影風格
        for genre_str in Movie.objects.values_list('movie_genre', flat=True).distinct():
            if genre_str:
                movie_genres.update([g.strip() for g in genre_str.split(',')])
        
        # 動畫風格
        for genre_str in Animation.objects.values_list('animation_genre', flat=True).distinct():
            if genre_str:
                animation_genres.update([g.strip() for g in genre_str.split(',')])
        
        # 遊戲風格
        for genre_str in Game.objects.values_list('game_genre', flat=True).distinct():
            if genre_str:
                game_genres.update([g.strip() for g in genre_str.split(',')])
        
        return Response({
            "movie": sorted(list(movie_genres)),
            "animation": sorted(list(animation_genres)),
            "game": sorted(list(game_genres)),
            "all": sorted(list(movie_genres | animation_genres | game_genres))
        })
    except Exception as e:
        logger.error(f"獲取類型/風格時發生錯誤: {str(e)}")
        return Response({
            "movie": [],
            "animation": [],
            "game": [],
            "all": []
        })


@api_view(['POST'])
def generate_vectors(request):
    """為所有內容生成向量表示"""
    try:
        # 檢查身份驗證 (可選)
        # if not request.user.is_staff:
        #    return Response({"message": "需要管理員權限"}, status=status.HTTP_403_FORBIDDEN)
        
        # 獲取請求參數
        content_type = request.data.get('content_type', None)  # 可以指定特定類型，如'movie'
        force_rebuild = request.data.get('force_rebuild', False)
        
        results = {}
        
        if content_type:
            # 更新特定類型的向量
            results[content_type] = vector_service.update_vectors_for_content(content_type)
        else:
            # 更新所有類型的向量
            results['movie'] = vector_service.update_vectors_for_content('movie')
            results['animation'] = vector_service.update_vectors_for_content('animation')
            results['game'] = vector_service.update_vectors_for_content('game')
        
        # 構建索引
        index_result = vector_service.build_index(force_rebuild=force_rebuild)
        results['index_built'] = index_result
        
        success = all(results.values())
        
        return Response({
            "success": success,
            "message": "內容向量生成" + ("成功" if success else "部分失敗"),
            "details": results
        })
    except Exception as e:
        logger.error(f"生成向量時發生錯誤: {str(e)}")
        return Response({
            "success": False,
            "message": f"生成向量時發生錯誤: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_test_vectors(request):
    """生成測試用的向量數據"""
    try:
        # 檢查是否為開發環境
        from django.conf import settings
        if not getattr(settings, 'DEBUG', False):
            return Response({
                "success": False,
                "message": "此功能僅適用於開發環境"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 獲取參數
        count = request.data.get('count', 10)
        try:
            count = int(count)
            if count <= 0:
                count = 10
        except (ValueError, TypeError):
            count = 10
        
        # 生成測試向量
        result = vector_service.generate_test_vectors(count_per_type=count)
        
        return Response({
            "success": result,
            "message": "測試向量生成" + ("成功" if result else "失敗"),
            "details": {
                "count_per_type": count,
                "total_vectors": count * 3 if result else 0  # 三種類型
            }
        })
    except Exception as e:
        logger.error(f"生成測試向量時發生錯誤: {str(e)}")
        return Response({
            "success": False,
            "message": f"生成測試向量時發生錯誤: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)