<script setup>
// 定義接收的屬性（props）
// props: 接收外部傳入的標題、連結列表和背景樣式等數據
defineProps({
  title: {
    type: String,
    required: true,
  },
  breadcrumbs: {
    type: Array,
    required: true,
    default: () => [],
  },
  backgroundClass: {
    type: String,
    default: 'page-header-default', // 預設樣式
  },
});
</script>

<template>
  <!-- Single Page Header start -->
  <div :class="['container-fluid', 'py-5', backgroundClass]">
    <h1 class="text-center text-white display-6">{{ title }}</h1>
    <ol class="breadcrumb justify-content-center mb-0">
      <li 
        v-for="(breadcrumb, index) in breadcrumbs" 
        :key="index" 
        :class="['breadcrumb-item', breadcrumb.isActive ? 'active text-white' : '']">
        <a v-if="!breadcrumb.isActive" :href="breadcrumb.link">{{ breadcrumb.text }}</a>
        <span v-else>{{ breadcrumb.text }}</span>
      </li>
    </ol>
  </div>
  <!-- End -->
</template>

<style>
.page-header-default {
  background-color: #333;
}
</style>
