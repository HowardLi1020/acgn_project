<script setup>
import { ref, onMounted } from 'vue';
import { storeAPI } from '../../utils/api';
import ReviewModal from './ReviewModal.vue';

const props = defineProps({
    productId: String,
});

const reviews = ref([]);
const isReviewModalOpen = ref(false);

// 獲取商品評論
const fetchReviews = async () => {
    const response = await storeAPI.getProductReviews(props.productId);
    reviews.value = response.data; // 假設返回的數據格式
};

onMounted(fetchReviews);

const openReviewModal = () => {
    isReviewModalOpen.value = true;
};
</script>

<template>
  <div class="reviews-section">
      <h2>商品評價</h2>
      <div v-if="reviews.length > 0">
          <ul>
              <li v-for="review in reviews" :key="review.id">
                  <StarRating :rating="review.rating" :readonly="true" />
                  <p>{{ review.content }}</p>
              </li>
          </ul>
      </div>
      <div v-else>
          <p>暫無評論</p> <!-- 當沒有評論時顯示的提示 -->
      </div>
  </div>
</template>

<style scoped>

</style>
