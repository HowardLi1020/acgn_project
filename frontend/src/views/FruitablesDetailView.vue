<script setup>
import { ref } from 'vue';
import SinglePageHeader from '@/components/SinglePageHeader.vue';
import FruitablesDetailProducts from '@/components/FruitablesDetailProducts.vue';
import FruitablesDetailDescription from '@/components/FruitablesDetailDescription.vue';
import FruitablesDetailReply from '@/components/FruitablesDetailReply.vue';
import FruitablesShopSearch from '@/components/FruitablesShopSearch.vue';
import FruitablesShopCategories from '@/components/FruitablesShopCategories.vue';
import FruitablesShopFeaturedArea from '@/components/FruitablesShopFeaturedArea.vue';
import FruitablesHomeRollingShop from '@/components/FruitablesHomeRollingShop.vue';
// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
{ text: 'Home 首頁', link: '/', isActive: false },
{ text: 'Pages 頁面', link: '#', isActive: false },
{ text: 'Detail 商品詳細', link: '#', isActive: true },
];

// 假設從 API 獲取的演算法推薦資料，對應FruitablesShopFeaturedArea.vue內導入的FruitablesShopFeaturedComponent.vue
const featuredProducts = ref([
    {
        imageSrc: new URL("@/assets/img/BadTimeStories_stick1.png", import.meta.url).href,
        title: '小雞汁',
        price: '2.99 $',
        originalPrice: '4.11 $',
        rating: 3
    },
    {
        imageSrc: new URL("@/assets/img/BadTimeStories_stick2.png", import.meta.url).href,
        title: '炸雞',
        price: '3.49 $',
        originalPrice: '5.00 $',
        rating: 4
    },
    {
        imageSrc: new URL("@/assets/img/BadTimeStories_stick3.png", import.meta.url).href,
        title: '烏骨雞',
        price: '2.99 $',
        originalPrice: '4.11 $',
        rating: 3
    },
    {
        imageSrc: new URL("@/assets/img/BadTimeStories_stick4.png", import.meta.url).href,
        title: '系勒烤',
        price: '2.99 $',
        originalPrice: '4.11 $',
        rating: 3
    },
    {
        imageSrc: new URL("@/assets/img/BadTimeStories_stick5.png", import.meta.url).href,
        title: '兔菇',
        price: '3.49 $',
        originalPrice: '5.00 $',
        rating: 5
    },
    {
        imageSrc: new URL("@/assets/img/BadTimeStories_stick6.png", import.meta.url).href,
        title: '蛤蜊',
        price: '2.99 $',
        originalPrice: '4.11 $',
        rating: 0
    },
]);

</script>

<template>
  <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->
  <SinglePageHeader 
      title="Detail 商品詳細" 
      :breadcrumbs="SinglePageLinks" 
      backgroundClass="page-header banner-background"
  />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->

  <!-- Single Product Start -->
  <div class="container-fluid py-5 mt-5">
      <div class="container py-5">
          <div class="row g-4 mb-5">
              <div class="col-lg-8 col-xl-9">
                  <div class="row g-4">
                      <!-- 商品簡介 Component (FruitablesDetailProducts.vue)-->
                      <FruitablesDetailProducts />
                      <!-- 商品描述 Component (FruitablesDetailDescription.vue)-->
                      <FruitablesDetailDescription />
                      <!-- 發送評論 Component (FruitablesDetailReply.vue)-->
                      <FruitablesDetailReply />
                  </div>
              </div>
              <div class="col-lg-4 col-xl-3">
                  <div class="row g-4 fruite">
                      <div class="col-lg-12">
                          <!-- 搜尋商品 Component (FruitablesShopSearch.vue)-->
                          <FruitablesShopSearch />
                          <!-- 商品分類 Component (FruitablesShopCategories.vue)-->
                          <FruitablesShopCategories />    
                      </div>
                      <!-- 演算法推薦區 Component (FruitablesShopFeaturedArea.vue)-->
                      <FruitablesShopFeaturedArea :featuredProducts="featuredProducts" />
                      
                  </div>
              </div>
          </div>
          <!-- 商品輪播 Component (FruitablesHomeRollingShop.vue) -->
          <FruitablesHomeRollingShop />
      </div>
  </div>
  <!-- Single Product End -->
</template>

<style>
.banner-background {
  background-image: url("@/assets/img/BadTimeStories_banner.jpg");
}
</style>