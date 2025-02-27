import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import pickle
from django.conf import settings
from openai import OpenAI
import jieba
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
    animes_data = None
    movies_index = None
    games_index = None
    animes_index = None
    movie_ids = None
    game_ids = None
    anime_ids = None
    movie_bm25 = None
    game_bm25 = None
    anime_bm25 = None
    model = None
    client = None  # OpenAI 客戶端
    
    def __init__(self):
        super().__init__()
        
        # 如果是第一次初始化，才載入數據
        if ChatBotView.model is None:
            # 初始化模型
            self.model_name = 'BAAI/bge-m3'
            # self.model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
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
            MOVIES_EXCEL = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_movies.xlsx')
            GAMES_EXCEL = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_games.xlsx')
            ANIMES_EXCEL = os.path.join(settings.BASE_DIR, 'member_api/original_data/data_animations.xlsx')
            TOKENIZED_MOVIE_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_vector.index')
            GAMES_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/games_excel_vector.index')
            ANIMES_INDEX_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/animations_excel_vector.index')
            TOKENIZED_MOVIE_IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/tokenized_movies_ids.pkl')
            GAMES_IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/games_excel_ids.pkl')
            ANIMES_IDS_PATH = os.path.join(settings.BASE_DIR, 'member_api/vector_data/animations__excel_ids.pkl')

            print("開始載入 Excel 數據...")
            # 載入電影.遊戲數據
            ChatBotView.movies_data = pd.read_excel(MOVIES_EXCEL).dropna(subset=['movie_description']).reset_index(drop=True)
            ChatBotView.games_data = pd.read_excel(GAMES_EXCEL).dropna(subset=['game_description']).reset_index(drop=True)
            ChatBotView.animes_data = pd.read_excel(ANIMES_EXCEL).dropna(subset=['animation_description']).reset_index(drop=True)

            print("開始載入向量索引...")
            ChatBotView.movies_index = faiss.read_index(TOKENIZED_MOVIE_INDEX_PATH)
            ChatBotView.games_index = faiss.read_index(GAMES_INDEX_PATH)
            ChatBotView.animes_index = faiss.read_index(ANIMES_INDEX_PATH)

            print("開始載入 ID 映射...")
            with open(TOKENIZED_MOVIE_IDS_PATH, 'rb') as f:
                ChatBotView.movie_ids = pickle.load(f)
            with open(GAMES_IDS_PATH, 'rb') as f:
                ChatBotView.game_ids = pickle.load(f)
            with open(ANIMES_IDS_PATH, 'rb') as f:
                ChatBotView.anime_ids = pickle.load(f)

            print("開始載入 BM25 索引...")
            # 構建電影 BM25
            movie_corpus = [jieba.lcut(desc) for desc in ChatBotView.movies_data['movie_description'].astype(str).tolist()]
            ChatBotView.movie_bm25 = BM25Okapi(movie_corpus)

            # 構建遊戲 BM25
            game_corpus = [jieba.lcut(desc) for desc in ChatBotView.games_data['game_description'].astype(str).tolist()]
            ChatBotView.game_bm25 = BM25Okapi(game_corpus)

            # 構建動畫 BM25
            anime_corpus = [jieba.lcut(desc) for desc in ChatBotView.animes_data['animation_description'].astype(str).tolist()]
            ChatBotView.anime_bm25 = BM25Okapi(anime_corpus)

            print("所有數據和索引載入成功")
            
        except Exception as e:
            print(f"首次載入數據和索引時發生錯誤: {e}")
            raise

    def hybrid_search(self, query, use_retrieval=True, is_movie=True, is_game=False, is_anime=False, top_k=5):
        """混合搜索：FuzzyWuzzy + BM25 + FAISS"""
        try:
            if not use_retrieval:
                return ["檢索模型已關閉，將使用 AI 直接回答問題。"]
            
            # 根據類型選擇對應的數據和索引
            if is_anime:
                print("查詢動畫數據庫") 
                data = ChatBotView.animes_data
                index = ChatBotView.animes_index
                bm25 = ChatBotView.anime_bm25
                ids = ChatBotView.anime_ids
                title_field = 'animation_title'
                desc_field = 'animation_description'
                genre_field = 'animation_genre'
            elif is_game:
                print("查詢遊戲數據庫") 
                data = ChatBotView.games_data
                index = ChatBotView.games_index
                bm25 = ChatBotView.game_bm25
                ids = ChatBotView.game_ids
                title_field = 'game_title'
                desc_field = 'game_description'
                genre_field = 'game_genre'
            else:  # 默認為電影
                print("查詢電影數據庫") 
                data = ChatBotView.movies_data
                index = ChatBotView.movies_index
                bm25 = ChatBotView.movie_bm25
                ids = ChatBotView.movie_ids
                title_field = 'movie_title'
                desc_field = 'movie_description'
                genre_field = 'movie_genre'
            
            # 1. 使用結巴分詞處理查詢
            query_words = set(jieba.lcut(query))
            
            # 2. FuzzyWuzzy 進行標題匹配
            title_matches = self.fuzzy_title_search(query, is_movie=is_movie, is_game=is_game, is_anime=is_anime)
            
            # 3. BM25 + One-Hot 進行類型匹配
            type_matches = self.type_search(query_words, is_movie=is_movie, is_game=is_game, is_anime=is_anime)
            
            # 4. 合併結果並取 top-k
            merged_results = self.merge_search_results(title_matches, type_matches, top_k)
            
            # 5. 使用 FAISS 進行語義搜索
            final_results = self.semantic_search(merged_results, query, is_movie=is_movie, is_game=is_game, is_anime=is_anime)
            
            return self.format_results(final_results)
        except Exception as e:
            print(f"混合搜索時發生錯誤：{str(e)}")
            return []


    def fuzzy_title_search(self, query, is_movie=True, is_game=False, is_anime=False):
        """使用 FuzzyWuzzy 進行標題匹配"""
        try:
            # 根據類型選擇對應的數據
            if is_anime:
                data = ChatBotView.animes_data
                title_field = 'animation_title'
                desc_field = 'animation_description'
                genre_field = 'animation_genre'
            elif is_game:
                data = ChatBotView.games_data
                title_field = 'game_title'
                desc_field = 'game_description'
                genre_field = 'game_genre'
            else:  # 默認為電影
                data = ChatBotView.movies_data
                title_field = 'movie_title'
                desc_field = 'movie_description'
                genre_field = 'movie_genre'
            
            # 計算每個標題的匹配分數
            matches = []
            for idx, row in data.iterrows():
                title = str(row[title_field])
                score = fuzz.token_set_ratio(query, title)
                if score > 50:  # 設定閾值
                    matches.append({
                        'index': idx,
                        'title': title,
                        'score': score,
                        'description': row[desc_field],
                        'genre': row[genre_field]
                    })
            
            # 根據分數排序
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches
        except Exception as e:
            print(f"標題匹配時發生錯誤：{str(e)}")
            return []

    def type_search(self, query_words, is_movie=True, is_game=False, is_anime=False):
        """使用 BM25 + One-Hot Encoding 進行類型匹配"""
        try:
            # 根據類型選擇對應的數據
            if is_anime:
                data = ChatBotView.animes_data
                bm25 = ChatBotView.anime_bm25
                genre_field = 'animation_genre'
                title_field = 'animation_title'
                desc_field = 'animation_description'
            elif is_game:
                data = ChatBotView.games_data
                bm25 = ChatBotView.game_bm25
                genre_field = 'game_genre'
                title_field = 'game_title'
                desc_field = 'game_description'
            else:  # 默認為電影
                data = ChatBotView.movies_data
                bm25 = ChatBotView.movie_bm25
                genre_field = 'movie_genre'
                title_field = 'movie_title'
                desc_field = 'movie_description'
            
            # 將類型轉換為 One-Hot 編碼
            mlb = MultiLabelBinarizer()
            genres = [set(g.split('/')) for g in data[genre_field]]
            genre_matrix = mlb.fit_transform(genres)
            
            # 使用 BM25 進行描述匹配
            desc_scores = bm25.get_scores(query_words)
            
            # 計算類型相似度
            matches = []
            for idx, (genre_vec, desc_score) in enumerate(zip(genre_matrix, desc_scores)):
                score = desc_score * 0.7 + np.sum(genre_vec) * 0.3
                if score > 0:
                    matches.append({
                        'index': idx,
                        'title': data.iloc[idx][title_field],
                        'score': float(score),
                        'description': data.iloc[idx][desc_field],
                        'genre': data.iloc[idx][genre_field]
                    })
            
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches
        except Exception as e:
            print(f"類型匹配時發生錯誤：{str(e)}")
            return []

    def merge_search_results(self, title_matches, type_matches, top_k):
        """合併不同搜索結果"""
        try:
            merged = {}
            
            # 合併標題匹配結果
            for match in title_matches:
                merged[match['title']] = {
                    'index': match['index'],
                    'title': match['title'],
                    'description': match['description'],
                    'genre': match['genre'],
                    'title_score': match['score'],
                    'type_score': 0
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
                        'type_score': match['score']
                    }
            
            # 計算綜合分數
            results = []
            for data in merged.values():
                final_score = data['title_score'] * 0.6 + data['type_score'] * 0.4
                results.append({**data, 'final_score': final_score})
            
            # 根據綜合分數排序並返回 top-k
            results.sort(key=lambda x: x['final_score'], reverse=True)
            return results[:top_k]
        except Exception as e:
            print(f"合併結果時發生錯誤：{str(e)}")
            return []
        
    def semantic_search(self, candidates, query, is_movie=True, is_game=False, is_anime=False):
        """對候選結果進行語義搜索"""
        try:
            if not candidates:
                return []
                
            # 生成查詢向量
            query_vector = ChatBotView.model.encode([query], normalize_embeddings=True)
            
            # 獲取候選項的索引
            indices = [c['index'] for c in candidates]
            
            # 根據類型選擇對應的索引
            if is_anime:
                index = ChatBotView.animes_index
            elif is_game:
                index = ChatBotView.games_index
            else:  # 默認為電影
                index = ChatBotView.movies_index
            
            # 使用 FAISS 搜索
            distances, _ = index.search(query_vector.astype('float32'), len(indices))
            
            # 添加語義相似度分數
            results = []
            for candidate, semantic_score in zip(candidates, distances[0]):
                results.append({
                    **candidate,
                    'semantic_score': float(semantic_score),
                    'final_score': candidate['final_score'] * 0.7 + float(semantic_score) * 0.3
                })
            
            # 根據最終分數排序
            results.sort(key=lambda x: x['final_score'], reverse=True)
            return results
        except Exception as e:
            print(f"語義搜索時發生錯誤：{str(e)}")
            return candidates
        
    def format_results(self, results):
        """格式化搜索結果"""
        try:
            formatted = []
            for r in results:
                formatted.append(
                    f"標題：{r['title']}\n"
                    f"類型：{r['genre']}\n"
                    f"簡介：{r['description']}\n"
                    f"標題匹配分數：{r.get('title_score', 0):.2f}\n"
                    f"類型匹配分數：{r.get('type_score', 0):.2f}\n"
                    f"語義相似度：{r.get('semantic_score', 0):.2f}\n"
                    f"綜合評分：{r['final_score']:.2f}"
                )
            return formatted
        except Exception as e:
            print(f"格式化結果時發生錯誤：{str(e)}")
            return []

    def is_entertainment_related(self, question):
        """判斷是否為娛樂相關問題"""
        # 直接相關關鍵詞
        direct_keywords = {
            '電影', '遊戲', '動畫', '漫畫', '卡通',
            '劇情', '主角', '角色', '故事', '演員', '導演',
            '玩法', '關卡', '通關', '打怪', '副本', '題材',
            '動漫', '聲優', '漫畫家', '作者', '製作','作品',
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

    def stream_response(self, response):
        """生成流式響應"""
        try:
            buffer = ""
            for chunk in response:
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
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            original_message = data.get("message", "").strip()  # 保存原始訊息
            use_retrieval = data.get("use_retrieval", True)
            top_k = data.get("top_k", 5)

            if not session_id or not original_message:
                return Response({'error': '缺少必要參數'}, status=400)

            # 主題範圍過濾（使用原始訊息進行判斷）
            if not self.is_entertainment_related(original_message):
                return Response({
                    'message': '抱歉，我僅限於娛樂相關話題喔！您可以試著詢問關於電影、遊戲、動畫等相關內容。',
                    'type': 'entertainment_filter'
                }, status=200)

            # 預設所有類型為 False
            is_movie, is_game, is_anime = False, False, False
            message = original_message  # 用於後續處理的訊息

            # 1. 判斷查詢類型
            if message.startswith("[電影]"):
                is_movie = True
                message = message.replace("[電影]", "").strip()
            elif message.startswith("[遊戲]"):
                is_game = True
                message = message.replace("[遊戲]", "").strip()
            elif message.startswith("[動畫]"):
                is_anime = True
                message = message.replace("[動畫]", "").strip()
            else:
                # 若未指定類型，則預設查詢電影
                is_movie = True


            # 初始化或更新會話歷史
            if session_id not in self.sessions_history:
                self.sessions_history[session_id] = [
                    {"role": "system", "content": 
                     "你是一個專業且熟悉『電影、遊戲、動畫』的推薦和查找助理。"
                    "不包括政治、宗教、新聞、體育、股票、教育等主題。\n"
                    "對於無關問題請回覆：\n"
                    "『抱歉，我僅限於『電影、遊戲、動畫』相關話題喔！您可以嘗試在網路上搜尋相關資訊。』"}
                ]

            # 更新會話歷史
            self.sessions_history[session_id].append({"role": "user", "content": original_message})

            # 2. 準備上下文
            context = []
            if use_retrieval:
                # 只搜索指定的類型
                if is_movie:
                    results = self.hybrid_search(message, use_retrieval=True, is_movie=True, is_game=False, is_anime=False, top_k=top_k)
                    if results:
                        context.append("\n=== 相關電影資訊 ===")
                        context.extend(results)
                elif is_game:
                    results = self.hybrid_search(message, use_retrieval=True, is_movie=False, is_game=True, is_anime=False, top_k=top_k)
                    if results:
                        context.append("\n=== 相關遊戲資訊 ===")
                        context.extend(results)
                elif is_anime:
                    results = self.hybrid_search(message, use_retrieval=True, is_movie=False, is_game=False, is_anime=True, top_k=top_k)
                    if results:
                        context.append("\n=== 相關動畫資訊 ===")
                        context.extend(results)

                context = "\n\n".join(context) if context else "未找到相關資料。"
            
            # 3. 構建 prompt
            category_display = {
                "movie": "電影",
                "game": "遊戲",
                "anime": "動畫"
            }

            # 確定當前查詢類別
            category = "movie" if is_movie else "game" if is_game else "anime"

            system_prompt = (
                "你是一個專業且熟悉電影、遊戲、動畫的推薦和查找助理。\n"
                "請根據用戶的查詢內容，提供準確且有幫助的回答。\n\n"
                f"### 用戶查詢類別：{category_display[category]}\n"
                f"### 用戶問題：{message}\n\n"
                "### 檢索到的相關資訊：\n"
                f"{context}\n\n"
                "### 請遵循以下規則回答：\n"
                "1. 嚴格遵守用戶選擇的類別範圍\n"
                "2. 優先使用上述檢索到的資訊來回答\n"
                "3. 如果檢索資訊中沒有相關內容：\n"
                "   - 明確說明「在資料庫中未找到相關資訊」\n"
                "   - 再根據知識庫提供相關資訊\n"
                "4. 清楚區分資料庫資訊和知識庫補充\n"
                "5. 回答要簡潔但包含重要細節\n"
                f"用戶問題：{message}\n"
                "請根據以上準則提供答案："
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