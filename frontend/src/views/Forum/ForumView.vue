<script setup>
import { ref, computed, onMounted, nextTick, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";
import Carousel from './Carousel.vue';
import DiscussionSection from "@/views/Forum/DiscussionSection.vue";
// 導入向量搜索推薦模組
import RecommendationModule from './recommendation/RecommendationModule.vue';

// Vue Router
const router = useRouter();
const route = useRoute();

// State Management
// State Management
const currentCategory = ref(route.query.category || "games");
const currentPage = ref(parseInt(route.query.page) || 1);
const itemsPerPage = ref(24);
const searchQuery = ref(route.query.search || "");
const items = ref([]);
const selectedGenre = ref(route.query.genre || "all");
const carouselItems = ref([]);
const carouselCategory = ref("");
const carouselScrollPosition = ref(0);
// 新增：推薦模組顯示控制
const showRecommendation = ref(false);

// 存儲所有類別的資料
const allCategoryData = ref({
  games: [],
  animations: [],
  movies: []
});

// 使用當前選擇的類別
const setupCarousel = () => {
  console.log('[Forum] Setting up carousel for current category:', currentCategory.value);
  
  // 檢查當前類別是否有足夠數據
  const categoryData = allCategoryData.value[currentCategory.value] || [];
  
  if (categoryData.length >= 5) {
    carouselCategory.value = currentCategory.value;
    
    // 使用當前類別的數據，隨機排序
    const shuffled = JSON.parse(JSON.stringify(categoryData))
      .sort(() => Math.random() - 0.5);
    
    carouselItems.value = shuffled;
    console.log(`[Forum] Selected ${shuffled.length} items for carousel, category: ${carouselCategory.value}`);
  } else {
    console.log(`[Forum] Not enough items in category: ${currentCategory.value} (${categoryData.length} items)`);
    carouselItems.value = [];
    carouselCategory.value = "";
  }
};

// 獲取所有類別的資料
const fetchAllCategoryData = async () => {
  try {
    console.log('[Forum] Fetching all category data...');
    const categories = ['games', 'animations', 'movies'];
    const promises = categories.map(category => 
      axios.get(`http://localhost:8000/api/${category}/`)
    );
    
    const responses = await Promise.all(promises);
    
    responses.forEach((response, index) => {
      allCategoryData.value[categories[index]] = response.data;
      console.log(`[Forum] Loaded ${response.data.length} items for ${categories[index]}`);
    });

    // 初始化輪播數據 - 使用當前選擇的類別
    setupCarousel();
  } catch (error) {
    console.error("[Forum] API Error:", error);
  }
};

// 獲取當前類別資料
const fetchCurrentCategoryData = async () => {
  try {
    console.log(`[Forum] Fetching data for category: ${currentCategory.value}`);
    const response = await axios.get(`http://localhost:8000/api/${currentCategory.value}/`);
    items.value = response.data;
    console.log(`[Forum] Loaded ${items.value.length} items for current category`);
  } catch (error) {
    console.error("[Forum] API Error:", error);
  }
};

// 不再使用預加載和狀態控制

// Available Genres Computation - 修改為處理多重類別
const availableGenres = computed(() => {
  const genres = new Set();
  genres.add("all");
  
  items.value.forEach(item => {
    const genreString = item.game_genre || item.animation_genre || item.movie_genre || "";
    if (genreString) {
      // 將逗號分隔的類別拆分並添加到集合中
      genreString.split(',').forEach(genre => {
        const trimmedGenre = genre.trim();
        if (trimmedGenre) {
          genres.add(trimmedGenre);
        }
      });
    }
  });
  
  return Array.from(genres);
});

// 輪播可用類型 - 同樣修改為處理多重類別
const carouselGenres = computed(() => {
  const genres = new Set();
  genres.add("all");
  
  carouselItems.value.forEach(item => {
    const genreString = item.game_genre || item.animation_genre || item.movie_genre || "";
    if (genreString) {
      // 將逗號分隔的類別拆分並添加到集合中
      genreString.split(',').forEach(genre => {
        const trimmedGenre = genre.trim();
        if (trimmedGenre) {
          genres.add(trimmedGenre);
        }
      });
    }
  });
  
  return Array.from(genres);
});

// Computed Properties for carousel display
const showCarousel = computed(() => {
  const isVisible = carouselItems.value.length >= 5 && carouselCategory.value !== "";
  console.log(`[Forum] Show carousel: ${isVisible} (${carouselItems.value.length} items, category: ${carouselCategory.value})`);
  return isVisible;
});

const carouselTitle = computed(() => {
  let baseTitle = {
    games: "熱門遊戲推薦",
    animations: "熱門動畫推薦",
    movies: "熱門電影推薦"
  }[carouselCategory.value] || "";
  
  // 如果選擇了特定類型，添加到標題
  if (selectedGenre.value !== "all") {
    baseTitle += ` - ${selectedGenre.value}`;
  }
  
  return baseTitle;
});

// 判斷當前是否在首頁
const isHomePage = computed(() => {
  return route.path === '/Forum' || route.path === '/Forum/';
});

// 處理輪播滾動位置變化
const handleCarouselScroll = (position) => {
  carouselScrollPosition.value = position;
  // 保存到 localStorage
  localStorage.setItem("carouselScrollPosition", position.toString());
  localStorage.setItem("carouselCategory", carouselCategory.value);
  localStorage.setItem("carouselGenre", selectedGenre.value);
  console.log(`[Forum] Saved carousel position: ${position}, category: ${carouselCategory.value}, genre: ${selectedGenre.value}`);
};

// 修改 changeCategory 函數，切換類別時更新輪播
const changeCategory = (category) => {
  if (category === currentCategory.value) return;
  
  // 保存當前輪播狀態
  localStorage.setItem("previousCarouselScrollPosition", carouselScrollPosition.value.toString());
  localStorage.setItem("previousCarouselCategory", carouselCategory.value);
  localStorage.setItem("previousCarouselGenre", selectedGenre.value);
  
  currentCategory.value = category;
  currentPage.value = 1;
  searchQuery.value = "";
  selectedGenre.value = "all";
  
  // 更新路由
  router.push({ 
    path: "/Forum", 
    query: { category, page: 1, search: "", genre: "all" } 
  });
  
  // 獲取當前類別數據
  fetchCurrentCategoryData();
  
  // 更新輪播數據以匹配新類別
  setupCarousel();
  
  // 重置輪播位置
  carouselScrollPosition.value = 0;
};

const navigateToDetail = (item) => {
  console.log('[Forum] Navigating to detail:', item);
  const id = item.id || item.game_id || item.animation_id || item.movie_id;
  
  // 保存當前狀態
  localStorage.setItem("scrollPosition", window.scrollY.toString());
  localStorage.setItem("searchQuery", searchQuery.value);
  localStorage.setItem("selectedGenre", selectedGenre.value);
  localStorage.setItem("carouselScrollPosition", carouselScrollPosition.value.toString());
  localStorage.setItem("carouselCategory", carouselCategory.value);
  localStorage.setItem("carouselGenre", selectedGenre.value);
  
  router.push({
    path: `/detail/${currentCategory.value}/${id}`,
    query: { 
      category: currentCategory.value, 
      page: currentPage.value, 
      search: searchQuery.value,
      genre: selectedGenre.value,
      from: "forum"
    }
  });
};

// 新增：控制推薦模組顯示
const toggleRecommendation = () => {
  showRecommendation.value = !showRecommendation.value;
  
  // 如果關閉推薦，滾動回頁面頂部
  if (!showRecommendation.value) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

// Utility Functions - 使用與輪播組件相同的圖片處理邏輯
const getGameImage = (gameTitle) => {
  if (!gameTitle) return '/images/default-poster.jpg';
  
  // 使用與輪播組件相同的方式處理
  return `/images/games/${encodeURIComponent(gameTitle)}.jpg`;
};

// Filtered and Paginated Items - 修改為正確處理多重類別
const filteredItems = computed(() => {
  return items.value.filter((item) => {
    const title = item.game_title || item.animation_title || item.movie_title || "";
    const year = item.release_date || "";
    const genreString = item.game_genre || item.animation_genre || item.movie_genre || "";
    // 將類別字串分割成陣列，便於多重類別匹配
    const genres = genreString.split(',').map(g => g.trim());
    
    const matchesSearch = searchQuery.value ?
      title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      year.includes(searchQuery.value) ||
      genres.some(g => g.toLowerCase().includes(searchQuery.value.toLowerCase()))
      : true;
    
    // 檢查是否匹配任何一個類別
    const matchesGenre = selectedGenre.value === "all" || 
                          genres.includes(selectedGenre.value);
    
    return matchesSearch && matchesGenre;
  });
});

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredItems.value.length / itemsPerPage.value));
});

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredItems.value.slice(start, end);
});

