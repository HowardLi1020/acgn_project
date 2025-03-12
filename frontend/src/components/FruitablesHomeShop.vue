<script setup>
import { ref, computed } from "vue";
import FruitablesShopCard from "@/components/FruitablesShopCard.vue";

// 商品小卡篩選功能
// 假設從 API 獲取的商品小卡資料，對應FruitablesShopCard.vue
const products = ref([
{
    id: 4,
    imageSrc: "http://127.0.0.1:8000/media/products/aot_mikasa_main.jpg",
    category: "公仔",
    title: "三笠 公仔",
    description:
      "來自《進擊的巨人》的三笠公仔，忠實呈現細節。",
    price: "NT$ 899",
  },
  {
    id: 2,
    imageSrc: "http://127.0.0.1:8000/media/products/knys_tanjiro_main.jpg",
    category: "模型",
    title: "炭治郎 模型",
    description:
      "《鬼滅之刃》炭治郎1/8比例模型，適合收藏。",
    price: "NT$ 1500",
  },
  {
    id: 3,
    imageSrc: "http://127.0.0.1:8000/media/products/op_luffy_keychain.jpg",
    category: "鑰匙圈",
    title: "魯夫 鑰匙圈",
    description:
      "《ONE PIECE》的魯夫Q版鑰匙圈，可愛又實用。",
    price: "NT$ 199",
  },
  {
    id: 6,
    imageSrc: "http://127.0.0.1:8000/media/products/op_zoro_keychain.jpg",
    category: "鑰匙圈",
    title: "索隆 鑰匙圈",
    description:
      "《ONE PIECE》的索隆鑰匙圈，帶有劍士風格。",
    price: "NT$ 249",
  },

  {
    id: 1,
    imageSrc: "http://127.0.0.1:8000/media/products/aot_eren_main.jpg",
    category: "公仔",
    title: "艾倫·葉卡 公仔",
    description:
      "來自《進擊的巨人》的艾倫公仔，精緻還原。",
    price: "NT$ 900",
  },

  {
    id: 5,
    imageSrc: "http://127.0.0.1:8000/media/products/knys_nezuko_main.jpg",
    category: "模型",
    title: "禰豆子 模型",
    description:
      "《鬼滅之刃》禰豆子精緻模型，細節一流。",
    price: "NT$ 1399",
  },

  // {
  //   imageSrc: new URL("@/assets/img/BadTimeStories7.jpg", import.meta.url).href,
  //   category: "模型",
  //   title: "菇狗",
  //   description:
  //     "你貼心的好朋友 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
  //   price: "$5.99 / kg",
  // },
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
    "tab-2": "公仔",
    "tab-3": "模型",
    "tab-4": "鑰匙圈",
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
              <h1>商城中心</h1>
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
                  <span class="text-dark" style="width: 130px">公仔</span>
                  </a>
              </li>
              <li class="nav-item">
                  <a class="d-flex m-2 py-2 bg-light rounded-pill" :class="{ active: currentCategory === 'tab-3' }" @click.prevent="currentCategory = 'tab-3'" href="#tab-3">
                  <span class="text-dark" style="width: 130px">模型</span>
                  </a>
              </li>
              <li class="nav-item">
                  <a class="d-flex m-2 py-2 bg-light rounded-pill" :class="{ active: currentCategory === 'tab-4' }" @click.prevent="currentCategory = 'tab-4'" href="#tab-4">
                  <span class="text-dark" style="width: 130px">鑰匙圈</span>
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
                      :id="product.id"
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
