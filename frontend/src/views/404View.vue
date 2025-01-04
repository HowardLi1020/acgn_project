<script setup>
import SinglePageHeader from "@/components/SinglePageHeader.vue";
// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
  { text: "Home 首頁", link: "/", isActive: false },
  { text: "Pages 頁面", link: "#", isActive: false },
  { text: "404 找不到", link: "#", isActive: true },
];

// 事件，回到頂部
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}
</script>

<template>
  <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->
  <SinglePageHeader
    title="404 找不到"
    :breadcrumbs="SinglePageLinks"
    backgroundClass="page-header banner-background"
  />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->

  <!-- 404 Start -->
  <div class="container-fluid py-5">
    <div class="container py-5 text-center">
      <div class="row justify-content-center">
        <div class="col-lg-6">
          <i class="bi bi-exclamation-triangle display-1 text-secondary"></i>
          <h1 class="display-1">404</h1>
          <h1 class="mb-4">Page Not Found</h1>
          <p class="mb-4">
            We're sorry, the page you have looked for does not exist in our
            website! Maybe go to our home page or try to use a search?
          </p>
          <button
            class="btn border-secondary rounded-pill py-3 px-5 me-3"
            @click="$router.go(-1)"
          >
            回上一頁
          </button>
          <router-link
            to="/"
            class="btn border-secondary rounded-pill py-3 px-5"
            @click="scrollToTop"
            >回首頁</router-link
          >
        </div>
      </div>
    </div>
  </div>
  <!-- 404 End -->
</template>

<style>
.banner-background {
  background-image: url("@/assets/img/BadTimeStories_banner.jpg");
}
</style>
