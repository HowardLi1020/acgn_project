<script setup>
import { ref } from 'vue'; 
import FruitablesDetailReviewCard from '@/components/FruitablesDetailReviewCard.vue';

// 假設從 API 獲取的商品評論資料，對應FruitablesDetailReviewCard.vue
const reviews = ref([
    {
        avatar: new URL("@/assets/img/BadTimeStories_avatar1.png", import.meta.url).href,
        date: 'April 12, 2024',
        name: '床編',
        rating: 4,
        review:
            '已購買，小孩愛吃'
    },
    {
        avatar: new URL("@/assets/img/BadTimeStories_avatar2.png", import.meta.url).href,
        date: 'April 10, 2024',
        name: '小雞汁',
        rating: 5,
        review:
            '哇！這麼神奇！那我也要來試試看！'
    }
]);
</script>

<template>
    <!-- 商品描述 Component (FruitablesDetailDescription.vue)-->
    <div class="col-lg-12 父組件highlight">
        <nav>
            <div class="nav nav-tabs mb-3">
                <button class="nav-link active border-white border-bottom-0" type="button" role="tab"
                    id="nav-about-tab" data-bs-toggle="tab" data-bs-target="#nav-about"
                    aria-controls="nav-about" aria-selected="true">Description</button>
                <button class="nav-link border-white border-bottom-0" type="button" role="tab"
                    id="nav-mission-tab" data-bs-toggle="tab" data-bs-target="#nav-mission"
                    aria-controls="nav-mission" aria-selected="false">Reviews 評論</button>
            </div>
        </nav>

        <div class="tab-content mb-5">
            <div class="tab-pane active" id="nav-about" role="tabpanel" aria-labelledby="nav-about-tab">
                <p>The generated Lorem Ipsum is therefore always free from repetition injected humour, or non-characteristic words etc. 
                    Susp endisse ultricies nisi vel quam suscipit </p>
                <p>Sabertooth peacock flounder; chain pickerel hatchetfish, pencilfish snailfish filefish Antarctic 
                    icefish goldeye aholehole trumpetfish pilot fish airbreathing catfish, electric ray sweeper.</p>
                <div class="px-2">
                    <div class="row g-4">
                        <div class="col-6">
                            <div class="row bg-light align-items-center text-center justify-content-center py-2">
                                <div class="col-6">
                                    <p class="mb-0">Weight</p>
                                </div>
                                <div class="col-6">
                                    <p class="mb-0">1 kg</p>
                                </div>
                            </div>
                            <div class="row text-center align-items-center justify-content-center py-2">
                                <div class="col-6">
                                    <p class="mb-0">Country of Origin</p>
                                </div>
                                <div class="col-6">
                                    <p class="mb-0">Agro Farm</p>
                                </div>
                            </div>
                            <div class="row bg-light text-center align-items-center justify-content-center py-2">
                                <div class="col-6">
                                    <p class="mb-0">Quality</p>
                                </div>
                                <div class="col-6">
                                    <p class="mb-0">Organic</p>
                                </div>
                            </div>
                            <div class="row text-center align-items-center justify-content-center py-2">
                                <div class="col-6">
                                    <p class="mb-0">Сheck</p>
                                </div>
                                <div class="col-6">
                                    <p class="mb-0">Healthy</p>
                                </div>
                            </div>
                            <div class="row bg-light text-center align-items-center justify-content-center py-2">
                                <div class="col-6">
                                    <p class="mb-0">Min Weight</p>
                                </div>
                                <div class="col-6">
                                    <p class="mb-0">250 Kg</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- 商品評論 Component (FruitablesDetailReviewCard.vue)-->
            <div class="tab-pane" id="nav-mission" role="tabpanel" aria-labelledby="nav-mission-tab">
                <FruitablesDetailReviewCard
                    v-for="(review, index) in reviews"
                    :key="index"
                    :avatar="review.avatar"
                    :date="review.date"
                    :name="review.name"
                    :rating="review.rating"
                    :review="review.review"
                />
            </div>
        </div>
    </div>
</template>

<style>
</style>