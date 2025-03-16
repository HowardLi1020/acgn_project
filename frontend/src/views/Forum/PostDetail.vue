<template>
    <div class="post-detail-container">
      <!-- 返回按鈕 -->
      <div class="back-nav">
        <button class="back-button" @click="goBack">
          ← 返回討論列表
        </button>
      </div>
  
      <!-- 載入狀態 -->
      <div v-if="isLoading" class="loading-wrapper">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>
  
      <!-- 文章找不到 -->
      <div v-else-if="!post" class="not-found">
        <div class="not-found-icon">😕</div>
        <h2>找不到文章</h2>
        <p>您請求的文章不存在或已被刪除</p>
        <button class="action-button" @click="goToDiscussion">返回討論區</button>
      </div>
  
      <!-- 文章內容 -->
      <div v-else class="post-content">
        <div class="post-header">
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="post-meta">
            <div class="author-info">
              <img :src="post.author_avatar || '/default-avatar.png'" alt="作者頭像" class="author-avatar" />
              <div>
                <div class="author-name">{{ post.author_name || '用戶 #' + post.author_id }}</div>
                <div class="post-date">發表於: {{ formatDate(post.created_at) }}</div>
              </div>
            </div>
            <div class="post-stats">
              <span class="stat-item">💬 {{ post.reply_count || 0 }}</span>
              <span class="stat-item">👁️ {{ post.view_count || 0 }}</span>
              <span class="stat-item" :class="{ 'liked': userLikedPost }">
                👍 {{ post.like_count || 0 }}
              </span>
            </div>
          </div>
        </div>
  
        <div class="post-tags" v-if="post.tags && post.tags.length">
          <span class="tag" v-for="tag in post.tags" :key="tag">{{ tag }}</span>
        </div>
  
        <div class="post-body">
          {{ post.body }}
        </div>
  
        <div class="action-buttons">
          <button 
            class="like-button" 
            :class="{ 'liked': userLikedPost }"
            @click="toggleLike"
            :disabled="isLiking"
          >
            {{ userLikedPost ? '❤️ 已點讚' : '👍 點讚' }}
          </button>
          <button class="share-button" @click="sharePost">
            分享
          </button>
        </div>
  
        <!-- 評論區 -->
        <div class="comments-section">
          <h3 class="section-title">評論區 ({{ comments.length }})</h3>
          
          <!-- 發表評論 -->
          <div class="comment-form">
            <div class="form-group">
              <textarea 
                v-model="commentText" 
                placeholder="發表評論..."
                rows="3"
                :disabled="isSubmittingComment"
              ></textarea>
              <div class="form-actions">
                <span class="word-count">{{ commentText.length }}/500</span>
                <button 
                  class="submit-button" 
                  :disabled="!commentText.trim() || isSubmittingComment"
                  @click="submitComment"
                >
                  {{ isSubmittingComment ? '發送中...' : '發送' }}
                </button>
              </div>
            </div>
          </div>
  
          <!-- 評論列表 -->
          <div v-if="comments.length === 0" class="no-comments">
            <p>暫無評論，成為第一個評論的人吧！</p>
          </div>
  
          <ul v-else class="comments-list">
            <li v-for="comment in comments" :key="comment.comment_id" class="comment-item">
              <div class="comment-header">
                <div class="commenter-info">
                  <img :src="comment.author_avatar || '/default-avatar.png'" alt="評論者頭像" class="commenter-avatar" />
                  <div>
                    <div class="commenter-name">{{ comment.author_name || '用戶 #' + comment.author_id }}</div>
                    <div class="comment-date">{{ formatDate(comment.created_at) }}</div>
                  </div>
                </div>
              </div>
              <div class="comment-body">
                {{ comment.content }}
              </div>
              <div class="comment-actions">
                <button 
                  class="action-link"
                  :class="{ 'active': comment.liked }"
                  @click="likeComment(comment.comment_id)"
                >
                  {{ comment.liked ? '已點讚' : '點讚' }} ({{ comment.like_count || 0 }})
                </button>
                <button class="action-link" @click="replyToComment(comment.comment_id)">
                  回覆
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';

  export default {
    name: 'PostDetail',
    setup() {
      const route = useRoute();
      const router = useRouter();
      const postId = route.params.id;

      const post = ref(null);
      const comments = ref([]);
      const isLoading = ref(true);
      const userLikedPost = ref(false);
      const isLiking = ref(false);
      const commentText = ref('');
      const isSubmittingComment = ref(false);
      const userId = ref(1); // 模擬目前登入的用戶 ID

      // 獲取文章詳情
      const fetchPostDetail = async () => {
        isLoading.value = true;
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/posts/${postId}`);
          post.value = response.data;
          
          await Promise.all([
            fetchComments(),
            checkLikeStatus()
          ]);
        } catch (error) {
          console.error('無法獲取文章詳情:', error);
          post.value = null;
        } finally {
          isLoading.value = false;
        }
      };

      // 獲取評論
      const fetchComments = async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/posts/${postId}/comments/`);
          
          if (Array.isArray(response.data)) {
            comments.value = response.data.map(comment => ({
              comment_id: comment.reply_id,
              post_id: Number(postId),
              content: comment.body,
              author_id: comment.author_id,
              author_name: `用戶 #${comment.author_id}`,
              author_avatar: '/default-avatar.png',
              created_at: comment.created_at,
              like_count: 0,
              liked: false
            }));
          } else {
            comments.value = [];
          }
          
          await checkCommentLikes();
        } catch (error) {
          console.error('無法獲取評論:', error);
          comments.value = [];
        }
      };
      
      // 檢查用戶是否已點讚該文章
      const checkLikeStatus = async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/posts/user_likes/?user_id=${userId.value}`);
          const userLikes = response.data.map(like => like.post_id);
          userLikedPost.value = userLikes.includes(Number(postId));
        } catch (error) {
          console.error('無法獲取點讚狀態:', error);
          userLikedPost.value = false;
        }
      };

      // 檢查用戶已點讚的評論
      const checkCommentLikes = async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/api/users/${userId.value}/comment-likes`);
          const likedCommentIds = response.data.map(like => like.comment_id);
          
          comments.value = comments.value.map(comment => ({
            ...comment,
            liked: likedCommentIds.includes(comment.comment_id)
          }));
        } catch (error) {
          console.error('無法獲取評論點讚狀態:', error);
        }
      };

      // 提交評論
      const submitComment = async () => {
        if (!commentText.value.trim() || isSubmittingComment.value) return;
        
        isSubmittingComment.value = true;
        try {
          const commentData = {
            post: Number(postId),
            body: commentText.value,
            author_id: userId.value
          };
          
          const response = await axios.post('http://127.0.0.1:8000/api/replies/', commentData);
          
          if (response.data) {
            const newComment = {
              comment_id: response.data.reply_id,
              post_id: Number(postId),
              content: response.data.body,
              author_id: response.data.author_id,
              author_name: '當前用戶',
              author_avatar: '/default-avatar.png',
              created_at: response.data.created_at,
              like_count: 0,
              liked: false
            };
            
            comments.value.unshift(newComment);
            post.value.reply_count = (post.value.reply_count || 0) + 1;
            commentText.value = '';
            localStorage.removeItem(`draft_comment_${postId}`);
          }
        } catch (error) {
          console.error('發送評論失敗:', error);
          alert('評論發送失敗，請稍後再試');
        } finally {
          isSubmittingComment.value = false;
        }
      };

      // 點讚或取消點讚
      const toggleLike = async () => {
        if (isLiking.value) return;
        
        isLiking.value = true;
        try {
          await axios.post(`http://127.0.0.1:8000/api/posts/${postId}/like/`, {
            user_id: userId.value
          });
          
          userLikedPost.value = !userLikedPost.value;
          
          if (userLikedPost.value) {
            post.value.like_count = (post.value.like_count || 0) + 1;
          } else {
            post.value.like_count = Math.max(0, (post.value.like_count || 1) - 1);
          }
        } catch (error) {
          console.error('點讚操作失敗:', error);
        } finally {
          isLiking.value = false;
        }
      };

      // 點讚評論
      const likeComment = async (commentId) => {
        const commentIndex = comments.value.findIndex(c => c.comment_id === commentId);
        if (commentIndex === -1) return;
        
        const comment = comments.value[commentIndex];
        try {
          if (comment.liked) {
            await axios.delete(`http://127.0.0.1:8000/api/comments/${commentId}/like`, {
              data: { user_id: userId.value }
            });
            comment.like_count = Math.max(0, (comment.like_count || 1) - 1);
          } else {
            await axios.post(`http://127.0.0.1:8000/api/comments/${commentId}/like`, {
              user_id: userId.value
            });
            comment.like_count = (comment.like_count || 0) + 1;
          }
          comment.liked = !comment.liked;
        } catch (error) {
          console.error('評論點讚操作失敗:', error);
        }
      };

      // 分享文章
      const sharePost = () => {
        if (navigator.share) {
          navigator.share({
            title: post.value.title,
            text: `查看這篇文章：${post.value.title}`,
            url: window.location.href
          }).catch(error => console.error('分享失敗:', error));
        } else {
          const el = document.createElement('textarea');
          el.value = window.location.href;
          document.body.appendChild(el);
          el.select();
          document.execCommand('copy');
          document.body.removeChild(el);
          alert('連結已複製到剪貼簿');
        }
      };

      // 返回上一頁
      const goBack = () => {
        // 檢查是否有 query 參數指定返回路徑
        const returnPath = route.query.from;
        if (returnPath) {
          router.push(returnPath);
        } else if (window.history.length > 1) {
          router.go(-1);
        } else {
          // 預設返回討論區，根據文章分類決定返回路徑
          const category = post.value?.category_id;
          let path = '/Forum/discussion';
          
          // 根據分類 ID 設定對應的路徑
          if (category) {
            const categoryMap = {
              1: '/Forum/discussion/movie',
              2: '/Forum/discussion/game',
              3: '/Forum/discussion/anime'
            };
            path = categoryMap[category] || path;
          }
          
          router.push(path);
        }
      };

      // 返回討論區
      const goToDiscussion = () => {
        router.push('/Forum/discussion');
      };

      // 保存草稿評論
      const saveDraftComment = () => {
        if (commentText.value.trim()) {
          localStorage.setItem(`draft_comment_${postId}`, commentText.value);
        } else {
          localStorage.removeItem(`draft_comment_${postId}`);
        }
      };

      // 載入草稿評論
      const loadDraftComment = () => {
        const draft = localStorage.getItem(`draft_comment_${postId}`);
        if (draft) {
          commentText.value = draft;
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
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      };

      // 監聽評論文本變化，保存草稿
      watch(commentText, saveDraftComment);

      onMounted(() => {
        window.scrollTo(0, 0);
        fetchPostDetail();
        loadDraftComment();
      });

      return {
        post,
        comments,
        isLoading,
        userLikedPost,
        isLiking,
        commentText,
        isSubmittingComment,
        toggleLike,
        submitComment,
        likeComment,
        sharePost,
        goBack,
        goToDiscussion,
        formatDate
      };
    }
  };
  </script>
  
  <style scoped>
  .post-detail-container {
  max-width: 900px;
  margin: 150px auto 0; /* 這裡添加了150px的上邊距 */
  padding: 30px 20px;
  }
  
  .back-nav {
    margin-bottom: 20px;
  }
  
  .back-button {
    background: none;
    border: none;
    color: #666;
    font-size: 16px;
    cursor: pointer;
    padding: 8px 0;
    display: flex;
    align-items: center;
    transition: color 0.2s;
  }
  
  .back-button:hover {
    color: #007bff;
  }
  
  /* 載入中 */
  .loading-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 300px;
  }
  
  .spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border-left-color: #007bff;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* 找不到文章 */
  .not-found {
    text-align: center;
    padding: 60px 0;
  }
  
  .not-found-icon {
    font-size: 50px;
    margin-bottom: 20px;
  }
  
  .not-found h2 {
    font-size: 28px;
    color: #333;
    margin-bottom: 10px;
  }
  
  .not-found p {
    color: #666;
    margin-bottom: 30px;
  }
  
  .action-button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .action-button:hover {
    background-color: #0069d9;
  }
  
  /* 文章內容 */
  .post-content {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
    overflow: hidden;
  }
  
  .post-header {
    padding: 25px 30px;
    border-bottom: 1px solid #eee;
  }
  
  .post-title {
    font-size: 28px;
    color: #333;
    margin: 0 0 20px 0;
    line-height: 1.3;
  }
  
  .post-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .author-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .author-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .author-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 5px;
  }
  
  .post-date {
    font-size: 14px;
    color: #777;
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
  
  .post-tags {
    padding: 15px 30px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    background-color: #f9f9f9;
  }
  
  .tag {
    padding: 5px 12px;
    background-color: #e9f5ff;
    color: #0077cc;
    border-radius: 30px;
    font-size: 14px;
  }
  
  .post-body {
    padding: 30px;
    font-size: 17px;
    line-height: 1.7;
    color: #333;
    white-space: pre-wrap;
  }
  
  .action-buttons {
    padding: 20px 30px;
    display: flex;
    justify-content: flex-start;
    gap: 15px;
    border-top: 1px solid #eee;
    background-color: #f9f9f9;
  }
  
  .like-button, 
  .share-button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
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
  
  .share-button {
    background-color: #f0f2f5;
    color: #444;
  }
  
  .share-button:hover {
    background-color: #e8f5e9;
    color: #28a745;
  }
  
  /* 評論區 */
  .comments-section {
    margin-top: 30px;
    padding: 0 30px 30px;
  }
  
  .section-title {
    font-size: 22px;
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }
  
  .comment-form {
    margin-bottom: 30px;
  }
  
  .form-group {
    position: relative;
  }
  
  .form-group textarea {
    width: 100%;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    resize: vertical;
    transition: border-color 0.2s;
  }
  
  .form-group textarea:focus {
    border-color: #007bff;
    outline: none;
  }
  
  .form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
  }
  
  .word-count {
    font-size: 14px;
    color: #777;
  }
  
  .submit-button {
    padding: 8px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .submit-button:hover {
    background-color: #0069d9;
  }
  
  .submit-button:disabled {
    background-color: #b3d7ff;
    cursor: not-allowed;
  }
  
  .no-comments {
    text-align: center;
    padding: 30px 0;
    color: #666;
  }
  
  .comments-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .comment-item {
    padding: 20px 0;
    border-bottom: 1px solid #eee;
  }
  
  .comment-item:last-child {
    border-bottom: none;
  }
  
  .comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
  }
  
  .commenter-info {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .commenter-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .commenter-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 3px;
  }
  
  .comment-date {
    font-size: 13px;
    color: #777;
  }
  
  .comment-body {
    font-size: 16px;
    line-height: 1.6;
    color: #333;
    margin-bottom: 15px;
    white-space: pre-wrap;
  }
  
  .comment-actions {
    display: flex;
    gap: 20px;
  }
  
  .action-link {
    background: none;
    border: none;
    font-size: 14px;
    color: #666;
    cursor: pointer;
    padding: 0;
    transition: color 0.2s;
  }
  
  .action-link:hover {
    color: #007bff;
  }
  
  .action-link.active {
    color: #e53935;
  }
  
  /* 響應式設計 */
  @media (max-width: 768px) {
    .post-detail-container {
      padding: 20px 15px;
    }
    
    .post-header {
      padding: 20px;
    }
    
    .post-title {
      font-size: 24px;
    }
    
    .post-meta {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .post-tags {
      padding: 15px 20px;
    }
    
    .post-body {
      padding: 20px;
      font-size: 16px;
    }
    
    .action-buttons {
      padding: 15px 20px;
    }
    
    .comments-section {
      padding: 0 20px 20px;
    }
  }
  </style>