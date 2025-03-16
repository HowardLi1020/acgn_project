<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeAPI, getCurrentUserId } from '../../utils/api'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import ErrorMessage from '../../components/ErrorMessage.vue'

const apiUrl = import.meta.env.VITE_APIURL

const products = ref([])
const categories = ref([])
const brands = ref([])
const series = ref([])
const isLoading = ref(false)
const error = ref(null)

const filters = ref({
  category: '',
  brand: '',
  series: '',
  min_price: '',
  max_price: '',
  sort: 'newest',
})

const searchQuery = ref('');
let searchTimeout = null;

// 獲取商品列表
const fetchProducts = async () => {
  isLoading.value = true
  error.value = null
  try {
    const params = {
      page: 1,
      page_size: 12,
      min_price: filters.value.min_price || '',
      max_price: filters.value.max_price || '',
      category: filters.value.category || '',
      brand: filters.value.brand || '',
      series: filters.value.series || '',
      sort: filters.value.sort || 'newest',
      search: searchQuery.value
    }

    const data = await storeAPI.getAllProducts(params)
    products.value = data.products || []
  } catch (err) {
    console.error('獲取商品列表失敗:', err)
    error.value = '獲取商品列表失敗，請稍後再試'
  } finally {
    isLoading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await fetch(`${apiUrl}/store/categories/`)
    if (response.ok) {
      categories.value = await response.json()
      console.log('Fetched categories:', categories.value)
    } else {
      console.error('Error fetching categories:', response.statusText)
    }
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const fetchBrands = async () => {
  try {
    const response = await fetch(`${apiUrl}/store/brands/`)
    if (response.ok) {
      brands.value = await response.json()
      console.log('Fetched brands:', brands.value)
    } else {
      console.error('Error fetching brands:', response.statusText)
    }
  } catch (error) {
    console.error('Error fetching brands:', error)
  }
}

const fetchSeries = async () => {
  try {
    const response = await fetch(`${apiUrl}/store/series/`)
    if (response.ok) {
      series.value = await response.json()
      console.log('Fetched series:', series.value)
    } else {
      console.error('Error fetching series:', response.statusText)
    }
  } catch (error) {
    console.error('Error fetching series:', error)
  }
}

// 添加搜索處理函數
const handleSearch = () => {
    // 使用防抖函數來避免過多請求
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        fetchProducts();
    }, 300);
};

// 監聽搜索輸入
watch(searchQuery, () => {
    handleSearch();
});


// 監聽篩選條件變化
watch(
  filters,
  () => {
    console.log('當前篩選條件:', filters.value) // 打印當前篩選條件
    fetchProducts() // 當篩選條件變化時重新獲取產品
  },
  { deep: true }
)

// 監聽排序條件變化（可選）
watch(
  () => filters.value.sort,
  (newSort) => {
    console.log('當前排序條件:', newSort) // 打印當前排序條件
    fetchProducts() // 當排序條件變化時重新獲取產品
  }
)

const router = useRouter() // 使用 useRouter
const isMember = ref(false)

// 檢查 localStorage 中是否有 memberData
const checkMemberData = () => {
    const userId = getCurrentUserId();
    isMember.value = !!userId;
};

// 導航到創建商品頁面
const checkMemberAndNavigateToCreateProduct = () => {
  checkMemberData() // 檢查會員狀態
  if (isMember.value) {
    router.push({ name: 'CreateProduct' }) // 如果是會員，導航到創建商品頁面
  } else {
    router.push({ name: 'login' }) // 如果不是會員，導航到登入頁面
  }
}


// 導航到我的商品頁面
const navigateToMyProducts = () => {
  router.push({ name: 'MyProduct' })
}

const navigateToPurchasedProducts = () => {
  router.push({ name: 'PurchasedProducts' })
}
const navigateToWishlist = () => {
  router.push({ name: 'Wishlist' })
}

onMounted(() => {
  fetchCategories()
  fetchBrands()
  fetchSeries()
  fetchProducts()
  checkMemberData()
})
</script>

