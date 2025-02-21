<template>
  <div class="discussion-board">
    <!-- 討論區標題 -->
    <h2 class="board-title">📢 討論區</h2>

    <!-- 分類選擇器 -->
    <div class="category-filter">
      <button 
        v-for="category in categories" 
        :key="category.id"
        :class="['category-button', { active: categoryFilter === category.id }]"
        @click="categoryFilter = category.id; handleCategoryChange()"
      >
        {{ getCategoryIcon(category.id) }} {{ category.name }}
      </button>
    </div>

    <!-- 發表新文章按鈕 -->
    <div class="action-bar">
      <button class="create-button" @click="goToCreatePost">➕ 發表新文章</button>
    </div>

    <!-- 搜尋和篩選功能 -->
    <div class="filter-bar">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜尋文章..." 
          @input="handleSearch"
        />
        <button class="search-button">🔍</button>
      </div>
      <div class="sort-options">
        <select v-model="sortOption" @change="handleSort">
          <option value="newest">最新發布</option>
          <option value="popular">最多點讚</option>
          <option value="mostReplies">最多回覆</option>
        </select>
      </div>
    </div>

    <!-- 文章列表 -->
    <div v-if="isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>載入中...</p>
    </div>
    
    <div v-else-if="paginatedPosts.length === 0" class="no-posts">
      <p>{{ getEmptyMessage() }}</p>
      <button class="create-button" @click="goToCreatePost">立即發表第一篇文章</button>
    </div>
    
    <transition-group name="post-fade" tag="ul" class="post-list" v-else>
      <li v-for="post in paginatedPosts" :key="post.post_id" class="post-card">
        <div class="post-header">
          <div>
            <h3 class="post-title">{{ post.title }}</h3>
            <div class="post-meta">
              <span class="post-date">📅 {{ formatDate(post.created_at) }}</span>
              <span class="post-category">{{ getCategoryIcon(post.category_id) }} {{ getCategoryName(post.category_id) }}</span>
            </div>
          </div>
          <div class="author-info">
            <img :src="post.author_avatar || '/default-avatar.png'" alt="作者頭像" class="author-avatar" />
            <span class="author">✍️ {{ post.author_name || '用戶 #' + post.author_id }}</span>
          </div>
        </div>
        
        <p class="post-body">{{ truncateText(post.body, 200) }}</p>
        
        <div class="post-tags" v-if="post.tags && post.tags.length">
          <span class="tag" v-for="tag in post.tags" :key="tag">{{ tag }}</span>
        </div>
        
        <div class="post-footer">
          <div class="post-stats">
            <span class="stat-item">💬 {{ post.reply_count || 0 }}</span>
            <span class="stat-item">👁️ {{ post.view_count || 0 }}</span>
            <span class="stat-item" :class="{ 'liked': userLikedPosts.includes(post.post_id) }">
              👍 {{ post.like_count || 0 }}
            </span>
          </div>
          <div class="post-actions">
            <button 
              class="action-button like-button" 
              :class="{ 'liked': userLikedPosts.includes(post.post_id) }"
              @click="likePost(post.post_id)"
              :disabled="isLiking"
            >
              {{ userLikedPosts.includes(post.post_id) ? '❤️ 已點讚' : '👍 點讚' }}
            </button>
            <button class="action-button" @click="viewPost(post.post_id)">
              查看全文
            </button>
          </div>
        </div>
      </li>
    </transition-group>

    <!-- 分頁 -->
    <div class="pagination" v-if="totalPages > 1">
      <button @click="goToPage(1)" :disabled="currentPage === 1" class="page-button first-page">
        « 第一頁
      </button>
      <button @click="prevPage" :disabled="currentPage === 1" class="page-button">
        ⬅️ 上一頁
      </button>
      
      <div class="page-numbers">
        <button 
          v-for="page in displayedPageNumbers" 
          :key="page" 
          @click="goToPage(page)"
          :class="['page-number', { active: currentPage === page }]"
        >
          {{ page }}
        </button>
      </div>
      
      <button @click="nextPage" :disabled="currentPage >= totalPages" class="page-button">
        下一頁 ➡️
      </button>
      <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages" class="page-button last-page">
        最後一頁 »
      </button>
    </div>
    
    <div class="page-size-selector">
      每頁顯示
      <select v-model="perPage" @change="handlePerPageChange">
        <option :value="5">5</option>
        <option :value="10">10</option>
        <option :value="20">20</option>
        <option :value="50">50</option>
      </select>
      篇文章
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";

