<script setup>
import { ref, computed } from "vue";
import SinglePageHeader from "@/components/SinglePageHeader.vue";
import FruitablesCartTable from "@/components/FruitablesCartTable.vue";
import FruitablesCartSummary from "@/components/FruitablesCartSummary.vue";
import FruitablesCartCouponInput from "@/components/FruitablesCartCouponInput.vue";
// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
  { text: "Home 首頁", link: "/", isActive: false },
  { text: "Pages 頁面", link: "#", isActive: false },
  { text: "Cart 購物車", link: "#", isActive: true },
];

// 假設從 API 獲取的商品資料，對應FruitablesCartTable.vue內導入的FruitablesCartTableRow.vue
const products = ref([
  {
    id: 1,
    name: "蛤蜊",
    price: 2.99,
    quantity: 1,
    image: new URL("@/assets/img/BadTimeStories_stick6.png", import.meta.url).href,
  },
  {
    id: 2,
    name: "兔菇",
    price: 2.99,
    quantity: 1,
    image: new URL("@/assets/img/BadTimeStories_stick5.png", import.meta.url).href,
  },
  {
    id: 3,
    name: "竹筍",
    price: 2.99,
    quantity: 1,
    image: new URL("@/assets/img/BadTimeStories_stick8.png", import.meta.url).href,
  },
]);

// 更新商品數量的函數
const updateProductQuantity = (productId, newQuantity) => {
  const product = products.value.find((p) => p.id === productId);
  if (product) {
    product.quantity = newQuantity;
  }
};

// 計算總金額的計算屬性
const subtotal = computed(() =>
  products.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
);

// 運費金額從這邊修正(或導入API)
const shipping = 3.0;
</script>

<template>
  <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->
  <SinglePageHeader
    title="Cart 購物車"
    :breadcrumbs="SinglePageLinks"
    backgroundClass="page-header banner-background"
  />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->

  <!-- Cart Page Start -->
  <div class="container-fluid py-5">
    <div class="container py-5">
      <!-- 購物車商品列表 component (FruitablesCartTable.vue)-->
      <FruitablesCartTable
        :products="products"
        @update-quantity="updateProductQuantity"
      />
      <!-- 優惠券輸入 component (FruitablesCartCouponInput.vue)-->
      <FruitablesCartCouponInput />
      <!-- 總計金額 component (FruitablesCartSummary.vue) -->
      <FruitablesCartSummary :subtotal="subtotal" :shipping="shipping" />
      <!-- 運費金額對應上面script裡宣告變數shipping的數字 -->
    </div>
  </div>
  <!-- Cart Page End -->
</template>

<style>
.banner-background {
  background-image: url("@/assets/img/BadTimeStories_banner.jpg");
}
</style>
