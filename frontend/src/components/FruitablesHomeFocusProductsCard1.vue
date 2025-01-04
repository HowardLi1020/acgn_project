<script setup>
    // 定義組件的屬性
    defineProps({
        product: {
            type: Object, // 產品類型為物件
            required: true, // 此屬性為必填
        },
    });
</script>

<template>
<!-- 白底小卡 component (FruitablesHomeFocusProductsCard1.vue) -->
    <div class="col-lg-6 col-xl-4 子組件highlight">
        <div class="p-4 rounded bg-light">
            <div class="row align-items-center">
                <div class="col-6">
                    <!-- 顯示產品圖片 -->
                    <img :src="product.image" class="img-fluid rounded-circle w-100" :alt="product.name" />
                </div>
                <div class="col-6">
                    <!-- 產品名稱連結 -->
                    <a :href="product.link" class="h5">{{ product.name }}</a>
                    <div class="d-flex my-3">
                        <!-- 顯示產品評分星星 -->
                        <i v-for="n in 5" :key="n" class="fas" :class="n <= product.rating ? 'fa-star text-primary' : 'fa-star'"></i>
                    </div>
                    <!-- 顯示產品價格 -->
                    <h4 class="mb-3">{{ product.price }} $</h4>
                    <!-- 加入購物車按鈕 -->
                    <a :href="product.addToCartLink" class="btn border border-secondary rounded-pill px-3 text-primary">
                        <i class="fa fa-shopping-bag me-2 text-primary"></i> Add to cart
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="css" scoped>

</style>