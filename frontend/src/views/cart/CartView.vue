<template>
  <div class="cart-view">
    <h1 class="cart-title">🛒 購物車</h1>

    <!-- 加載中提示 -->
    <div v-if="isLoading" class="loading">加載中...</div>

    <!-- 錯誤提示 -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>

    <!-- 購物車內容 -->
    <div v-if="cartItems.length > 0" class="cart-container">
      <!-- 顯示購物車商品 -->
      <div class="cart-items">
        <CartItem
          v-for="item in cartItems"
          :key="item.cart_item_id"
          :item="item"
          @update-quantity="updateQuantity"
          @remove-item="removeItem"
        />
      </div>

      <!-- 總計與優惠券 -->
      <div class="cart-summary">
        <div class="summary-item">
          <span>商品總價：</span>
          <span class="summary-value">NT$ {{ total }}</span>
        </div>
        <CouponInput :coupon-code="couponCode" @apply-coupon="applyCoupon" />
        <button class="checkout-button" @click="submitOrder">結帳</button>
      </div>
    </div>

    <!-- 空購物車提示 -->
    <div v-else class="empty-cart">
      <p>購物車是空的，快去添加商品吧！</p>
      <router-link to="/store" class="go-shopping-button">去逛逛</router-link>
    </div>
  </div>
</template>

<script>
import CartItem from "@/components/cart/CartItem.vue";
import CouponInput from "@/components/cart/CouponInput.vue";
import { api } from "@/utils/api.js";

export default {
  name: "CartView",
  components: { CartItem, CouponInput },
  data() {
    return {
      cartItems: [],
      isLoading: false,
      errorMessage: "",
      couponCode: "",
    };
  },
  computed: {
    // 計算商品總價
    total() {
      return this.cartItems.reduce((sum, item) => sum + item.product_price * item.quantity, 0);
    },
  },
  methods: {
    async fetchCartItems() {
      this.isLoading = true;
      this.errorMessage = "";
      try {
        const response = await api.get("/cart_api/");
        console.log("Fetched cart items:", response.data);
        this.cartItems = response.data;
      } catch (error) {
        this.errorMessage = "無法加載購物車數據，請稍後重試。";
        console.error(error);
      } finally {
        this.isLoading = false;
      }
    },
    async updateQuantity({ cartItemId, newQuantity }) {
      this.errorMessage = "";
      try {
        await api.put(`/cart_api/update/${cartItemId}/`, { quantity: newQuantity });
        this.fetchCartItems();
      } catch (error) {
        this.errorMessage = "更新數量失敗，請稍後重試。";
        console.error(error);
      }
    },
    async removeItem(cartItemId) {
      this.errorMessage = "";
      try {
        await api.delete(`/cart_api/delete/${cartItemId}/`);
        this.fetchCartItems();
      } catch (error) {
        this.errorMessage = "刪除商品失敗，請稍後重試。";
        console.error(error);
      }
    },
    applyCoupon(code) {
      this.couponCode = code.trim();
      console.log(`套用優惠券: ${this.couponCode}`);
    },
    async submitOrder() {
      this.errorMessage = "";
      try {
        const response = await api.post("/orders/create/", {
          coupon_code: this.couponCode,
        });
        alert(`訂單提交成功，訂單編號: ${response.data.order_id}`);
        this.fetchCartItems();
        this.couponCode = "";
      } catch (error) {
        this.errorMessage = "提交訂單失敗，請稍後重試。";
        console.error("提交訂單失敗:", error);
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cart-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  font-size: 18px;
  color: #007bff;
}

.error-message {
  color: red;
  text-align: center;
}

.cart-container {
  display: flex;
  gap: 20px;
}

.cart-items {
  flex: 3;
}

.cart-summary {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.summary-value {
  font-weight: bold;
}

.checkout-button {
  width: 100%;
  padding: 10px 0;
  background-color: #28a745;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.checkout-button:hover {
  background-color: #218838;
}

.empty-cart {
  text-align: center;
  padding: 40px;
}

.go-shopping-button {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #007bff;
  color: #fff;
  text-decoration: none;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.go-shopping-button:hover {
  background-color: #0056b3;
}
</style>
