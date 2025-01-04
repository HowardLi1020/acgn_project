<script setup>
    defineProps({
        product: {
            type: Object,
            required: true,
        },
    });
</script>

<template>
<!-- 無背景小卡 component (FruitablesHomeFocusProductsCard2.vue)-->
    <div class="col-md-6 col-lg-6 col-xl-3 子組件highlight">
        <div class="text-center">
            <img :src="product.image" class="img-fluid rounded" :alt="product.name">
            <div class="py-2">
                <a href="#" class="h5">{{ product.name }}</a>
                <div class="d-flex my-3 justify-content-center">
                    <i v-for="n in 5" :key="n" class="fas" :class="n <= product.rating ? 'fa-star text-primary' : 'fa-star'"></i>
                </div>
                <h4 class="mb-3">{{ product.price }} $</h4>
                <a href="#" class="btn border border-secondary rounded-pill px-3 text-primary">
                    <i class="fa fa-shopping-bag me-2 text-primary"></i> Add to cart
                </a>
            </div>
        </div>
    </div>
</template>

<style lang="css" scoped>

</style>