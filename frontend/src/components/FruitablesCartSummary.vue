<script setup>
import { computed } from 'vue';

// 定義組件的輸入屬性
const props = defineProps({
    subtotal: {
        type: Number,
        required: true
    },
    shipping: {
        type: Number,
        required: true
    }
});

// 計算購物車總金額（小計 + 運費）
const total = computed(() => {
    return props.subtotal + props.shipping;
});
</script>

<template>
<!-- 總計金額 component (FruitablesCartSummary.vue)-->
    <!-- 購物車總計區塊 -->
    <div class="row g-4 justify-content-end 父組件highlight">
        <div class="col-8"></div>
        <!-- 響應式布局設定 -->
        <div class="col-sm-8 col-md-7 col-lg-6 col-xl-4">
            <div class="bg-light rounded">
                <div class="p-4">
                    <h1 class="display-6 mb-4">Cart <span class="fw-normal">Total 購物車總計</span></h1>
                    <!-- 小計區塊 -->
                    <div class="d-flex justify-content-between mb-4">
                        <h5 class="mb-0 me-4">Subtotal 小計：</h5>
                        <p class="mb-0">${{ subtotal.toFixed(2) }}</p>
                    </div>
                    <!-- 運費區塊 -->
                    <div class="d-flex justify-content-between">
                        <h5 class="mb-0 me-4">Shipping</h5>
                        <div class="">
                            <!-- 對應FruitablesCartView.vue裡script宣告變數shipping的運費 -->
                            <p class="mb-0">Flat rate 固定運費: ${{ shipping.toFixed(2) }}</p>
                        </div>
                    </div>
                    <p class="mb-0 text-end">Shipping to Ukraine.</p>
                </div>
                <!-- 總計區塊 -->
                <div class="py-4 mb-4 border-top border-bottom d-flex justify-content-between">
                    <h5 class="mb-0 ps-4 me-4">Total 總計</h5>
                    <p class="mb-0 pe-4">${{ total.toFixed(2) }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
</style>