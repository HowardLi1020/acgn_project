<template>
    <div class="discussion-section">
      <!-- 標題和操作欄 -->
      <div class="section-header">
        <h3 class="section-subtitle">
          {{ getCategoryIcon(category) }} {{ getCategoryTitle() }}
        </h3>
        <div class="header-actions">
          <div class="search-mini">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜尋文章..." 
              @input="handleSearch"
            />
            <button class="search-button">🔍</button>
          </div>
          <button class="create-button" @click="goToCreatePost">發表文章</button>
        </div>
      </div>
  
      <!-- 文章列表 -->
      <div v-if="isLoading" class="loading-wrapper">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>
      
      <div v-else-if="displayedPosts.length === 0" class="empty-state">
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-button" @click="goToCreatePost">立即發表第一篇文章</button>
      </div>
      
      <transition-group name="post-fade" tag="ul" class="post-grid" v-else>
        <li 
          v-for="post in displayedPosts" 
          :key="post.post_id" 
          class="post-card" 
          @click="viewPost(post.post_id)"
        >
          <div class="post-header">
            <div class="post-meta">
              <h4 class="post-title">{{ truncateText(post.title, 60) }}</h4>
              <div class="post-info">
                <span class="post-date">📅 {{ formatDate(post.created_at) }}</span>
                <div class="author-info">
                  <img :src="post.author_avatar || '/default-avatar.png'" alt="作者頭像" class="author-avatar" />
                  <span class="author">{{ post.author_name || '用戶 #' + post.author_id }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="post-tags" v-if="post.tags && post.tags.length">
            <span class="tag" v-for="tag in post.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
            <span v-if="post.tags.length > 3" class="more-tags">+{{ post.tags.length - 3 }}</span>
          </div>
          
          <div class="post-footer">
            <div class="post-stats">
              <span class="stat-item">💬 {{ post.reply_count || 0 }}</span>
              <span class="stat-item">👁️ {{ post.view_count || 0 }}</span>
              <span class="stat-item" :class="{ 'liked': userLikedPosts.includes(post.post_id) }">
                👍 {{ post.like_count || 0 }}
              </span>
            </div>
          </div>
        </li>
      </transition-group>
      
      <!-- 底部按鈕 -->
      <div class="section-footer">
        <button class="load-more-button" v-if="hasMorePosts && !isLoading" @click="loadMore">
          載入更多
        </button>
      </div>
    </div>
  </template>
  
  <script>
    import { ref, computed, onMounted } from "vue";
    import { useRouter } from "vue-router";
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
      name: "DiscussionSection",
      props: {
        category: {
          type: String,
          default: null,
        }
      },
      setup(props) {
        const router = useRouter();
        const posts = ref([]);
        const displayCount = ref(6);
        const isLoading = ref(true);
        const searchQuery = ref("");
        const userLikedPosts = ref([]);
        const userId = ref(1);

        // 獲取分類標題
        const getCategoryTitle = () => {
          if (!props.category) return '最新討論';
          
          switch(props.category) {
            case 'game': return '遊戲討論';
            case 'anime': return '動畫討論';
            case 'movie': return '電影討論';
            default: return '最新討論';
          }
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

        // 分類 ID 映射
        const getCategoryIdByName = (categoryName) => {
          const categoryMap = {
            'movie': 1,
            'game': 2, 
            'anime': 3
          };
          return categoryMap[categoryName];
        };

        // 獲取空列表提示訊息
        const getEmptyMessage = () => {
          if (searchQuery.value.trim()) {
            return '找不到符合搜尋條件的文章';
          } else if (props.category) {
            const categoryName = {
              'game': '遊戲',
              'anime': '動畫',
              'movie': '電影'
            }[props.category] || '';
            return `${categoryName}分類下暫無文章`;
          }
          return '目前沒有文章';
        };

        // 篩選後的文章
        const filteredPosts = computed(() => {
          let filtered = posts.value;
          
          if (props.category) {
            const categoryId = getCategoryIdByName(props.category);
            filtered = filtered.filter(post => post.category_id === categoryId);
          }
          
          if (searchQuery.value.trim()) {
            const query = searchQuery.value.toLowerCase();
            filtered = filtered.filter(post => 
              post.title.toLowerCase().includes(query) || 
              (post.tags && post.tags.some(tag => tag.toLowerCase().includes(query)))
            );
          }
          
          return filtered;
        });

        // 當前顯示的文章
        const displayedPosts = computed(() => {
          return filteredPosts.value.slice(0, displayCount.value);
        });

        // 是否還有更多文章
        const hasMorePosts = computed(() => {
          return displayedPosts.value.length < filteredPosts.value.length;
        });

        // 獲取文章列表
        const fetchPosts = async () => {
          isLoading.value = true;
          try {
            let apiUrl = "http://127.0.0.1:8000/api/posts/";
            if (props.category) {
              const categoryId = getCategoryIdByName(props.category);
              apiUrl += `?category=${categoryId}`;
            }

            const response = await axios.get(apiUrl);
            posts.value = response.data.map(post => ({
              ...post,
              reply_count: post.reply_count || 0,
              like_count: post.like_count || 0,
              view_count: post.view_count || 0,
              created_at: post.created_at || new Date().toISOString()
            }));

            if (props.category) {
              const categoryId = getCategoryIdByName(props.category);
              posts.value = posts.value.filter(post => post.category_id === categoryId);
            }

            posts.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            await fetchUserLikes();
          } catch (error) {
            console.error("無法獲取文章:", error);
            posts.value = [];
          } finally {
            isLoading.value = false;
          }
        };

        // 獲取用戶已點讚的文章
        const fetchUserLikes = async () => {
          try {
            const response = await axios.get(`http://127.0.0.1:8000/api/users/${userId.value}/likes/`);
            userLikedPosts.value = response.data.map(like => like.post_id);
          } catch (error) {
            console.error("無法獲取用戶點讚記錄:", error);
            userLikedPosts.value = [];
          }
        };

        // 防抖處理搜索
        const handleSearch = createDebounce(() => {
          displayCount.value = 6;
        }, 300);

        // 載入更多文章
        const loadMore = () => {
          displayCount.value += 6;
        };

        // 導航到發文頁面
        const goToCreatePost = () => {
          router.push({
            name: 'CreatePost',
            query: props.category ? { category: props.category } : {}
          }).catch(err => {
            console.error('Navigation failed:', err);
          });
        };

        // 查看文章詳情
        const viewPost = (postId) => {
          if (!postId) {
            console.error("Post ID is missing!");
            return;
          }
  
          console.log('Navigating to post:', postId); // 方便除錯用
  
          router.push({
            name: 'PostDetail',
            params: { id: postId.toString() },
            query: { from: router.currentRoute.value.fullPath } // 記錄來源路徑，方便返回
          }).catch(err => {
            console.error('Navigation failed:', err);
            // 如果導航失敗，可以提供備用方案
            router.push('/Forum/discussion');
          });
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

        onMounted(() => {
          fetchPosts();
        });

        return {
          posts,
          displayedPosts,
          hasMorePosts,
          isLoading,
          searchQuery,
          userLikedPosts,
          getCategoryTitle,
          getCategoryIcon,
          getEmptyMessage,
          handleSearch,
          loadMore,
          goToCreatePost,
          viewPost,
          formatDate,
          truncateText
        };
      }
    };
  </script>
  <style scoped>
  .discussion-section {
    width: 100%;
    background: #f9f9f9;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  }
  
  /* 標題和操作欄 */
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .section-subtitle {
    font-size: 24px;
    color: #333;
    margin: 0;
    position: relative;
    padding-left: 15px;
  }
  
  .section-subtitle:before {
    content: "";
    position: absolute;
    left: 0;
    top: 8px;
    bottom: 8px;
    width: 5px;
    background: #007bff;
    border-radius: 3px;
  }
  
  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }
  
  .search-mini {
    display: flex;
    max-width: 240px;
  }
  
  .search-mini input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 5px 0 0 5px;
    font-size: 14px;
    width: 100%;
  }
  
  .search-button {
    padding: 8px 12px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 0 5px 5px 0;
    cursor: pointer;
  }
  
  .create-button {
    padding: 8px 15px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  .create-button:hover {
    background-color: #218838;
  }
  
  /* 載入中 */
  .loading-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
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
  
  /* 無文章狀態 */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    text-align: center;
  }
  
  .empty-state p {
    font-size: 18px;
    color: #666;
    margin-bottom: 20px;
  }
  
  /* 文章列表改為單列顯示 */
  .post-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 0;
    list-style: none;
    margin: 0;
    width: 100%;
  }
  
  /* 文章卡片 */
  .post-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;
    cursor: pointer; /* 添加指針樣式表示可點擊 */
  }
  
  .post-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  /* 文章標頭 */
  .post-header {
    padding: 15px 15px 10px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .post-meta {
    display: flex;
    flex-direction: column;
  }
  
  .post-title {
    font-size: 18px;
    margin: 0 0 10px;
    line-height: 1.4;
    font-weight: 600;
    color: #333;
  }
  
  .post-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 13px;
    color: #777;
  }
  
  .post-date {
    display: inline-block;
  }
  
  .author-info {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .author-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .author {
    max-width: 120px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* 文章標籤 */
  .post-tags {
    padding: 0 15px 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .tag {
    padding: 2px 8px;
    background-color: #e9f5ff;
    color: #0077cc;
    border-radius: 30px;
    font-size: 12px;
  }
  
  .more-tags {
    font-size: 12px;
    color: #777;
    padding: 2px 5px;
  }
  
  /* 文章底部 */
  .post-footer {
    padding: 10px 15px 15px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    background: #fafafa;
    border-top: 1px solid #f0f0f0;
  }
  
  .post-stats {
    display: flex;
    gap: 10px;
  }
  
  .stat-item {
    font-size: 13px;
    color: #666;
  }
  
  .stat-item.liked {
    color: #e53935;
  }
  
  /* 底部按鈕 */
  .section-footer {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
  }
  
  .load-more-button {
    padding: 10px 20px;
    background-color: transparent;
    color: #007bff;
    border: 1px solid #007bff;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  .load-more-button:hover {
    background-color: #007bff10;
  }
  
  /* 動畫 */
  .post-fade-enter-active,
  .post-fade-leave-active {
    transition: all 0.3s ease;
  }
  
  .post-fade-enter-from,
  .post-fade-leave-to {
    opacity: 0;
    transform: translateY(20px);
  }
  
  /* 響應式調整 */
  @media (max-width: 768px) {
    .discussion-section {
      padding: 15px;
    }
    
    .section-header {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .header-actions {
      width: 100%;
      justify-content: space-between;
    }
    
    .search-mini {
      max-width: 100%;
      flex: 1;
    }
    
    .section-footer {
      flex-direction: column;
      gap: 10px;
    }
    
    .load-more-button {
      width: 100%;
    }
  }
  </style>