<template>
    <div>
        <button @click="submitOrder" :disabled="isLoading" class="submit-order">
            {{ isLoading ? "提交中..." : "提交訂單" }}
        </button>
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
            isLoading: false,
        };
    },
    methods: {
        async submitOrder() {
            if (this.isLoading) return;
            this.isLoading = true;
            await this.$emit("submit-order", this.couponCode);
            this.isLoading = false;
        },
    },
};
</script>

<style scoped>

</style>