// Event Handlers
const handleGenreChange = (event) => {
  selectedGenre.value = event.target.value;
  currentPage.value = 1;
  
  // 更新路由
  router.push({
    path: "/Forum",
    query: {
      category: currentCategory.value,
      page: 1,
      search: searchQuery.value,
      genre: selectedGenre.value
    }
  });
  
  // 當類型變更時重置輪播位置
  carouselScrollPosition.value = 0;
};

// 輪播類型變更處理
const handleCarouselGenreChange = (event) => {
  selectedGenre.value = event.target.value;
  
  // 更新路由但保持在當前頁
  router.push({
    path: "/Forum",
    query: {
      category: currentCategory.value,
      page: currentPage.value,
      search: searchQuery.value,
      genre: selectedGenre.value
    }
  });
  
  // 重置輪播位置
  carouselScrollPosition.value = 0;
};

// 搜索處理函數
const handleSearch = () => {
  currentPage.value = 1;
  
  router.push({
    path: "/Forum",
    query: {
      category: currentCategory.value,
      page: 1,
      search: searchQuery.value,
      genre: selectedGenre.value
    }
  });
};

// 清空搜索
const clearSearch = () => {
  searchQuery.value = "";
  handleSearch();
};

// 按下 Enter 鍵進行搜索
const handleSearchKeyDown = (event) => {
  if (event.key === 'Enter') {
    handleSearch();
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    
    // 滾動到頁面頂部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    router.push({
      path: "/Forum",
      query: { 
        category: currentCategory.value, 
        page: currentPage.value, 
        search: searchQuery.value,
        genre: selectedGenre.value
      }
    });
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    
    // 滾動到頁面頂部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    router.push({
      path: "/Forum",
      query: { 
        category: currentCategory.value, 
        page: currentPage.value, 
        search: searchQuery.value,
        genre: selectedGenre.value
      }
    });
  }
};

