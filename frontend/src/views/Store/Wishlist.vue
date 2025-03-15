<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { storeAPI } from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner.vue';
import ErrorMessage from '../../components/ErrorMessage.vue';

const apiUrl = import.meta.env.VITE_APIURL;
const router = useRouter();

const wishlistItems = ref([]);
const isLoading = ref(false);
const error = ref(null);

// 獲取收藏商品列表
const fetchWishlist = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const data = await storeAPI.getWishlist();
    wishlistItems.value = data.products || [];
  } catch (err) {
    console.error('獲取收藏商品失敗:', err);
    error.value = err.message || '獲取收藏商品失敗，請稍後再試';
    
    // 如果是未登入錯誤，導向登入頁面
    if (err.message.includes('登入')) {
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    }
  } finally {
    isLoading.value = false;
  }
};

// 移除收藏
const removeFromWishlist = async (productId) => {
  try {
    await storeAPI.toggleWishlist(productId);
    // 重新獲取收藏列表
    fetchWishlist();
  } catch (err) {
    console.error('移除收藏失敗:', err);
    error.value = err.message || '移除收藏失敗，請稍後再試';
  }
};

// 返回商店頁面
const backToStore = () => {
  router.push('/store');
};

onMounted(() => {
  fetchWishlist();
});
</script>

<template>
  <div class="wishlist-container">
    <h1>我的收藏</h1>
    <button @click="backToStore" class="back-button">返回商店</button>
    
    <!-- 錯誤提示 -->
    <ErrorMessage v-if="error">{{ error }}</ErrorMessage>
    
    <!-- 載入中狀態 -->
    <LoadingSpinner v-if="isLoading" />
    
    <!-- 收藏商品列表 -->
    <div v-else>
      <div v-if="wishlistItems.length === 0" class="no-items">
        您還沒有收藏任何商品
      </div>
      
      <div v-else class="wishlist-grid">
        <div v-for="item in wishlistItems" :key="item.product_id" class="wishlist-item">
          <div class="product-card">
            <img
              :src="item.image_url ? `${apiUrl}/media/${item.image_url}` : '/placeholder.png'"
              :alt="item.product_name"
              @error="$event.target.src = '/placeholder.png'"
              @click="router.push({ name: 'ProductDetail', params: { id: item.product_id } })"
            />
            <div class="product-info">
              <h3 @click="router.push({ name: 'ProductDetail', params: { id: item.product_id } })">
                {{ item.product_name }}
              </h3>
              <p class="price">NT$ {{ Math.floor(item.price) }}</p>
              <button @click="removeFromWishlist(item.product_id)" class="remove-button">
                移除收藏
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wishlist-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  margin-top: 150px;
}

.back-button {
  margin-bottom: 20px;
  padding: 8px 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.back-button:hover {
  background-color: #45a049;
}

.no-items {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.wishlist-item {
  background-color: #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.wishlist-item:hover {
  transform: translateY(-5px);
}

.product-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.product-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
}

.product-info {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.product-info h3 {
  color: white;
  font-size: 1.2rem;
  margin-bottom: 10px;
  cursor: pointer;
}

.product-info h3:hover {
  text-decoration: underline;
}

.price {
  color: #28a745;
  font-weight: bold;
  font-size: 1.4rem;
  margin: 10px 0;
}

.remove-button {
  margin-top: auto;
  padding: 8px 16px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.remove-button:hover {
  background-color: #d32f2f;
}

@media (max-width: 768px) {
  .wishlist-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style>