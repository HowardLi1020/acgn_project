<template>
	<div class="order-list-container">
		<h1 class="page-title">我的訂單</h1>
		<p v-if="loading" class="loading-text">載入中...</p>
		<p v-if="error" class="error-text">{{ error }}</p>

		<div v-if="orders.length > 0" class="orders">
			<div v-for="order in orders" :key="order.order_id" class="order-card">
				<div class="order-header">
					<span class="order-id">訂單編號: {{ order.order_id }}</span>
					<span class="order-date">{{ order.created_at }}</span>
				</div>
				<div class="order-info">
					<p><strong>總金額：</strong> ${{ order.total_amount }}</p>
					<p>
						<strong>付款方式：</strong> {{ order.payment_method || "未付款" }}
					</p>
					<p>
						<strong>付款狀態：</strong> {{ order.payment_status || "Pending" }}
					</p>
					<p>
						<strong>訂單狀態：</strong> {{ order.order_status || "待處理" }}
					</p>
				</div>
			</div>
		</div>
		<p v-else class="empty-text">目前沒有訂單</p>
	</div>
</template>

<script>
import { ref, onMounted } from "vue";
import { orderAPI } from "@/utils/api.js";

export default {
	setup() {
		const orders = ref([]);
		const loading = ref(true);
		const error = ref(null);

		const fetchOrders = async () => {
			try {
				const response = await orderAPI.getOrderList();
				orders.value = response.orders;
			} catch (err) {
				console.error("獲取訂單失敗:", err);
				error.value = "無法加載訂單列表，請稍後再試";
			} finally {
				loading.value = false;
			}
		};

		onMounted(fetchOrders);

		return { orders, loading, error };
	},
};
</script>

<style scoped>
.order-list-container {
	padding: 20px;
	max-width: 800px;
	margin: auto;
	margin-top: 180px;
	font-family: Arial, sans-serif;
}

.page-title {
	text-align: center;
	font-size: 24px;
	color: #333;
}

.loading-text,
.error-text,
.empty-text {
	text-align: center;
	font-size: 16px;
	color: #777;
}

.orders {
	display: flex;
	flex-direction: column;
	gap: 15px;
}

.order-card {
	border: 1px solid #ddd;
	padding: 15px;
	border-radius: 8px;
	background-color: #fff;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.order-header {
	display: flex;
	justify-content: space-between;
	font-size: 16px;
	color: #555;
	border-bottom: 1px solid #ddd;
	padding-bottom: 8px;
	margin-bottom: 10px;
}

.order-info p {
	margin: 5px 0;
	font-size: 18px;
	color: #444;
}
</style>
