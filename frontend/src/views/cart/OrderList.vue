<template>
	<div class="order-list">
		<h1>我的訂單</h1>
		<div v-if="orders.length > 0" class="orders">
			<div v-for="order in orders" :key="order.id" class="order">
				<p><strong>訂單編號：</strong>{{ order.order_id }}</p>
				<p><strong>收件人：</strong>{{ order.recipient }}</p>
				<p><strong>總金額：</strong>{{ order.total_amount }}</p>
				<p><strong>付款方式：</strong>{{ formatPaymentMethod(order.payment_method) }}</p>
				<p><strong>建立時間：</strong>{{ formatDate(order.created_at) }}</p>
			</div>
		</div>
		<p v-else>目前沒有任何訂單。</p>
	</div>
</template>

<script>
import { orderAPI } from "@/utils/api";

export default {
	name: "OrderList",
	data() {
		return {
			orders: [], // 儲存訂單清單
		};
	},
	methods: {
		// 格式化付款方式
		formatPaymentMethod(method) {
			switch (method) {
				case 'CREDIT_CARD':
					return '信用卡';
				case 'BANK_TRANSFER':
					return '銀行轉帳';
				case 'PAYPAL':
					return 'PayPal';
				default:
					return '未知';
			}
		},
		// 格式化日期
		formatDate(date) {
			return new Date(date).toLocaleString();
		},
	},
	async created() {
		try {
			this.orders = await orderAPI.getOrderList(); // 獲取訂單清單
		} catch (error) {
			alert(error.message || "無法加載訂單清單！");
		}
	},
};

</script>

<style scoped>
.order-list {
	padding: 20px;
	max-width: 800px;
	margin: 0 auto;
    margin-top: 160px;
	background-color: #f9f9f9;
	border-radius: 10px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.orders .order {
	padding: 15px;
	margin-bottom: 10px;
	background-color: white;
	border-radius: 5px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.orders .order p {
	margin: 5px 0;
	font-size: 16px;
}
</style>