// 自定義防抖函數
const createDebounce = (fn, delay) => {
  let timer = null;
  return function(...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
};

export default {
  setup() {
    const router = useRouter();
    const route = useRoute();
    const posts = ref([]);
    const filteredPosts = ref([]);
    const currentPage = ref(1);
    const perPage = ref(10);
    const userId = ref(1); // 模擬目前登入的用戶 ID
    const isLoading = ref(true);
    const isLiking = ref(false);
    const searchQuery = ref("");
    const sortOption = ref("newest");
    const userLikedPosts = ref([]);
    const categoryFilter = ref(route.params.category || 'all');
    
    // 分類選項
    const categories = ref([
      { id: 'all', name: '全部' },
      { id: 'game', name: '遊戲' },
      { id: 'anime', name: '動畫' },
      { id: 'movie', name: '電影' }
    ]);
    
    // 獲取分類名稱
    const getCategoryName = (categoryId) => {
      const category = categories.value.find(cat => cat.id === categoryId);
      return category ? category.name : '未分類';
    };
    
    // 獲取分類圖標
    const getCategoryIcon = (categoryId) => {
      switch (categoryId) {
        case 'movie': return '🎬';
        case 'game': return '🎮';
        case 'anime': return '📺';
        default: return '📋';
      }
    };
    
    // 計算總頁數
    const totalPages = computed(() => 
      Math.ceil(filteredPosts.value.length / perPage.value)
    );
    
    // 計算目前頁面應顯示的文章
    const paginatedPosts = computed(() => {
      const start = (currentPage.value - 1) * perPage.value;
      return filteredPosts.value.slice(start, start + perPage.value);
    });
    
    // 獲取空列表提示訊息
    const getEmptyMessage = () => {
      if (searchQuery.value.trim()) {
        return '找不到符合搜尋條件的文章';
      } else if (categoryFilter.value !== 'all') {
        return `${getCategoryName(categoryFilter.value)}分類下暫無文章`;
      } else {
        return '目前沒有文章';
      }
    };
    
    // 計算要顯示哪些頁碼
    const displayedPageNumbers = computed(() => {
      const total = totalPages.value;
      const current = currentPage.value;
      
      let result = [];
      
      if (total <= 7) {
        // 總頁數較少，全部顯示
        result = Array.from({ length: total }, (_, i) => i + 1);
      } else {
        // 總頁數較多，採用智能顯示
        if (current <= 4) {
          // 在前面頁數
          result = [1, 2, 3, 4, 5, '...', total];
        } else if (current >= total - 3) {
          // 在後面頁數
          result = [1, '...', total - 4, total - 3, total - 2, total - 1, total];
        } else {
          // 在中間頁數
          result = [
            1, '...', 
            current - 1, current, current + 1,
            '...', total
          ];
        }
      }
      
      return result;
    });
    
    // 獲取文章列表
    const fetchPosts = async () => {
      isLoading.value = true;
      try {
        // 構建API URL，根據分類過濾
        let apiUrl = "http://127.0.0.1:8000/api/posts/";
        if (categoryFilter.value !== 'all') {
          apiUrl += `?category=${categoryFilter.value}`;
        }
        
        try {
          const response = await axios.get(apiUrl);
          posts.value = response.data.map(post => ({
            ...post,
            reply_count: post.reply_count || 0,
            like_count: post.like_count || 0,
            view_count: post.view_count || 0,
            created_at: post.created_at || new Date().toISOString()
          }));
        } catch (apiError) {
          console.warn('API調用失敗，使用模擬數據', apiError);
          // 創建模擬數據
          posts.value = generateMockPosts();
        }
        
        // 獲取用戶已點讚的文章
        await fetchUserLikes();
        
        // 應用排序和過濾
        applyFiltersAndSort();
      } catch (error) {
        console.error("無法獲取文章:", error);
        posts.value = [];
        filteredPosts.value = [];
      } finally {
        isLoading.value = false;
      }
    };
    
    // 生成模擬文章數據
    const generateMockPosts = () => {
      // 生成10篇模擬文章
      const mockPosts = [];
      const categories = ['game', 'anime', 'movie'];
      const titles = {
        game: ['最新遊戲體驗', '遊戲角色分析', '新作評測：黑神話悟空', '2025年值得期待的RPG', '多人在線遊戲推薦'],
        anime: ['冬季新番推薦', '經典動畫回顧', '動畫角色設計賞析', '熱門續作前瞻', '國產動畫發展趨勢'],
        movie: ['年度最佳影片盤點', '電影音效製作解析', '導演作品風格對比', '特效技術突破', '經典電影重映評價']
      };
      
      for (let i = 1; i <= 15; i++) {
        // 如果有分類篩選，只生成該分類的文章
        let category = categoryFilter.value;
        if (category === 'all') {
          category = categories[Math.floor(Math.random() * categories.length)];
        } else if (!categories.includes(category)) {
          // 如果篩選的分類不在預設範圍內，使用默認
          category = 'game';
        }
        
        const titleList = titles[category];
        const title = titleList[Math.floor(Math.random() * titleList.length)] + ' #' + i;
        
        // 生成發布時間，隨機在過去30天內
        const date = new Date();
        date.setDate(date.getDate() - Math.floor(Math.random() * 30));
        
        mockPosts.push({
          post_id: i,
          title: title,
          body: `這是一篇關於${getCategoryName(category)}的模擬文章內容，用於展示討論區功能。這篇文章討論了相關的主題和發展趨勢，希望能引起讀者的共鳴和思考。\n\n包含了一些分析和見解，同時也有個人的觀點和建議。`,
          author_id: Math.floor(Math.random() * 10) + 1,
          author_name: `用戶${Math.floor(Math.random() * 1000)}`,
          author_avatar: '/default-avatar.png',
          category_id: category,
          created_at: date.toISOString(),
          tags: [`${category}`, '討論', '分享'],
          reply_count: Math.floor(Math.random() * 20),
          like_count: Math.floor(Math.random() * 50),
          view_count: Math.floor(Math.random() * 200) + 50
        });
      }
      
      return mockPosts;
    };
    
    // 獲取用戶已點讚的文章
    const fetchUserLikes = async () => {
      try {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/users/${userId.value}/likes/`);
          userLikedPosts.value = response.data.map(like => like.post_id);
        } catch (apiError) {
          console.warn('獲取點讚記錄API調用失敗，使用空數組', apiError);
          // 隨機模擬一些已點讚的文章
          userLikedPosts.value = posts.value
            .filter(() => Math.random() > 0.7)
            .map(post => post.post_id);
        }
      } catch (error) {
        console.error("無法獲取用戶點讚記錄:", error);
        userLikedPosts.value = [];
      }
    };
    
    // 點讚文章
    const likePost = async (postId) => {
      if (isLiking.value) return;
      
      isLiking.value = true;
      try {
        // 檢查是否已點讚
        if (userLikedPosts.value.includes(postId)) {
          // 嘗試取消點讚
          try {
            await axios.delete(`http://127.0.0.1:8000/api/posts/${postId}/like/`, {
              data: { user_id: userId.value }
            });
          } catch (apiError) {
            console.warn('取消點讚API調用失敗，僅前端模擬', apiError);
          }
          
          userLikedPosts.value = userLikedPosts.value.filter(id => id !== postId);
        } else {
          // 嘗試點讚
          try {
            await axios.post(`http://127.0.0.1:8000/api/posts/${postId}/like/`, {
              user_id: userId.value
            });
          } catch (apiError) {
            console.warn('點讚API調用失敗，僅前端模擬', apiError);
          }
          
          userLikedPosts.value.push(postId);
        }
        
        // 更新點讚數量
        const postIndex = posts.value.findIndex(p => p.post_id === postId);
        if (postIndex !== -1) {
          if (userLikedPosts.value.includes(postId)) {
            posts.value[postIndex].like_count++;
          } else {
            posts.value[postIndex].like_count = Math.max(0, posts.value[postIndex].like_count - 1);
          }
          
          // 重新應用排序和過濾
          applyFiltersAndSort();
        }
      } catch (error) {
        console.error("點讚操作失敗:", error);
      } finally {
        isLiking.value = false;
      }
    };
    
    // 應用過濾和排序
    const applyFiltersAndSort = () => {
      // 先過濾
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase();
        filteredPosts.value = posts.value.filter(post => 
          post.title.toLowerCase().includes(query) || 
          post.body.toLowerCase().includes(query) ||
          (post.tags && post.tags.some(tag => tag.toLowerCase().includes(query)))
        );
      } else {
        filteredPosts.value = [...posts.value];
      }
      
      // 再排序
      switch (sortOption.value) {
        case "newest":
          filteredPosts.value.sort((a, b) => 
            new Date(b.created_at) - new Date(a.created_at)
          );
          break;
        case "popular":
          filteredPosts.value.sort((a, b) => b.like_count - a.like_count);
          break;
        case "mostReplies":
          filteredPosts.value.sort((a, b) => b.reply_count - a.reply_count);
          break;
      }
      
      // 重置頁碼（如果當前頁碼超出範圍）
      if (currentPage.value > totalPages.value && totalPages.value > 0) {
        currentPage.value = 1;
      }
    };
    
    // 處理分類變更
    const handleCategoryChange = () => {
      // 更新URL，不重新加載頁面
      if (categoryFilter.value === 'all') {
        router.push('/Forum/discussion');
      } else {
        router.push(`/Forum/discussion/${categoryFilter.value}`);
      }
      
      // 重新獲取文章
      fetchPosts();
    };
    
    // 防抖處理搜索
    const handleSearch = createDebounce(() => {
      applyFiltersAndSort();
    }, 300);
    
    // 處理排序變更
    const handleSort = () => {
      applyFiltersAndSort();
    };
    
    // 處理每頁顯示數量變更
    const handlePerPageChange = () => {
      // 調整當前頁碼以保持大致相同的內容位置
      const firstItemIndex = (currentPage.value - 1) * perPage.value;
      currentPage.value = Math.floor(firstItemIndex / perPage.value) + 1;
      
      // 確保頁碼在有效範圍內
      if (currentPage.value < 1) currentPage.value = 1;
      if (currentPage.value > totalPages.value) currentPage.value = totalPages.value;
    };
    
    // 導航方法
    const goToCreatePost = () => {
      // 創建文章時帶上當前分類
      if (categoryFilter.value !== 'all') {
        router.push(`/create?category=${categoryFilter.value}`);
      } else {
        router.push("/create");
      }
    };
    
    const viewPost = (postId) => {
      router.push(`/post/${postId}`);
    };
    
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };
    
    const goToPage = (page) => {
      if (typeof page === 'number' && page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
      }
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return "未知時間";
      
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);
      
      if (diffSec < 60) return "剛剛";
      if (diffMin < 60) return `${diffMin}分鐘前`;
      if (diffHour < 24) return `${diffHour}小時前`;
      if (diffDay < 7) return `${diffDay}天前`;
      
      return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    };
    
    // 截斷文本
    const truncateText = (text, maxLength) => {
      if (!text) return "";
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + "...";
    };
    
    // 監聽排序選項變更
    watch(sortOption, () => {
      applyFiltersAndSort();
    });
    
    // 監聽路由變化，更新分類過濾器
    watch(
      () => route.params.category,
      (newCategory) => {
        categoryFilter.value = newCategory || 'all';
        fetchPosts();
      }
    );
    
    onMounted(() => {
      fetchPosts();
    });
    
    return {
      posts,
      filteredPosts,
      currentPage,
      perPage,
      totalPages,
      paginatedPosts,
      displayedPageNumbers,
      isLoading,
      isLiking,
      searchQuery,
      sortOption,
      userLikedPosts,
      categoryFilter,
      categories,
      getCategoryName,
      getCategoryIcon,
      getEmptyMessage,
      fetchPosts,
      likePost,
      handleSearch,
      handleSort,
      handleCategoryChange,
      handlePerPageChange,
      goToCreatePost,
      viewPost,
      prevPage,
      nextPage,
      goToPage,
      formatDate,
      truncateText
    };
  }
};
</script>

