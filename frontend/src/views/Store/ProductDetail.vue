<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeAPI } from "../../utils/api";
import { cartAPI } from '@/utils/api';
import StarRating from "../../components/store/StarRating.vue";
import ProductReviews from "../../components/store/ProductReviews.vue";
import WishlistButton from "../../components/store/WishlistButton.vue";
import ProductRecommendations from "../../components/store/ProductRecommendations.vue";

const router = useRouter();
const route = useRoute();
const product = ref({});
const loading = ref(true);
const error = ref(null);
const apiUrl = import.meta.env.VITE_APIURL;
const currentImageIndex = ref(0);
const quantity = ref(1);

// 獲取商品訊息
const fetchProduct = async () => {
    try {
        loading.value = true;
        error.value = null;
        const productId = route.params.id;
        const data = await storeAPI.getProductDetail(productId);

        if (data) {
            product.value = data;
        } else {
            error.value = "商品資料錯誤";
        }
    } catch (err) {
        console.error("獲取商品信息失败:", err);
        error.value = "獲取商品信息失败";
    } finally {
        loading.value = false;
        window.scrollTo(0, 0);
    }
};

const checkQuantity = () => {
    // 確保數量不小於 1
    if (quantity.value < 1) {
        quantity.value = 1;
    }
    // 確保數量不超過庫存
    else if (quantity.value > product.value.stock) {
        quantity.value = product.value.stock;
    }
    // 確保是整數
    quantity.value = Math.floor(quantity.value);
};

const addToCart = async () => {
    try {
        const payload = {
            product_id: product.value.product_id,
            quantity: quantity.value,
        };
        console.log("Payload:", payload);

        // 調用 API 添加商品到購物車
        const response = await cartAPI.addCartItem(payload);
        console.log("Response from API:", response);

        // 成功提示
        alert("商品已成功加入購物車！");
        
    } catch (error) {
        console.error("加入購物車失敗:", error.message);
        alert("加入購物車失敗，請稍後再試！");
    }
};


const buyNow = async () => {
    try {
        const payload = {
            product_id: product.value.product_id,
            quantity: quantity.value,
        };
        // 調用 API 添加商品到購物車
        const response = await cartAPI.addCartItem(payload);
        console.log("Response from API:", response);

        router.push('/shoppingcart'); // 跳轉到購物車頁面
        
    } catch (error) {
        console.error('立即購買失敗:', error.response?.data || error.message);
        alert('立即購買失敗，請稍後再試！');
    }
};


// 獲取當前主圖 URL 的函數
const getMainImageUrl = () => {
    console.log('apiUrl:', apiUrl); // 檢查 API URL
    console.log('product images:', product.value?.images); // 檢查圖片數據
    if (product.value?.images?.length > 0) {

        
        // 直接使用當前選中的圖片索引
        const currentImage = product.value.images[currentImageIndex.value];
        return currentImage ? `${apiUrl}${currentImage.image_url}` : '/placeholder.png';
    }
    return '/placeholder.png';
};

// 切换主圖的函數
const switchMainImage = (index) => {
    currentImageIndex.value = index; // 更新當前圖片索引
};

watch(
    () => route.params.id,
    (newId) => {
        if (newId) {
            // 添加判斷
            fetchProduct();
        }
    }
);

onMounted(async () => {
    if (route.params.id) {
        // 添加判斷
        await fetchProduct();
    }
});
</script>

