<template>
  <div class="recommendation-module">
    <h2>內容推薦系統</h2>
    
    <!-- 搜索表單組件 -->
    <search-form 
      :contentTypes="contentTypes"
      :genres="processedGenres"
      @search="handleSearch"
      :isLoading="isLoading"
    />
    
    <!-- 診斷按鈕 -->
    <div v-if="error" class="diagnostic-tools">
      <button class="btn-diagnostic" @click="diagnoseApiConnection">
        診斷連接問題
      </button>
    </div>
    
    <!-- 清除緩存按鈕 -->
    <div class="diagnostic-tools">
      <button class="btn-diagnostic" @click="clearAllCache">
        清除結果緩存
      </button>
    </div>
    
    <!-- 加載指示器 -->
    <div v-if="isLoading" class="loading-indicator">
      <span>{{ loadingStage === 'initial' ? '載入中...' : '搜索中...' }}</span>
    </div>
    
    <!-- 錯誤信息 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- 調試信息 -->
    <div v-if="debugInfo" class="debug-info">
      <strong>調試信息:</strong>
      <pre>{{ debugInfo }}</pre>
    </div>
    
    <!-- 搜索歷史 -->
    <div v-if="searchHistory.length > 0" class="search-history">
      <h3>
        搜索歷史
        <button class="clear-history-btn" @click="clearSearchHistory">清除</button>
      </h3>
      <ul class="history-list">
        <li v-for="(item, index) in searchHistory" :key="index" class="history-item">
          <button @click="repeatSearch(item)" :disabled="isLoading">
            <span class="history-query">{{ item.params.query }}</span>
            <small class="history-meta">
              {{ new Date(item.timestamp).toLocaleString() }}
            </small>
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import SearchForm from './SearchForm.vue';
import { getContentTypes, getGenres, testBackendConnection } from './recommendationService';

