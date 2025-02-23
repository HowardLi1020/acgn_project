import pandas as pd
import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from django.conf import settings

# 全局設置
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
EXCEL_FILE = os.path.join(settings.BASE_DIR, 'member_api/original_data/tokenized_descriptions.xlsx')
VECTOR_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_vector.index')
IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_ids.pkl')

# 讀取斷詞結果 Excel
def read_tokenized_excel(file_path):
    """讀取已經人工檢查的斷詞結果"""
    print(f"📥 從 {file_path} 讀取已斷詞資料...")
    df = pd.read_excel(file_path)

    if 'movie_title' not in df.columns or 'tokenized_corpus' not in df.columns:
        raise ValueError("❌ Excel 檔案必須包含 'movie_title' 與 'tokenized_corpus' 欄位！")

    df.dropna(subset=['tokenized_corpus'], inplace=True)
    df['id'] = range(1, len(df) + 1)  # 自動生成唯一 ID
    return df

# 語義向量生成
def generate_embeddings(texts, model_name):
    """使用 Sentence-BERT 生成語義向量"""
    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True
    )
    # 向量正規化 (使用 Inner Product 等同於 Cosine Similarity)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings

# 創建 FAISS 向量索引並保存
def create_faiss_index(embeddings, ids, index_path):
    """使用 FAISS 建立向量索引並保存"""
    # 檢查資料夾是否存在，若無則建立
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # 使用 Inner Product
    index = faiss.IndexIDMap(index)
    index.add_with_ids(embeddings.astype('float32'), ids)

    faiss.write_index(index, index_path)
    print(f"💾 向量索引已保存至：{index_path}")

# 保存 ID 對映表
def save_ids_mapping(df, ids_path):
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
    print(f"💾 ID 對映表已保存至：{ids_path}")

# 主程序
def main():
    try:
        # 讀取已斷詞的描述
        df = read_tokenized_excel(EXCEL_FILE)

        # 語義向量生成
        print("🚀 正在生成語義向量...")
        embeddings = generate_embeddings(
            texts=df['tokenized_corpus'].tolist(),
            model_name=MODEL_NAME
        )

        # 創建 FAISS 向量索引
        create_faiss_index(
            embeddings=embeddings,
            ids=df['id'].values.astype('int64'),
            index_path=VECTOR_INDEX_PATH
        )

        # 保存 ID 對映
        save_ids_mapping(df, IDS_PATH)

        print("🎉 語義向量索引建立完成！")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    main()
