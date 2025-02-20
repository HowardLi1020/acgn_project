import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import pickle
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 全局設置
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
MOVIES_EXCEL = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/original_data/data_movies.xlsx'
GAMES_EXCEL = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/original_data/data_games.xlsx'
MOVIES_INDEX_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/movies_excel_vector.index'
GAMES_INDEX_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/games_excel_vector.index'
MOVIES_IDS_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/movies_excel_ids.pkl'
GAMES_IDS_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/games_excel_ids.pkl'


def read_excel_data(file_path, is_movie=True):
    """從 Excel 文件讀取數據"""
    try:
        print(f"從 {file_path} 讀取數據...")
        data = pd.read_excel(file_path)

        # 检查是否有数据
        if data.empty:
            raise ValueError(f"Excel 文件 {file_path} 中沒有數據。")
        
        # 根據數據類型刪除沒有簡介的資料
        if is_movie:
            print("刪除沒有電影簡介的資料...")
            data = data.dropna(subset=['movie_description'])
        else:
            print("刪除沒有遊戲簡介的資料...")
            data = data.dropna(subset=['game_description'])

        # 確認是否還有足夠的資料
        if data.empty:
            raise ValueError(f"刪除空值後沒有剩餘資料")
        else:
            print(f"處理後剩餘資料筆數：{len(data)}")

        print("Excel 數據讀取完成。")
        return data
    except Exception as e:
        print(f"讀取 Excel 文件時發生錯誤：{str(e)}")
        raise e


def create_vector_index_from_excel(data, is_movie=True):
    """從Excel創建向量索引"""
    try:
        # 載入模型
        print(f"載入 {MODEL_NAME} 模型中...")
        model = SentenceTransformer(MODEL_NAME)

        # 根據電影/遊戲"簡述"生成嵌入向量
        if is_movie:
            combined_texts = [
                f"{row['movie_description']}"
                for _, row in data.iterrows()
            ]
            index_path = MOVIES_INDEX_PATH
            ids_path = MOVIES_IDS_PATH
        else:
            combined_texts = [
                f"{row['game_description']}"
                for _, row in data.iterrows()
            ]
            index_path = GAMES_INDEX_PATH
            ids_path = GAMES_IDS_PATH

        print("生成嵌入向量...")
        embeddings = model.encode(
            combined_texts,
            batch_size=16,
            show_progress_bar=True,
            # normalize_embeddings=True
        )

        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)  # 正規化

        # 檢查資料夾是否存在，若無則建立
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # 創建 FAISS 索引
        print("創建 FAISS 索引...")
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIDMap(index)

        # 添加向量到索引
        ids = data['id'].values.astype('int64')
        index.add_with_ids(embeddings.astype('float32'), ids)

        # 保存索引
        print(f"保存索引到 {index_path}")
        faiss.write_index(index, index_path)

        # 保存 ID 映射
        print("保存 ID 映射...")
        if is_movie:
            ids_dict = {
                row['id']: {
                    'title': row['movie_title'],
                    'genre': row['movie_genre'],
                    'type': 'movie'
                }
                for _, row in data.iterrows()
            }
        else:
            ids_dict = {
                row['id']: {
                    'title': row['game_title'],
                    'genre': row['game_genre'],
                    'type': 'game'
                }
                for _, row in data.iterrows()
            }
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(ids_path), exist_ok=True)
            
        with open(ids_path, 'wb') as f:
            pickle.dump(ids_dict, f)
            print(f"ID 映射已保存至 {ids_path}")

        print("向量索引創建成功")
    except Exception as e:
        print(f"創建向量索引時發生錯誤：{str(e)}")
        raise e

def main():
    try:
        # 分別讀取電影和遊戲數據
        movies_data = read_excel_data(MOVIES_EXCEL, is_movie=True)
        games_data = read_excel_data(GAMES_EXCEL, is_movie=False)

        # 分別創建向量索引
        create_vector_index_from_excel(movies_data, is_movie=True)
        create_vector_index_from_excel(games_data, is_movie=False)
        
        print("所有操作完成！")
    except Exception as e:
        print(f"程序執行時發生錯誤：{str(e)}")
        raise e

if __name__ == "__main__":
    main()