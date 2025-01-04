<script setup>
import FruitablesShopFeaturedAreaCard from '@/components/FruitablesShopFeaturedAreaCard.vue';
import FruitablesShopSideAdvertising from '@/components/FruitablesShopSideAdvertising.vue';
defineProps({
  featuredProducts: {
    type: Array,
    required: true
  }
});
</script>

<template>
  <!-- 演算法推薦區 Component (FruitablesShopFeaturedArea.vue)-->
  <!-- 於FruitablesShopView.vue、FruitablesDetailView.vue重複使用 -->
  <div class="跨View組件highlight">
    <div class="col-lg-12">
      <h4 class="mb-4">Featured products 演算法推薦區</h4>
      <!-- 推薦區小卡 Component (FruitablesShopFeaturedAreaCard.vue)-->
      <FruitablesShopFeaturedAreaCard
        v-for="(product, index) in featuredProducts"
        :key="index"
        :imageSrc="product.imageSrc"
        :title="product.title"
        :price="product.price"
        :originalPrice="product.originalPrice"
        :rating="product.rating"
      />
    </div>
    <div class="d-flex justify-content-center my-4">
        <a href="#"
          class="btn border border-secondary px-4 py-3 rounded-pill text-primary w-100"
          >Vew More</a>
      </div>
    <!-- 側邊廣告 Component (FruitablesShopSideAdvertising.vue)-->
    <FruitablesShopSideAdvertising />
</div>
</template>

<style lang="css" scoped>
</style>
