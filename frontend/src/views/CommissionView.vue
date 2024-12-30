<script setup>
import SinglePageHeader from '@/components/SinglePageHeader.vue';
// 各自頁面標題下的子連結(標頭在下面template的<SinglePageHeader/>設定)
//isActive: true←為白色不能按；false←為綠色可以按
const SinglePageLinks = [
{ text: '大廳', link: '/', isActive: true },
{ text: '需求', link: '#', isActive: false },
{ text: '接案', link: '#', isActive: false },
{ text: '名片', link: '#', isActive: false },
];
</script>

<template>
    <!-- 各自頁面的標頭(子連結在上面script的SinglePageLinks設定) -->
    <SinglePageHeader 
        title="委託專區" 
        :breadcrumbs="SinglePageLinks" 
        backgroundClass="page-header banner-background"
    />
  <!-- Banner背景圖片從下面CSS的.banner-background自訂 -->
   
</template>

<style>
.banner-background {
  background-image: url("@/assets/img/BadTimeStories_banner.jpg");
}
</style>