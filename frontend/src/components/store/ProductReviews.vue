<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import StarRating from '../store/StarRating.vue'

const props = defineProps({
  productId: {
    type: String,
    required: true
  }
})

const route = useRoute()
const reviews = ref([])
const newReview = ref({
  rating: 0,
  content: ''
})
const isSubmitting = ref(false)
const errorMessage = ref('')

const apiUrl = import.meta.env.VITE_APIURL; // 獲取 API URL

// 獲取商品評價
const fetchReviews = async () => {
  try {
    const response = await fetch(`${apiUrl}/store/products/${props.productId}/reviews/`);
    if (!response.ok) throw new Error('Network response was not ok');
    reviews.value = await response.json();
  } catch (error) {
    console.error('獲取評價失敗:', error);
  }
}

// 提交評價
const submitReview = async () => {
  if (newReview.value.rating === 0) {
    errorMessage.value = '請選擇評分';
    return;
  }

  isSubmitting.value = true;
  try {
    const response = await fetch(`${apiUrl}/store/products/${props.productId}/reviews/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(newReview.value)
    });

    if (!response.ok) throw new Error('Network response was not ok');

    await fetchReviews();
    newReview.value = { rating: 0, content: '' };
    errorMessage.value = '';
  } catch (error) {
    errorMessage.value = '系統錯誤，請稍後再試';
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(fetchReviews)
</script>

<template>
  <div class="reviews-section">
    <h2>商品評價</h2>

    <!-- 評價統計 -->
    <div class="reviews-summary" v-if="reviews.length > 0">
      <div class="average-rating">
        <h3>平均評分</h3>
        <StarRating 
          :rating="reviews.reduce((acc, review) => acc + review.rating, 0) / reviews.length"
          :readonly="true"
          size="large"
        />
        <p>{{ reviews.length }} 則評價</p>
      </div>

      <div class="rating-distribution">
        <div v-for="i in 5" :key="i" class="rating-bar">
          <span>{{ 6 - i }}星</span>
          <div class="bar-container">
            <div 
              class="bar" 
              :style="{
                width: `${(reviews.filter(r => r.rating === 6-i).length / reviews.length) * 100}%`
              }"
            ></div>
          </div>
          <span>{{ reviews.filter(r => r.rating === 6-i).length }}</span>
        </div>
      </div>
    </div>

    <!-- 撰寫評價 -->
    <div class="write-review">
      <h3>撰寫評價</h3>
      <form @submit.prevent="submitReview">
        <div class="rating-input">
          <label>評分</label>
          <StarRating v-model="newReview.rating" />
        </div>

        <div class="content-input">
          <label>評價內容</label>
          <textarea 
            v-model="newReview.content"
            rows="4"
            placeholder="分享您的使用心得..."
            required
          ></textarea>
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button 
          type="submit" 
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '提交中...' : '提交評價' }}
        </button>
      </form>
    </div>

    <!-- 評價列表 -->
    <div class="reviews-list">
      <div v-for="review in reviews" 
           :key="review.id" 
           class="review-item">
        <div class="review-header">
          <StarRating :rating="review.rating" :readonly="true" />
          <span class="review-date">{{ new Date(review.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="review-user">
          {{ review.user_name }}
        </div>
        <p class="review-content">{{ review.content }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reviews-section {
  margin-top: 3rem;
}

.reviews-summary {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2rem;
  margin: 2rem 0;
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.average-rating {
  text-align: left; /* 左對齊 */
}

.rating-distribution {
  padding-left: 2rem;
}

.rating-bar {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin: 0.5rem 0;
}

.bar-container {
  flex: 1;
  height: 8px;
  background: #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: #15a362;
  transition: width 0.3s ease;
}

.write-review {
  margin: 2rem 0;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.rating-input,
.content-input {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

button {
  padding: 0.75rem 1.5rem;
  background: #15a362;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.review-item {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.review-date {
  color: #666;
  font-size: 0.9rem;
}

.review-user {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.review-content {
  color: #333;
  line-height: 1.5;
}

.error-message {
  color: #e53935;
  margin-bottom: 1rem;
}

/* 確保整個評價區域左對齊 */
.product-reviews {
  display: flex;
  flex-direction: column; /* 垂直排列 */
  align-items: flex-start; /* 左對齊 */
  margin-top: 20px; /* 上邊距 */
}

.product-reviews h2 {
  margin-bottom: 10px; /* 標題下邊距 */
}

.review-form {
  width: 100%; /* 確保表單寬度 */
}

.review-form textarea {
  width: 100%; /* 確保文本區域寬度 */
  margin-bottom: 10px; /* 下邊距 */
}

.submit-button {
  align-self: flex-start; /* 按鈕左對齊 */
}
</style>
