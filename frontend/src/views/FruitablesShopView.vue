<script setup>
import { ref, computed } from "vue";
import SinglePageHeader from "@/components/SinglePageHeader.vue";
import FruitablesShopSearch from "@/components/FruitablesShopSearch.vue";
import FruitablesShopSorting from "@/components/FruitablesShopSorting.vue";
import FruitablesShopCategories from "@/components/FruitablesShopCategories.vue";
import FruitablesShopPrice from "@/components/FruitablesShopPrice.vue";
import FruitablesShopAdditional from "@/components/FruitablesShopAdditional.vue";
import FruitablesShopFeaturedArea from "@/components/FruitablesShopFeaturedArea.vue";
import FruitablesShopCard from "@/components/FruitablesShopCard.vue";

// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
  { text: "Home 首頁", link: "/", isActive: false },
  { text: "Pages 頁面", link: "#", isActive: false },
  { text: "Shop 商店", link: "/shop", isActive: true },
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
]);

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
    imageSrc: new URL("@/assets/img/BadTimeStories2.jpg", import.meta.url).href,
    category: "生鮮",
    title: "蛤蜊",
    description:
      "痾痾痾痾痾痾我要**你 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
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
  },{
    imageSrc: new URL("@/assets/img/BadTimeStories3.jpg", import.meta.url).href,
    category: "蔬菜",
    title: "洋蔥",
    description:
      "食材沒地方放可以先放小雞汁頭上 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },
  {
    imageSrc: new URL("@/assets/img/BadTimeStories1.jpg", import.meta.url).href,
    category: "水果",
    title: "西瓜",
    description:
      "你是在拍三... Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
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
  },{
    imageSrc: new URL("@/assets/img/BadTimeStories4.jpg", import.meta.url).href,
    category: "水果",
    title: "香蕉",
    description:
      "你看你媽媽她有三顆眼睛啦 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },{
    imageSrc: new URL("@/assets/img/BadTimeStories2.jpg", import.meta.url).href,
    category: "生鮮",
    title: "蛤蜊",
    description:
      "痾痾痾痾痾痾我要**你 Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },{
    imageSrc: new URL("@/assets/img/BadTimeStories5.jpg", import.meta.url).href,
    category: "水果",
    title: "蘋果",
    description:
      "下面的好像比較漂亮耶！ Lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod te incididunt",
    price: "$5.99 / kg",
  },
]);
// 分頁相關的邏輯
const currentPage = ref(1);
const itemsPerPage = 6; // 每頁顯示的商品數量
const totalPages = computed(() => Math.ceil(products.value.length / itemsPerPage)); // 計算總頁數

// 計算當前頁面應該顯示的商品
const displayedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return products.value.slice(start, end);
});
// 頁面切換函數
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};
// 上一頁
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};
// 下一頁
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

</script>

<template>
  <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->

  <SinglePageHeader
    title="Shop 商店"
    :breadcrumbs="SinglePageLinks"
    backgroundClass="page-header banner-background"
  />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->

  <!-- Fruits Shop Start-->
  <div class="container-fluid fruite py-5">
    <div class="container py-5">
      <h1 class="mb-4">Fresh fruits shop</h1>
      <div class="row g-4">
        <div class="col-lg-12">
          <div class="row g-4">
            <div class="col-xl-3">
              <!-- 搜尋Bar Component (FruitablesShopSearch.vue)-->
              <FruitablesShopSearch />
            </div>
            <div class="col-6"></div>
            <div class="col-xl-3">
              <!-- 排序選單 Component (FruitablesShopSorting.vue)-->
              <FruitablesShopSorting />
            </div>
          </div>
          <div class="row g-4">
            <div class="col-lg-3">
              <div class="row g-4">
                <!-- 分類數量 Component (FruitablesShopCategories.vue)-->
                <FruitablesShopCategories />
                <!-- 價格拉條 Component (FruitablesShopPrice.vue)-->
                <FruitablesShopPrice />
                <!-- 分類標籤 Component (FruitablesShopAdditional.vue)-->
                <FruitablesShopAdditional />
                <!-- 演算法推薦區 Component (FruitablesShopFeaturedArea.vue)-->
                <FruitablesShopFeaturedArea :featuredProducts="featuredProducts" />
              </div>
            </div>
            <div class="col-lg-9">
              <div class="row g-4 justify-content-center">
                <!-- 動態生成商品小卡 Component (FruitablesShopCard.vue)-->
                <FruitablesShopCard
                  class="col-xl-4"
                  v-for="(product, index) in displayedProducts"
                  :key="index"
                  :imageSrc="product.imageSrc"
                  :category="product.category"
                  :title="product.title"
                  :description="product.description"
                  :price="product.price"
                />
                <div class="col-12">
                  <div class="pagination d-flex justify-content-center mt-5">
                    <a href="#" class="rounded" @click.prevent="prevPage">&laquo;</a>
                    <template v-for="page in totalPages" :key="page">
                      <a
                        href="#"
                        class="rounded"
                        :class="{ active: currentPage === page }"
                        @click.prevent="changePage(page)"
                      >
                        {{ page }}
                      </a>
                    </template>
                    <a href="#" class="rounded" @click.prevent="nextPage">&raquo;</a>
                  </div>
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

<style>
.banner-background {
  background-image: url("@/assets/img/BadTimeStories_banner.jpg");
}
</style>
