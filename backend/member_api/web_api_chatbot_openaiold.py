import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import os
import pickle
from django.conf import settings
from openai import OpenAI
import openai
from dotenv import load_dotenv
import jieba
from typing import List, Tuple

from rest_framework.views import APIView
from django.http import StreamingHttpResponse
from rest_framework.response import Response
import json
from rank_bm25 import BM25Okapi

class ChatBotView(APIView):
    # 類變量，所有實例共享
    movies_data = None
    games_data = None
    movies_index = None
    games_index = None
    movie_ids = None
    game_ids = None
    movie_bm25 = None
    game_bm25 = None
    model = None
    
    def __init__(self):
        super().__init__()
        
        # 如果是第一次初始化，才載入數據
        if ChatBotView.model is None:
            # 初始化模型
            self.model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
            ChatBotView.model = SentenceTransformer(self.model_name)
            
            # 初始化結巴斷詞
            jieba.initialize()
            
            # 載入所有數據
            self.first_time_load()
        
        # 從環境變數獲取 openai API 金鑰
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("未設置 OPENAI_API_KEY 環境變量")
        
        # 初始化 OpenAI 客戶端
        self.client = OpenAI(
            api_key=api_key,
            timeout=60.0
        )
        
        # 定義停用詞
        self.stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '與', '著'}
        
        # 對話歷史記錄
        self.sessions_history = {}

    def first_time_load(self):
        """首次載入所有必要的數據和索引"""
        try:
            # Excel 文件路徑
            MOVIES_EXCEL = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/original_data/data_movies.xlsx'
            GAMES_EXCEL = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/original_data/data_games.xlsx'
            TOKENIZED_MOVIE_INDEX_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/tokenized_movies_vector.index'
            GAMES_INDEX_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/games_excel_vector.index'
            TOKENIZED_MOVIE_IDS_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/tokenized_movies_ids.pkl'
            GAMES_IDS_PATH = 'C:/Users/User/Desktop/0215/acgn_project/backend/member_api/vector_data/games_excel_ids.pkl'

            print("開始載入 Excel 數據...")
            # 載入電影數據
            ChatBotView.movies_data = pd.read_excel(MOVIES_EXCEL)
            ChatBotView.movies_data = ChatBotView.movies_data.dropna(subset=['movie_description'])
            ChatBotView.movies_data = ChatBotView.movies_data.reset_index(drop=True)
            
            # 載入遊戲數據
            ChatBotView.games_data = pd.read_excel(GAMES_EXCEL)
            ChatBotView.games_data = ChatBotView.games_data.dropna(subset=['game_description'])
            ChatBotView.games_data = ChatBotView.games_data.reset_index(drop=True)

            print("開始載入向量索引...")
            ChatBotView.movies_index = faiss.read_index(TOKENIZED_MOVIE_INDEX_PATH)
            ChatBotView.games_index = faiss.read_index(GAMES_INDEX_PATH)

            print("開始載入 ID 映射...")
            with open(TOKENIZED_MOVIE_IDS_PATH, 'rb') as f:
                ChatBotView.movie_ids = pickle.load(f)
            with open(GAMES_IDS_PATH, 'rb') as f:
                ChatBotView.game_ids = pickle.load(f)

            print("開始載入 BM25 索引...")
            # 構建電影 BM25
            movie_corpus = [jieba.lcut(desc) for desc in ChatBotView.movies_data['movie_description'].astype(str).tolist()]
            ChatBotView.movie_bm25 = BM25Okapi(movie_corpus)

            # 構建遊戲 BM25
            game_corpus = [jieba.lcut(desc) for desc in ChatBotView.games_data['game_description'].astype(str).tolist()]
            ChatBotView.game_bm25 = BM25Okapi(game_corpus)

            print("所有數據和索引載入成功")
            
        except Exception as e:
            print(f"首次載入數據和索引時發生錯誤: {e}")
            raise

    def preprocess_query(self, user_query: str) -> str:
        """使用結巴斷詞處理查詢字串"""
        try:
            # 使用結巴斷詞
            words = jieba.cut(user_query, cut_all=False)
            # 過濾停用詞
            filtered_words = [word for word in words if word not in self.stop_words]
            # 重新組合成字串
            processed_query = ' '.join(filtered_words)
            print(f"原始查詢: {user_query}")
            print(f"處理後查詢: {processed_query}")
            return processed_query
        except Exception as e:
            print(f"查詢預處理時發生錯誤：{str(e)}")
            return user_query

    def search_similar_items(self, query, is_movie=True, top_k= 5) -> List[Tuple[str, float]]:
        """使用 FAISS 索引 + 餘弦相似度搜尋"""
        try:
            # 預處理查詢
            processed_query = self.preprocess_query(query)
            
            # 生成查詢向量
            query_vector = ChatBotView.model.encode([processed_query], normalize_embeddings=True)
            
            # 選擇使用的索引和數據
            index = ChatBotView.movies_index if is_movie else ChatBotView.games_index
            data = ChatBotView.movies_data if is_movie else ChatBotView.games_data
            
            # 使用 FAISS 搜索
            distances, indices = index.search(query_vector.astype('float32'), top_k)
            
            results = []
            for idx, score in zip(indices[0], distances[0]):
                if 0 <= idx < len(data):
                    title = data.iloc[idx]['movie_title' if is_movie else 'game_title']
                    description = data.iloc[idx]['movie_description' if is_movie else 'game_description']
                    genre = data.iloc[idx]['movie_genre' if is_movie else 'game_genre']
                    results.append({
                        'title': title,
                        'description': description,
                        'genre': genre,
                        'score': float(score)
                    })
            
            # 按相似度分數排序
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        except Exception as e:
            print(f"語義搜尋時發生錯誤：{str(e)}")
            return []
        
    
    def load_bm25_index(self):
        """載入 BM25 索引"""
        # 構建電影 BM25
        movie_corpus = [jieba.lcut(desc) for desc in ChatBotView.movies_data['movie_description'].astype(str).tolist()]
        self.movie_bm25 = BM25Okapi(movie_corpus)

        # 構建遊戲 BM25
        game_corpus = [jieba.lcut(desc) for desc in ChatBotView.games_data['game_description'].astype(str).tolist()]
        self.game_bm25 = BM25Okapi(game_corpus)

    def search_bm25(self, query, is_movie=True, top_k=5):
        """使用 BM25 搜尋結果"""
        bm25 = self.movie_bm25 if is_movie else self.game_bm25
        corpus = ChatBotView.movies_data if is_movie else ChatBotView.games_data
        processed_query = jieba.lcut(query)
        scores = bm25.get_scores(processed_query)

        # 獲取分數最高的索引
        top_indices = scores.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            item = corpus.iloc[idx]
            score = scores[idx]
            results.append({
                'title': item['movie_title' if is_movie else 'game_title'],
                'description': item['movie_description' if is_movie else 'game_description'],
                'genre': item['movie_genre' if is_movie else 'game_genre'],
                'score': float(score),
                'type': 'BM25'
            })
        return results
    
    def hybrid_search(self, query, is_movie=True, top_k=5, alpha=0.5, beta=0.5):
        """綜合 BM25 與 FAISS 語義檢索結果"""
        bm25_results = self.search_bm25(query, is_movie, top_k=top_k*2)
        semantic_results = self.search_similar_items(query, is_movie, top_k=top_k*2)

        # 建立結果字典以合併
        merged = {}

        # 加入 BM25 結果
        for res in bm25_results:
            title = res['title']
            merged[title] = {'bm25_score': res['score'], 'semantic_score': 0, 'type': 'BM25'}

        # 加入語義檢索結果
        for res in semantic_results:
            title = res['title']
            if title in merged:
                merged[title]['semantic_score'] = res['score']
            else:
                merged[title] = {'bm25_score': 0, 'semantic_score': res['score'], 'type': 'Semantic'}

        # 加權計算並排序
        results = []
        for title, scores in merged.items():
            final_score = alpha * scores['bm25_score'] + beta * scores['semantic_score']
            results.append({
                'title': title,
                'bm25_score': scores['bm25_score'],
                'semantic_score': scores['semantic_score'],
                'final_score': final_score
            })

        # 根據加權分數排序
        results = sorted(results, key=lambda x: x['final_score'], reverse=True)[:top_k]
        
        return results

    def determine_search_type(self, query):
        """判斷查詢類型（電影/遊戲/兩者）"""
        movie_keywords = {'電影', '影片', '動畫', '動畫片', '劇情片', '電視劇'}
        game_keywords = {'遊戲', '遊戲機', '電玩', '手遊', '遊戲片', '玩遊戲'}
        
        # 使用結巴分詞處理查詢
        words = set(jieba.lcut(query))
        
        # 判斷是否包含特定關鍵字
        has_movie = any(keyword in words for keyword in movie_keywords)
        has_game = any(keyword in words for keyword in game_keywords)
        
        # 返回搜索類型
        if has_movie and not has_game:
            return "movie"
        elif has_game and not has_movie:
            return "game"
        else:
            return "both"

    def prepare_context(self, query, use_retrieval, top_k=5):
        """準備上下文信息"""
        if not use_retrieval:
            return "檢索模型已關閉，無背景資訊。"

        # 判斷查詢類型
        search_type = self.determine_search_type(query)
        context = []
        
        # 根據查詢類型進行搜索
        if search_type in ["movie", "both"]:
            movie_results = self.hybrid_search(query, is_movie=True, top_k=top_k)
            context.append("\n=== 相關電影推薦 ===\n")
            for result in movie_results:
                movie_info = ChatBotView.movies_data[
                    ChatBotView.movies_data['movie_title'] == result['title']
                ].iloc[0]
                context.append(
                    f"電影：{result['title']}\n"
                    f"類型：{movie_info['movie_genre']}\n"
                    f"BM25 分數：{result['bm25_score']:.2f}\n"
                    f"語義分數：{result['semantic_score']:.2f}\n"
                    f"綜合評分：{result['final_score']:.2f}\n"
                    f"簡介：{movie_info['movie_description']}\n"
                )

        if search_type in ["game", "both"]:
            game_results = self.hybrid_search(query, is_movie=False, top_k=top_k)
            context.append("\n=== 相關遊戲推薦 ===\n")
            for result in game_results:
                game_info = ChatBotView.games_data[
                    ChatBotView.games_data['game_title'] == result['title']
                ].iloc[0]
                context.append(
                    f"遊戲：{result['title']}\n"
                    f"類型：{game_info['game_genre']}\n"
                    f"BM25 分數：{result['bm25_score']:.2f}\n"
                    f"語義分數：{result['semantic_score']:.2f}\n"
                    f"綜合評分：{result['final_score']:.2f}\n"
                    f"簡介：{game_info['game_description']}\n"
                )

        return "\n".join(context)

    def stream_response(self, completion):
        """生成流式響應"""
        try:
            buffer = ""
            for chunk in completion:
                # 正確獲取內容
                if chunk.choices[0].delta.content is not None:
                    buffer += chunk.choices[0].delta.content
                    # 在句號、驚嘆號、問號或換行符後添加換行
                    if any(buffer.endswith(end) for end in ["。", "！", "？", "\n"]):
                        yield buffer + "\n"
                        buffer = ""
            # 確保最後的內容也被輸出
            if buffer:
                yield buffer + "\n"
        except Exception as e:
            print(f"生成響應時發生錯誤: {e}")
            yield f"生成響應時發生錯誤: {str(e)}"

    def post(self, request):
        """處理POST請求"""
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            user_message = data.get('message')
            use_retrieval = data.get('use_retrieval', True)
            top_k = data.get('top_k', 5)

            if not session_id or not user_message:
                return Response({'error': '缺少必要參數'}, status=400)

            # 初始化或更新會話歷史
            if session_id not in self.sessions_history:
                self.sessions_history[session_id] = [
                    {"role": "system", "content": "你是一個熟悉電影和遊戲的助理，根據用戶需求提供相關推薦和介紹。"}
                ]

            # 更新會話歷史
            self.sessions_history[session_id].append({"role": "user", "content": user_message})

            # 準備上下文
            context = self.prepare_context(user_message, use_retrieval, top_k)
            
            # 判斷查詢類型
            search_type = self.determine_search_type(user_message)
            
            if not context:
                system_prompt = (
                    "你是一個熟悉電影和遊戲的推薦助理。用戶的描述可能過於模糊，目前未找到相關內容。\n\n"
                    "請遵循以下格式回覆：\n"
                    "1. 每個完整的想法使用一個段落\n"
                    "2. 在每個重要句子後使用換行\n"
                    "3. 使用適當的標點符號來分隔句子\n"
                    "請嘗試提出進一步問題幫助用戶明確需求。"
                )
            else:
                system_prompt = (
                    "你是一個專業且熟悉電影和遊戲的推薦助理。以下是檢索到的相關資訊：\n\n"
                    f"{context}\n\n"
                    "請遵循以下格式回覆：\n"
                    "1. 先簡短總結找到的相關內容\n"
                    "2. 分點列出推薦的原因\n"
                    "3. 每個重點使用獨立段落\n"
                    "4. 在每個句子後適當換行\n"
                    f"5. {'只討論電影相關內容' if search_type == 'movie' else '只討論遊戲相關內容' if search_type == 'game' else '同時討論電影和遊戲的內容'}\n\n"
                    f"用戶問題：{user_message}\n"
                    "基於以上資訊，請提供清晰且結構化的回答。"
                )

            messages = self.sessions_history[session_id] + [{"role": "system", "content": system_prompt}]

            # 調用生成模型
            try:
                # 修改為新版 OpenAI API 調用方式
                completion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
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