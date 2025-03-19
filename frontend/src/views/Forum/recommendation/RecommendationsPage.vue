<template>
  <div class="recommendations-page">
    <div class="page-header">
      <h1>電影推薦結果</h1>
      <div class="search-info">
        <span v-if="searchQuery">搜索關鍵詞: <strong>{{ searchQuery }}</strong></span>
      </div>
    </div>
    
    <!-- 返回按鈕 -->
    <div class="action-buttons">
      <button @click="goBack" class="btn-back">返回</button>
      <button @click="modifySearch" class="btn-modify">修改搜索</button>
    </div>
    
    <!-- 加載指示器 -->
    <div v-if="isLoading" class="loading-indicator">
      <span>搜索中...</span>
    </div>
    
    <!-- 錯誤信息 -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="retry" class="btn-retry">重試</button>
    </div>
    
    <!-- 推薦結果內容 -->
    <div v-if="!isLoading && !error" class="recommendation-results-container">
      <!-- 找到結果 -->
      <div v-if="movieRecommendations.length > 0">
        <!-- 主要推薦結果 -->
        <div class="main-result" v-if="movieRecommendations.length > 0">
          <h2 class="section-title">最佳電影推薦</h2>
          <div class="main-result-card" @click="navigateToDetail(movieRecommendations[0])">
            <div class="result-poster">
              <img :src="getPosterUrl(movieRecommendations[0])" :alt="movieRecommendations[0].title">
              <div class="content-type-badge type-movie">電影</div>
            </div>
            <div class="result-details">
              <h3 class="result-title">{{ movieRecommendations[0].title }}</h3>
              <div class="result-metadata">
                <span class="similarity" v-if="movieRecommendations[0].similarity_score">
                  相似度: {{ formatPercentage(movieRecommendations[0].similarity_score) }}
                </span>
                <span class="genres" v-if="getFormattedGenres(movieRecommendations[0])">
                  {{ getFormattedGenres(movieRecommendations[0]) }}
                </span>
              </div>
              <p class="result-description">{{ movieRecommendations[0].description }}</p>
              <div class="metadata-details">
                <div class="metadata-row" v-if="getMetadataField(movieRecommendations[0], 'director')">
                  <span class="label">導演:</span>
                  <span>{{ getMetadataField(movieRecommendations[0], 'director') }}</span>
                </div>
                <div class="metadata-row" v-if="getMetadataField(movieRecommendations[0], 'cast')">
                  <span class="label">主演:</span>
                  <span>{{ getMetadataField(movieRecommendations[0], 'cast') }}</span>
                </div>
                <div class="metadata-row" v-if="getMetadataField(movieRecommendations[0], 'release_date')">
                  <span class="label">發行日期:</span>
                  <span>{{ formatDate(getMetadataField(movieRecommendations[0], 'release_date')) }}</span>
                </div>
              </div>
              <button class="btn-view-details">查看詳情</button>
            </div>
          </div>
        </div>
        
        <!-- 其他相似推薦 -->
        <div class="other-results" v-if="movieRecommendations.length > 1">
          <h2 class="section-title">其他相似電影推薦</h2>
          <div class="results-grid">
            <div 
              v-for="(item, index) in movieRecommendations.slice(1)" 
              :key="item.id || index"
              class="result-card"
              @click="navigateToDetail(item)"
            >
              <div class="result-poster">
                <img :src="getPosterUrl(item)" :alt="item.title">
                <div class="content-type-badge type-movie">電影</div>
                <div v-if="item.similarity_score" class="similarity-badge">
                  {{ formatPercentage(item.similarity_score) }}
                </div>
              </div>
              <div class="result-info">
                <h3 class="result-title">{{ item.title }}</h3>
                <p class="result-genres" v-if="getFormattedGenres(item)">{{ getFormattedGenres(item) }}</p>
                <p class="result-description">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 沒有找到結果 -->
      <div v-else class="no-results">
        <div class="no-results-message">
          <h2>沒有找到相關電影推薦內容</h2>
          <p>嘗試使用不同的關鍵詞進行搜索。</p>
          <button @click="modifySearch" class="btn-new-search">新的搜索</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getRecommendations } from './recommendationService';

