<script setup>
import { computed } from 'vue';

// 定義從父元件接收的屬性
const props = defineProps({
  product: {
    type: Object,
    required: true,
    // 預期的物件結構，當沒有傳入值時的預設值
    default: () => ({
      image: '',
      name: '',
      price: 0,
      quantity: 0
    })
  }
})

// 計算總價的計算屬性
// 當 price 或 quantity 改變時會自動重新計算
const totalPrice = computed(() => {
  return props.product.price * props.product.quantity
})
</script>

<template>
<!-- 品項列 component (FruitablesCheckoutTableRow.vue)-->
  <!-- 商品列表的單行元素 -->
  <tr class="子組件highlight">
    <!-- 商品圖片欄位 -->
    <th scope="row">
      <div class="d-flex align-items-center mt-2">
        <!-- 圖片容器：控制圖片的顯示區域 -->
        <div class="product-image-container">
          <img :src="props.product.image" 
               class="img-fluid rounded-circle product-image" 
               :alt="props.product.name">
        </div>
      </div>
    </th>
    <!-- 商品名稱欄位 -->
    <td class="py-5">{{ props.product.name }}</td>
    <!-- 商品單價欄位，使用 toFixed(2) 確保顯示兩位小數 -->
    <td class="py-5">${{ props.product.price.toFixed(2) }}</td>
    <!-- 商品數量欄位 -->
    <td class="py-5">{{ props.product.quantity }}</td>
    <!-- 商品總價欄位，使用計算屬性 totalPrice -->
    <td class="py-5">${{ totalPrice.toFixed(2) }}</td>
  </tr>
</template>

<style scoped>
/* 圖片容器樣式：設定固定大小和圓形裁切 */
.product-image-container {
  width: 90px;
  height: 90px;
  overflow: hidden;  /* 隱藏超出容器的部分 */
  border-radius: 50%;  /* 設定圓形邊框 */
}

/* 圖片本身的樣式 */
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;  /* 確保圖片填滿容器並保持比例，必要時進行裁切 */
}
</style>