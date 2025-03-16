import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import pickle
from django.conf import settings
from openai import OpenAI
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
from rest_framework.response import Response
import json

class ChatBotView(APIView):
    def __init__(self):
        super().__init__()
        # 初始化模型和客戶端
        self.model_name = 'BAAI/bge-m3'
        # self.model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        self.model = SentenceTransformer(self.model_name)
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

        # Excel 文件路徑
        self.MOVIES_EXCEL = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_movies.xlsx')
        self.GAMES_EXCEL = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_games.xlsx')

        # 索引存放路徑
        self.TOKENIZED_MOVIE_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_vector.index')
        self.GAMES_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/games_excel_vector.index')
        self.TOKENIZED_MOVIE_IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_ids.pkl')
        self.GAMES_IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/games_excel_ids.pkl')

        # 載入資料和索引
        self.load_data_and_indices()
        
        # 對話歷史記錄
        self.sessions_history = {}

    def load_data_and_indices(self):
        """載入所有必要的數據和索引"""
        try:
            # 載入 Excel 數據
            print("開始載入 Excel 數據...")
            
            # 載入電影數據並清理
            self.movies_data = pd.read_excel(self.MOVIES_EXCEL)
            print(f"原始電影數據數量: {len(self.movies_data)}")
            self.movies_data = self.movies_data.dropna(subset=['movie_description'])
            print(f"清理後電影數據數量: {len(self.movies_data)}")
            
            # 載入遊戲數據並清理
            self.games_data = pd.read_excel(self.GAMES_EXCEL)
            print(f"原始遊戲數據數量: {len(self.games_data)}")
            self.games_data = self.games_data.dropna(subset=['game_description'])
            print(f"清理後遊戲數據數量: {len(self.games_data)}")

            # 重置索引，確保索引連續
            self.movies_data = self.movies_data.reset_index(drop=True)
            self.games_data = self.games_data.reset_index(drop=True)

            print("開始載入向量索引...")
            # 載入索引
            self.movies_index = faiss.read_index(self.TOKENIZED_MOVIE_INDEX_PATH)
            self.games_index = faiss.read_index(self.GAMES_INDEX_PATH)

            print("開始載入 ID 映射...")
            # 載入 ID 映射
            with open(self.TOKENIZED_MOVIE_IDS_PATH, 'rb') as f:
                self.movie_ids = pickle.load(f)
            with open(self.GAMES_IDS_PATH, 'rb') as f:
                self.game_ids = pickle.load(f)

            # 驗證數據一致性
            print("驗證數據一致性...")
            movies_count = len(self.movies_data)
            games_count = len(self.games_data)
            
            if self.movies_index.ntotal != movies_count:
                print(f"警告：電影索引數量 ({self.movies_index.ntotal}) 與數據數量 ({movies_count}) 不匹配")
            if self.games_index.ntotal != games_count:
                print(f"警告：遊戲索引數量 ({self.games_index.ntotal}) 與數據數量 ({games_count}) 不匹配")

            print("所有數據和索引載入成功")
            
        except Exception as e:
            print(f"載入數據和索引時發生錯誤: {e}")
            raise

    def search_similar_items(self, query, is_movie=True, top_k=5):
        """搜索相似項目"""
        try:
            # 將查詢文本轉換為向量
            query_vector = self.model.encode([query], normalize_embeddings=True)
            
            # 選擇使用的索引
            index = self.movies_index if is_movie else self.games_index
            
            # 使用 FAISS 進行搜索
            distances, indices = index.search(query_vector.astype('float32'), top_k)
            return distances[0], indices[0]
        except Exception as e:
            print(f"搜索過程中發生錯誤: {e}")
            return [], []

    def get_item_details(self, idx, is_movie=True):
        """獲取項目詳細信息"""
        try:
            data = self.movies_data if is_movie else self.games_data
            if 0 <= idx < len(data):
                item = data.iloc[idx]
                if is_movie:
                    return {
                        'title': item['movie_title'],
                        'description': item['movie_description'],
                        'genre': item['movie_genre'],
                        'release_date': str(item['release_date']),
                        'type': '電影'
                    }
                else:
                    return {
                        'title': item['game_title'],
                        'description': item['game_description'],
                        'genre': item['game_genre'],
                        'release_date': str(item['release_date']),
                        'type': '遊戲'
                    }
            return None
        except Exception as e:
            print(f"獲取詳情時發生錯誤: {e}")
            return None

    def prepare_context(self, query):
        """準備上下文信息"""
        # 搜索電影和遊戲
        movie_distances, movie_indices = self.search_similar_items(query, is_movie=True)
        game_distances, game_indices = self.search_similar_items(query, is_movie=False)

        context = []
        # 添加電影信息
        for idx in movie_indices:
            if idx >= 0:
                details = self.get_item_details(idx, is_movie=True)
                if details:
                    context.append(
                        f"電影：{details['title']}\n"
                        f"類型：{details['genre']}\n"
                        f"簡介：{details['description']}\n"
                    )

        # 添加遊戲信息
        for idx in game_indices:
            if idx >= 0:
                details = self.get_item_details(idx, is_movie=False)
                if details:
                    context.append(
                        f"遊戲：{details['title']}\n"
                        f"類型：{details['genre']}\n"
                        f"簡介：{details['description']}\n"
                    )

        return "\n".join(context)

    def stream_response(self, completion):
        """生成流式響應"""
        try:
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"生成響應時發生錯誤: {e}")
            yield f"生成響應時發生錯誤: {str(e)}"

    def post(self, request):
        """處理POST請求"""
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            user_message = data.get('message')

            if not session_id or not user_message:
                return Response({'error': '缺少必要參數'}, status=400)

            # 初始化或更新會話歷史
            if session_id not in self.sessions_history:
                self.sessions_history[session_id] = [
                    {"role": "system", "content": "你是一個熟悉電影和遊戲的助理，可以根據用戶需求提供相關推薦和介紹。"}
                ]

            # 更新會話歷史
            self.sessions_history[session_id].append({"role": "user", "content": user_message})

            # 準備上下文
            context = self.prepare_context(user_message)
            
            if not context:
                system_prompt = (
                    "你是一個孰悉電影和遊戲的推薦助理。用戶的描述可能過於模糊，目前未找到相關內容。"
                    "請嘗試提出進一步問題幫助用戶明確需求，或者提供一些通用的推薦。"
                )
            else:
                system_prompt = (
                    "你是一個專業且孰悉電影和遊戲的推薦助理。以下是檢索到的相關信息：\n\n"
                    f"{context}\n\n"
                    "基於檢索到的電影、遊戲資訊（名稱、類型、電影簡介、遊戲簡介等）提供相關推薦，並解釋推薦的原因"
                    "用戶提問的內容可能包含電影、遊戲名稱、類型、關鍵詞等，除非用戶要求同時提供電影和遊戲的信息，否則只需回答其中一種"
                    "請根據這些資訊，以友善和清晰的方式回答用戶的問題。"
                )

            messages = self.sessions_history[session_id] + [{"role": "system", "content": system_prompt}]

            # 調用生成模型
            try:
                completion = self.client.chat.completions.create(
                    model="Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
                    messages=messages,
                    temperature=0.7,
                    stream=True,
                )
                return StreamingHttpResponse(
                    self.stream_response(completion), 
                    content_type='text/event-stream'
                )
            except Exception as e:
                return Response(
                    {'error': f"生成回應時發生錯誤: {str(e)}", 'context': context}, 
                    status=500
                )

        except Exception as e:
            return Response({'error': f"處理請求時發生錯誤: {str(e)}"}, status=500)