<template>
  <div class="cart-view">
    <h1>購物車頁面</h1>

    <!-- 加載中提示 -->
    <div v-if="isLoading" class="loading">加載中...</div>

    <!-- 錯誤提示 -->
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <!-- 購物車內容 -->
    <div v-if="cartItems.length > 0">
      <CartItem
        v-for="item in cartItems"
        :key="item.cart_item_id"
        :item="item"
        @update-quantity="updateQuantity"
        @remove-item="removeItem"
      />
      <CouponInput :coupon-code="couponCode" @apply-coupon="applyCoupon" />
      <SubmitOrder :coupon-code="couponCode" @submit-order="submitOrder" />
    </div>

    <!-- 空購物車提示 -->
    <div v-else class="empty-cart">
      <p>購物車是空的，快去添加商品吧！</p>
    </div>
  </div>
</template>

<script>
import CartItem from "@/components/cart/CartItem.vue";
import CouponInput from "@/components/cart/CouponInput.vue";
import SubmitOrder from "@/components/cart/SubmitOrder.vue";
import axios from "@/utils/api.js"; // 假設這是配置了基礎 API 的 axios 實例

export default {
  name: "CartView",
  components: { CartItem, CouponInput, SubmitOrder },
  data() {
    return {
      cartItems: [],
      couponCode: "",
      isLoading: false,
      errorMessage: "",
    };
  },
  methods: {
    // 獲取購物車內容
    async fetchCartItems() {
      this.isLoading = true;
      this.errorMessage = "";
      try {
        const response = await axios.get("/cart/");
        this.cartItems = response.data;
      } catch (error) {
        this.errorMessage = "無法加載購物車數據，請稍後重試。";
        console.error(error);
      } finally {
        this.isLoading = false;
      }
    },
    // 更新商品數量
    async updateQuantity({ cartItemId, newQuantity }) {
      this.errorMessage = "";
      try {
        await axios.put(`/cart/update/${cartItemId}/`, { quantity: newQuantity });
        this.fetchCartItems(); // 更新購物車內容
      } catch (error) {
        this.errorMessage = "更新數量失敗，請稍後重試。";
        console.error(error);
      }
    },
    // 刪除商品
    async removeItem(cartItemId) {
      this.errorMessage = "";
      try {
        await axios.delete(`/cart/delete/${cartItemId}/`);
        this.fetchCartItems(); // 更新購物車內容
      } catch (error) {
        this.errorMessage = "刪除商品失敗，請稍後重試。";
        console.error(error);
      }
    },
    // 套用優惠券
    applyCoupon(code) {
      this.couponCode = code.trim();
      console.log(`套用優惠券: ${this.couponCode}`);
      // 可在此調用後端 API 驗證優惠券
    },
    // 提交訂單
    async submitOrder() {
      this.errorMessage = "";
      try {
        const response = await axios.post("/orders/create/", {
          coupon_code: this.couponCode,
        });
        alert(`訂單提交成功，訂單編號: ${response.data.order_id}`);
        this.fetchCartItems(); // 清空購物車
        this.couponCode = ""; // 清空優惠券
      } catch (error) {
        this.errorMessage = "提交訂單失敗，請稍後重試。";
        console.error(error);
      }
    },
  },
  mounted() {
    this.fetchCartItems();
  },
};
</script>

<style scoped>
.cart-view {
  padding: 20px;
}
.loading {
  color: #007bff;
}
.error {
  color: red;
}
.empty-cart {
  text-align: center;
  color: gray;
}
</style>
