<script setup>
import { ref, onMounted } from 'vue';
import { storeAPI } from '../../utils/api';
import StarRating from './StarRating.vue';

const props = defineProps({
    productId: {
        type: [String, Number],
        required: true
    },
    initialReview: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['close', 'submitted', 'cancel']);

const reviewText = ref('');
const rating = ref(0);

// 初始化表單數據
onMounted(() => {
    if (props.initialReview) {
        reviewText.value = props.initialReview.review_text;
        rating.value = props.initialReview.rating;
    }
});

const handleSubmit = async () => {
    if (rating.value === 0) {
        alert('請選擇評分');
        return;
    }
    
    try {
        const reviewData = {
            rating: rating.value,
            review_text: reviewText.value
        };

        if (props.initialReview) {
            // 編輯現有評論
            await storeAPI.updateReview(
                props.productId, 
                props.initialReview.review_id, 
                reviewData
            );
        } else {
            // 提交新評論
            await storeAPI.submitReview(props.productId, reviewData);
        }
        
        emit('submitted');
        // 清空表單
        reviewText.value = '';
        rating.value = 0;
    } catch (error) {
        console.error('提交評論失敗:', error);
        alert(error.message || '提交評論失敗，請稍後再試');
    }
};

const handleCancel = () => {
    emit('cancel');
};
</script>

<template>
    <div class="review-form">
        <h3>{{ initialReview ? '編輯評論' : '撰寫評論' }}</h3>
        <div class="rating-section">
            <label>評分：</label>
            <StarRating v-model="rating" />
        </div>
        <div class="text-section">
            <textarea 
                v-model="reviewText" 
                :placeholder="initialReview ? '編輯你的評論...' : '寫下你的評論...'"
                rows="4"
            ></textarea>
        </div>
        <div class="button-section">
            <button @click="handleSubmit" class="submit-btn">
                {{ initialReview ? '更新評論' : '提交評論' }}
            </button>
        </div>
    </div>
</template>

<style scoped>
.review-form {
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
}

.rating-section {
    margin-bottom: 15px;
}

.text-section textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
    min-height: 100px;
}

.button-section {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 15px;
}

.cancel-btn {
    background-color: #95a5a6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.cancel-btn:hover {
    background-color: #7f8c8d;
}

.submit-btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.submit-btn:hover {
    background-color: #2980b9;
}
</style>