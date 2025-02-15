<script setup>
import { ref, onMounted } from 'vue';
import { storeAPI } from '../../utils/api';
import ReviewModal from './ReviewModal.vue';
import StarRating from './StarRating.vue';

const props = defineProps({
    productId: {
        type: [String, Number],
        required: true
    }
});

const reviews = ref([]);
const canReview = ref(false);
const showReviewForm = ref(false);
const editingReview = ref(null);

// 獲取商品評論
const fetchReviews = async () => {
    try {
        const response = await storeAPI.getProductReviews(props.productId);
        reviews.value = Array.isArray(response) ? response : [];
    } catch (error) {
        console.error('獲取評論失敗:', error);
        reviews.value = [];
    }
};

// 檢查是否可以評論
const checkCanReview = async () => {
    try {
        const { can_review } = await storeAPI.checkCanReview(props.productId);
        canReview.value = can_review;
        showReviewForm.value = can_review && !editingReview.value;
    } catch (error) {
        console.error('檢查評論權限時出錯:', error);
        canReview.value = false;
        showReviewForm.value = false;
    }
};

// 開始編輯評論
const startEdit = (review) => {
    editingReview.value = review;
    showReviewForm.value = false;
};

// 取消編輯
const cancelEdit = () => {
    editingReview.value = null;
    checkCanReview();
};

const confirmDelete = async (review) => {
    if (confirm('確定要刪除這條評論嗎？')) {
        try {
            await storeAPI.deleteReview(props.productId, review.review_id);
            // 重新加載評論列表
            await fetchReviews();
            // 重新檢查是否可以評論
            await checkCanReview();
            // 如果可以評論，顯示評論表單
            if (canReview.value) {
                showReviewForm.value = true;
            }
        } catch (error) {
            alert(error.message || '刪除評論失敗');
        }
    }
};

// 處理評論提交（包括新評論和編輯評論）
const handleReviewSubmitted = async () => {
    editingReview.value = null;
    await fetchReviews();
    await checkCanReview();
};

onMounted(async () => {
    await Promise.all([fetchReviews(), checkCanReview()]);
});
</script>

<template>
    <div class="reviews-container">
        <h1 class="reviews-title">商品評論</h1>
        <!-- 新評論表單 -->
        <div v-if="canReview && !editingReview" class="review-section">
            <ReviewModal 
                :product-id="productId"
                @submitted="handleReviewSubmitted"
                @cancel="showReviewForm = false"
            />
        </div>

        <!-- 編輯評論表單 -->
        <div v-if="editingReview" class="review-section">
            <ReviewModal 
                :product-id="productId"
                :initial-review="editingReview"
                @submitted="handleReviewSubmitted"
                @cancel="cancelEdit"
            />
        </div>
        
        <!-- 評論列表 -->
        <div v-if="reviews.length > 0" class="reviews-list">
            <div v-for="review in reviews" :key="review.review_id" class="review-item">
                <div class="review-header">
                    <div class="review-info">
                        <StarRating :modelValue="review.rating" readonly />
                        <span class="review-user">{{ review.user_name }}</span>
                        <span class="review-date">{{ new Date(review.review_date).toLocaleDateString() }}</span>
                    </div>
                    <div>
                        <button 
                            v-if="review.is_owner" 
                            @click="startEdit(review)"
                            class="edit-button"
                        >
                            編輯評論
                        </button>
                        <button 
                            @click="confirmDelete(review)"
                            class="delete-button"
                        >
                            刪除評論
                        </button>
                    </div>  
                </div>
                <p class="review-text">{{ review.review_text }}</p>
            </div>
        </div>
        <div v-else class="no-reviews">
            <p>暫無評論</p>
        </div>
    </div>
</template>

<style scoped>
.reviews-container {
    padding: 20px;
    margin: 0;
    text-align: left;
}

.reviews-title {
    font-size: 1.5em;
    color: #333;
    margin-bottom: 20px;
    text-align: left;  /* 標題靠左對齊 */
    font-weight: bold;
}

.review-section {
    margin-bottom: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.reviews-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.review-item {
    background-color: #fff;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    text-align: left;
}

.review-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;  
    margin-bottom: 10px;
    width: 100%;  
}

.review-info {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;  
}

.review-user {
    font-weight: 600;
    color: #333;
}

.review-date {
    color: #666;
    font-size: 0.9em;
}

.review-text {
    color: #444;
    line-height: 1.5;
    margin: 10px 0;
    text-align: left;
    word-break: break-word;  
}

.review-actions {
    display: flex;
    gap: 4px;
    align-items: center;
    margin-left: auto;  
}

.edit-button,
.delete-button {
    padding: 4px 8px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.2s ease;
    white-space: nowrap;  
}

.edit-button {
    background-color: #4CAF50;
    color: white;
}

.edit-button:hover {
    background-color: #45a049;
}

.delete-button {
    background-color: #dc3545;
    color: white;
}

.delete-button:hover {
    background-color: #c82333;
}

.no-reviews {
    text-align: center;
    padding: 30px;
    color: #666;
    background-color: #f8f9fa;
    border-radius: 8px;
    margin-top: 20px;
}

/* 響應式設計 */
@media (max-width: 768px) {
    .reviews-container {
        padding: 10px;
    }

    .reviews-title {
        font-size: 1.3em;
        margin-bottom: 15px;
    }

    .review-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .review-actions {
        width: 100%;
        justify-content: flex-start;  
        margin-top: 8px;  
    }

    .edit-button,
    .delete-button {
        padding: 6px 12px;
    }

    .review-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
}
</style>