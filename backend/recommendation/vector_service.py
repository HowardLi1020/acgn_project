# recommendation/vector_service.py
import numpy as np
import pickle
import os
import logging
from sentence_transformers import SentenceTransformer
from django.conf import settings
from django.db import connection
from .models import ContentVector, Category, Movie, Animation, Game

logger = logging.getLogger(__name__)

class VectorSearchService:
    """向量搜索服務 - 單例模式確保只有一個實例"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorSearchService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 初始化屬性
        self.model = None
        self.transformer_data = None
        self.vectors = None
        self.id_mapping = {}
        
        # 從設置中獲取配置
        # 設定專案根目錄和App目錄
        base_dir = getattr(settings, 'BASE_DIR', '')
        app_dir = os.path.join(base_dir, 'recommendation')
        
        # 設定模型相關路徑
        self.model_dir = os.path.join(app_dir, 'model_files')
        self.transformer_dir = os.path.join(self.model_dir, 'sentence_transformer')
        
        # 設定PKL文件路徑 - 修正這裡，確保檔案路徑不同
        self.data_dir = os.path.join(app_dir, 'data')
        self.transformer_data_path = os.path.join(self.data_dir, 'transformer_data.pkl')
        self.vectors_path = os.path.join(self.data_dir, 'vectors.pkl')  # 修正：使用不同的檔案名稱
        self.mapping_path = os.path.join(self.data_dir, 'content_mapping.pkl')
        
        # 確保目錄存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        self._initialized = True
        logger.info("向量搜索服務初始化完成")
    
    def load_model(self):
        """載入自訓練的Transformer模型"""
        if self.model is None:
            try:
                logger.info(f"開始嘗試載入模型，自訓練模型目錄: {self.transformer_dir}")
                logger.info(f"目錄是否存在: {os.path.exists(self.transformer_dir)}")
                
                if os.path.exists(self.transformer_dir):
                    # 列出目錄中的文件
                    files = os.listdir(self.transformer_dir)
                    logger.info(f"目錄中的文件: {files}")
                    
                    self.model = SentenceTransformer(self.transformer_dir)
                    logger.info("成功載入自訓練模型")
                else:
                    logger.warning(f"找不到自訓練模型，使用預設模型")
                    self.model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
                    logger.info("成功載入預設模型")
                
                
                # 載入額外的轉換器數據（如果有）
                if os.path.exists(self.transformer_data_path):
                    logger.info(f"載入轉換數據: {self.transformer_data_path}")
                    with open(self.transformer_data_path, 'rb') as f:
                        self.transformer_data = pickle.load(f)
                
                return True
            except Exception as e:
                logger.error(f"載入模型失敗: {str(e)}")
                return False
        return True
    
    def load_vectors(self):
        """載入向量數據"""
        if self.vectors is None:
            try:
                if os.path.exists(self.vectors_path):
                    logger.info(f"從文件載入向量數據: {self.vectors_path}")
                    with open(self.vectors_path, 'rb') as f:
                        data = pickle.load(f)
                        # 確保加載的數據是正確的向量數組
                        if isinstance(data, np.ndarray) and data.dtype == np.float32:
                            self.vectors = data
                        else:
                            logger.warning(f"載入的向量數據格式不正確，嘗試重建...")
                            return self.build_index(force_rebuild=True)
                    
                    # 載入ID映射
                    if os.path.exists(self.mapping_path):
                        with open(self.mapping_path, 'rb') as f:
                            self.id_mapping = pickle.load(f)
                        logger.info(f"載入ID映射，包含 {len(self.id_mapping)} 個項目")
                    else:
                        logger.warning("找不到ID映射文件，將創建新的映射")
                        self._rebuild_id_mapping()
                    
                    return True
                else:
                    logger.warning(f"找不到向量數據文件: {self.vectors_path}")
                    logger.info("將嘗試從數據庫重新構建向量數據")
                    return self.build_index()
            except Exception as e:
                logger.error(f"載入向量數據失敗: {str(e)}")
                logger.info("將嘗試重建索引")
                return self.build_index(force_rebuild=True)
        return True
    
    def _rebuild_id_mapping(self):
        """重新構建ID映射"""
        try:
            # 從數據庫重建映射
            vectors = ContentVector.objects.all()
            self.id_mapping = {i: (item.content_type, item.content_id) for i, item in enumerate(vectors)}
            
            # 保存映射
            with open(self.mapping_path, 'wb') as f:
                pickle.dump(self.id_mapping, f)
            
            logger.info(f"已重建ID映射，包含 {len(self.id_mapping)} 個項目")
            return True
        except Exception as e:
            logger.error(f"重建ID映射失敗: {str(e)}")
            return False
    
    def generate_embedding(self, text):
        """生成文本嵌入向量"""
        if not self.load_model():
            return None
        
        try:
            # 生成嵌入向量
            embedding = self.model.encode([text])[0]
            
            # 確保嵌入向量是 float32 類型
            embedding = np.array(embedding, dtype=np.float32)
            
            # 改進: 對嵌入向量進行正規化處理，提高相似度計算的穩定性
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            # 檢查向量維度是否與存儲的向量匹配
            if hasattr(self, 'vectors') and self.vectors is not None and len(self.vectors) > 0:
                expected_dim = self.vectors.shape[1]
                actual_dim = embedding.shape[0]
                if actual_dim != expected_dim:
                    logger.warning(f"查詢向量維度 ({actual_dim}) 與數據向量維度 ({expected_dim}) 不匹配")
                    # 調整維度
                    if actual_dim < expected_dim:
                        # 如果維度較小，進行填充
                        padding = np.zeros(expected_dim - actual_dim, dtype=np.float32)
                        embedding = np.concatenate([embedding, padding])
                        # 再次正規化
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = embedding / norm
                    else:
                        # 如果維度較大，進行截斷
                        embedding = embedding[:expected_dim]
                        # 再次正規化
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = embedding / norm
                    logger.info(f"已調整查詢向量維度為: {embedding.shape[0]}")
            
            # 如果有額外的轉換器數據，可以在這裡應用額外處理
            if self.transformer_data:
                # 根據您的轉換數據格式進行處理
                # 舉例: 如果transformer_data包含標準化參數
                # if 'mean' in self.transformer_data and 'std' in self.transformer_data:
                #     embedding = (embedding - self.transformer_data['mean']) / self.transformer_data['std']
                pass
            
            return embedding
        except Exception as e:
            logger.error(f"生成嵌入向量失敗: {str(e)}")
            return None
    
    def build_index(self, force_rebuild=False):
        """構建或重建向量索引 (使用PKL)"""
        if self.vectors is not None and not force_rebuild:
            logger.info("向量數據已存在，使用force_rebuild=True強制重建")
            return True
        
        if not self.load_model():
            return False
        
        try:
            # 從數據庫獲取所有內容向量
            logger.info("從數據庫獲取內容向量...")
            vector_items = ContentVector.objects.all()
            
            if not vector_items.exists():
                logger.warning("數據庫中沒有向量數據，請先生成向量")
                return False
            
            # 準備向量數據和ID映射
            vectors = []
            id_mapping = {}
            
            for i, vector_item in enumerate(vector_items):
                # 從二進制字段獲取向量
                vector_binary = vector_item.vector_binary
                vector = np.frombuffer(vector_binary, dtype=np.float32)
                
                # 改進: 對存儲的向量也進行正規化
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
                
                vectors.append(vector)
                id_mapping[i] = (vector_item.content_type, vector_item.content_id)
            
            # 轉換為numpy數組
            vectors = np.array(vectors).astype('float32')
            
            logger.info(f"構建向量數據，向量維度: {vectors.shape[1]}，項目數: {len(vectors)}")
            
            # 保存向量數據和映射
            logger.info(f"保存向量數據到: {self.vectors_path}")
            with open(self.vectors_path, 'wb') as f:
                pickle.dump(vectors, f)
            
            with open(self.mapping_path, 'wb') as f:
                pickle.dump(id_mapping, f)
            
            # 更新實例屬性
            self.vectors = vectors
            self.id_mapping = id_mapping
            
            logger.info(f"向量數據構建完成，包含 {len(vectors)} 個向量")
            return True
        except Exception as e:
            logger.error(f"構建向量數據失敗: {str(e)}")
            return False
    
    def search(self, query_text, top_k=10, filters=None):
        """搜索最相似的內容 (使用PKL)"""
        # 確保模型和向量數據已加載
        if not self.load_model() or not self.load_vectors():
            logger.error("模型或向量數據未加載")
            return []
        
        try:
            # 生成查詢向量
            query_vector = self.generate_embedding(query_text)
            if query_vector is None:
                return []
            
            # 確保查詢向量是 float32 類型
            query_vector = np.array(query_vector, dtype=np.float32)
            
            # 檢查向量維度
            if query_vector.shape[0] != self.vectors.shape[1]:
                logger.warning(f"查詢向量維度 ({query_vector.shape[0]}) 與數據向量維度 ({self.vectors.shape[1]}) 不匹配")
                # 調整維度
                if query_vector.shape[0] < self.vectors.shape[1]:
                    padding = np.zeros(self.vectors.shape[1] - query_vector.shape[0], dtype=np.float32)
                    query_vector = np.concatenate([query_vector, padding])
                    # 再次正規化
                    norm = np.linalg.norm(query_vector)
                    if norm > 0:
                        query_vector = query_vector / norm
                else:
                    query_vector = query_vector[:self.vectors.shape[1]]
                    # 再次正規化
                    norm = np.linalg.norm(query_vector)
                    if norm > 0:
                        query_vector = query_vector / norm
                logger.info(f"已調整查詢向量維度為: {query_vector.shape[0]}")
            
            # 計算與所有向量的相似度
            similarities = []
            for i, vector in enumerate(self.vectors):
                # 確保向量是 float32 類型
                vector = np.array(vector, dtype=np.float32)
                
                # 改進: 使用餘弦相似度替代歐氏距離
                # 計算餘弦相似度
                dot_product = np.dot(vector, query_vector)
                norm_a = np.linalg.norm(vector)
                norm_b = np.linalg.norm(query_vector)
                
                # 避免除以零
                if norm_a > 0 and norm_b > 0:
                    similarity_score = dot_product / (norm_a * norm_b)
                else:
                    similarity_score = 0
                
                # 同時記錄歐氏距離作為備用（保持向後兼容）
                distance = np.sqrt(np.sum((vector - query_vector) ** 2))
                
                similarities.append((i, similarity_score, distance))
            
            # 按相似度排序（從高到低）
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # 獲取結果並應用過濾
            results = []
            content_types_seen = set()  # 用於追蹤已經看到的內容類型
            for idx, similarity_score, distance in similarities[:top_k * 3]:
                if idx < 0 or idx >= len(self.id_mapping):
                    continue
                    
                content_type, content_id = self.id_mapping[int(idx)]
                
                # 根據內容類型從相應的表獲取數據
                content = self._get_content_by_type_id(content_type, content_id)
                if not content:
                    continue
                
                # 應用過濾條件
                if filters and not self._apply_filters(content, content_type, filters):
                    continue
                
                # 改進: 添加內容多樣性控制，限制每種類型的最大數量
                # 如果我們已經有足夠數量的該類型內容，跳過
                max_per_type = max(2, top_k // 3)  # 每種類型最多占1/3
                if content_type in content_types_seen and list(content_types_seen).count(content_type) >= max_per_type:
                    continue
                
                content_types_seen.add(content_type)
                
                # 添加到結果
                results.append({
                    "id": content_id,
                    "title": self._get_title_by_type(content, content_type),
                    "type": content_type,
                    "description": self._get_description_by_type(content, content_type),
                    "genres": self._get_genres_by_type(content, content_type),
                    "similarity_score": float(similarity_score),
                    "poster": self._get_poster_by_type(content, content_type),
                    "metadata": self._get_metadata_by_type(content, content_type)
                })
                
                # 獲取足夠的結果後停止
                if len(results) >= top_k:
                    break
            
            return results
        except Exception as e:
            logger.error(f"搜索失敗: {str(e)}")
            return []
    
    def _get_content_by_type_id(self, content_type, content_id):
        """根據類型和ID獲取內容詳情"""
        try:
            if content_type == 'movie':
                return Movie.objects.get(movie_id=content_id)
            elif content_type == 'animation':
                return Animation.objects.get(animation_id=content_id)
            elif content_type == 'game':
                return Game.objects.get(game_id=content_id)
            else:
                logger.warning(f"未知的內容類型: {content_type}")
                return None
        except Exception as e:
            logger.error(f"獲取內容失敗: {content_type}_{content_id}: {str(e)}")
            return None
    
    def _get_title_by_type(self, content, content_type):
        """根據類型獲取內容標題"""
        if content_type == 'movie':
            return content.movie_title
        elif content_type == 'animation':
            return content.animation_title
        elif content_type == 'game':
            return content.game_title
        return ""
    
    def _get_description_by_type(self, content, content_type):
        """根據類型獲取內容描述"""
        if content_type == 'movie':
            return content.movie_description
        elif content_type == 'animation':
            return content.animation_description
        elif content_type == 'game':
            return content.game_description
        return ""
    
    def _get_genres_by_type(self, content, content_type):
        """根據類型獲取內容類型/風格"""
        if content_type == 'movie':
            return content.movie_genre.split(',')
        elif content_type == 'animation':
            return content.animation_genre.split(',')
        elif content_type == 'game':
            return content.game_genre.split(',')
        return []
    
    def _get_poster_by_type(self, content, content_type):
        """根據類型獲取海報URL"""
        if hasattr(content, 'poster'):
            return content.poster
        return ""
    
    def _get_metadata_by_type(self, content, content_type):
        """根據類型獲取附加元數據"""
        metadata = {}
        
        if content_type == 'movie':
            metadata = {
                'director': content.director,
                'cast': content.cast,
                'rating': float(content.rating) if content.rating else 0,
                'release_date': content.release_date.strftime('%Y-%m-%d') if content.release_date else None
            }
        elif content_type == 'animation':
            metadata = {
                'episodes': content.episodes,
                'studio': content.animation_studio,
                'voice_actors': content.voice_actors,
                'release_date': content.release_date.strftime('%Y-%m-%d') if content.release_date else None
            }
        elif content_type == 'game':
            metadata = {
                'platform': content.game_platform,
                'developer': content.developer,
                'release_date': content.release_date.strftime('%Y-%m-%d') if content.release_date else None
            }
            
        return metadata
    
    def _apply_filters(self, content, content_type, filters):
        """應用過濾條件"""
        # 過濾內容類型
        if 'content_type' in filters and filters['content_type'] and filters['content_type'] != content_type:
            return False
        
        # 過濾類型/風格
        if 'genres' in filters and filters['genres']:
            content_genres = self._get_genres_by_type(content, content_type)
            # 處理不同的傳入格式
            filter_genres = filters['genres']
            if isinstance(filter_genres, str):
                filter_genres = [filter_genres]
                
            if not any(genre in content_genres for genre in filter_genres):
                return False
        
        # 新增: 過濾評分（如果有）
        if 'min_rating' in filters and filters['min_rating'] > 0:
            if content_type == 'movie' and hasattr(content, 'rating'):
                if not content.rating or float(content.rating) < filters['min_rating']:
                    return False
            # 可以為其他內容類型添加類似邏輯
        
        return True
    
    def update_vectors_for_content(self, content_type, content_id=None, batch_size=100):
        """更新指定類型內容的向量表示，可選擇指定ID或更新所有"""
        if not self.load_model():
            return False
        
        try:
            # 根據內容類型選擇合適的查詢
            contents = []
            if content_type == 'movie':
                query = Movie.objects.all()
                if content_id:
                    query = query.filter(movie_id=content_id)
                contents = list(query)
            elif content_type == 'animation':
                query = Animation.objects.all()
                if content_id:
                    query = query.filter(animation_id=content_id)
                contents = list(query)
            elif content_type == 'game':
                query = Game.objects.all()
                if content_id:
                    query = query.filter(game_id=content_id)
                contents = list(query)
            else:
                logger.error(f"未知的內容類型: {content_type}")
                return False
            
            if not contents:
                logger.warning(f"找不到指定類型的內容: {content_type}")
                return False
            
            # 批量處理
            success_count = 0
            error_count = 0
            
            for i in range(0, len(contents), batch_size):
                batch = contents[i:i+batch_size]
                for content in batch:
                    try:
                        # 獲取內容ID
                        if content_type == 'movie':
                            content_id = content.movie_id
                            content_text = self._prepare_movie_text(content)
                        elif content_type == 'animation':
                            content_id = content.animation_id
                            content_text = self._prepare_animation_text(content)
                        elif content_type == 'game':
                            content_id = content.game_id
                            content_text = self._prepare_game_text(content)
                        else:
                            continue
                        
                        # 生成向量
                        vector = self.generate_embedding(content_text)
                        if vector is None:
                            raise ValueError("無法生成向量嵌入")
                            
                        vector_binary = vector.astype(np.float32).tobytes()
                        
                        # 更新或創建向量記錄
                        ContentVector.objects.update_or_create(
                            content_type=content_type,
                            content_id=content_id,
                            defaults={'vector_binary': vector_binary}
                        )
                        
                        success_count += 1
                    except Exception as e:
                        logger.error(f"更新向量失敗 {content_type}_{content_id}: {str(e)}")
                        error_count += 1
            
            logger.info(f"向量更新完成: 成功 {success_count}, 失敗 {error_count}")
            
            # 標記向量數據需要重建
            self.vectors = None
            
            return success_count > 0
        except Exception as e:
            logger.error(f"更新向量處理失敗: {str(e)}")
            return False
    
    # 改進: 優化文本表示方法，增加字段權重
    def _prepare_movie_text(self, movie):
        """準備電影的文本表示，增加重要字段的權重"""
        # 標題重複三次，增加其權重
        text = f"{movie.movie_title} {movie.movie_title} {movie.movie_title} 電影 "
        
        # 添加描述
        if movie.movie_description:
            text += f"{movie.movie_description} "
        
        # 處理類型/風格，每個類型單獨強調
        if movie.movie_genre:
            genres = [g.strip() for g in movie.movie_genre.split(',')]
            for genre in genres:
                if genre:  # 確保不是空字串
                    text += f"{genre} {genre} "  # 重複兩次增加權重
        
        # 添加導演，加上標籤提高語義清晰度
        if movie.director:
            text += f"導演:{movie.director} "
        
        # 添加演員，加上標籤提高語義清晰度
        if movie.cast:
            text += f"演員:{movie.cast} "
        
        return text
    
    def _prepare_animation_text(self, animation):
        """準備動畫的文本表示，增加重要字段的權重"""
        # 標題重複三次，增加其權重
        text = f"{animation.animation_title} {animation.animation_title} {animation.animation_title} 動畫 "
        
        # 添加描述
        if animation.animation_description:
            text += f"{animation.animation_description} "
        
        # 處理類型/風格，每個類型單獨強調
        if animation.animation_genre:
            genres = [g.strip() for g in animation.animation_genre.split(',')]
            for genre in genres:
                if genre:  # 確保不是空字串
                    text += f"{genre} {genre} "  # 重複兩次增加權重
        
        # 添加製作公司，加上標籤提高語義清晰度
        if animation.animation_studio:
            text += f"製作公司:{animation.animation_studio} "
        
        # 添加聲優，加上標籤提高語義清晰度
        if animation.voice_actors:
            text += f"聲優:{animation.voice_actors} "
        
        # 添加集數信息，加上標籤並重複強調
        text += f"共{animation.episodes}集 {animation.episodes}集 "
        
        return text
    
    def _prepare_game_text(self, game):
        """準備遊戲的文本表示，增加重要字段的權重"""
        # 標題重複三次，增加其權重
        text = f"{game.game_title} {game.game_title} {game.game_title} 遊戲 "
        
        # 添加描述
        if game.game_description:
            text += f"{game.game_description} "
        
        # 處理類型/風格，每個類型單獨強調
        if game.game_genre:
            genres = [g.strip() for g in game.game_genre.split(',')]
            for genre in genres:
                if genre:  # 確保不是空字串
                    text += f"{genre} {genre} "  # 重複兩次增加權重
        
        # 添加平台，加上標籤提高語義清晰度
        if game.game_platform:
            platforms = [p.strip() for p in game.game_platform.split(',')]
            for platform in platforms:
                if platform:
                    text += f"平台:{platform} "
        
        # 添加開發商，加上標籤提高語義清晰度
        if game.developer:
            text += f"開發商:{game.developer} "
        
        return text
    
    # 新增: 生成測試向量數據，用於開發和測試環境
    def generate_test_vectors(self, count_per_type=10):
        """為測試生成隨機向量"""
        try:
            # 清除現有向量
            ContentVector.objects.all().delete()
            
            # 內容類型
            content_types = ['movie', 'animation', 'game']
            dim = 384  # 預設向量維度
            
            # 為每種類型生成隨機向量
            for content_type in content_types:
                for i in range(1, count_per_type + 1):
                    # 生成隨機向量
                    vector = np.random.rand(dim).astype(np.float32)
                    # 正規化向量
                    vector = vector / np.linalg.norm(vector)
                    # 轉換為二進制
                    vector_binary = vector.tobytes()
                    
                    # 存儲向量
                    ContentVector.objects.create(
                        content_type=content_type,
                        content_id=i,
                        vector_binary=vector_binary
                    )
                    
                    logger.info(f"已生成測試向量: {content_type}_{i}")
            
            # 構建索引
            result = self.build_index(force_rebuild=True)
            
            logger.info(f"測試向量生成完成，每種類型 {count_per_type} 個，索引構建結果: {result}")
            return result
        except Exception as e:
            logger.error(f"生成測試向量失敗: {str(e)}")
            return False

# 創建全局實例
vector_service = VectorSearchService()