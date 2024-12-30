<script setup>
</script>

<template>
  <!-- 側邊廣告 Component (FruitablesShopSideAdvertising.vue)-->
  <!-- 於FruitablesShopView.vue、FruitablesDetailView.vue重複使用 -->
  <div class="col-lg-12 跨View組件highlight">
    <div class="position-relative">
      <img
        src="@/assets/img/banner-fruits.jpg"
        class="img-fluid w-100 rounded"
        alt=""
      />
      <div
        class="position-absolute"
        style="top: 50%; right: 10px; transform: translateY(-50%)"
      >
        <h3 class="text-secondary fw-bold">
          Fresh <br />
          Fruits <br />
          Banner
        </h3>
      </div>
    </div>
  </div>
</template>

<style lang="css" scoped>
</style>
