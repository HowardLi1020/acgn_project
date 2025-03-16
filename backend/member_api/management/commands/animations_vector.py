from django.core.management.base import BaseCommand
import pandas as pd
import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from django.conf import settings

class Command(BaseCommand):
    help = '為動畫資料創建向量索引'

    def handle(self, *args, **options):
        # 全局設置
        MODEL_NAME = 'BAAI/bge-m3'
        # MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        EXCEL_FILE = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_animations.xlsx')
        VECTOR_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/animations_excel_vector.index')
        IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/animations__excel_ids.pkl')

        def read_excel_data(file_path):
            """從 Excel 文件讀取數據"""
            try:
                self.stdout.write(f"從 {file_path} 讀取數據...")
                data = pd.read_excel(file_path)

                if data.empty:
                    raise ValueError(f"Excel 文件 {file_path} 中沒有數據。")
                
                data = data.dropna(subset=['animation_description'])

                if data.empty:
                    raise ValueError(f"刪除空值後沒有剩餘資料")
                else:
                    self.stdout.write(f"處理後剩餘資料筆數：{len(data)}")

                self.stdout.write("Excel 數據讀取完成。")
                return data
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"讀取 Excel 文件時發生錯誤：{str(e)}"))
                raise e

        def create_vector_index_from_excel(data):
            """從Excel創建向量索引"""
            try:
                self.stdout.write(f"載入 {MODEL_NAME} 模型中...")
                model = SentenceTransformer(MODEL_NAME)

                texts = [
                    f"{row['animation_description']}"
                    for _, row in data.iterrows()
                ]
                index_path = VECTOR_INDEX_PATH
                ids_path = IDS_PATH

                self.stdout.write("生成嵌入向量...")
                embeddings = model.encode(
                    texts,
                    batch_size=16,
                    show_progress_bar=True,
                )

                embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

                os.makedirs(os.path.dirname(index_path), exist_ok=True)
                
                self.stdout.write("創建 FAISS 索引...")
                dimension = embeddings.shape[1]
                index = faiss.IndexFlatIP(dimension)
                index = faiss.IndexIDMap(index)

                ids = data['id'].values.astype('int64')
                index.add_with_ids(embeddings.astype('float32'), ids)

                self.stdout.write(f"保存索引到 {index_path}")
                faiss.write_index(index, index_path)

                self.stdout.write("保存 ID 映射...")
                ids_dict = {
                    row['id']: {
                        'title': row['animation_title'],
                        'genre': row['animation_genre'],
                        'type': 'anime'
                    }
                    for _, row in data.iterrows()
                }
                
                os.makedirs(os.path.dirname(ids_path), exist_ok=True)
                    
                with open(ids_path, 'wb') as f:
                    pickle.dump(ids_dict, f)
                    self.stdout.write(f"ID 映射已保存至 {ids_path}")

                self.stdout.write(self.style.SUCCESS("向量索引創建成功"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"創建向量索引時發生錯誤：{str(e)}"))
                raise e

        try:
            data = read_excel_data(EXCEL_FILE)
            create_vector_index_from_excel(data)
            self.stdout.write(self.style.SUCCESS("所有操作完成！"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"程序執行時發生錯誤：{str(e)}"))
            raise e
