<script setup>
import { computed } from 'vue';

// 假設從父層傳入的 props
const props = defineProps({
    imageSrc: { type: String, required: true }, // 圖片路徑
    title: { type: String, required: true },    // 商品名稱
    price: { type: String, required: true },    // 現在價格
    originalPrice: { type: String, required: true }, // 原價
    rating: { type: Number, required: true }    // 資料庫回傳的星星數量 (1~5)
});

// 計算星星 class 陣列
const starClasses = computed(() =>
    Array.from({ length: 5 }, (_, index) =>
        index < props.rating ? "fa fa-star text-secondary" : "fa fa-star"
    )
);
</script>

<template>
    <!-- 推薦區小卡 Component (FruitablesShopFeaturedAreaCard.vue)-->
    <div class="d-flex align-items-center justify-content-start 子組件highlight">
        <div class="rounded me-4" style="width: 100px; height: 100px;">
            <img :src="imageSrc" class="img-fluid rounded" alt="Image">
        </div>
        <div>
            <h6 class="mb-2">{{ title }}</h6>
            <!-- 動態渲染星星 -->
            <div class="d-flex mb-2">
                <i v-for="(starClass, index) in starClasses" :key="index" :class="starClass"></i>
            </div>
            <div class="d-flex mb-2">
                <h5 class="fw-bold me-2">{{ price }}</h5>
                <h5 class="text-danger text-decoration-line-through">{{ originalPrice }}</h5>
            </div>
        </div>
    </div>
</template>

<style>
</style>
