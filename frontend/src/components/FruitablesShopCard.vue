<script setup>
// 定義組件的 props，接收外部傳入的資料
defineProps({
    imageSrc: { type: String, required: true }, // 圖片路徑
    category: { type: String, required: true }, // 類別
    title: { type: String, required: true },    // 標題
    description: { type: String, required: true }, // 描述
    price: { type: String, required: true }     // 價格
});
</script>

<template>
<!-- 動態生成商品小卡 Component (FruitablesShopCard.vue)-->
 <!-- 於FruitablesShopView.vue、FruitablesHomeView.vue重複使用 -->
    <div class="col-md-6 col-lg-6 跨View組件highlight">
        <div class="rounded position-relative fruite-item">
            <!-- 動態圖片 -->
            <div class="fruite-img">
                <img :src="imageSrc" class="img-fluid w-100 rounded-top" alt="Product Image">
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
                    <a href="#" class="btn border border-secondary rounded-pill px-3 text-primary"><i class="fa fa-shopping-bag me-2 text-primary"></i> Add to cart</a>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
</style>