<style scoped>
/* 基本樣式 */
.discussion-board {
  width: 100%;
  max-width: 1600px; /* 增加最大寬度，與主頁保持一致 */
  margin: 80px auto 0; /* 添加頂部邊距，避免被導航欄遮擋 */
  padding: 20px;
  background: #f8f9fa;
  min-height: calc(100vh - 80px); /* 調整最小高度 */
  display: flex;
  flex-direction: column;
}

/* 討論區標題 */
.board-title {
  font-size: 28px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 700;
}

/* 分類選擇器 */
.category-filter {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 25px;
}

.category-button {
  padding: 10px 15px;
  background-color: #f0f2f5;
  color: #444;
  border: none;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.category-button:hover {
  background-color: #e4e6e8;
}

.category-button.active {
  background-color: #007bff;
  color: white;
}

/* 操作欄 */
.action-bar {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

/* 搜尋和篩選欄 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  width: 100%;
  flex-wrap: wrap;
  gap: 10px;
}

.search-box {
  flex: 1;
  display: flex;
  max-width: 500px;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 5px 0 0 5px;
  font-size: 16px;
}

.search-button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 0 5px 5px 0;
  cursor: pointer;
}

.sort-options select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  background-color: white;
  cursor: pointer;
}

/* 載入中動畫 */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  width: 100%;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #007bff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 無文章顯示 */
.no-posts {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  text-align: center;
}

.no-posts p {
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}

/* 文章列表動畫 */
.post-fade-enter-active,
.post-fade-leave-active {
  transition: all 0.3s ease;
}

.post-fade-enter-from,
.post-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 文章列表 - 垂直排列 */
.post-list {
  width: 100%;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 900px; /* 控制最大寬度，保持良好的閱讀體驗 */
  margin: 0 auto;
}

/* 文章卡片 */
.post-card {
  width: 100%;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

/* 文章標頭 */
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.post-title {
  font-size: 22px;
  color: #333;
  margin: 0 0 10px 0;
  word-break: break-word;
}

.post-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #777;
  flex-wrap: wrap;
}

.post-date {
  display: inline-flex;
  align-items: center;
}

.post-category {
  display: inline-flex;
  align-items: center;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.author {
  font-size: 14px;
  color: #555;
}

/* 文章內容 */
.post-body {
  font-size: 16px;
  line-height: 1.7;
  color: #444;
  margin-bottom: 15px;
  word-break: break-word;
}

/* 文章標籤 */
.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.tag {
  padding: 4px 10px;
  background-color: #e9f5ff;
  color: #0077cc;
  border-radius: 30px;
  font-size: 14px;
}

/* 文章統計和操作 */
.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.post-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  font-size: 15px;
  color: #666;
}

.stat-item.liked {
  color: #e53935;
  font-weight: 500;
}

.post-actions {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 8px 15px;
  background-color: #f0f2f5;
  color: #444;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-button:hover {
  background-color: #e4e6e8;
}

.like-button {
  background-color: #f0f2f5;
  color: #444;
}

.like-button:hover {
  background-color: #ffebee;
  color: #e53935;
}

.like-button.liked {
  background-color: #ffebee;
  color: #e53935;
}

/* 分頁控制 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  flex-wrap: wrap;
  gap: 8px;
}

.page-button {
  padding: 8px 15px;
  background-color: #f0f2f5;
  color: #444;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.page-button:hover:not(:disabled) {
  background-color: #e4e6e8;
}

.page-button:disabled {
  background-color: #f0f2f5;
  color: #bbb;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.page-number {
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 5px;
  background-color: #f0f2f5;
  color: #444;
  cursor: pointer;
}

.page-number.active {
  background-color: #007bff;
  color: white;
}

.page-number:hover:not(.active) {
  background-color: #e4e6e8;
}

/* 每頁顯示選擇器 */
.page-size-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.page-size-selector select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: white;
  cursor: pointer;
}

/* 創建按鈕 */
.create-button {
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.create-button:hover {
  background-color: #218838;
}

/* RWD - 響應式設計 */
@media (max-width: 768px) {
  .discussion-board {
    padding: 15px;
    margin-top: 60px; /* 在小屏幕上減小頂部邊距 */
  }
  
  .post-header {
    flex-direction: column;
  }
  
  .author-info {
    margin-top: 10px;
  }
  
  .post-footer {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .post-stats {
    width: 100%;
    justify-content: space-between;
    margin-bottom: 10px;
  }
  
  .post-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-bar {
    flex-direction: column;
  }
  
  .search-box {
    max-width: 100%;
    margin-bottom: 10px;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
  
  .first-page,
  .last-page {
    display: none;
  }
  
  .category-filter {
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: 5px;
  }
  
  .category-button {
    white-space: nowrap;
  }
}
</style>