// 恢復之前的輪播狀態
const restoreCarouselState = () => {
  // 檢查路由參數是否包含 from=detail
  const fromDetail = route.query.from === 'detail';
  const savedPosition = localStorage.getItem("carouselScrollPosition");
  const savedCategory = localStorage.getItem("carouselCategory");
  const savedGenre = localStorage.getItem("carouselGenre");
  
  // 只有從詳情頁返回時才恢復狀態
  if (fromDetail && savedPosition && savedCategory) {
    if (savedCategory === currentCategory.value) {
      carouselScrollPosition.value = parseInt(savedPosition);
      if (savedGenre) {
        selectedGenre.value = savedGenre;
      }
      console.log(`[Forum] Restored carousel position: ${carouselScrollPosition.value}, genre: ${selectedGenre.value}`);
    }
  }
};

// 不再監聽圖片狀態

// Lifecycle Hooks
onMounted(async () => {
  console.log('[Forum] Component mounted');
  
  // 從路由同步狀態
  if (route.query.search) {
    searchQuery.value = route.query.search;
  }
  
  if (route.query.genre) {
    selectedGenre.value = route.query.genre;
  }
  
  await fetchAllCategoryData();
  await fetchCurrentCategoryData();
  
  nextTick(() => {
    // 恢復頁面滾動位置
    const savedPosition = localStorage.getItem("scrollPosition");
    if (savedPosition) {
      window.scrollTo({
        top: parseInt(savedPosition),
        behavior: 'instant'
      });
      localStorage.removeItem("scrollPosition");
    }

    // 恢復搜索和過濾條件
    const savedSearch = localStorage.getItem("searchQuery");
    if (savedSearch) {
      searchQuery.value = savedSearch;
      localStorage.removeItem("searchQuery");
    }

    const savedGenre = localStorage.getItem("selectedGenre");
    if (savedGenre) {
      selectedGenre.value = savedGenre;
      localStorage.removeItem("selectedGenre");
    }
    
    // 恢復輪播狀態
    restoreCarouselState();
  });
});

// Watch for changes
watch(
  () => route.query,
  (newQuery) => {
    // 同步路由參數到本地狀態
    if (newQuery.category && newQuery.category !== currentCategory.value) {
      currentCategory.value = newQuery.category;
      fetchCurrentCategoryData();
    }
    
    if (newQuery.page) {
      currentPage.value = parseInt(newQuery.page) || 1;
    }
    
    if (newQuery.search !== undefined && newQuery.search !== searchQuery.value) {
      searchQuery.value = newQuery.search;
    }
    
    if (newQuery.genre !== undefined && newQuery.genre !== selectedGenre.value) {
      selectedGenre.value = newQuery.genre;
    }
  },
  { deep: true }
);

