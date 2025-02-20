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
from sklearn.preprocessing import MultiLabelBinarizer
from fuzzywuzzy import fuzz

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
            # 載入電影.遊戲數據
            ChatBotView.movies_data = pd.read_excel(MOVIES_EXCEL).dropna(subset=['movie_description']).reset_index(drop=True)
            ChatBotView.games_data = pd.read_excel(GAMES_EXCEL).dropna(subset=['game_description']).reset_index(drop=True)

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
        try:
            # 1. 使用結巴分詞處理查詢
            query_words = set(jieba.lcut(query))
            
            # 2. FuzzyWuzzy 進行標題匹配
            title_matches = self.fuzzy_title_search(query, is_movie)
            
            # 3. BM25 + One-Hot 進行類型匹配
            type_matches = self.type_search(query_words, is_movie)
            
            # 4. 合併結果並取 top-k
            merged = {}
            
            # 合併標題匹配結果
            for match in title_matches:
                merged[match['title']] = {
                    'index': match['index'],
                    'title': match['title'],
                    'description': match['description'],
                    'genre': match['genre'],
                    'title_score': match['score'],
                    'type_score': 0,
                    'semantic_score': 0
                }
            
            # 合併類型匹配結果
            for match in type_matches:
                if match['title'] in merged:
                    merged[match['title']]['type_score'] = match['score']
                else:
                    merged[match['title']] = {
                        'index': match['index'],
                        'title': match['title'],
                        'description': match['description'],
                        'genre': match['genre'],
                        'title_score': 0,
                        'type_score': match['score'],
                        'semantic_score': 0
                    }
            
            # 5. 使用 FAISS 進行語義搜索
            query_vector = ChatBotView.model.encode([query], normalize_embeddings=True)
            index = ChatBotView.movies_index if is_movie else ChatBotView.games_index
            distances, indices = index.search(query_vector.astype('float32'), top_k * 2)
            
            # 將語義搜索結果加入合併結果
            data = ChatBotView.movies_data if is_movie else ChatBotView.games_data
            for idx, score in zip(indices[0], distances[0]):
                if 0 <= idx < len(data):
                    title = data.iloc[idx]['movie_title' if is_movie else 'game_title']
                    if title in merged:
                        merged[title]['semantic_score'] = float(score)
                    else:
                        merged[title] = {
                            'index': idx,
                            'title': title,
                            'description': data.iloc[idx]['movie_description' if is_movie else 'game_description'],
                            'genre': data.iloc[idx]['movie_genre' if is_movie else 'game_genre'],
                            'title_score': 0,
                            'type_score': 0,
                            'semantic_score': float(score)
                        }
            
            # 計算最終分數並排序
            results = []
            for item in merged.values():
                # 加權計算最終分數
                final_score = (
                    item['title_score'] * 0.4 +  # 標題匹配權重
                    item['type_score'] * 0.3 +   # 類型匹配權重
                    item['semantic_score'] * 0.3  # 語義相似度權重
                )
                results.append({**item, 'final_score': final_score})
            
            # 根據最終分數排序
            results.sort(key=lambda x: x['final_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"混合搜索時發生錯誤：{str(e)}")
            return []

    def fuzzy_title_search(self, query, is_movie=True):
        """使用 FuzzyWuzzy 進行標題匹配"""
        try:
            data = ChatBotView.movies_data if is_movie else ChatBotView.games_data
            title_field = 'movie_title' if is_movie else 'game_title'
            
            # 計算每個標題的匹配分數
            matches = []
            for idx, row in data.iterrows():
                title = str(row[title_field])
                # 使用多種匹配方式
                ratio = fuzz.ratio(query, title)  # 完全匹配
                partial_ratio = fuzz.partial_ratio(query, title)  # 部分匹配
                token_sort_ratio = fuzz.token_sort_ratio(query, title)  # 排序後匹配
                token_set_ratio = fuzz.token_set_ratio(query, title)  # 集合匹配
                
                # 取最高分數
                max_score = max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
                
                if max_score > 30:  # 降低閾值，增加匹配機會
                    matches.append({
                        'index': idx,
                        'title': title,
                        'score': max_score / 100.0,  # 將分數標準化到 0-1 範圍
                        'description': row['movie_description' if is_movie else 'game_description'],
                        'genre': row['movie_genre' if is_movie else 'game_genre']
                    })
            
            # 根據分數排序
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches
        except Exception as e:
            print(f"標題匹配時發生錯誤：{str(e)}")
            return []

    def type_search(self, query_words, is_movie=True):
        """使用 BM25 + One-Hot Encoding 進行類型匹配"""
        try:
            data = ChatBotView.movies_data if is_movie else ChatBotView.games_data
            genre_field = 'movie_genre' if is_movie else 'game_genre'
            
            # 將類型轉換為 One-Hot 編碼
            mlb = MultiLabelBinarizer()
            genres = [set(g.split('/')) for g in data[genre_field]]
            genre_matrix = mlb.fit_transform(genres)
            
            # 使用 BM25 進行描述匹配
            bm25 = ChatBotView.movie_bm25 if is_movie else ChatBotView.game_bm25
            desc_scores = bm25.get_scores(query_words)
            
            # 標準化 BM25 分數
            if len(desc_scores) > 0:
                max_score = max(desc_scores)
                if max_score > 0:
                    desc_scores = desc_scores / max_score
            
            # 計算類型相似度
            matches = []
            for idx, (genre_vec, desc_score) in enumerate(zip(genre_matrix, desc_scores)):
                # 結合 BM25 分數和類型匹配
                score = desc_score * 0.7 + np.sum(genre_vec) * 0.3
                if score > 0:
                    matches.append({
                        'index': idx,
                        'title': data.iloc[idx]['movie_title' if is_movie else 'game_title'],
                        'score': float(score),
                        'description': data.iloc[idx]['movie_description' if is_movie else 'game_description'],
                        'genre': data.iloc[idx][genre_field]
                    })
            
            # 根據分數排序
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches
        except Exception as e:
            print(f"類型匹配時發生錯誤：{str(e)}")
            return []

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
            return ["檢索模型已關閉，將使用 AI 直接回答問題。"]

        # 判斷查詢類型
        search_type = self.determine_search_type(query)
        context = []
        
        # 根據查詢類型進行搜索
        if search_type in ["movie", "both"]:
            movie_results = self.hybrid_search(query, is_movie=True, top_k=top_k)
            context.append("\n=== 相關電影推薦 ===\n")
            for result in movie_results:
                context.append(
                    f"電影：{result['title']}\n"
                    f"類型：{result['genre']}\n"
                    f"標題匹配分數：{result.get('title_score', 0):.2f}\n"
                    f"類型匹配分數：{result.get('type_score', 0):.2f}\n"
                    f"語義相似度：{result.get('semantic_score', 0):.2f}\n"
                    f"綜合評分：{result['final_score']:.2f}\n"
                    f"簡介：{result['description']}\n"
                )

        if search_type in ["game", "both"]:
            game_results = self.hybrid_search(query, is_movie=False, top_k=top_k)
            context.append("\n=== 相關遊戲推薦 ===\n")
            for result in game_results:
                context.append(
                    f"遊戲：{result['title']}\n"
                    f"類型：{result['genre']}\n"
                    f"標題匹配分數：{result.get('title_score', 0):.2f}\n"
                    f"類型匹配分數：{result.get('type_score', 0):.2f}\n"
                    f"語義相似度：{result.get('semantic_score', 0):.2f}\n"
                    f"綜合評分：{result['final_score']:.2f}\n"
                    f"簡介：{result['description']}\n"
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

    def is_entertainment_related(self, question):
        """判斷是否為娛樂相關問題"""
        # 直接相關關鍵詞
        direct_keywords = {
            '電影', '遊戲', '動畫', '漫畫', '卡通',
            '劇情', '角色', '故事', '演員', '導演',
            '玩法', '關卡', '通關', '打怪', '副本',
            '動漫', '聲優', '漫畫家', '作者', '製作',
            '上映', '發售', '續作', '系列', '評價',
            '推薦', '好看', '好玩', '劇場版', '新作'
        }
        
        # 間接相關詞（需要配合上下文判斷）
        context_keywords = {
            '主角', '結局', '情節', '場景', '配樂',
            '畫面', '特效', '表現', '風格', '體驗',
            '精彩', '有趣', '感人', '刺激', '好聽',
            '經典', '熱門', '最新', '排行', '分數'
        }
        
        # 使用結巴分詞處理問題
        words = set(jieba.lcut(question))
        
        # 檢查是否包含直接相關關鍵詞
        if any(keyword in words for keyword in direct_keywords):
            return True
            
        # 檢查是否包含間接相關關鍵詞（需要更多上下文判斷）
        context_matches = sum(1 for keyword in context_keywords if keyword in words)
        if context_matches >= 2:  # 如果包含兩個以上的間接關鍵詞，也認為是相關的
            return True
            
        return False

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

            # 判斷是否為娛樂相關問題
            if not self.is_entertainment_related(user_message):
                return Response({
                    'message': '抱歉，我僅限於娛樂相關話題喔！您可以試著詢問關於電影、遊戲、動畫、漫畫等相關內容。',
                    'type': 'entertainment_filter'
                }, status=200)

            # 初始化或更新會話歷史
            if session_id not in self.sessions_history:
                self.sessions_history[session_id] = [
                    {"role": "system", "content": 
                     "你是一個專業且熟悉『電影、遊戲、卡通、動畫、漫畫』的娛樂助理。"
                    "不包括政治、宗教、新聞、體育、股票、教育等主題。\n"
                    "對於無關問題請回覆：\n"
                    "『抱歉，我僅限於娛樂相關話題喔！您可以嘗試在網路上搜尋相關資訊。』"}
                ]

            # 更新會話歷史
            self.sessions_history[session_id].append({"role": "user", "content": user_message})

            # 準備上下文
            context = self.prepare_context(user_message, use_retrieval, top_k)
            
            # 判斷查詢類型
            search_type = self.determine_search_type(user_message)
            
            system_prompt = (
                    "你是一個專業且熟悉電影、遊戲、動畫、漫畫的推薦助理，請根據以下資訊回答問題。\n\n"
                    "檢索到的相關資訊：\n"
                    f"{context}\n\n"
                    "請遵循以下規則回答：\n"
                    "1. 優先使用上述檢索到的資訊來回答\n"
                    "2. 簡短總結找到的相關內容\n"
                    "3. 如果檢索資訊中沒有相關內容，請說明「抱歉，在資料庫中未找到相關資訊」"
                    f"直接根據你的知識，回答關於「{user_message}」的相關資訊\n"
                    "4. 不要編造資訊，清楚區分哪些是來自資料庫，哪些是你的補充說明\n"
                    "5. 回答要簡潔但要包含重要細節\n"
                    "6. 如果有多個相關結果，請綜合整理後回答\n\n"
                    f"用戶問題：{user_message}\n"
                    "請根據以上資訊提供答案："
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