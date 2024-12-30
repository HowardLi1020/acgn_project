<script setup>
</script>

<template>
<!-- 價格拉條 Component (FruitablesShopPrice.vue)-->
  <div class="col-lg-12 父組件highlight">
    <div class="mb-3">
        <h4 class="mb-2">Price</h4>
        <input type="range" class="form-range w-100" id="rangeInput" name="rangeInput" min="0" max="500" value="0" oninput="amount.value=rangeInput.value">
        <output id="amount" name="amount" min-velue="0" max-value="500" for="rangeInput">0</output>
    </div>
  </div>
</template>

<style lang="css" scoped>
</style>
