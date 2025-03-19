from django.core.management.base import BaseCommand
from django.db import transaction, connections
import numpy as np
import os
import pickle
import shutil
from django.conf import settings
from sentence_transformers import SentenceTransformer
from recommendation.models import ContentVector
from tqdm import tqdm  # 進度條庫

class Command(BaseCommand):
    help = '從數據庫中生成向量表示並構建 PKL 索引'

    def add_arguments(self, parser):
        parser.add_argument('--content_type', type=str, help='指定內容類型：movie, animation, game')
        parser.add_argument('--rebuild', action='store_true', help='重建索引，即使文件已存在')
        parser.add_argument('--model_name', type=str, default='all-MiniLM-L6-v2', help='要使用的sentence-transformer模型')
        parser.add_argument('--force', action='store_true', help='強制執行，忽略錯誤')

    def handle(self, *args, **options):
        content_type = options.get('content_type')
        rebuild = options.get('rebuild', False)
        model_name = options.get('model_name')
        force = options.get('force', False)

        # 設定路徑
        base_dir = settings.BASE_DIR
        app_dir = os.path.join(base_dir, 'recommendation')
        model_dir = os.path.join(app_dir, 'model_files')
        data_dir = os.path.join(app_dir, 'data')
        
        # 確保目錄存在
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(model_dir, exist_ok=True)
        
        # 設定檔案路徑
        vectors_path = os.path.join(data_dir, 'vectors.pkl')
        mapping_path = os.path.join(data_dir, 'content_mapping.pkl')
        transformer_data_path = os.path.join(data_dir, 'transformer_data.pkl')
        sentence_transformer_path = os.path.join(model_dir, 'sentence_transformer')
        
        if os.path.exists(vectors_path) and not rebuild:
            self.stdout.write(self.style.WARNING('向量數據已經存在。使用 --rebuild 參數來重建。'))
            return

        existing_transformer_data = None
        if os.path.exists(transformer_data_path) and not rebuild:
            try:
                with open(transformer_data_path, 'rb') as f:
                    existing_transformer_data = pickle.load(f)
                    model_name = existing_transformer_data.get('model_name', model_name)
                    self.stdout.write(self.style.SUCCESS(f'成功加載現有的transformer數據，使用模型: {model_name}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'無法加載現有的transformer數據: {str(e)}'))

        self.stdout.write(f'正在加載 Sentence Transformer 模型: {model_name}')
        try:
            if os.path.exists(sentence_transformer_path):
                model = SentenceTransformer(sentence_transformer_path)
                self.stdout.write(self.style.SUCCESS('成功從本地路徑加載模型'))
            else:
                model = SentenceTransformer(model_name)
                self.stdout.write(self.style.SUCCESS('成功從Hugging Face加載模型'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'加載模型失敗: {str(e)}'))
            return

        contents = self._get_contents(content_type)
        if not contents:
            self.stdout.write(self.style.ERROR('沒有找到內容數據'))
            if force:
                self.stdout.write(self.style.WARNING('強制繼續執行，創建空的向量數據'))
                vectors_array = np.array([]).astype('float32').reshape(0, model.get_sentence_embedding_dimension())
                id_mapping = {}
                content_data = []
            else:
                return
        else:
            self.stdout.write(f'為 {len(contents)} 項內容生成向量表示')
            vectors = []
            content_data = []
            id_mapping = {}

            # 使用tqdm進度條
            for i, item in enumerate(tqdm(contents, desc="Processing data", unit="item")):
                text = self._prepare_text(item)
                embedding = model.encode(text)
                
                # 確保嵌入向量是 float32 類型
                embedding = np.array(embedding, dtype=np.float32)
                
                vectors.append(embedding)
                content_data.append({
                    'id': item['id'],
                    'content_type': item['content_type'],
                    'title': item['title'],
                    'description': item['description'],
                    'text': text
                })
                
                # 建立ID映射
                id_mapping[i] = (item['content_type'], item['id'])

            vectors_array = np.array(vectors, dtype=np.float32)
            if vectors_array.ndim == 1:
                vectors_array = vectors_array.reshape(-1, 1)

        self.stdout.write('正在保存向量數據到 PKL 文件')
        
        # 備份現有文件
        if os.path.exists(vectors_path) and not rebuild:
            backup_path = vectors_path + '.backup'
            shutil.copy2(vectors_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f'已備份現有的向量數據到: {backup_path}'))
        
        # 保存向量數據
        with open(vectors_path, 'wb') as f:
            pickle.dump(vectors_array, f)
        
        # 保存ID映射
        with open(mapping_path, 'wb') as f:
            pickle.dump(id_mapping, f)
        
        # 保存transformer數據 - 注意這個與向量數據是分開的
        with open(transformer_data_path, 'wb') as f:
            pickle.dump({
                'content_data': content_data, 
                'model_name': model_name,
                'model_dimension': model.get_sentence_embedding_dimension()
            }, f)

        # 只有當有內容數據時才保存到數據庫
        if len(content_data) > 0:
            self._save_vectors_to_db(content_data, vectors_array)
            
        self.stdout.write(self.style.SUCCESS(f'成功生成並保存向量表示和PKL索引。'))
        self.stdout.write(self.style.SUCCESS(f'向量路徑: {vectors_path}'))
        self.stdout.write(self.style.SUCCESS(f'映射路徑: {mapping_path}'))
        self.stdout.write(self.style.SUCCESS(f'轉換器數據路徑: {transformer_data_path}'))

    def _get_contents(self, content_type=None):
        cursor = connections['default'].cursor()
        query_parts = []

        movie_query = """
        SELECT movie_id as id, 'movie' as content_type, movie_title as title, movie_description as description
        FROM movies
        """

        animation_query = """
        SELECT animation_id as id, 'animation' as content_type, animation_title as title, animation_description as description
        FROM animations
        """

        game_query = """
        SELECT game_id as id, 'game' as content_type, game_title as title, game_description as description
        FROM games
        """

        if content_type == 'movie':
            query_parts.append(movie_query)
        elif content_type == 'animation':
            query_parts.append(animation_query)
        elif content_type == 'game':
            query_parts.append(game_query)
        else:
            query_parts.extend([movie_query, animation_query, game_query])

        try:
            full_query = " UNION ALL ".join(query_parts)
            cursor.execute(full_query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'查詢內容失敗: {str(e)}'))
            return []

    def _prepare_text(self, item):
        return f"{item.get('title', '')} {item.get('description', '')}"

    def _save_vectors_to_db(self, content_data, vectors_array):
        try:
            # 檢查長度是否匹配
            if len(content_data) != vectors_array.shape[0]:
                self.stdout.write(self.style.ERROR(f'內容數據和向量數據長度不匹配: {len(content_data)} vs {vectors_array.shape[0]}'))
                return
                
            with transaction.atomic():
                # 清空現有向量
                ContentVector.objects.all().delete()
                
                # 批量創建新向量
                vector_objects = [
                    ContentVector(
                        content_id=data['id'], 
                        content_type=data['content_type'], 
                        vector_binary=vectors_array[i].astype(np.float32).tobytes()
                    )
                    for i, data in enumerate(content_data)
                ]
                ContentVector.objects.bulk_create(vector_objects)
                self.stdout.write(f'成功將 {len(vector_objects)} 個向量保存到數據庫')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'保存向量到數據庫時出錯: {str(e)}'))
            # 提供更詳細的錯誤信息
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))