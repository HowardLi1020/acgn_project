<script setup>
</script>

<template>
  <!-- 排序選單 Component (FruitablesShopSorting.vue)-->
  <div class="bg-light ps-3 py-3 rounded d-flex justify-content-between mb-4 父組件highlight">
    <label for="fruits">Default Sorting:</label>
    <select
      id="fruits"
      name="fruitlist"
      class="border-0 form-select-sm bg-light me-3"
      form="fruitform"
    >
      <option value="volvo">Nothing</option>
      <option value="saab">Popularity</option>
      <option value="opel">Organic</option>
      <option value="audi">Fantastic</option>
    </select>
  </div>
</template>

<style>
</style>