export default {
  name: 'RecommendationsPage',
  data() {
    return {
      searchQuery: '',
      recommendations: [],
      isLoading: true,
      error: null,
      
      defaultPosterUrls: {
        movie: '/images/default-movie-poster.jpg',
        default: '/images/default-poster.jpg'
      }
    };
  },
  computed: {
    // 只過濾出電影推薦，排除特定電影
    movieRecommendations() {
      return this.recommendations.filter(item => 
        this.getContentType(item) === 'movie' &&
        !this.isExcludedMovie(item.title)
      );
    }
  },
  created() {
    // 從 URL 參數獲取搜索條件
    this.parseSearchParams();
    
    // 執行搜索
    this.fetchRecommendations();
  },
  methods: {
    // 解析 URL 參數
    parseSearchParams() {
      const urlParams = new URLSearchParams(window.location.search);
      this.searchQuery = urlParams.get('query') || '';
    },
    
    // 獲取推薦結果
    async fetchRecommendations() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const params = {
          query: this.searchQuery,
          contentTypes: ['movie'], // 強制只搜索電影
          limit: 10
        };
        
        console.log('Fetching movie recommendations with params:', params);
        
        const response = await getRecommendations(params);
        console.log('API Response:', response);
        
        // 處理不同的響應格式
        if (response.data && response.data.recommendations) {
          this.recommendations = response.data.recommendations;
        } else if (Array.isArray(response.data)) {
          this.recommendations = response.data;
        } else if (response.data && response.data.results) {
          this.recommendations = response.data.results;
        } else {
          this.recommendations = [];
          console.warn('Unexpected API response format:', response.data);
        }
        
        console.log('Processed recommendations:', this.recommendations);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
        this.error = '獲取電影推薦失敗: ' + (error.message || '未知錯誤');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 導航到內容詳情頁
    navigateToDetail(item) {
      if (!item) return;
      
      const contentId = item.id;
      
      if (!contentId) {
        console.warn('無法導航: 缺少內容ID', item);
        return;
      }
      
      const detailUrl = `/movie/${contentId}`;
      
      console.log('導航到電影詳情頁:', detailUrl);
      
      // 使用 Vue Router 或直接導航
      if (this.$router) {
        this.$router.push(detailUrl);
      } else {
        window.location.href = detailUrl;
      }
    },
    
    // 返回上一頁
    goBack() {
      if (window.history.length > 1) {
        this.$router ? this.$router.back() : window.history.back();
      } else {
        this.$router ? this.$router.push('/') : (window.location.href = '/');
      }
    },
    
    // 修改搜索條件
    modifySearch() {
      // 可以返回到搜索頁面並保留當前參數
      this.$router ? 
        this.$router.push({ path: '/', query: { lastQuery: this.searchQuery } }) : 
        (window.location.href = `/?lastQuery=${encodeURIComponent(this.searchQuery)}`);
    },
    
    // 重試搜索
    retry() {
      this.fetchRecommendations();
    },
    
    // 獲取內容類型
    getContentType(item) {
      return item.type || item.contentType || 'movie'; // 默認返回 'movie'
    },
    
    // 檢查是否為要排除的電影
    isExcludedMovie(title) {
      if (!title) return false;
      
      const excludedMovies = [
        '英雄美人',
        '布偶大電影之最高通緝',
        '默殺獨家紀錄片'
      ];
      
      return excludedMovies.some(excludedTitle => 
        title.includes(excludedTitle)
      );
    },
    
    // 從 metadata 對象或直接從項目獲取字段值
    getMetadataField(item, fieldName) {
      // 首先檢查 metadata 對象
      if (item.metadata && item.metadata[fieldName] !== undefined) {
        return item.metadata[fieldName];
      }
      
      // 然後檢查項目本身
      if (item[fieldName] !== undefined) {
        return item[fieldName];
      }
      
      return null;
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          return dateString;
        }
        
        return date.toLocaleDateString('zh-TW', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch (e) {
        return dateString;
      }
    },
    
    // 格式化百分比
    formatPercentage(value) {
      if (typeof value !== 'number') return '0%';
      return Math.round(value * 100) + '%';
    },
    
    // 獲取格式化的類型/風格
    getFormattedGenres(item) {
      if (!item.genres) return '';
      
      if (Array.isArray(item.genres)) {
        return item.genres.slice(0, 3).join(', ');
      }
      
      if (typeof item.genres === 'string') {
        return item.genres;
      }
      
      return '';
    },
    
    // 獲取海報 URL
    getPosterUrl(item) {
      if (item.poster) return item.poster;
      return this.defaultPosterUrls.movie || this.defaultPosterUrls.default;
    },
    
    // 截斷文本
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    }
  }
};
</script>

<style scoped>
.recommendations-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  font-family: 'Noto Sans TC', Arial, sans-serif;
  background-color: #f8f9fa;
  color: #333;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.page-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e1e4e8;
  position: relative;
}

.page-header:after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100px;
  height: 2px;
  background-color: #e74c3c;
}

