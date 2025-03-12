<script setup>
import Swal from 'sweetalert2';

// 定義委託資料
const commissionData = [
    {
        id: 1,
        image: "http://127.0.0.1:8000/media/commission/avatar/1019_avatar.png",
        title: "圖標工匠",
        description: "APP設計師圖標，專注於SEO主題。",
        fullDescription: `專業APP圖標設計師，擅長：
        • UI/UX設計
        • 品牌識別設計
        • SEO優化圖標
        • 跨平台圖標適配
        
        超過5年設計經驗，完成200+專案。`
    },
    {
        id: 2,
        image: "http://127.0.0.1:8000/media/commission/avatar/1020_avatar.png",
        title: "展覽夢設計師",
        description: "空間設計師，精於藝術展覽空間規劃。",
        fullDescription: `資深空間設計師：
        • 展覽空間規劃
        • 燈光設計
        • 動線規劃
        • 展示設計
        
        曾參與多個國際藝術展覽設計。`
    },
    {
        id: 3,
        image: "http://127.0.0.1:8000/media/commission/avatar/1006_avatar.png",
        title: "醉夢貓娘教主",
        description: "動漫迷，喜歡cosplay。",
        fullDescription: `專業Cosplayer：
        • 角色扮演
        • 攝影合作
        • 動漫活動主持
        • 服裝製作指導
        
        參與過100+場動漫展覽活動。`
    }
];

// 處理點擊事件，顯示詳細資訊
const showDetails = (commission) => {
    Swal.fire({
        title: commission.title,
        html: `<div class="commission-details">
            <img src="${commission.image}" class="commission-image" alt="${commission.title}">
            <div class="commission-text">
                ${commission.fullDescription.replace(/\n/g, '<br>')}
            </div>
        </div>`,
        showCloseButton: true,
        showConfirmButton: false,
        customClass: {
            popup: 'commission-popup'
        }
    });
};
</script>

<template>
<!-- 優惠折扣 Component (FruitablesHomeDiscounts.vue)-->
    <!-- Featurs Start -->
    <div class="container-fluid service py-5 父組件highlight">
        <div class="container py-5">
            <div class="row g-4 justify-content-center">
                <div v-for="commission in commissionData" :key="commission.id" class="col-md-6 col-lg-4">
                    <div class="commission-item" @click="showDetails(commission)">
                        <div class="service-item bg-dark rounded border border-dark">
                            <img :src="commission.image" class="img-fluid rounded-top w-100" alt="">
                            <div class="px-4 rounded-bottom">
                                <div class="service-content bg-light text-center p-4 rounded">
                                    <h5 class="text-primary">{{ commission.title }}</h5>
                                    <h5 class="mb-0">{{ commission.description }}</h5>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Featurs End -->
</template>

<style lang="css" scoped>
.commission-item {
    cursor: pointer;
    transition: transform 0.3s ease;
}

.commission-item:hover {
    transform: translateY(-5px);
}

/* 彈窗內容樣式 */
:deep(.commission-popup) {
    max-width: 600px;
}

:deep(.commission-details) {
    text-align: left;
    padding: 20px;
}

:deep(.commission-image) {
    width: 150px;
    height: 150px;
    object-fit: cover;
    border-radius: 50%;
    margin: 0 auto 20px;
    display: block;
}

:deep(.commission-text) {
    font-size: 16px;
    line-height: 1.6;
    white-space: pre-line;
}

:deep(.swal2-title) {
    color: #333;
    font-size: 24px;
    margin-bottom: 20px;
}

:deep(.swal2-close) {
    font-size: 2em;
    color: #666;
}

:deep(.swal2-close:hover) {
    color: #333;
}
</style>