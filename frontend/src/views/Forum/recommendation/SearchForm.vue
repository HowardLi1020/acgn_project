<template>
  <div class="search-form">
    <form @submit.prevent="handleSubmit">
      <!-- 主要搜索輸入框 -->
      <div class="form-group search-input-group">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="輸入關鍵詞查找電影、動畫或遊戲..."
          class="search-input"
          :disabled="isLoading"
        />
        <button type="submit" class="search-button" :disabled="isLoading">
          <span v-if="!isLoading">搜索</span>
          <span v-else>搜索中...</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'SearchForm',
  props: {
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      searchQuery: ''
    };
  },
  methods: {
    handleSubmit() {
      // 構建搜索參數對象
      const searchParams = {
        query: this.searchQuery
      };

      // 發送搜索事件到父組件
      this.$emit('search', searchParams);
    }
  }
};
</script>

<style scoped>
.search-form {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f5f5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

.search-input-group {
  display: flex;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 16px;
}

.search-button {
  padding: 10px 20px;
  background-color: #4a6fdc;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.search-button:hover {
  background-color: #3a5fc9;
}

.search-button:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
  }
  
  .search-input {
    border-radius: 4px;
    margin-bottom: 10px;
  }
  
  .search-button {
    border-radius: 4px;
    width: 100%;
  }
}
</style>