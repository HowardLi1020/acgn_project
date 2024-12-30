<script setup>
import NavbarComponent from '@/components/NavbarComponent.vue';
import FooterComponent from '@/components/FooterComponent.vue';
</script>

<template>
    <NavbarComponent />
    <RouterView></RouterView>
    <FooterComponent />
</template>

<style>
/* 為方便辨認是有切過 Component 的全域樣式 */

/* 賦予在每個component最外層，只針對有當前View中被使用的component */
.父組件highlight {
    border: 2px solid red;
}
/* 當組件有跨其他View被使用時 */
.跨View組件highlight {
    border: 2px solid brown;
}
/* 當外層不能包div時賦予的子component樣式 */
.子組件highlight {
    border: 2px solid blueviolet;
}

</style>