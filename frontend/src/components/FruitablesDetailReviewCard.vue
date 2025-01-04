<script setup>
import { computed } from 'vue';

// 接收來自父層的 props
const props = defineProps({
    avatar: { type: String, required: true },        // 使用者頭像
    date: { type: String, required: true },          // 日期
    name: { type: String, required: true },          // 使用者名稱
    rating: { type: Number, required: true },        // 評分 (1~5)
    review: { type: String, required: true }         // 評論文字
});

// 計算星星 class 陣列
const starClasses = computed(() =>
    Array.from({ length: 5 }, (_, index) =>
        index < props.rating ? "fa fa-star text-secondary" : "fa fa-star"
    )
);
</script>

<template>
    <!-- 商品評論 Component (FruitablesDetailReviewCard.vue)-->
    <div class="d-flex 子組件highlight">
        <!-- 使用者頭像 -->
        <div class="avatar-container">
            <img :src="avatar" class="img-fluid rounded-circle p-3" alt="User Avatar">
        </div>
        <!-- 評論內容區塊 -->
        <div class="review-content">
            <!-- 日期 -->
            <p class="date-text mb-2">{{ date }}</p>
            <!-- 名稱和評分區塊 -->
            <div class="d-flex justify-content-between">
                <h5 class="mb-0">{{ name }}</h5>
                <!-- 動態星星 -->
                <div class=" d-flex mb-3">
                    <i v-for="(starClass, index) in starClasses" :key="index" :class="starClass"></i>
                </div>
            </div>
            <!-- 評論內容 -->
            <p class="review-text">{{ review }}</p>
        </div>
    </div>
</template>

<style scoped>
.avatar-container {
    width: 100px;
    min-width: 100px;
    height: 100px;
}

.avatar-container img {
    width: 100px;
    height: 100px;
    object-fit: cover;
}

.review-content {
    flex: 1;
}

.date-text {
    font-size: 14px;
    color: #6c757d;
}

.review-text {
    color: #666;
}
</style>
