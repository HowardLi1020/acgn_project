<template>
  <div class="recommendation-item" :class="{ 'main-item': isMain }">
    <div class="item-poster" @click="navigateToDetail">
      <img :src="posterUrl" :alt="item.title" class="poster-image">
      <div class="content-type-badge" :class="`type-${contentType}`">
        {{ getContentTypeLabel(contentType) }}
      </div>
    </div>
    
    <div class="item-info">
      <h3 class="item-title" @click="navigateToDetail">{{ item.title }}</h3>
      
      <div class="item-meta">
        <span class="similarity-score" v-if="item.similarity_score">
          相似度: {{ formatScore(item.similarity_score) }}
        </span>
        <span class="genres" v-if="formattedGenres">
          {{ formattedGenres }}
        </span>
      </div>
      
      <p class="item-description">{{ shortenedDescription }}</p>
      
      <div class="item-actions">
        <button class="btn-details" @click="showDetails">查看詳情</button>
        <button class="btn-goto" @click="navigateToDetail">前往頁面</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecommendationItem',
  props: {
    item: {
      type: Object,
      required: true
    },
    isMain: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    // 獲取內容類型
    contentType() {
      return this.item.type || this.item.contentType || 'unknown';
    },
    
    // 獲取格式化的類型/風格列表
    formattedGenres() {
      const genres = this.item.genres;
      
      if (!genres) return '';
      
      if (Array.isArray(genres)) {
        return genres.slice(0, 3).join(', ');
      }
      
      if (typeof genres === 'string') {
        return genres;
      }
      
      return '';
    },
    
    // 獲取縮短的描述
    shortenedDescription() {
      const desc = this.item.description || '';
      const maxLength = this.isMain ? 200 : 100;
      
      if (desc.length <= maxLength) {
        return desc;
      }
      
      return desc.substring(0, maxLength) + '...';
    },
    
    // 獲取海報 URL
    posterUrl() {
      // 如果有海報，則使用它
      if (this.item.poster) {
        return this.item.poster;
      }
      
      // 否則根據內容類型使用預設海報
      const defaultPosters = {
        movie: '/images/default-movie-poster.jpg',
        animation: '/images/default-animation-poster.jpg',
        game: '/images/default-game-poster.jpg'
      };
      
      return defaultPosters[this.contentType] || '/images/default-poster.jpg';
    }
  },
  methods: {
    // 顯示詳情
    showDetails() {
      this.$emit('show-details', this.item);
    },
    
    // 跳轉到詳情頁
    navigateToDetail() {
      this.$emit('navigate-to-detail', this.item);
    },
    
    // 格式化相似度分數
    formatScore(score) {
      return (score * 100).toFixed(0) + '%';
    },
    
    // 獲取內容類型標籤
    getContentTypeLabel(type) {
      if (!type) return '未知';
      
      const labels = {
        movie: '電影',
        animation: '動畫',
        game: '遊戲'
      };
      
      return labels[type] || type;
    }
  }
};
</script>

<style scoped>
.recommendation-item {
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
}

.recommendation-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

/* 主要項目（最高相似度）的樣式 */
.main-item {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: row;
  height: auto;
}

.main-item .item-poster {
  width: 250px;
  height: 320px;
  flex-shrink: 0;
}

.main-item .item-info {
  flex-grow: 1;
  padding: 20px;
}

.item-poster {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  cursor: pointer;
}

.poster-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.item-poster:hover .poster-image {
  transform: scale(1.05);
}

.content-type-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.type-movie {
  background-color: #e74c3c;
}

.type-animation {
  background-color: #3498db;
}

.type-game {
  background-color: #2ecc71;
}

.item-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: 15px;
}

.item-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  cursor: pointer;
}

.item-title:hover {
  color: #3498db;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 12px;
  color: #777;
}

.similarity-score {
  color: #e74c3c;
  font-weight: bold;
}

.item-description {
  flex-grow: 1;
  margin-bottom: 15px;
  font-size: 14px;
  line-height: 1.5;
  color: #555;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.btn-details, .btn-goto {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-details {
  background-color: #f0f0f0;
  color: #333;
}

.btn-details:hover {
  background-color: #e0e0e0;
}

.btn-goto {
  background-color: #3498db;
  color: white;
}

.btn-goto:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .main-item {
    flex-direction: column;
  }
  
  .main-item .item-poster {
    width: 100%;
    height: 250px;
  }
  
  .main-item .item-info {
    padding: 15px;
  }
}
</style>