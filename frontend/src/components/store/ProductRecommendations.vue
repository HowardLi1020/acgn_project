<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { storeAPI } from '../../utils/api';
import LoadingSpinner from '../LoadingSpinner.vue';
import ErrorMessage from '../ErrorMessage.vue';

const props = defineProps({
    productId: {
        type: String,
        required: true
    },
    type: {
        type: String,
        default: 'similar'
    }
});

const router = useRouter();
const recommendations = ref([]);
const loading = ref(true);
const error = ref('');

const apiUrl = import.meta.env.VITE_APIURL;

// 獲取推薦商品
const fetchRecommendations = async () => {
    if (!props.productId) return; // 添加防護

    try {
        loading.value = true;
        error.value = null;
        const data = await storeAPI.getRecommendations(props.productId, props.type);
        if (data) {
            recommendations.value = data;
        }
    } catch (err) {
        console.error('獲取推薦商品失敗:', err);
        error.value = '獲取推薦商品失敗';
    } finally {
        loading.value = false;
    }
};

const goToProduct = (productId) => {
    router.push({
        name: 'ProductDetail',
        params: { id: productId }
    });
};

// 監聽路由變化以重新獲取推薦商品
watch(() => props.productId, (newId) => {
    if (newId) {
        fetchRecommendations();
    }
}, { immediate: true });


</script>

<template>
  <div class="recommendations-section" v-if="!error">
        <h2>相似商品推薦</h2>
        <div v-if="loading" class="loading">加載中...</div>
        <div v-else-if="recommendations && recommendations.length > 0" class="recommendations-grid">
            <router-link
                v-for="product in recommendations"
                :key="product.product_id"
                :to="{ name: 'ProductDetail', params: { id: product.product_id }}"
                class="product-card"
            >
                <img
                    :src="product.image_url ? `${apiUrl}/media/${product.image_url}` : '/placeholder.png'"
                    :alt="product.product_name"
                    @error="$event.target.src = '/placeholder.png'"
                />
                <div class="product-info">
                    <h3>{{ product.product_name }}</h3>
                    <p class="price">NT$ {{ product.price }}</p>
                </div>
            </router-link>
        </div>
        <div v-else class="no-recommendations">
            暫無相關推薦商品
        </div>
    </div>
</template>

<style scoped>
.recommendations-section {
    margin-top: 40px;
}

.recommendations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.product-card {
    text-decoration: none;
    color: inherit;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.2s;
}

.product-card:hover {
    transform: translateY(-5px);
}

.product-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.product-info {
    padding: 15px;
}

.product-info h3 {
    margin: 0;
    font-size: 1rem;
}

.price {
    color: #e74c3c;
    font-weight: bold;
    margin-top: 10px;
}

.loading, .no-recommendations {
    text-align: center;
    padding: 20px;
    color: #666;
}
</style>