<template>
  <div class="store">
    <!-- 錯誤提示 -->
    <ErrorMessage v-if="error">{{ error }}</ErrorMessage>
    <h1> 所有商品 </h1>
    <!-- 創建商品按鈕 -->
    <button @click="checkMemberAndNavigateToCreateProduct">創建商品</button>
    <button v-if="isMember" @click="navigateToMyProducts">我的商品</button>
    <button v-if="isMember" @click="navigateToPurchasedProducts" class="purchased-btn">
        購買紀錄
    </button>
    <button v-if="isMember" @click="navigateToWishlist" class="wishlist-btn">
        我的收藏
    </button>

    <!-- 添加搜索欄 -->
    <div class="search-bar">
      <input
        type="text"
        v-model="searchQuery"
        @input="handleSearch"
        placeholder="搜尋商品..."
        class="search-input"
      />
    </div>
    <!-- 篩選器 -->
    <div class="filters">
      <select v-if="categories.length > 0" v-model="filters.category">
        <option value="">所有分類</option>
        <option
          v-for="category in categories"
          :key="category.category_id"
          :value="category.category_id"
        >
          {{ category.category_name }}
        </option>
      </select>

      <select v-if="brands.length > 0" v-model="filters.brand">
        <option value="">所有品牌</option>
        <option v-for="brand in brands" :key="brand.brand_id" :value="brand.brand_id">
          {{ brand.brand_name }}
        </option>
      </select>

      <select v-if="series.length > 0" v-model="filters.series">
        <option value="">所有系列</option>
        <option
          v-for="series_item in series"
          :key="series_item.series_id"
          :value="series_item.series_id"
        >
          {{ series_item.series_name }}
        </option>
      </select>

      <div class="price-range">
        <input type="number" v-model="filters.min_price" placeholder="最低價格" />
        <input type="number" v-model="filters.max_price" placeholder="最高價格" />
      </div>

      <select v-model="filters.sort">
        <option value="newest">最新上架</option>
        <option value="price_asc">價格由低到高</option>
        <option value="price_desc">價格由高到低</option>
      </select>
    </div>

    <!-- 載入中狀態 -->
    <LoadingSpinner v-if="isLoading" />

    <!-- 商品列表 -->
    <div v-else class="products-grid">
      <div v-if="products.length === 0" class="no-products">暫無商品</div>
      <router-link
        v-else
        v-for="product in products"
        :key="product?.product_id"
        :to="{
          name: 'ProductDetail',
          params: { id: product.product_id },
        }"
        class="product-card"
      >
        <img
          :src="product.image_url ? `${apiUrl}/media/${product.image_url}` : '/placeholder.png'"
          :alt="product.product_name"
          @error="$event.target.src = '/placeholder.png'"
        />
        <div class="product-info">
          <h3>{{ product.product_name }}</h3>
          <p class="price">NT$ {{ Math.floor(product.price) }}</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.error-message {
  margin-top: 100px; /* 添加上邊距，確保不被導航欄擋住 */
  color: red; /* 錯誤提示顏色 */
  font-weight: bold; /* 錯誤提示字體加粗 */
  text-align: center; /* 置中對齊 */
}
.store {
  max-width: 1200px; /* 最大寬度 */
  margin: 0 auto; /* 自動邊距以置中 */
  padding: 20px; /* 內邊距 */
  margin-top: 150px; /* 添加上邊距，根據 NAVBAR 的高度調整 */
}

.filters {
  display: flex; /* 使用 Flexbox 來排列篩選器 */
  flex-wrap: wrap; /* 允許換行 */
  gap: 10px; /* 篩選器之間的間距 */
  margin-bottom: 20px; /* 篩選器下方的間距 */
}

.filters select,
.price-range input {
  padding: 10px; /* 內邊距 */
  border-radius: 5px; /* 圓角 */
  border: 1px solid #ccc; /* 邊框 */
}

.price-range {
  display: flex; /* 使用 Flexbox 來排列價格範圍 */
  align-items: center; /* 垂直置中 */
}

.price-range input {
  width: 100px; /* 設定寬度 */
  margin: 0 5px; /* 左右間距 */
}

/* 商品列表樣式 */
.products-grid {
  display: grid; /* 或者使用 display: flex; */
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); /* 每列的最小寬度為 200px */
  gap: 20px; /* 調整產品之間的間距 */
  padding: 20px 0; /* 上下內邊距 */
}

.product-card {
  background-color: #2a2a2a;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  max-width: 200px; /* 設置最大寬度 */
  flex: 1 1 200px; /* 使產品卡片可以根據可用空間自動調整大小 */
  margin: 0; /* 移除外邊距 */
}

.product-card img {
  width: 150px; /* 固定寬度 */
  height: 150px; /* 固定高度 */
  object-fit: cover; /* 確保圖片保持比例並填滿容器 */
}

.product-info {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-info h3 {
  color: white;
  font-size: 1.2rem;
  margin-bottom: 15px;
  font-weight: 600;
  line-height: 1.4;
}

.price {
  color: #28a745;
  font-weight: bold;
  font-size: 1.4rem;
  margin: 15px 0;
}

/* 響應式設計優化 */
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
}

.search-bar {
    margin-bottom: 20px;
    width: 100%;
}

.search-input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 16px;
    background-color: #2a2a2a;
    color: white;
}

.search-input:focus {
    outline: none;
    border-color: #4caf50;
    box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
}

</style>
