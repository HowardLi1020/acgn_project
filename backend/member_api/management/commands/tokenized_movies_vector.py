from django.core.management.base import BaseCommand
import pandas as pd
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Import Excel files and create FAISS index'

    def __init__(self):
        super().__init__()
        # 模型名稱與檔案路徑
        self.model_name = 'BAAI/bge-m3'
        # self.model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        self.EXCEL_FILE = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_movies_tokenized.xlsx')
        self.VECTOR_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_vector.index')
        self.IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_ids.pkl')

    def read_tokenized_excel(self, file_path):
        """讀取已經人工檢查的斷詞結果"""
        self.stdout.write(f"📥 從 {file_path} 讀取已斷詞資料...")
        df = pd.read_excel(file_path)

        if 'movie_title' not in df.columns or 'tokenized_corpus' not in df.columns:
            raise ValueError("❌ Excel 必須包含 'movie_title' 與 'tokenized_corpus' 欄位！")

        df.dropna(subset=['tokenized_corpus'], inplace=True)
        df['id'] = range(1, len(df) + 1)  # 自動生成唯一 ID
        self.stdout.write(f"✅ 成功讀取 {len(df)} 筆資料")
        return df

    def generate_embeddings(self, texts, model_name):
        """使用 Sentence-BERT 生成語義向量"""
        self.stdout.write("🚀 正在生成語義向量...")
        model = SentenceTransformer(model_name)
        embeddings = model.encode(
            texts,
            batch_size=16,
            show_progress_bar=True
        )
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)  # 正規化
        self.stdout.write(f"✅ 語義向量生成完成，共 {len(embeddings)} 筆")
        return embeddings

    def create_faiss_index(self, embeddings, ids, index_path):
        """建立 FAISS 語義向量索引並保存"""
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIDMap(index)
        index.add_with_ids(embeddings.astype('float32'), ids)

        faiss.write_index(index, index_path)
        self.stdout.write(f"💾 向量索引已保存至：{index_path}")

    def save_ids_mapping(self, df, ids_path):
        """將 ID 對映表保存為 pkl"""
        ids_dict = {
            row['id']: {
                'title': row['movie_title'],
                'tokens': row['tokenized_corpus']
            }
            for _, row in df.iterrows()
        }
        with open(ids_path, 'wb') as f:
            pickle.dump(ids_dict, f)
        self.stdout.write(f"💾 ID 對映表已保存至：{ids_path}")

    def handle(self, *args, **kwargs):
        try:
            # 讀取已斷詞資料
            df = self.read_tokenized_excel(self.EXCEL_FILE)

            # 生成語義向量
            embeddings = self.generate_embeddings(
                texts=df['tokenized_corpus'].tolist(),
                model_name=self.model_name
            )

            # 建立 FAISS 向量索引
            self.create_faiss_index(
                embeddings=embeddings,
                ids=df['id'].values.astype('int64'),
                index_path=self.VECTOR_INDEX_PATH
            )

            # 保存 ID 對映表
            self.save_ids_mapping(df, self.IDS_PATH)

            self.stdout.write(self.style.SUCCESS("🎉 語義向量索引建立完成！"))

        except Exception as e:
            self.stderr.write(f"❌ 發生錯誤：{e}")
