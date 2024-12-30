<script setup>
import SinglePageHeader from "@/components/SinglePageHeader.vue";
import FruitablesContactMap from "@/components/FruitablesContactMap.vue";
import FruitablesContactForm from "@/components/FruitablesContactForm.vue";

// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
  { text: "Home 首頁", link: "/", isActive: false },
  { text: "Pages 頁面", link: "#", isActive: false },
  { text: "Contact 聯絡我們", link: "#", isActive: true },
];
</script>

<template>
  <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->
  <SinglePageHeader
    title="Contact 聯絡我們"
    :breadcrumbs="SinglePageLinks"
    backgroundClass="page-header banner-background"
  />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->

  <!-- Contact Start -->
  <div class="container-fluid contact py-5">
    <div class="container py-5">
      <div class="p-5 bg-light rounded">
        <div class="row g-4">
          <div class="col-12">
            <div class="text-center mx-auto" style="max-width: 700px">
              <h1 class="text-primary">Get in touch</h1>
              <p class="mb-4">
                The contact form is currently inactive. Get a functional and
                working contact form with Ajax & PHP in a few minutes. Just copy
                and paste the files, add a little code and you're done.
                <a href="https://htmlcodex.com/contact-form">Download Now</a>.
              </p>
            </div>
          </div>
          <!-- 地圖 Component (FruitablesContactMap.vue)-->
          <FruitablesContactMap />

          <!-- 聯絡表單 Component (FruitablesContactForm.vue)-->
          <FruitablesContactForm />

          <div class="col-lg-5">
            <div class="d-flex p-4 rounded mb-4 bg-white">
              <i class="fas fa-map-marker-alt fa-2x text-primary me-4"></i>
              <div>
                <h4>Address</h4>
                <p class="mb-2">123 Street New York.USA</p>
              </div>
            </div>
            <div class="d-flex p-4 rounded mb-4 bg-white">
              <i class="fas fa-envelope fa-2x text-primary me-4"></i>
              <div>
                <h4>Mail Us</h4>
                <p class="mb-2">info@example.com</p>
              </div>
            </div>
            <div class="d-flex p-4 rounded bg-white">
              <i class="fa fa-phone-alt fa-2x text-primary me-4"></i>
              <div>
                <h4>Telephone</h4>
                <p class="mb-2">(+012) 3456 7890</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Contact End -->
</template>

<style></style>
