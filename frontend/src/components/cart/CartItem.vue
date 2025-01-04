<template>
    <div class="cart-item">
        <img :src="item.product_image || defaultImage" alt="商品圖片" />
        <div class="item-details">
            <h3>{{ item.product_name }}</h3>
            <p>單價: {{ item.product_price }}</p>
            <div class="quantity-controls">
                <button
                    @click="updateQuantity(item.cart_item_id, item.quantity - 1)"
                    :disabled="item.quantity <= 1 || isLoading">
                    -
                </button>
                <span>{{ item.quantity }}</span>
                <button
                    @click="updateQuantity(item.cart_item_id, item.quantity + 1)"
                    :disabled="isLoading">
                    +
                </button>
            </div>
            <button @click="removeItem(item.cart_item_id)" class="remove-item" :disabled="isLoading">
                刪除
            </button>
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            item: {
                type: Object,
                required: true,
                validator(value) {
                    return value.product_name && value.product_price !== undefined && value.quantity !== undefined;
                },
            },
        },
        data() {
            return {
                isLoading: false,
                defaultImage: "https://via.placeholder.com/150",
            };
        },
        methods: {
            async updateQuantity(cartItemId, newQuantity) {
                this.isLoading = true;
                this.$emit("update-quantity", { cartItemId, newQuantity });
                this.isLoading = false;
            },
            async removeItem(cartItemId) {
                this.isLoading = true;
                this.$emit("remove-item", cartItemId);
                this.isLoading = false;
            },
        },
    };
</script>

<style scoped>

</style>
