<script setup>
import { ref, onMounted } from "vue";
import { storeAPI } from "../../utils/api"; // 確保您有這個 API 工具
import { useRouter } from "vue-router";
import Swal from "sweetalert2"; // 引入 Sweetalert2

const router = useRouter();
const products = ref([]);
const loading = ref(true);
const error = ref(null);
const apiUrl = import.meta.env.VITE_APIURL; // 使用環境變量

// 獲取用戶創建的產品
const fetchUserProducts = async () => {
    try {
        loading.value = true;
        error.value = null;

        const response = await storeAPI.getUserProducts();
        products.value = response.products || [];
    } catch (err) {
        console.error("獲取產品失敗:", err);
        error.value = err.message || "獲取產品失敗";
        
        if (err.message.includes("未登入") || err.message.includes("登入已過期")) {
            Swal.fire({
                title: '請先登入',
                text: '您需要登入才能查看您的產品',
                icon: 'warning',
                confirmButtonText: '前往登入'
            }).then((result) => {
                if (result.isConfirmed) {
                    router.push('/login');
                }
            });
        }
    } finally {
        loading.value = false;
    }
};

// 編輯商品
const handleEdit = (productId) => {
    router.push({
        name: 'EditProduct',
        params: { productId: productId }
    });
};

// 刪除商品
const handleDelete = async (productId) => {
    try {
        const result = await Swal.fire({
            title: "確定要刪除此商品嗎？",
            text: "此操作不可恢復！",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "確定刪除",
            cancelButtonText: "取消",
        });

        if (result.isConfirmed) {
            await storeAPI.deleteProduct(productId);
            await fetchUserProducts();

            await Swal.fire({
                title: "已刪除！",
                text: "商品已成功刪除。",
                icon: "success",
                timer: 1500,
            });
        }
    } catch (err) {
        console.error("刪除商品失敗:", err);
        
        if (err.message.includes('登入已過期')) {
            await Swal.fire({
                title: "錯誤",
                text: err.message,
                icon: "error",
                confirmButtonText: "前往登入"
            });
            router.push('/login');
            return;
        }

        await Swal.fire({
            title: "錯誤",
            text: err.message || "刪除商品失敗，請稍後再試",
            icon: "error",
        });
    }
};

// 返回商店頁面
const backToStore = () => {
  router.push('/store');
};

onMounted(() => {
    fetchUserProducts();
});
</script>

<template>
    <div class="my-products">
        <h1>我的產品</h1>
        <button @click="backToStore" class="back-button">返回商店</button>
        <div v-if="loading" class="loading">加載中...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <!-- 商品列表 -->
        <div v-else class="products-grid">
            <div v-if="products.length === 0" class="no-products">暫無商品</div>
            <div
                v-else
                v-for="product in products"
                :key="product.product_id"
                class="product-card"
            >
                <!-- 商品圖片 -->
                <img
                    :src="
                        product.image_url
                            ? `${apiUrl}/media/${product.image_url}`
                            : '/placeholder.png'
                    "
                    :alt="product.product_name"
                    @error="$event.target.src = '/placeholder.png'"
                />

                <!-- 商品信息 -->
                <div class="product-info">
                    <h3>{{ product.product_name }}</h3>
                    <p class="price">NT$ {{ Math.floor(product.price) }}</p>
                </div>

                <!-- 操作按鈕 -->
                <div class="product-actions">
                    <button
                        class="edit-btn"
                        @click.prevent="handleEdit(product.product_id)"
                    >
                        編輯
                    </button>
                    <button
                        class="delete-btn"
                        @click.prevent="handleDelete(product.product_id)"
                    >
                        刪除
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.my-products {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    margin-top: 150px;
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    padding: 20px 0;
}

.product-card {
    background-color: #2a2a2a;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease;
    text-decoration: none;
    color: inherit;
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
    font-size: 1.1em;
    color: #ffffff;
}

.price {
    margin: 10px 0 0;
    color: #00ff00;
    font-weight: bold;
}

/* 新增按鈕樣式 */
.product-actions {
    display: flex;
    justify-content: space-between;
    padding: 10px 15px;
    gap: 10px;
}

.edit-btn,
.delete-btn {
    flex: 1;
    padding: 8px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s;
}

.edit-btn {
    background-color: #4caf50;
    color: white;
}

.edit-btn:hover {
    background-color: #45a049;
}

.delete-btn {
    background-color: #f44336;
    color: white;
}

.delete-btn:hover {
    background-color: #da190b;
}

.no-products {
    text-align: center;
    grid-column: 1 / -1;
    padding: 20px;
    color: #666;
}

.error {
    color: red;
    text-align: center;
    padding: 20px;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #666;
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