// 監視過濾後列表大小變化，確保頁碼有效
watch(filteredItems, (newItems) => {
  const maxPage = Math.max(1, Math.ceil(newItems.length / itemsPerPage.value));
  if (currentPage.value > maxPage) {
    currentPage.value = maxPage;
    
    router.push({
      path: "/Forum",
      query: { 
        category: currentCategory.value, 
        page: currentPage.value, 
        search: searchQuery.value,
        genre: selectedGenre.value
      }
    });
  }
}, { deep: true });
</script>

<template>
  <div class="content-wrapper">
    <!-- Carousel Section -->
    <div v-if="showCarousel" class="carousel-section">
      <div class="carousel-header">
        <h2 class="carousel-title">{{ carouselTitle }}</h2>
        
        <!-- 輪播類型選擇器 -->
        <select 
          v-if="carouselGenres.length > 1"
          class="carousel-genre-select form-select"
          v-model="selectedGenre"
          @change="handleCarouselGenreChange"
        >
          <option 
            v-for="genre in carouselGenres" 
            :key="genre" 
            :value="genre"
          >
            {{ genre === 'all' ? '全部類型' : genre }}
          </option>
        </select>
      </div>
      
      <Carousel 
        :items="carouselItems"
        :currentCategory="carouselCategory"
        :maxItems="15"
        :savedScrollPosition="carouselScrollPosition"
        :selectedGenre="selectedGenre"
        @itemClick="navigateToDetail"
        @scrollPositionChange="handleCarouselScroll"
      />
    </div>

    <div class="container py-5">
      <!-- Category Buttons -->
      <div class="text-center mb-4">
        <button 
          class="btn mx-2" 
          :class="{ 'btn-primary': currentCategory === 'games', 'btn-light': currentCategory !== 'games' }" 
          @click="changeCategory('games')"
        >
          🎮 遊戲
        </button>
        <button 
          class="btn mx-2" 
          :class="{ 'btn-primary': currentCategory === 'animations', 'btn-light': currentCategory !== 'animations' }" 
          @click="changeCategory('animations')"
        >
          📺 動畫
        </button>
        <button 
          class="btn mx-2" 
          :class="{ 'btn-primary': currentCategory === 'movies', 'btn-light': currentCategory !== 'movies' }" 
          @click="changeCategory('movies')"
        >
          🎬 電影
        </button>
      </div>

      <!-- Search Section -->
      <div class="text-center mb-4 search-container">
        <div class="search-input-group">
          <input 
            type="text" 
            class="form-control search-bar" 
            v-model="searchQuery" 
            placeholder="🔍 搜尋名稱、年份、類別" 
            @keydown="handleSearchKeyDown"
          >
          <button 
            v-if="searchQuery" 
            class="btn btn-clear" 
            @click="clearSearch"
            aria-label="清除搜尋"
          >
            ×
          </button>
        </div>
        
        <select 
          class="form-select genre-select" 
          v-model="selectedGenre"
          @change="handleGenreChange"
        >
          <option 
            v-for="genre in availableGenres" 
            :key="genre" 
            :value="genre"
          >
            {{ genre === 'all' ? '全部類型' : genre }}
          </option>
        </select>
        
        <!-- 新增：推薦功能按鈕 -->
        <button 
          class="btn btn-recommendation" 
          @click="toggleRecommendation"
          :class="{ 'active': showRecommendation }"
        >
          <span v-if="!showRecommendation">💡 智能推薦</span>
          <span v-else>✖️ 關閉推薦</span>
        </button>
      </div>
      
      <!-- 新增：推薦模組 (條件渲染) -->
      <div v-if="showRecommendation" class="recommendation-wrapper">
        <RecommendationModule />
      </div>

      <!-- Content Grid -->
      <div class="row">
        <div v-for="(item, index) in paginatedItems" :key="index" class="col-lg-2 col-md-3 col-sm-4 col-6 mb-4">
          <div class="card">
            <div class="poster-container">
              <!-- 遊戲圖片處理 -->
              <img
                v-if="currentCategory === 'games'"
                :src="getGameImage(item.game_title)"
                class="card-img-top"
                alt="Game Poster"
                @click="navigateToDetail(item)"
                @error="$event.target.src = '/images/default-poster.jpg'"
                draggable="false"
              />
              <!-- 其他類別圖片 -->
              <img
                v-else
                :src="item.poster"
                class="card-img-top"
                alt="Poster"
                @click="navigateToDetail(item)"
                @error="$event.target.src = '/images/default-poster.jpg'"
                draggable="false"
              />
            </div>
            <div class="card-body">
              <h5 class="card-title">
                {{ item.game_title || item.animation_title || item.movie_title }}
              </h5>
              <p class="card-text description">
                {{ item.game_description || item.animation_description || item.movie_description }}
              </p>
              <button class="btn btn-sm btn-outline-primary" @click="navigateToDetail(item)">
                查看詳情
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results Message -->
      <div v-if="paginatedItems.length === 0" class="no-results">
        <div class="alert alert-info text-center">
          <div class="no-results-icon">🔍</div>
          <h4>找不到符合條件的項目</h4>
          <p>請嘗試不同的搜尋關鍵字或類型</p>
          <div class="mt-3">
            <button v-if="searchQuery" class="btn btn-outline-primary mx-2" @click="clearSearch">
              清除搜尋
            </button>
            <button v-if="selectedGenre !== 'all'" class="btn btn-outline-primary mx-2" @click="selectedGenre = 'all'; handleGenreChange($event)">
              顯示所有類型
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredItems.length > 0" class="pagination-buttons text-center mt-4">
        <button 
          class="btn btn-outline-primary mx-2" 
          @click="prevPage" 
          :disabled="currentPage === 1"
        >
          ⬅️ 上一頁
        </button>
        <span class="page-indicator">第 {{ currentPage }} 頁 / 共 {{ totalPages }} 頁</span>
        <button 
          class="btn btn-outline-primary mx-2" 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
        >
          下一頁 ➡️
        </button>
      </div>
    </div>

    <!-- 討論區部分 -->
    <div v-if="isHomePage" class="discussion-wrapper">
      <div class="section-divider">
        <h2 class="section-title">社群討論</h2>
        <div class="divider-line"></div>
      </div>
      
      <!-- 引入討論區精簡版組件 -->
      <DiscussionSection />
    </div>

    <!-- 路由視圖 - 顯示子路由 -->
    <div>
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.content-wrapper {
  margin-top: 100px;
}

