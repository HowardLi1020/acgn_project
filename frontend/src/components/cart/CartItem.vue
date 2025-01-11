<template>
    <div class="cart-item">
      <!-- 商品圖片 -->
      <img
        :src="getFullImageUrl(item.product_image)"
        alt="商品圖片"
        class="product-image"
        @error="handleImageError"
      />
      <div class="item-details">
        <h3>{{ item.product_name }}</h3>
        <p>單價: {{ item.product_price }}</p>
        <div class="quantity-controls">
          <button
            @click="updateQuantity(item.cart_item_id, item.quantity - 1)"
            :disabled="item.quantity <= 1 || isLoading"
            class="quantity-btn"
          >
            -
          </button>
          <span class="quantity-display">{{ item.quantity }}</span>
          <button
            @click="updateQuantity(item.cart_item_id, item.quantity + 1)"
            :disabled="isLoading"
            class="quantity-btn"
          >
            +
          </button>
        </div>
        <button
          @click="removeItem(item.cart_item_id)"
          class="remove-item"
          :disabled="isLoading"
        >
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
      },
      isLoading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        baseURL: "http://127.0.0.1:8000", // 後端靜態圖片的基礎 URL
      };
    },
    methods: {
      getFullImageUrl(relativePath) {
        if (!relativePath) {
          console.error("圖片路徑不存在，請檢查資料庫內容");
          return ""; // 若資料庫無圖片，回傳空字串或可替換為另一圖片
        }
        return `${this.baseURL}${relativePath}`; // 拼接完整 URL
      },
      handleImageError(event) {
        event.target.src = ""; // 圖片加載失敗時不顯示圖片
      },
      async updateQuantity(cartItemId, newQuantity) {
        this.$emit("update-quantity", { cartItemId, newQuantity });
      },
      async removeItem(cartItemId) {
        this.$emit("remove-item", cartItemId);
      },
    },
  };
  </script>
  
  <style scoped>
  .cart-item {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;
  }
  
  .product-image {
    width: 150px;
    height: 150px;
    object-fit: cover; /* 確保圖片按比例填滿 */
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-right: 15px;
  }
  
  .item-details {
    flex-grow: 1;
  }
  
  .quantity-controls {
    display: flex;
    align-items: center;
    margin-top: 10px;
  }
  
  .quantity-btn {
    width: 35px;
    height: 35px;
    border: none;
    border-radius: 50%;
    background-color: #28a745;
    color: white;
    font-size: 1.2rem;
    font-weight: bold;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .quantity-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .quantity-btn:hover:not(:disabled) {
    background-color: #218838;
  }
  
  .quantity-display {
    font-size: 1.2rem;
    margin: 0 10px;
    min-width: 20px;
    text-align: center;
    font-weight: bold;
  }
  
  .remove-item {
    margin-top: 10px;
    background-color: #ff4d4d;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .remove-item:hover {
    background-color: #e03e3e;
  }
  </style>