.page-header h1 {
  font-size: 32px;
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.search-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.search-info strong {
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.btn-back, .btn-modify {
  padding: 10px 20px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 15px;
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn-back {
  background-color: #f1f3f5;
  color: #495057;
}

.btn-back:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-modify {
  background-color: #e74c3c;
  color: white;
}

.btn-modify:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
}

.loading-indicator {
  text-align: center;
  padding: 30px;
  font-size: 18px;
  color: #666;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-retry {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

/* 主要推薦結果樣式 */
.section-title {
  font-size: 24px;
  margin: 40px 0 25px 0;
  color: #2c3e50;
  padding-bottom: 12px;
  border-bottom: 2px solid #e1e4e8;
  position: relative;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.section-title:after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 80px;
  height: 2px;
  background-color: #e74c3c;
}

.main-result-card {
  display: flex;
  background-color: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 40px;
  position: relative;
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.main-result-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(231, 76, 60, 0.15);
}

.main-result-card:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #e74c3c, #c0392b);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.main-result-card:hover:after {
  opacity: 1;
}

.result-poster {
  position: relative;
  width: 300px;
  height: 450px;
  flex-shrink: 0;
  overflow: hidden;
}

.result-poster:before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%);
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.main-result-card:hover .result-poster:before {
  opacity: 1;
}

.result-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.main-result-card:hover .result-poster img {
  transform: scale(1.05);
}

.content-type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: bold;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(4px);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(231, 76, 60, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(231, 76, 60, 0);
  }
}

.type-movie {
  background-color: rgba(231, 76, 60, 0.9);
}

.result-details {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.result-title {
  font-size: 24px;
  margin: 0 0 10px 0;
  color: #333;
}

.result-metadata {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
}

.similarity {
  color: #e74c3c;
  font-weight: bold;
}

.result-description {
  margin-bottom: 20px;
  font-size: 16px;
  line-height: 1.6;
  color: #555;
  flex-grow: 1;
}

.metadata-details {
  background-color: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.03);
  border: 1px solid #f1f3f5;
}

.metadata-row {
  margin-bottom: 8px;
  font-size: 14px;
}

.metadata-row .label {
  font-weight: bold;
  color: #666;
  display: inline-block;
  width: 80px;
}

.btn-view-details {
  align-self: flex-start;
  padding: 12px 24px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.2);
  z-index: 1;
}

.btn-view-details:before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.7s ease;
  z-index: -1;
}

.btn-view-details:hover {
  background-color: #c0392b;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(192, 57, 43, 0.3);
}

.btn-view-details:hover:before {
  left: 100%;
}

/* 其他推薦結果樣式 */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.result-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #f1f3f5;
  position: relative;
}

.result-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  border-color: rgba(231, 76, 60, 0.3);
}

.result-card:before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(231, 76, 60, 0.05) 0%, rgba(255, 255, 255, 0) 50%);
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.result-card:hover:before {
  opacity: 1;
}

.result-card .result-poster {
  height: 200px;
}

.similarity-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(231, 76, 60, 0.85);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 2;
  letter-spacing: 0.5px;
}

.result-info {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.result-info .result-title {
  font-size: 18px;
  margin-bottom: 5px;
}

.result-genres {
  color: #666;
  font-size: 13px;
  margin-bottom: 10px;
}

.result-info .result-description {
  font-size: 14px;
  margin-bottom: 0;
  flex-grow: 1;
  line-height: 1.6;
  color: #555;
  max-height: 200px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #e74c3c #f1f3f5;
}

.result-info .result-description::-webkit-scrollbar {
  width: 6px;
}

.result-info .result-description::-webkit-scrollbar-track {
  background: #f1f3f5;
  border-radius: 10px;
}

.result-info .result-description::-webkit-scrollbar-thumb {
  background-color: #e74c3c;
  border-radius: 10px;
}

/* 沒有結果樣式 */
.no-results {
  padding: 50px 0;
  text-align: center;
}

.no-results-message {
  max-width: 500px;
  margin: 0 auto;
  background-color: #f8f9fa;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-results-message h2 {
  font-size: 24px;
  margin-top: 0;
  margin-bottom: 15px;
  color: #555;
}

.no-results-message p {
  color: #777;
  margin-bottom: 20px;
}

.btn-new-search {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.btn-new-search:hover {
  background-color: #2980b9;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .main-result-card {
    flex-direction: column;
  }
  
  .result-poster {
    width: 100%;
    height: 250px;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .search-info {
    flex-direction: column;
    gap: 5px;
  }
}
</style>