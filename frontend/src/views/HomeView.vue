<script setup>
import FruitablesHomeTopBanner from '@/components/FruitablesHomeTopBanner.vue';
import FruitablesHomeMerit from '@/components/FruitablesHomeMerit.vue';
import FruitablesHomeShop from '@/components/FruitablesHomeShop.vue';
import FruitablesHomeDiscounts from '@/components/FruitablesHomeDiscounts.vue';
import FruitablesHomeRollingShop from '@/components/FruitablesHomeRollingShop.vue';
import FruitablesHomeBillboard from '@/components/FruitablesHomeBillboard.vue';
import FruitablesHomeFocusProducts from '@/components/FruitablesHomeFocusProducts.vue';
import FruitablesHomeQualityAssurance from '@/components/FruitablesHomeQualityAssurance.vue';
import FruitablesHomeTastimonial from '@/components/FruitablesHomeTastimonial.vue';
</script>

<template>
    <div class="acgn-home">
        <h1 class="main-title">ACGN Home</h1>
        <!-- 首頁頂端Banner Component (FruitablesHomeTopBanner.vue)-->
        <FruitablesHomeTopBanner />
        <!-- 優勢亮點 Component (FruitablesHomeMerit.vue)-->
        <FruitablesHomeMerit />
        <!-- 簡易商店 Component (FruitablesHomeShop.vue)-->
        <FruitablesHomeShop />
        <!-- 優惠折扣 Component (FruitablesHomeDiscounts.vue)-->
        <FruitablesHomeDiscounts />
        <!-- 商品輪播 Component (FruitablesHomeRollingShop.vue) 功能炸開^q^-->
        <FruitablesHomeRollingShop />
        <!-- 大型橫幅廣告 Component (FruitablesHomeBillboard.vue)-->
        <FruitablesHomeBillboard />
        <!-- 焦點商品 Component (FruitablesHomeFocusProducts.vue)-->
        <FruitablesHomeFocusProducts />
        <!-- 品質保證 Component (FruitablesHomeQualityAssurance.vue)-->
        <FruitablesHomeQualityAssurance />
        <!-- 顧客評論輪播 Component (FruitablesHomeTastimonial.vue) 功能炸開^q^-->
        <FruitablesHomeTastimonial />
    </div>
</template>

<style>
.acgn-home {
    background-color: #e6f3ff;  /* 淺藍色背景 */
    min-height: 100vh;  /* 確保背景色至少覆蓋整個視窗高度 */
    width: 100%;
}

.acgn-home .main-title {
    margin-top: 150px;  /* 根據 NAVBar 的高度調整上邊距 */
    color: #333;  /* 深色文字 */
    text-align: center;  /* 置中對齊 */
    padding: 20px 0;  /* 上下間距 */
    font-size: 2rem;  /* 適當的文字大小 */
}
</style>