<script setup>
import { ref, computed } from "vue";
import FruitablesShopCard from "@/components/FruitablesShopCard.vue";

// 商品小卡篩選功能
// 假設從 API 獲取的商品小卡資料，對應FruitablesShopCard.vue
const products = ref([
  {
    imageSrc: new URL("@/assets/img/BadTimeStories1.jpg", import.meta.url).href,
    category: "水果",
    title: "西瓜",
    description:
      "你是在拍三... Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$2.99 / kg",
  },
  {
    imageSrc: new URL("@/assets/img/BadTimeStories3.jpg", import.meta.url).href,
    category: "蔬菜",
    title: "洋蔥",
    description:
      "食材沒地方放可以先放小雞汁頭上 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$1.49 / kg",
  },
  {
    imageSrc: new URL("@/assets/img/BadTimeStories4.jpg", import.meta.url).href,
    category: "水果",
    title: "香蕉",
    description:
      "你看你媽媽她有三顆眼睛啦 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },
  {
    imageSrc: new URL("@/assets/img/BadTimeStories5.jpg", import.meta.url).href,
    category: "水果",
    title: "蘋果",
    description:
      "下面的好像比較漂亮耶！ Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },

  {
    imageSrc: new URL("@/assets/img/BadTimeStories6.jpg", import.meta.url).href,
    category: "水果",
    title: "鳳梨",
    description:
      "你吼狗姆茲咖系 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },
  {
    imageSrc: new URL("@/assets/img/BadTimeStories2.jpg", import.meta.url).href,
    category: "生鮮",
    title: "蛤蜊",
    description:
      "痾痾痾痾痾痾我要**你 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },
  {
    imageSrc: new URL("@/assets/img/BadTimeStories7.jpg", import.meta.url).href,
    category: "蔬菜",
    title: "菇狗",
    description:
      "你貼心的好朋友 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },
]);

// 添加當前選中的分類狀態
const currentCategory = ref("all");

// 根據分類篩選商品的計算屬性
const filteredProducts = computed(() => {
  if (currentCategory.value === "all") {
    return products.value;
  }
  //對應上面宣告變數products的category有的分類
  const categoryMap = {
    "tab-2": "蔬菜",
    "tab-3": "水果",
    "tab-4": "生鮮",
  };

  return products.value.filter(
    (product) => product.category === categoryMap[currentCategory.value]
  );
});
</script>

<template>
<!-- 簡易商店 Component (FruitablesHomeShop.vue)-->
  <!-- Fruits Shop Start-->
  <div class="container-fluid fruite py-5 父組件highlight">
      <div class="container py-5">
      <div class="tab-class text-center">
          <div class="row g-4">
          <div class="col-lg-4 text-start">
              <h1>Our Organic Products 我們的有機產品</h1>
          </div>
          <div class="col-lg-8 text-end">
              <ul class="nav nav-pills d-inline-flex text-center mb-5">
              <li class="nav-item">
                  <a class="d-flex m-2 py-2 bg-light rounded-pill" :class="{ active: currentCategory === 'all' }" @click.prevent="currentCategory = 'all'" href="#tab-1">
                  <span class="text-dark" style="width: 130px">所有產品</span>
                  </a>
              </li>
              <li class="nav-item">
                  <a class="d-flex py-2 m-2 bg-light rounded-pill" :class="{ active: currentCategory === 'tab-2' }" @click.prevent="currentCategory = 'tab-2'" href="#tab-2">
                  <span class="text-dark" style="width: 130px">蔬菜</span>
                  </a>
              </li>
              <li class="nav-item">
                  <a class="d-flex m-2 py-2 bg-light rounded-pill" :class="{ active: currentCategory === 'tab-3' }" @click.prevent="currentCategory = 'tab-3'" href="#tab-3">
                  <span class="text-dark" style="width: 130px">水果</span>
                  </a>
              </li>
              <li class="nav-item">
                  <a class="d-flex m-2 py-2 bg-light rounded-pill" :class="{ active: currentCategory === 'tab-4' }" @click.prevent="currentCategory = 'tab-4'" href="#tab-4">
                  <span class="text-dark" style="width: 130px">生鮮</span>
                  </a>
              </li>
              </ul>
          </div>
          </div>
          <div class="tab-content">
          <div id="tab-1" class="tab-pane fade show p-0 active">
              <div class="row g-4">
              <div class="col-lg-12">
                  <div class="row g-4">
                  <!-- 動態生成商品小卡 Component (FruitablesShopCard.vue)-->
                  <FruitablesShopCard
                      class="col-xl-3"
                      v-for="(product, index) in filteredProducts"
                      :key="index"
                      :imageSrc="product.imageSrc"
                      :category="product.category"
                      :title="product.title"
                      :description="product.description"
                      :price="product.price"
                  />
                  </div>
              </div>
              </div>
          </div>
          </div>
      </div>
      </div>
  </div>
  <!-- Fruits Shop End-->
</template>

<style lang="css" scoped>
</style>
