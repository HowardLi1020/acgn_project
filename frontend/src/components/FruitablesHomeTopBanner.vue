<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const searchQuery = ref('');
const modalSearchQuery = ref('');

// 統一的搜尋處理函數
const performSearch = (category = 'animations') => {
    if (!searchQuery.value.trim()) return; // 如果搜尋詞為空，不執行搜尋
    
    // 導航到論壇頁面並帶上搜尋參數
    router.push({
        path: '/Forum',
        query: {
            search: searchQuery.value,
            category: category,
            page: 1
        }
    });
};

// Modal 搜尋處理函數
const performModalSearch = () => {
    if (!modalSearchQuery.value.trim()) return;
    
    router.push({
        path: '/Forum',
        query: {
            search: modalSearchQuery.value,
            category: 'movies', // Modal 搜尋預設使用 movies 類別
            page: 1
        }
    });
    
    // 關閉 modal
    const modal = document.getElementById('searchModal');
    const modalInstance = bootstrap.Modal.getInstance(modal);
    if (modalInstance) {
        modalInstance.hide();
    }
};

// 處理 Enter 鍵搜尋
const handleSearch = (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        performSearch();
    }
};

// 處理 Modal Enter 鍵搜尋
const handleModalSearch = (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        performModalSearch();
    }
};

// 處理按鈕點擊搜尋
const handleSearchClick = () => {
    performSearch();
};

// 處理 Modal 按鈕點擊搜尋
const handleModalSearchClick = () => {
    performModalSearch();
};
</script>

<template>
<!-- 首頁頂端Banner Component (FruitablesHomeTopBanner.vue)-->
<div class="父組件highlight">
  <!-- Modal Search Start -->
  <div
    class="modal fade"
    id="searchModal"
    tabindex="-1"
    aria-labelledby="exampleModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content rounded-0">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel">關鍵字搜尋</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body d-flex align-items-center">
          <div class="input-group w-75 mx-auto d-flex">
            <input
              class="form-control border-2 border-secondary w-50 py-3 px-4 rounded-pill"
              type="text"
              v-model="modalSearchQuery"
              placeholder="🔍 搜尋電影 名稱、年份、類別"
              @keydown="handleModalSearch"
            />
            <button
              type="button"
              class="btn btn-primary border-2 border-secondary py-3 px-4 position-absolute rounded-pill text-white h-100 search-button"
              style="top: 0; right: 0%"
              @click="handleModalSearchClick"
            >
              立即搜尋
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal Search End -->

  <!-- Hero Start -->
  <div class="container-fluid py-5 mb-5 hero-header">
    <div class="container py-5">
      <div class="row g-5 align-items-center">
        <div class="col-md-12 col-lg-7">
          <h4 class="mb-3 text-secondary">✧ Welcome to ACGN 綜合論壇 ✧</h4>
          <h1 class="mb-5 display-3 text-primary">
            ACGN的交流與分享
          </h1>
          <div class="position-relative mx-auto">
            <input
              class="form-control border-2 border-secondary w-75 py-3 px-4 rounded-pill"
              type="text"
              v-model="searchQuery"
              placeholder="🔍 搜尋動畫 名稱、年份、類別"
              @keydown="handleSearch"
            />
            <button
              type="button"
              class="btn btn-primary border-2 border-secondary py-3 px-4 position-absolute rounded-pill text-white h-100 search-button"
              style="top: 0; right: 25%"
              @click="handleSearchClick"
            >
              立即搜尋
            </button>
            <button 
              v-if="searchQuery" 
              @click="searchQuery = ''" 
              class="btn-clear"
              type="button"
            >
              ×
            </button>
          </div>
        </div>
        <div class="col-md-12 col-lg-5">
          <div
            id="carouselId"
            class="carousel slide position-relative"
            data-bs-ride="carousel"
          >
            <div class="carousel-inner" role="listbox">
              <div class="carousel-item active rounded">
                <img
                  src="https://p2.bahamut.com.tw/B/ACG/c/47/0000136647.JPG"
                  class="img-fluid w-100 h-100 bg-secondary rounded"
                  alt="First slide"
                />
                <router-link 
                  :to="{ path: '/Forum', query: { category: 'animations' }}" 
                  class="btn px-4 py-2 text-white rounded"
                >動畫 Anime
                </router-link>
              </div>
              <div class="carousel-item rounded">
                <img
                  src="https://p-cdnstatic.svc.litv.tv/pics/9045-000000-025783.jpg"
                  class="img-fluid w-100 h-100 rounded"
                  alt="Second slide"
                />
                <router-link 
                  :to="{ path: '/Forum', query: { category: 'movies' }}" 
                  class="btn px-4 py-2 text-white rounded"
                >電影 Movie
                </router-link>
              </div>
              <div class="carousel-item rounded">
                <img
                  src="http://localhost:5173/images/games/%E4%B8%96%E7%BA%AA%E4%B9%8B%E7%9F%B32.jpg"
                  class="img-fluid w-100 h-100 rounded"
                  alt="Second slide"
                />
                <router-link 
                  :to="{ path: '/Forum', query: { category: 'games' }}" 
                  class="btn px-4 py-2 text-white rounded"
                >遊戲 Game
                </router-link>
              </div>
            </div>
            <button
              class="carousel-control-prev"
              type="button"
              data-bs-target="#carouselId"
              data-bs-slide="prev"
            >
              <span
                class="carousel-control-prev-icon"
                aria-hidden="true"
              ></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button
              class="carousel-control-next"
              type="button"
              data-bs-target="#carouselId"
              data-bs-slide="next"
            >
              <span
                class="carousel-control-next-icon"
                aria-hidden="true"
              ></span>
              <span class="visually-hidden">Next</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Hero End -->
</div>
</template>

<style lang="css" scoped>
.position-relative {
  position: relative;
}

.btn-clear {
  position: absolute;
  right: 40%; /* 調整位置，遠離搜尋按鈕 */
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
  padding: 0 15px;
  line-height: 1;
  z-index: 2; /* 確保清除按鈕在最上層 */
}

/* 搜尋按鈕樣式 */
.search-button {
  z-index: 1;
}

.btn-clear:hover {
  color: #333;
}

/* 確保搜尋框內的文字垂直居中 */
.form-control {
  line-height: 1.5;
  padding-right: 80px; /* 為清除按鈕預留空間 */
}

/* 輪播按鈕樣式 */
.carousel-item .btn {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    background-color: rgba(0, 0, 0, 0.6);
    transition: background-color 0.3s ease;
}

.carousel-item .btn:hover {
    background-color: rgba(0, 0, 0, 0.8);
}

/* Modal 搜尋按鈕樣式 */
.modal .input-group {
  position: relative;
}

.modal .search-button {
  position: absolute;
  right: 25%;
  z-index: 4;
}

/* 修復 Modal 背景 */
:deep(.modal-backdrop) {
  background-color: rgba(0, 0, 0, 0.5);
}

:deep(.modal-content) {
  background-color: white;
}
</style>
