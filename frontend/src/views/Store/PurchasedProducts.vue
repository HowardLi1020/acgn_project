<script setup>
import { ref, onMounted } from 'vue';
import { storeAPI } from '../../utils/api';
import { useRouter } from 'vue-router';
import LoadingSpinner from '../../components/LoadingSpinner.vue';

const apiUrl = import.meta.env.VITE_APIURL;  // 添加這行
const router = useRouter();
const purchasedProducts = ref([]);
const isLoading = ref(true);
const error = ref(null);

const formatDate = (dateString) => {
  if (!dateString) return '未知日期';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    console.error('日期格式化錯誤:', e);
    return '日期格式錯誤';
  }
};

const fetchPurchasedProducts = async () => {
  try {
    isLoading.value = true;
    const response = await storeAPI.getPurchasedProducts();
    purchasedProducts.value = response.data;
  } catch (err) {
    console.error('獲取購買紀錄失敗:', err);
    error.value = '獲取購買紀錄失敗，請稍後再試';
  } finally {
    isLoading.value = false;
  }
};

// 返回商店頁面
const backToStore = () => {
  router.push('/store');
};


onMounted(() => {
  fetchPurchasedProducts();
});
</script>

<template>
    <div class="purchased-products">
      <h1>購買紀錄</h1>
      <button @click="backToStore" class="back-button">返回商店</button>
      
      <LoadingSpinner v-if="isLoading" />
      
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-else-if="purchasedProducts.length === 0" class="no-products">
        尚未購買任何商品
      </div>
      
      <div v-else class="products-grid">
        <div v-for="product in purchasedProducts" 
             :key="product.order_id" 
             class="product-card">
          <div class="image-container">
            <img 
              :src="product.image_url ? `${apiUrl}/media/${product.image_url}` : '/placeholder.png'"
              :alt="product.product_name"
              @error="$event.target.src = '/placeholder.png'"
            />
          </div>
          <div class="product-info">
            <h3>{{ product.product_name }}</h3>
            <p class="price">NT$ {{ Math.floor(product.price) }}</p>
            <p class="quantity">購買數量：{{ product.quantity }}</p>
            <p class="purchase-date">購買日期：{{ formatDate(product.purchase_date) }}</p>
            <button @click="router.push(`/store/product/${product.product_id}`)" 
                    class="view-detail-btn">
              查看商品
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>

<style scoped>
.purchased-products {
  max-width: 1200px;
  margin: 150px auto 0;
  padding: 20px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.product-card {
  background-color: #2a2a2a;
  border-radius: 12px;
  padding: 15px;
  transition: transform 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
}

.product-info {
  padding: 15px;
}

.product-info h3 {
  color: #fff;
  margin: 10px 0;
}

.price {
  color: #2ecc71;
  font-weight: bold;
  font-size: 1.2em;
}

.purchase-date {
  color: #888;
  font-size: 0.9em;
  margin: 5px 0;
}

.view-detail-btn {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.view-detail-btn:hover {
  background-color: #2980b9;
}

.no-products {
  text-align: center;
  color: #888;
  padding: 50px;
  font-size: 1.2em;
}

.error-message {
  text-align: center;
  color: #e74c3c;
  padding: 20px;
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
</style>