<template>
    <div class="movie-detail-container">
      <!-- ✅ 如果 movie 存在，顯示內容 -->
      <div v-if="movie" class="movie-detail-card">
        <button @click="goBack" class="btn btn-secondary back-button">🔙 返回</button>
  
        <div class="movie-detail-content">
          <!-- 左側圖片 -->
          <div class="movie-poster">
            <img v-if="movie.poster" :src="movie.poster" alt="Movie Poster" class="poster-img" />
          </div>
  
          <!-- 右側文字內容 -->
          <div class="movie-info">
            <h1 class="movie-title">{{ movie.movie_title }}</h1>
            <p class="movie-description">{{ movie.movie_description }}</p>
            
            <div class="movie-details">
              <div class="detail-item"><strong>🎭 類別：</strong> {{ movie.movie_genre }}</div>
              <div class="detail-item"><strong>📅 發行日期：</strong> {{ movie.release_date }}</div>
              <div class="detail-item"><strong>🎬 導演：</strong> {{ movie.director }}</div>
              <div class="detail-item"><strong>🎭 演員：</strong> {{ movie.cast }}</div>
              <div class="detail-item"><strong>⭐ 評分：</strong> {{ movie.rating }} / 10</div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- ✅ 如果 movie 還在載入，顯示 Loading 狀態 -->
      <div v-else-if="!errorMessage" class="loading-container">
        <p>⏳ 載入中，請稍後...</p>
      </div>
  
      <!-- ✅ 如果 API 回傳錯誤，顯示錯誤訊息 -->
      <div v-else class="error-container">
        <p>❌ {{ errorMessage }}</p>
        <button @click="goBack" class="btn btn-primary">返回</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, nextTick } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import axios from "axios";
  
  const route = useRoute();
  const router = useRouter();
  const movie = ref(null);  // ✅ 預設為 null，防止渲染錯誤
  const errorMessage = ref("");  // ✅ 儲存 API 錯誤訊息
  
  // **🔙 返回上一頁**
  const goBack = () => {
    if (window.history.length > 1) {
      router.back(); // ✅ 返回上一頁（確保不是首頁）
    } else {
      router.push("/Forum"); // ✅ 如果沒有上一頁，就回到 Forum
    }
  };
  
  // **獲取 API 資料**
  const fetchDetail = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/movies/${route.params.id}/`);
      if (response.data) {
        movie.value = response.data;
      } else {
        errorMessage.value = "❌ 找不到該電影的資料";
      }
    } catch (error) {
      console.error("API 請求失敗:", error);
      errorMessage.value = "⚠️ API 請求失敗，請稍後再試";
    }
  };
  
  // **進入頁面後，自動滾動到頂部**
  onMounted(async () => {
    await fetchDetail();
    nextTick(() => {
      window.scrollTo(0, 0); // ✅ 自動滾動到最上方
    });
  });
  </script>
  
  <style scoped>
  /* ✅ 背景淡綠色 */
  .movie-detail-container {
    background: #d4edda;  /* ✅ 淡綠色背景 */
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: 150px; /* ✅ 整體往下移動 150px */
  }
  
  /* ✅ 卡片容器，讓它左右更寬 */
  .movie-detail-card {
    background: white;
    border-radius: 15px;
    padding: 30px;
    max-width: 1400px;  /* ✅ 增加最大寬度 */
    width: 95%;  /* ✅ 讓它接近頁面左右邊界 */
    box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.5s ease-in-out;
  }
  
  /* ✅ 內部內容排列（左圖右文） */
  .movie-detail-content {
    display: flex;
    align-items: flex-start;
    gap: 40px;
  }
  
  /* ✅ 返回按鈕 */
  .back-button {
    margin-bottom: 20px;
  }
  
  /* ✅ 左側圖片樣式 */
  .movie-poster {
    flex: 1;
    max-width: 50%;
  }
  
  .poster-img {
    width: 100%;
    border-radius: 10px;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  /* ✅ 右側文字內容 */
  .movie-info {
    flex: 2;
  }
  
  /* ✅ 標題樣式（放大 1.5 倍） */
  .movie-title {
    font-size: 48px; /* ✅ 放大 1.5 倍 */
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
  }
  
  /* ✅ 文字描述樣式 */
  .movie-description {
    font-size: 22px; /* ✅ 放大一點 */
    line-height: 1.8;
    color: #555;
    margin-bottom: 20px;
  }
  
  /* ✅ 詳細資訊樣式 */
  .movie-details {
    border-top: 2px solid #ccc;
    padding-top: 20px;
    margin-top: 20px;
  }
  
  .detail-item {
    font-size: 20px;
    color: #444;
    margin-bottom: 15px;
    padding: 10px;
    border-bottom: 1px solid #ddd;
  }
  
  /* ✅ 錯誤 & 載入中 */
  .loading-container, .error-container {
    text-align: center;
    font-size: 22px;
    color: black;
    font-weight: bold;
  }
  
  /* ✅ 動畫效果 */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* ✅ 響應式調整 */
  @media (max-width: 1024px) {
    .movie-detail-card {
      max-width: 95%;
    }
  }
  
  @media (max-width: 768px) {
    .movie-detail-content {
      flex-direction: column;
      align-items: center;
    }
    .movie-poster {
      max-width: 100%;
      text-align: center;
    }
    .movie-title {
      font-size: 36px; /* ✅ 在手機上適當縮小 */
    }
    .movie-description {
      font-size: 18px;
    }
  }
  </style>
  