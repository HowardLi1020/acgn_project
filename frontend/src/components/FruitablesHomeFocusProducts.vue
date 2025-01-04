<script setup>
import { ref } from 'vue';
import FruitablesHomeFocusProductsCard1 from "@/components/FruitablesHomeFocusProductsCard1.vue";
import FruitablesHomeFocusProductsCard2 from "@/components/FruitablesHomeFocusProductsCard2.vue";

// 假設從 API 獲取的商品資料，對應FruitablesHomeFocusProductsCard1.vue
const products1 = ref([
  {
    id: 1,
    name: "烤雞",
    image: new URL("@/assets/img/BadTimeStories_stick4.png", import.meta.url).href,
    rating: 4,
    price: "3.12",
  },
  {
    id: 2,
    name: "兔菇",
    image: new URL("@/assets/img/BadTimeStories_stick5.png", import.meta.url).href,
    rating: 5,
    price: "2.50",
  },
  {
    id: 3,
    name: "人生",
    image: new URL("@/assets/img/BadTimeStories_stick7.png", import.meta.url).href,
    rating: 1,
    price: "2.50",
  },
  {
    id: 4,
    name: "蛤蜊",
    image: new URL("@/assets/img/BadTimeStories_stick6.png", import.meta.url).href,
    rating: 0,
    price: "2.50",
  },
  {
    id: 5,
    name: "烏骨雞",
    image: new URL("@/assets/img/BadTimeStories_stick3.png", import.meta.url).href,
    rating: 5,
    price: "5.57",
  },
  {
    id: 6,
    name: "竹筍",
    image: new URL("@/assets/img/BadTimeStories_stick8.png", import.meta.url).href,
    rating: 4,
    price: "7.00",
  },
]);

// 假設從 API 獲取的商品資料，對應FruitablesHomeFocusProductsCard2.vue
const products2 = ref([
  {
    id: 1,
    name: "香蕉",
    image: new URL("@/assets/img/BadTimeStories4.jpg", import.meta.url).href,
    rating: 4,
    price: "3.12",
  },
  {
    id: 2,
    name: "鳳梨",
    image: new URL("@/assets/img/BadTimeStories6.jpg", import.meta.url).href,
    rating: 4,
    price: "2.50",
  },
  {
    id: 3,
    name: "西瓜",
    image: new URL("@/assets/img/BadTimeStories1.jpg", import.meta.url).href,
    rating: 5,
    price: "8.888888",
  },
  {
    id: 4,
    name: "菇狗",
    image: new URL("@/assets/img/BadTimeStories7.jpg", import.meta.url).href,
    rating: 3,
    price: "2.50",
  },
]);
</script>

<template>
<!-- 焦點商品 Component (FruitablesHomeFocusProducts.vue)-->
    <!-- Bestsaler Product Start -->
    <div class="container-fluid py-5 父組件highlight">
        <div class="container py-5">
            <div class="text-center mx-auto mb-5" style="max-width: 700px;">
                <h1 class="display-4">Bestseller Products</h1>
                <p>Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable.</p>
            </div>
            <div class="row g-4">
                <!-- 白底小卡 component (FruitablesHomeFocusProductsCard1.vue)-->
                <FruitablesHomeFocusProductsCard1
                    v-for="product in products1"
                    :key="product.id"
                    :product="product"
                />

                <!-- 無背景小卡 component (FruitablesHomeFocusProductsCard2.vue)-->
                <FruitablesHomeFocusProductsCard2
                    v-for="product in products2"
                    :key="product.id"
                    :product="product"
                />                
            </div>
        </div>
    </div>
    <!-- Bestsaler Product End -->
</template>

<style lang="css" scoped>

</style>