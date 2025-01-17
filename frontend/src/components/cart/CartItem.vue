<template>
	<div class="cart-item">
		<div class="cart-item-image">
			<img :src="getImageUrl(item.product_image)" alt="商品圖片" />
		</div>
		<div class="cart-item-info">
			<h3>{{ item.product_name }}</h3>
			<p>單價：{{ formatPrice(item.price) }}</p>
			<p>數量：{{ item.quantity }}</p>
			<p>小計：{{ formatPrice(item.price * item.quantity) }}</p>
		</div>
		<div class="cart-item-actions">
			<button class="action-btn increment" @click="increment">+</button>
			<button class="action-btn decrement" @click="decrement" :disabled="item.quantity <= 1">-</button>
			<button class="action-btn delete" @click="deleteItem">刪除</button>
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
		onUpdate: {
			type: Function,
			required: true,
		},
	},
	methods: {
		getImageUrl(imagePath) {
			// 如果是相對路徑，拼接基礎 URL
			if (imagePath && !imagePath.startsWith("http")) {
				return `${window.location.origin}${imagePath}`;
			}
			return imagePath || "/images/default-product.png"; // 預設圖片
		},
		handleImageError(event) {
			event.target.src = "/images/default-product.png"; // 當圖片加載失敗時，顯示預設圖片
		},
		formatPrice(value) {
			// 如果值為空，返回 0.00；否則格式化為兩位小數
			return value ? parseFloat(value).toFixed(2) : "0.00";
		},
		increment() {
			this.onUpdate({ action: "increment", product_id: this.item.product_id });
		},
		decrement() {
			this.onUpdate({ action: "decrement", product_id: this.item.product_id });
		},
		deleteItem() {
			this.onUpdate({ product_id: this.item.product_id });
		},
	},
};
</script>

<style scoped>
.cart-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 15px;
	margin-bottom: 15px;
	background-color: #fff;
	border-radius: 10px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cart-item-image {
	flex-shrink: 0;
	margin-right: 20px;
}

.cart-item-image img {
	width: 80px;
	height: 80px;
	object-fit: cover;
	border-radius: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cart-item-info {
	flex-grow: 1;
}

.cart-item-info h3 {
	margin: 0 0 10px;
	font-size: 18px;
	font-weight: bold;
	color: #333;
}

.cart-item-info p {
	margin: 5px 0;
	font-size: 14px;
	color: #666;
}

.cart-item-actions {
	display: flex;
	align-items: center;
	gap: 10px;
}

.action-btn {
	padding: 8px 16px;
	border: none;
	border-radius: 5px;
	cursor: pointer;
	font-size: 14px;
	transition: background-color 0.3s ease, color 0.3s ease;
}

.action-btn.increment {
	background-color: #007bff;
	color: white;
}

.action-btn.increment:hover {
	background-color: #0056b3;
}

.action-btn.decrement {
	background-color: #ffc107;
	color: #333;
}

.action-btn.decrement:hover {
	background-color: #e0a800;
}

.action-btn.delete {
	background-color: #dc3545;
	color: white;
}

.action-btn.delete:hover {
	background-color: #a71d2a;
}

.action-btn:disabled {
	background-color: #e4e4e4;
	color: #aaa;
	cursor: not-allowed;
}
</style>