<template>
    <div class="product-detail" :key="route.params.id">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else-if="product" class="product-content">
            <div class="product-images">
                <!-- 主圖 -->
                <div class="main-image-container">
                    <img
                        :src="getMainImageUrl()"
                        :alt="product.product_name"
                        class="main-image"
                        @error="$event.target.src = '/placeholder.png'"
                        crossorigin="anonymous"
                    />
                </div>

                <!-- 縮略圖 -->
                <div class="thumbnail-images" v-if="product.images?.length > 1">
                    <img
                        v-for="(image, index) in product.images"
                        :key="index"
                        :src="`${apiUrl}${image.image_url}`"
                        :alt="product.product_name"
                        class="thumbnail"
                        :class="{ active: currentImageIndex === index }"
                        @click="switchMainImage(index)"
                        @error="$event.target.src = '/placeholder.png'"
                        crossorigin="anonymous"
                    />
                </div>
            </div>

            <div class="product-info">
                <h1 class="product-name">{{ product.product_name }}</h1>
                <p class="price">NT$ {{ product.price }}</p>

                <div class="details">
                    <p v-if="product.brand">
                        <strong>品牌：</strong>{{ product.brand_name }}
                    </p>
                    <p v-if="product.category">
                        <strong>分類：</strong>{{ product.category_name }}
                    </p>
                    <p v-if="product.series">
                        <strong>系列：</strong>{{ product.series_name }}
                    </p>
                    <p>
                        <strong>庫存：</strong>
                        {{ product.stock > 0 ? product.stock : "暫時缺貨" }}
                    </p>
                </div>

                <div v-if="product.stock > 0" class="quantity-selector">
                    <label for="quantity">數量：</label>
                    <input
                        type="number"
                        id="quantity"
                        v-model.number="quantity"
                        min="1"
                        :max="product.stock"
                        @input="checkQuantity"
                    />
                </div>

                <div class="actions">
                    <button class="add-to-cart" @click="addToCart">加入購物車</button>
                    <button class="buy-now" @click="buyNow">立即購買</button>
                    <WishlistButton :product-id="String(product.product_id)" />
                </div>
            </div>
        </div>

        <!-- 商品描述區域 -->
        <div class="product-description" v-if="product">
            <h2>商品描述</h2>
            <p>{{ product.description_text }}</p>
        </div>
        <!-- 商品評論區域 -->
        <ProductReviews 
            :productId="route.params.id"
        />
        <!-- 商品推薦區域 -->
        <ProductRecommendations
            v-if="product && product.product_id"
            :product-id="String(product.product_id)"
            type="similar"
        />
    </div>
</template>

<style scoped>
.product-detail {
    margin-top: 200px;
    display: flex;
    flex-direction: column;
    align-items: left;
    padding: 0 15%;
}

.product-content {
    display: flex;
    max-width: 1200px; /* 限制最大寬度 */
    width: 100%;
}

.product-images {
    padding-top: 20px;
    flex: 1;
    margin-right: 20px; /* 右邊距 */
}

.main-image-container {
    width: 100%;
    height: 300px; /* 調整為您希望的高度 */
    overflow: hidden; /* 隱藏超出容器的部分 */
}

.main-image {
    width: 100%;
    height: 100%; /* 可以根據需要調整 */
    object-fit: contain; /* 確保圖片保持比例並適應容器 */
    border-radius: 8px;
}

.thumbnail-images {
    display: flex;
    margin-top: 10px;
    justify-content: center;
}

.thumbnail {
    width: 80px;
    height: 80px;
    margin-right: 5px;
    cursor: pointer;
    border-radius: 4px;
    transition: transform 0.2s;
}

.thumbnail:hover {
    transform: scale(1.1);
}

.product-info {
    flex: 1;
    padding: 20px;
}

.product-name {
    font-size: 24px;
    font-weight: bold;
}

.price {
    font-size: 20px;
    color: #e74c3c;
}

.details {
    margin: 10px 0;
}

.quantity-selector {
    margin: 10px 0;
}

.actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

.add-to-cart,
.buy-now {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.add-to-cart:hover,
.buy-now:hover {
    background-color: #2980b9;
}

/* 商品描述樣式 */
.product-description {
    max-width: 1200px; /* 限制最大寬度 */
    width: 100%;
    padding: 20px;
    background-color: #f9f9f9; /* 背景顏色 */
    border-radius: 8px; /* 圓角 */
    margin-top: 20px; /* 上邊距 */
}

.product-description h2 {
    font-size: 20px;
    margin-bottom: 10px;
}
@media (max-width: 768px) {
    .main-image-container {
        height: 200px; /* 在小屏幕上設置較小的高度 */
    }
}
</style>
