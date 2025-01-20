<template>
	<div class="cart-view">
		<h1>購物車</h1>
		<!-- 檢查是否有商品 -->
		<div v-if="cartItems.length > 0">
			<!-- 顯示每個購物車商品 -->
			<CartItem
				v-for="item in cartItems"
				:key="item.cart_item_id"
				:item="item"
				:onUpdate="handleCartUpdate"
			/>
			<div class="cart-summary">
				<p>總金額：<span class="total-price">{{ totalPrice }}</span></p>
				<button @click="checkout" class="checkout-btn">前往結帳</button>
			</div>
		</div>
		<p v-else class="empty-cart">購物車內沒有商品</p>
		<div class="cart-summary">
				<button @click="orderlist" class="checkout-btn">我的訂單</button>
		</div>
	</div>
</template>

<script>
import CartItem from "@/components/cart/CartItem.vue";
import { cartAPI } from "@/utils/api";

export default {
	components: {
		CartItem,
	},
	data() {
		return {
			cartItems: [], // 儲存購物車內容
		};
	},
	computed: {
		// 計算總金額
		totalPrice() {
			return this.cartItems
				.reduce((total, item) => total + item.price * item.quantity, 0)
				.toFixed(2);
		},
	},
	methods: {
		// 獲取購物車內容的函示
		async fetchCartItems() {
			try {
				this.cartItems = await cartAPI.getCartItems();
			} catch (error) {
				alert(error.message);
			}
		},
		async handleCartUpdate(action) {
			try {
				if (action.action === "increment") {
					// 增加數量
					await cartAPI.updateCartItem({
            product_id: action.product_id,
						action: "increment",
					});
				} else if (action.action === "decrement") {
					// 減少數量
					await cartAPI.updateCartItem({
            product_id: action.product_id,
						action: "decrement",
					});
				} else if (!action.action) {
					// 如果沒有 action，執行刪除操作
					await cartAPI.deleteCartItem(action.product_id);
				}
				// 操作完成後刷新購物車
				this.fetchCartItems();
			} catch (error) {
				console.error("操作失敗：", error);
				alert("操作失敗，請稍後再試！");
			}
		},
		// 前往結帳
		checkout() {
			this.$router.push({ name: "Checkout" });
		},

		orderlist(){
			this.$router.push({ name: "orderlist"})
		}
	},
	created() {
		this.fetchCartItems(); // 初始化時獲取購物車內容
	},
};
</script>

<style scoped>
.cart-view {
	padding: 20px;
	margin: 100px auto;
	margin-top: 180px;
	max-width: 800px;
	background-color: #f9f9f9;
	border-radius: 10px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cart-view h1 {
	margin-bottom: 20px;
	font-size: 28px;
	text-align: center;
	font-weight: bold;
	color: #333;
}

.cart-container {
	background-color: white;
	border-radius: 10px;
	padding: 20px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cart-summary {
	margin-top: 20px;
	padding-top: 10px;
	border-top: 1px solid #ccc;
	text-align: right;
}

.cart-summary p {
	margin-bottom: 10px;
	font-size: 18px;
	font-weight: bold;
	color: #444;
}

.cart-summary .total-price {
	color: #007bff;
}

.cart-summary .checkout-btn {
	padding: 12px 24px;
	background-color: #007bff;
	color: white;
	border: none;
	border-radius: 5px;
	cursor: pointer;
	font-size: 16px;
	transition: background-color 0.3s ease;
}

.cart-summary .checkout-btn:hover {
	background-color: #0056b3;
}

.empty-cart {
	text-align: center;
	margin-top: 50px;
	font-size: 18px;
	color: #777;
	font-style: italic;
}
</style>

