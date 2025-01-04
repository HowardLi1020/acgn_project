<template>
    <div class="coupon">
        <input type="text" v-model="localCouponCode" placeholder="輸入優惠券" />
        <button @click="applyCoupon" :disabled="isLoading">套用優惠券</button>
    </div>
</template>

<script>
    export default {
        props: {
            couponCode: {
                type: String,
                default: "",
            },
        },
        data() {
            return {
                localCouponCode: this.couponCode,
                isLoading: false,
            };
        },
        methods: {
            applyCoupon() {
                if (this.isLoading) return;
                this.isLoading = true;
                this.$emit("apply-coupon", this.localCouponCode.trim());
                this.isLoading = false;
            },
        },
    };
</script>

<style scoped>

</style>
