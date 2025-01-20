<template>
    <div class="checkout">
        <h1>確認訂單</h1>

        <!-- 商品區 -->
        <div class="section">
            <h2>購物車商品</h2>
            <div v-if="cartItems.length > 0" class="cart-items">
                <OrderItem
                    v-for="item in cartItems"
                    :key="item.cart_item_id"
                    :item="item"
                />
            </div>
            <p v-else class="empty-cart">購物車內沒有商品</p>
        </div>

        <!-- 總金額 -->
        <div class="section order-summary">
            <h2>訂單摘要</h2>
            <p class="total-price-label">總金額：</p>
            <p class="total-price">{{ totalPrice }}</p>
        </div>

        <!-- 收件資料 -->
        <div class="section user-details">
            <h2>收件資料</h2>
            <input
                v-model="userDetails.recipient"
                type="text"
                placeholder="收件人"
                required
            />
            <input
                v-model="userDetails.recipient_phone"
                type="text"
                placeholder="收件人電話"
                required
            />
            <input
                v-model="userDetails.city"
                type="text"
                placeholder="城市"
                required
            />
            <input
                v-model="userDetails.region"
                type="text"
                placeholder="地區"
                required
            />
            <input
                v-model="userDetails.detailed_address"
                type="text"
                placeholder="詳細地址"
                required
            />
            <input
                v-model="userDetails.postal_code"
                type="text"
                placeholder="郵遞區號"
                required
            />
            <h3>付款方式</h3>
            <select v-model="userDetails.payment_method" required>
		        <option disabled value="">選擇付款方式</option>
		        <option value="CREDIT_CARD">信用卡</option>
		        <option value="BANK_TRANSFER">銀行轉帳</option>
		        <option value="PAYPAL">PayPal</option>
	        </select>
        </div>

        <!-- 提交按鈕 -->
        <div class="section submit-section">
            <button
                @click="submitOrder"
                class="checkout-btn"
                :disabled="loading || !isFormValid || cartItems.length === 0"
            >
                {{ loading ? "提交中..." : "提交訂單" }}
            </button>
        </div>
    </div>
</template>

<script>
import OrderItem from "@/components/cart/OrderItem.vue";
import { cartAPI, orderAPI } from "@/utils/api";

export default {
    components: {
        OrderItem,
    },
    data() {
        return {
            cartItems: [], // 儲存購物車內容
            userDetails: {
                recipient: "",
                recipient_phone: "",
                city: "",
                region: "",
                detailed_address: "",
                postal_code: "",
            },
            loading: false,
        };
    },
    computed: {
        // 計算總金額
        totalPrice() {
            return this.cartItems
                .reduce((total, item) => total + item.price * item.quantity, 0)
                .toFixed(2);
        },
        // 表單驗證
        isFormValid() {
            return (
                this.userDetails.recipient &&
                this.userDetails.recipient_phone &&
                this.userDetails.city &&
                this.userDetails.region &&
                this.userDetails.detailed_address &&
                this.userDetails.postal_code &&
                this.userDetails.payment_method
            );
        },
    },
    methods: {
        // 獲取購物車內容
        async fetchCartItems() {
            try {
                this.cartItems = await cartAPI.getCartItems();
            } catch (error) {
                alert("無法加載購物車內容，請稍後再試！");
            }
        },
        // 提交訂單
        async submitOrder() {
            // console.log("表單驗證狀態：", this.isFormValid);
		    // console.log("表單數據：", this.userDetails);
            if (!this.isFormValid) {
                alert("請完整填寫收件資料！");
                return;
            }
            this.loading = true;

            // 構建提交數據
            const orderData = {
                ...this.userDetails,
                total_amount: parseFloat(this.totalPrice),
            };
            // console.log("API 基礎 URL：", import.meta.env.VITE_APIURL);
            // console.log("提交的訂單數據：", orderData);

            try {
                await orderAPI.submitOrder(orderData);
                alert(`訂單提交成功！`);
                this.$router.push({ name: "ShoppingCart" });
            } catch (error) {
                alert(error.message || "提交訂單失敗！");
            } finally {
                this.loading = false;
            }
        },
    },
    created() {
        this.fetchCartItems(); // 初始化時獲取購物車內容
    },
};
</script>

<style scoped>
.checkout {
    padding: 20px;
    margin: 50px auto;
    max-width: 800px;
    background-color: #f9f9f9;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    font-family: "Arial", sans-serif;
    color: #333;
}

.checkout h1 {
    font-size: 28px;
    text-align: center;
    font-weight: bold;
    color: #007bff;
    margin-bottom: 30px;
}

.section {
    margin-bottom: 30px;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section h2 {
    font-size: 20px;
    margin-bottom: 15px;
    color: #444;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
}

.cart-items {
    margin-bottom: 20px;
}

.empty-cart {
    text-align: center;
    font-size: 16px;
    color: #777;
    font-style: italic;
}

.order-summary .total-price-label {
    display: inline-block;
    font-size: 18px;
    color: #555;
}

.order-summary .total-price {
    font-size: 24px;
    font-weight: bold;
    color: #007bff;
    margin-left: 10px;
}

.user-details input {
    display: block;
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: border-color 0.3s ease;
}

.user-details input:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: inset 0 1px 3px rgba(0, 123, 255, 0.3);
}

.submit-section {
    text-align: center;
}

.checkout-btn {
    padding: 12px 24px;
    font-size: 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.checkout-btn:hover {
    background-color: #0056b3;
}

.checkout-btn:disabled {
    background-color: #e4e4e4;
    color: #aaa;
    cursor: not-allowed;
}
.payment-method {
    margin-top: 10px;
}
.payment-method label {
    display: block;
    margin-bottom: 10px;
    font-size: 16px;
    color: #333;
    cursor: pointer;
}
.payment-method input[type="radio"] {
    margin-right: 10px;
}
</style>