export default {
  name: 'RecommendationModule',
  components: {
    SearchForm
  },
  data() {
    return {
      // 基本數據
      contentTypes: [],       // 內容類型列表
      genres: [],             // 風格/類型列表
      
      // 搜索狀態
      currentSearchParams: null,  // 當前搜索參數
      searchHistory: [],          // 搜索歷史
      
      // UI 狀態
      isLoading: false,       // 加載狀態
      loadingStage: null,     // 加載階段（'initial', 'search'）
      error: null,            // 錯誤信息
      debugInfo: null,        // 調試信息
      
      // 結果緩存
      resultsCache: {},       // 搜索結果緩存
    };
  },
  computed: {
    // 處理 genres 數據，確保組件能接受各種格式
    processedGenres() {
      if (!this.genres) return [];
      
      // 如果已經是陣列，直接返回
      if (Array.isArray(this.genres)) return this.genres;
      
      // 如果是物件，保持物件格式
      if (typeof this.genres === 'object') return this.genres;
      
      // 其他情況返回空陣列
      return [];
    }
  },
  created() {
    // 加載保存的搜索歷史
    try {
      const savedHistory = localStorage.getItem('recommendationSearchHistory');
      if (savedHistory) {
        this.searchHistory = JSON.parse(savedHistory);
      }
    } catch (e) {
      console.warn('Failed to load search history from localStorage');
    }
    
    // 加載初始數據
    this.loadInitialData();
    
    // 設置緩存清理定時器
    setInterval(() => this.clearOldCache(), 10 * 60 * 1000); // 每10分鐘清理一次過期緩存
  },
  methods: {
    async loadInitialData() {
      try {
        // 獲取內容類型和風格列表
        this.setLoading(true, 'initial');
        const [contentTypesResponse, genresResponse] = await Promise.all([
          getContentTypes(),
          getGenres()
        ]);
        
        this.contentTypes = contentTypesResponse.data;
        this.genres = genresResponse.data;
        
        // 輸出調試信息
        console.log('已載入內容類型:', this.contentTypes);
        console.log('已載入類型/風格:', this.genres);
      } catch (error) {
        this.setError('加載初始數據失敗: ' + (error.message || '未知錯誤'));
        console.error('Failed to load initial data', error);
        
        // 如果初始加載失敗，自動運行診斷
        await this.diagnoseApiConnection();
      } finally {
        this.setLoading(false);
      }
    },
    
    // 新增：清除所有緩存
    clearAllCache() {
      this.resultsCache = {};
      this.debugInfo = "已清除結果緩存。下次搜索將從服務器獲取新數據。";
      console.log('已清除結果緩存');
      setTimeout(() => {
        this.debugInfo = null;
      }, 3000);
    },
    
    async handleSearch(searchParams, saveToHistory = true) {
      try {
        // 輸出搜索參數用於調試
        console.log('Recommendation request payload:', searchParams);
        
        // 轉換 Proxy 為普通對象
        const normalizedParams = {
          query: searchParams.query,
          contentTypes: Array.isArray(searchParams.contentTypes) ? 
            [...searchParams.contentTypes] : [],
          genres: Array.isArray(searchParams.genres) ? 
            [...searchParams.genres] : [],
          limit: parseInt(searchParams.limit) || 10,
          sortBy: searchParams.sortBy
        };
        
        console.log('正規化的參數:', normalizedParams);
        
        // 保存到搜索歷史
        if (saveToHistory) {
          this.saveSearchHistory(normalizedParams);
        }
        
        // 設置加載狀態
        this.setLoading(true, 'search');
        
        // 構建查詢字符串
        const queryParams = new URLSearchParams();
        queryParams.append('query', normalizedParams.query);
        
        if (normalizedParams.contentTypes.length > 0) {
          normalizedParams.contentTypes.forEach(type => {
            queryParams.append('contentType', type);
          });
        }
        
        if (normalizedParams.genres.length > 0) {
          normalizedParams.genres.forEach(genre => {
            queryParams.append('genre', genre);
          });
        }
        
        queryParams.append('limit', normalizedParams.limit.toString());
        
        if (normalizedParams.sortBy) {
          queryParams.append('sortBy', normalizedParams.sortBy);
        }
        
        // 跳轉到結果頁面
        const resultPageUrl = `/recommendations?${queryParams.toString()}`;
        console.log('跳轉到結果頁面:', resultPageUrl);
        
        // 使用 Vue Router 導航（如果存在）
        if (this.$router) {
          this.$router.push(resultPageUrl);
        } else {
          // 如果沒有 Vue Router，使用普通的頁面導航
          window.location.href = resultPageUrl;
        }
      } catch (error) {
        console.error('搜索跳轉失敗:', error);
        this.setError('搜索跳轉失敗: ' + (error.message || '未知錯誤'));
        this.setLoading(false);
      }
    },
    
    // 診斷 API 連接問題
    async diagnoseApiConnection() {
      try {
        this.setLoading(true, 'diagnosis');
        this.error = "正在診斷 API 連接問題...";
        
        const result = await testBackendConnection();
        
        if (result.success) {
          this.error = `API 連接測試成功! ${result.message}`;
        } else {
          this.error = `API 連接診斷: ${result.message} - ${result.error || '未知錯誤'}`;
        }
      } catch (error) {
        this.error = `診斷過程中出錯: ${error.message}`;
      } finally {
        this.setLoading(false);
      }
    },
    
    // 保存搜索歷史
    saveSearchHistory(searchParams) {
      // 檢查是否與最新的歷史記錄相同
      if (this.searchHistory.length > 0 && 
          JSON.stringify(this.searchHistory[0].params) === JSON.stringify(searchParams)) {
        return; // 避免重複記錄相同的搜索
      }
      
      // 限制歷史記錄數量
      if (this.searchHistory.length >= 10) {
        this.searchHistory.pop(); // 移除最舊的記錄
      }
      
      // 添加新記錄到頂部
      this.searchHistory.unshift({
        params: searchParams,
        timestamp: new Date().toISOString()
      });
      
      // 將歷史保存到 localStorage
      try {
        localStorage.setItem('recommendationSearchHistory', 
          JSON.stringify(this.searchHistory));
      } catch (e) {
        console.warn('Failed to save search history to localStorage');
      }
    },
    
    // 從歷史中重新執行搜索
    repeatSearch(historyItem) {
      this.handleSearch(historyItem.params, false); // 不再次添加到歷史記錄
    },
    
    // 清除搜索歷史
    clearSearchHistory() {
      this.searchHistory = [];
      try {
        localStorage.removeItem('recommendationSearchHistory');
      } catch (e) {
        console.warn('Failed to clear search history from localStorage');
      }
    },
    
    // 設置加載狀態
    setLoading(isLoading, stage = null) {
      this.isLoading = isLoading;
      if (stage) {
        this.loadingStage = stage;
      }
    },
    
    // 設置錯誤狀態
    setError(error) {
      this.error = error;
      this.isLoading = false;
    },
    
    // 清理過期緩存
    clearOldCache() {
      const now = Date.now();
      const cacheExpiry = 30 * 60 * 1000; // 30分鐘緩存過期時間
      
      Object.keys(this.resultsCache).forEach(key => {
        if (now - this.resultsCache[key].timestamp > cacheExpiry) {
          delete this.resultsCache[key];
        }
      });
    }
  }
};
</script>

<style scoped>
.recommendation-module {
  margin: 20px 0;
  padding: 15px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 24px;
}

.loading-indicator {
  text-align: center;
  margin: 20px 0;
  padding: 15px;
  font-style: italic;
  color: #666;
  background-color: #f2f2f2;
  border-radius: 6px;
}

.error-message {
  color: #d9534f;
  padding: 12px;
  margin: 15px 0;
  border-radius: 6px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.debug-info {
  padding: 12px;
  margin: 15px 0;
  border-radius: 6px;
  background-color: #e8f4fd;
  border: 1px solid #b8daff;
  color: #004085;
  font-family: monospace;
  white-space: pre-wrap;
}

.diagnostic-tools {
  text-align: center;
  margin: 10px 0;
}

.btn-diagnostic {
  background-color: #5bc0de;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin: 0 5px;
}

.btn-diagnostic:hover {
  background-color: #46b8da;
}

.search-history {
  margin: 20px 0;
  padding: 15px;
  border-radius: 6px;
  background-color: #f2f2f2;
}

.search-history h3 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0;
  font-size: 16px;
}

.clear-history-btn {
  background: none;
  border: none;
  color: #d9534f;
  cursor: pointer;
  font-size: 14px;
}

.clear-history-btn:hover {
  text-decoration: underline;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.history-item {
  margin-bottom: 8px;
}

.history-item button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.history-item button:hover {
  background-color: #f9f9f9;
}

.history-query {
  font-weight: bold;
}

.history-meta {
  color: #777;
}

@media (max-width: 768px) {
  .recommendation-module {
    padding: 10px;
  }
  
  h2 {
    font-size: 20px;
  }
  
  .history-item button {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .history-meta {
    margin-top: 5px;
    font-size: 12px;
  }
}
</style>