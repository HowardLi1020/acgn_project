<script setup>
import FruitablesCartTableRow from '@/components/FruitablesCartTableRow.vue';
// 定義組件的輸入屬性
const props = defineProps({
    products: {
        type: Array,
        required: true
    }
});
// 定義可觸發的事件
const emit = defineEmits(['update-quantity']);
// 處理數量更新的事件處理器
const handleQuantityUpdate = (productId, newQuantity) => {
    emit('update-quantity', productId, newQuantity);
};
</script>

<template>
  <!-- 購物車商品列表 component (FruitablesCartTable.vue)-->
  <div class="table-responsive 父組件highlight">
    <table class="table">
        <thead>
            <tr>
                <!-- 使用固定寬度確保布局穩定 -->
                <th scope="col" style="width: 120px; min-width: 120px;">Products 圖片</th>
                <th scope="col" style="width: 200px; min-width: 200px;">Name 品名</th>
                <th scope="col" style="width: 120px; min-width: 120px;">Price 單價</th>
                <th scope="col" style="width: 150px; min-width: 150px;">Quantity 數量</th>
                <th scope="col" style="width: 120px; min-width: 120px;">Total 總計</th>
                <th scope="col" style="width: 100px; min-width: 100px;">Handle</th>
            </tr>
        </thead>
        <tbody>
            <!-- 商品列 component (FruitablesCartTableRow.vue)-->
            <FruitablesCartTableRow
                v-for="product in products"
                :key="product.id"
                :product="product"
                @update-quantity="handleQuantityUpdate"
                class="子組件highlight"
            />
        </tbody>
    </table>
  </div>
</template>

<style>
</style>
