<script setup>
// 定義組件的輸入屬性
const props = defineProps({
    product: {
        type: Object,
        required: true
    }
});

// 定義可觸發的事件
const emit = defineEmits(['update-quantity']);

// 用於存儲定時器ID
let intervalId = null;
// 開始持續增減前的延遲時間（毫秒）
const INITIAL_DELAY = 500;
// 持續增減的時間間隔（毫秒）
const INTERVAL_SPEED = 100;

// 更新商品數量的基本函數
const updateQuantity = (change) => {
    const newQuantity = props.product.quantity + change;
    // 確保數量不會小於1
    if (newQuantity > 0) {
        emit('update-quantity', props.product.id, newQuantity);
    }
};

// 開始持續更新數量（用於長按按鈕）
const startContinuousUpdate = (change) => {
    // 首次點擊立即更新一次
    updateQuantity(change);
    
    // 設定延遲後的持續更新
    const timeoutId = setTimeout(() => {
        intervalId = setInterval(() => {
            updateQuantity(change);
        }, INTERVAL_SPEED);
    }, INITIAL_DELAY);
    
    intervalId = timeoutId;
};

// 停止持續更新（用於釋��按鈕或滑鼠離開）
const stopContinuousUpdate = () => {
    if (intervalId) {
        clearInterval(intervalId);
        clearTimeout(intervalId);
        intervalId = null;
    }
};

// 計算單項商品總價
const calculateTotal = () => {
    return (props.product.price * props.product.quantity).toFixed(2);
};
</script>

<template>
<!-- 品項列 component (FruitablesCartTableRow.vue)-->
    <tr>
        <!-- 商品圖片欄位 -->
        <th scope="row">
            <div class="d-flex align-items-center mt-2">
                <!-- 圖片容器：使用 aspect-ratio 保持圖片比例 -->
                <div class="product-image-container">
                    <img :src="props.product.image" 
                         class="img-fluid rounded-circle product-image" 
                         :alt="props.product.name">
                </div>
            </div>
        </th>
        <!-- 商品名稱欄位 -->
        <td style="width: 200px; min-width: 200px;">
            <p class="mb-0 mt-4">{{ props.product.name }}</p>
        </td>
        <!-- 商品單價欄位 -->
        <td style="width: 120px; min-width: 120px;">
            <p class="mb-0 mt-4">{{ props.product.price }} $</p>
        </td>
        <!-- 商品數量調整欄位 -->
        <td style="width: 150px; min-width: 150px;">
            <div class="input-group quantity mt-4" style="width: 100px;">
                <!-- 減少數量按鈕 -->
                <div class="input-group-btn">
                    <button type="button" 
                            class="btn btn-sm btn-minus rounded-circle bg-light border"
                            @mousedown="startContinuousUpdate(-1)"
                            @mouseup="stopContinuousUpdate"
                            @mouseleave="stopContinuousUpdate">
                        <i class="fa fa-minus"></i>
                    </button>
                </div>
                <!-- 數量顯示輸入框 -->
                <input type="text" class="form-control form-control-sm text-center border-0" v-model="props.product.quantity">
                <!-- 增加數量按鈕 -->
                <div class="input-group-btn">
                    <button type="button" 
                            class="btn btn-sm btn-plus rounded-circle bg-light border"
                            @mousedown="startContinuousUpdate(1)"
                            @mouseup="stopContinuousUpdate"
                            @mouseleave="stopContinuousUpdate">
                        <i class="fa fa-plus"></i>
                    </button>
                </div>
            </div>
        </td>
        <!-- 商品總價欄位 -->
        <td style="width: 120px; min-width: 120px;">
            <p class="mb-0 mt-4">{{ calculateTotal() }} $</p>
        </td>
        <!-- 刪除商品按鈕欄位 -->
        <td style="width: 100px; min-width: 100px;">
            <button class="btn btn-md rounded-circle bg-light border mt-4">
                <i class="fa fa-times text-danger"></i>
            </button>
        </td>
    </tr>
</template>

<style scoped>
/* 圖片容器樣式 */
.product-image-container {
    width: 90px;  /* 設定容器寬度 */
    aspect-ratio: 1/1;  /* 保持 1:1 的比例 */
    overflow: hidden;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 圖片本身的樣式 */
.product-image {
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: auto;
    object-fit: cover;
    object-position: center;
}
</style>