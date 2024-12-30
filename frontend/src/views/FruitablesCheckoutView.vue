<script setup>
import { ref } from "vue";
import SinglePageHeader from '@/components/SinglePageHeader.vue';
import FruitablesCheckoutForm from '@/components/FruitablesCheckoutForm.vue';
import FruitablesCheckoutPriceCalculation from '@/components/FruitablesCheckoutPriceCalculation.vue';
import FruitablesCheckoutPaymentMethod from '@/components/FruitablesCheckoutPaymentMethod.vue';
// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
{ text: 'Home 首頁', link: '/', isActive: false },
{ text: 'Pages 頁面', link: '#', isActive: false },
{ text: 'Checkout 結帳', link: '#', isActive: true },
];

// 假設從 API 獲取的商品資料，對應FruitablesCheckoutPriceCalculation.vue內導入的FruitablesCheckoutTableRow.vue
const products = ref([
  {
    id: 1,
    name: "蛤蜊",
    price: 2.99,
    quantity: 3,
    image: new URL("@/assets/img/BadTimeStories_stick6.png", import.meta.url).href,
  },
  {
    id: 2,
    name: "兔菇",
    price: 2.99,
    quantity: 2,
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
</script>

<template>
    <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->
    <SinglePageHeader 
        title="Checkout 結帳" 
        :breadcrumbs="SinglePageLinks" 
        backgroundClass="page-header banner-background"
    />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->
   
      <!-- Checkout Page Start -->
      <div class="container-fluid py-5">
      <div class="container py-5">
          <h1 class="mb-4">Billing details</h1>
          <form action="#">
              <div class="row g-5">
                  <!-- 收件資訊 component (FruitablesCheckoutForm.vue)-->
                  <FruitablesCheckoutForm />
                  <div class="col-md-12 col-lg-6 col-xl-5">
                      <!-- 價格計算 component (FruitablesCheckoutPriceCalculation.vue)-->
                      <FruitablesCheckoutPriceCalculation :products="products" />
                      <!-- 付款方式 component (FruitablesCheckoutPaymentMethod.vue) -->
                      <FruitablesCheckoutPaymentMethod />
                      <div class="row g-4 text-center align-items-center justify-content-center pt-4">
                          <button type="button" class="btn border-secondary py-3 px-4 text-uppercase w-100 text-primary">Place Order</button>
                      </div>
                  </div>
              </div>
          </form>
      </div>
  </div>
  <!-- Checkout Page End -->
</template>

<style>
.banner-background {
  background-image: url("@/assets/img/BadTimeStories_banner.jpg");
}
</style>