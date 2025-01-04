<script setup>
</script>

<template>
  <!-- 搜尋Bar Component (FruitablesShopSearch.vue)-->
  <!-- 於FruitablesShopView.vue、FruitablesDetailView.vue重複使用 -->
    <div class="input-group w-100 mx-auto d-flex mb-4 跨View組件highlight">
      <input
        type="search"
        class="form-control p-3"
        placeholder="keywords"
        aria-describedby="search-icon-1"
      />
      <span id="search-icon-1" class="input-group-text p-3"
        ><i class="fa fa-search"></i
      ></span>
    </div>
</template>

<style lang="css" scoped>
</style>
