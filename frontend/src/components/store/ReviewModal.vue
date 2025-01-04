
<script setup>
import { ref } from 'vue';
import { storeAPI } from '../../utils/api';

const props = defineProps({
    productId: String,
});

const reviewText = ref('');
const rating = ref(0);

const submitReview = async () => {
    await storeAPI.submitReview(props.productId, { text: reviewText.value, rating: rating.value });
    $emit('close'); // 提交後關閉模態框
};
</script><template>
    <div class="review-modal">
        <h2>請評價您的購買</h2>
        <textarea v-model="reviewText" placeholder="寫下你的評論..."></textarea>
        <StarRating v-model="rating" />
        <button @click="submitReview">提交評論</button>
        <button @click="$emit('close')">關閉</button>
    </div>
</template>

