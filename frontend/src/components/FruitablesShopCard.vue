<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { cartAPI } from '@/utils/api';
import Swal from 'sweetalert2';

const router = useRouter();
const userStore = useUserStore();

// 定義組件的 props，接收外部傳入的資料
const props = defineProps({
    id: { type: Number, required: true },     // 商品 ID
    imageSrc: { type: String, required: true }, // 圖片路徑
    category: { type: String, required: true }, // 類別
    title: { type: String, required: true },    // 標題
    description: { type: String, required: true }, // 描述
    price: { type: String, required: true }     // 價格
});

// 處理加入購物車
const handleAddToCart = async () => {
    // 檢查用戶是否登入
    if (!userStore.isLoggedIn) {
        // 使用 Sweetalert2 提示用戶
        Swal.fire({
            title: '尚未登入',
            text: '請先登入後再加入購物車',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '前往登入',
            cancelButtonText: '取消'
        }).then((result) => {
            if (result.isConfirmed) {
                router.push('/login');
            }
        });
        
        return;
    }

    try {
        // 已登入，加入購物車
        await cartAPI.addCartItem({
            product_name: props.title,
            price: parseFloat(props.price.replace('NT$ ', '')), // 轉換為數字
            quantity: 1,
            product_id: props.id
        });
        
        // 使用 Sweetalert2 顯示成功訊息
        Swal.fire({
            title: '成功！',
            text: '商品已加入購物車',
            icon: 'success',
            timer: 1500,
            showConfirmButton: false
        });
    } catch (error) {
        console.error('加入購物車失敗:', error);
        Swal.fire({
            title: '錯誤',
            text: '加入購物車失敗，請稍後再試',
            icon: 'error',
            confirmButtonText: '確定'
        });
    }
};
</script>

<template>
<!-- 動態生成商品小卡 Component (FruitablesShopCard.vue)-->
 <!-- 於FruitablesShopView.vue、FruitablesHomeView.vue重複使用 -->
    <div class="col-md-6 col-lg-6 跨View組件highlight">
        <div class="rounded position-relative fruite-item">
            <!-- 動態圖片 -->
            <div class="fruite-img">
                <img :src="imageSrc" class="img-fluid w-100 rounded-top product-image" alt="Product Image">
            </div>
            <!-- 動態類別 -->
            <div class="text-white bg-secondary px-3 py-1 rounded position-absolute" style="top: 10px; left: 10px;">{{ category }}</div>
            <div class="p-4 border border-secondary border-top-0 rounded-bottom">
                <!-- 動態標題 -->
                <h4>{{ title }}</h4>
                <!-- 動態描述 -->
                <p>{{ description }}</p>
                <div class="d-flex justify-content-between flex-lg-wrap">
                    <!-- 動態價格 -->
                    <p class="text-dark fs-5 fw-bold mb-0">{{ price }}</p>
                    <button @click="handleAddToCart" class="btn border border-secondary rounded-pill px-3 text-primary">
                        <i class="fa fa-shopping-bag me-2 text-primary"></i> Add to cart
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.product-image {
    width: 304px !important;
    height: 304px !important;
    object-fit: cover; /* 保持圖片比例並填滿容器 */
}

.fruite-img {
    width: 304px;
    height: 304px;
    overflow: hidden;
}

.btn {
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn:hover {
    background-color: #007bff;
    color: white !important;
}

.btn:hover i {
    color: white !important;
}
</style>
