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
          :isLoading="isLoading"
          @update-quantity="updateQuantity"
          @remove-item="removeItem"
        />
      </div>

      <!-- 總計與優惠券 -->
      <div class="cart-summary">
        <h2>購物車總覽</h2>
        <div class="summary-item">
          <span>商品總價：</span>
          <span class="summary-value">NT$ {{ total }}</span>
        </div>
        <div class="coupon-section">
          <input
            type="text"
            class="coupon-input"
            v-model="couponCode"
            placeholder="輸入優惠券代碼"
          />
          <button class="apply-coupon-btn" @click="applyCoupon">套用優惠券</button>
        </div>
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
  margin-top: 200px;
  padding: 20px;
}

.cart-title {
  text-align: center;
  font-size: 2rem;
  color: #333;
  margin-bottom: 30px;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  color: #007bff;
}

.error-message {
  color: red;
  text-align: center;
  font-size: 1rem;
  margin-bottom: 20px;
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
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cart-summary h2 {
  font-size: 1.5rem;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.summary-value {
  font-weight: bold;
  color: #28a745;
}

.coupon-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.coupon-input {
  flex: 1;
  padding: 8px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.apply-coupon-btn {
  padding: 8px 12px;
  background-color: #28a745;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.apply-coupon-btn:hover {
  background-color: #218838;
}

.checkout-button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.checkout-button:hover {
  background-color: #0056b3;
}

.empty-cart {
  text-align: center;
  font-size: 1.2rem;
  color: #888;
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