.carousel-section {
  margin: 0 0 2rem 0;
  position: relative;
}

.carousel-header {
  position: absolute;
  top: -40px; /* 負值會使元素向上移動 */
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.carousel-title {
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.carousel-genre-select {
  width: 150px;
  padding: 5px 10px;
  font-size: 1rem;
  border-radius: 5px;
}

.search-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  align-items: center;
}

.search-input-group {
  position: relative;
  width: 40%;
}

.search-bar {
  width: 100%;
  margin: 0;
  padding: 10px 30px 10px 10px;
  font-size: 16px;
}

.btn-clear {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 20px;
  font-weight: bold;
  color: #666;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.genre-select {
  width: 150px;
  padding: 10px;
  font-size: 16px;
}

/* 推薦功能按鈕樣式 */
.btn-recommendation {
  background-color: #6c5ce7;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.btn-recommendation:hover {
  background-color: #5846e7;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-recommendation.active {
  background-color: #e74c3c;
}

/* 推薦模組容器 */
.recommendation-wrapper {
  margin: 20px 0;
  padding: 15px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.card {
  margin-bottom: 5px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  height: 100%;
  min-width: 220px;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.poster-container {
  height: 300px;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-img-top {
  width: 100%;
  height: auto;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.card-img-top:hover {
  transform: scale(1.05);
}

.card-title {
  font-size: 1.1rem;
  margin: 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.description {
  font-size: 0.9rem;
  line-height: 1.5;
  height: 4.5em;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.no-results {
  margin: 30px 0;
  padding: 20px;
}

.no-results-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.pagination-buttons {
  margin-top: 2rem;
}

.page-indicator {
  margin: 0 1rem;
  font-size: 1.1rem;
}

/* 討論區樣式 */
.discussion-wrapper {
  max-width: 1600px;
  margin: 60px auto;
  padding: 0 20px;
}

.section-divider {
  margin: 40px 0;
  text-align: center;
  position: relative;
}

.section-title {
  display: inline-block;
  background: #fff;
  padding: 0 20px;
  position: relative;
  z-index: 1;
  font-size: 30px;
  color: #333;
}

.divider-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #ddd;
  z-index: 0;
}

@media (max-width: 768px) {
  .search-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input-group {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .search-bar {
    width: 100%;
  }
  
  .genre-select {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .btn-recommendation {
    width: 100%;
    margin-top: 10px;
  }
  
  .carousel-header {
    flex-direction: column;
  }
  
  .carousel-genre-select {
    width: 100%;
  }
  
  .section-title {
    font-size: 24px;
  }
}
</style>