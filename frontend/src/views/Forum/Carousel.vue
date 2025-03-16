<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  },
  currentCategory: {
    type: String,
    required: true
  },
  maxItems: {
    type: Number,
    default: 15  // 一次顯示15筆
  },
  savedScrollPosition: {
    type: Number,
    default: 0
  },
  selectedGenre: {
    type: String,
    default: 'all'
  }
});

const emit = defineEmits(['itemClick', 'scrollPositionChange']);

// 輪播狀態
const scrollContainer = ref(null);
const isHovering = ref(false);
const isDragging = ref(false);
const dragStartTime = ref(0);
const startX = ref(0);
const scrollLeft = ref(0);
const autoScrollInterval = ref(null);
const currentScrollPosition = ref(0);
const isTransitioning = ref(false);
const cardWidth = ref(200); // 預設卡片寬度
const cardGap = ref(20);    // 預設卡片間距
const isAutoScrollPaused = ref(false); // 新增：標記自動滾動是否暫停

// 過濾符合選定類型的項目
const filteredItems = computed(() => {
  if (props.selectedGenre === 'all') {
    return props.items;
  }
  
  return props.items.filter(item => {
    const genre = item.game_genre || item.animation_genre || item.movie_genre || '';
    const genres = genre.split(',').map(g => g.trim());
    return genres.includes(props.selectedGenre);
  });
});

// 創建循環顯示用的項目陣列 - 前後各複製一組以實現無縫循環
const displayItems = computed(() => {
  if (filteredItems.value.length === 0) {
    return [];
  }
  
  const maxToShow = Math.min(props.maxItems, filteredItems.value.length);
  const items = filteredItems.value.slice(0, maxToShow);
  
  // 創建三組項目: 前面一組、中間一組(原始)、後面一組
  return [...items, ...items, ...items];
});

// 計算實際顯示的項目數量
const visibleItemCount = computed(() => {
  if (!scrollContainer.value) return 0;
  return Math.floor(scrollContainer.value.clientWidth / (cardWidth.value + cardGap.value));
});

// 計算每組項目的總寬度
const groupWidth = computed(() => {
  const count = Math.min(props.maxItems, filteredItems.value.length);
  return count * (cardWidth.value + cardGap.value);
});

// 保存滾動位置
const saveScrollPosition = () => {
  if (!scrollContainer.value || isTransitioning.value) return;
  
  const totalWidth = groupWidth.value;
  if (totalWidth <= 0) return;
  
  // 計算真實位置 (相對於中間組)
  let realPosition = scrollContainer.value.scrollLeft % totalWidth;
  if (realPosition < 0) realPosition += totalWidth;
  
  currentScrollPosition.value = realPosition;
  emit('scrollPositionChange', realPosition);
};

// 拖曳功能
const startDrag = (e) => {
  if (isTransitioning.value) return;
  
  isDragging.value = true;
  dragStartTime.value = Date.now();
  startX.value = e.pageX || (e.touches && e.touches[0] ? e.touches[0].pageX : 0);
  scrollLeft.value = scrollContainer.value.scrollLeft;
  
  document.body.style.cursor = 'grabbing';
  stopAutoScroll();
  
  // 防止觸發後續點擊事件
  e.preventDefault();
};

const doDrag = (e) => {
  if (!isDragging.value) return;
  
  const pageX = e.pageX || (e.touches && e.touches[0] ? e.touches[0].pageX : 0);
  if (!pageX) return;
  
  const x = pageX;
  const walk = (startX.value - x) * 1.2; // 調低靈敏度以減少跳動
  
  if (scrollContainer.value) {
    scrollContainer.value.scrollLeft = scrollLeft.value + walk;
    checkInfiniteScroll(false);
  }
  
  // 防止頁面滾動
  e.preventDefault();
};

const stopDrag = (e) => {
  if (!isDragging.value) return;
  
  // 計算拖曳持續時間和距離，判斷是否是點擊
  const dragTime = Date.now() - dragStartTime.value;
  const dragDistance = Math.abs(scrollContainer.value.scrollLeft - scrollLeft.value);
  
  isDragging.value = false;
  document.body.style.cursor = '';
  
  saveScrollPosition();
  
  // 只有在短時間小距離拖曳時才視為點擊
  const isClick = dragTime < 200 && dragDistance < 10;
  if (isClick && e.target.closest('.carousel-card')) {
    // 這裡不做任何處理，讓點擊事件自然傳播
  }
  
  if (!isHovering.value) {
    // 標記自動滾動暫停，並設置2秒後恢復
    isAutoScrollPaused.value = true;
    setTimeout(() => {
      isAutoScrollPaused.value = false;
      if (!isHovering.value && !isDragging.value) {
        startAutoScroll();
      }
    }, 2000);
  }
};

// 無限循環滾動處理
const checkInfiniteScroll = (smooth = true) => {
  if (!scrollContainer.value || displayItems.value.length === 0 || isTransitioning.value) {
    return;
  }
  
  const container = scrollContainer.value;
  const totalWidth = groupWidth.value;
  if (totalWidth <= 0) return;
  
  // 檢測滾動位置，確保中間組始終可見
  if (container.scrollLeft < totalWidth * 0.5) {
    // 快到第一組結束時，跳到第二組相同位置
    isTransitioning.value = true;
    container.style.scrollBehavior = smooth ? 'smooth' : 'auto';
    container.scrollLeft += totalWidth;
    
    // 等待滾動完成
    setTimeout(() => {
      container.style.scrollBehavior = 'auto';
      isTransitioning.value = false;
    }, smooth ? 500 : 0);
  }
  else if (container.scrollLeft > totalWidth * 1.5) {
    // 快到第三組開始時，跳到第二組相同位置
    isTransitioning.value = true;
    container.style.scrollBehavior = smooth ? 'smooth' : 'auto';
    container.scrollLeft -= totalWidth;
    
    // 等待滾動完成
    setTimeout(() => {
      container.style.scrollBehavior = 'auto';
      isTransitioning.value = false;
    }, smooth ? 500 : 0);
  }
  
  saveScrollPosition();
};

// 左右按鈕循環滾動
const scrollToNext = () => {
  if (!scrollContainer.value || isTransitioning.value) return;
  
  // 滾動一個卡片的寬度
  const scrollAmount = cardWidth.value + cardGap.value;
  scrollContainer.value.style.scrollBehavior = 'smooth';
  scrollContainer.value.scrollLeft += scrollAmount;
  
  // 檢查是否需要循環
  setTimeout(() => {
    checkInfiniteScroll(true);
  }, 300);
};

const scrollToPrev = () => {
  if (!scrollContainer.value || isTransitioning.value) return;
  
  // 滾動一個卡片的寬度
  const scrollAmount = cardWidth.value + cardGap.value;
  scrollContainer.value.style.scrollBehavior = 'smooth';
  scrollContainer.value.scrollLeft -= scrollAmount;
  
  // 檢查是否需要循環
  setTimeout(() => {
    checkInfiniteScroll(true);
  }, 300);
};

// 自動滾動 - 使用 requestAnimationFrame 實現平滑滾動
let animationFrameId = null;
const autoScrollSpeed = 1.0; // 增加滾動速度，原本為0.5

const startAutoScroll = () => {
  console.log('[Carousel] Try to start auto scroll:', {
    isHovering: isHovering.value,
    isDragging: isDragging.value,
    isPaused: isAutoScrollPaused.value,
    hasContainer: !!scrollContainer.value
  });

  if (isHovering.value || isDragging.value || isAutoScrollPaused.value || !scrollContainer.value) return;
  
  console.log('[Carousel] Auto scroll starting');
  stopAutoScroll();
  
  const scroll = () => {
    if (scrollContainer.value && !isTransitioning.value && !isHovering.value && !isDragging.value && !isAutoScrollPaused.value) {
      scrollContainer.value.scrollLeft += autoScrollSpeed;
      checkInfiniteScroll(false);
    }
    animationFrameId = requestAnimationFrame(scroll);
  };
  
  animationFrameId = requestAnimationFrame(scroll);
};

const stopAutoScroll = () => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }
};

const handleMouseEnter = () => {
  isHovering.value = true;
  stopAutoScroll();
};

const handleMouseLeave = () => {
  isHovering.value = false;
  if (!isDragging.value && !isAutoScrollPaused.value) {
    startAutoScroll();
  }
};

// 手動滾動控制 - 修正方向按鈕
const handleManualScrollLeft = () => {
  stopAutoScroll();
  scrollToPrev(); // 修正為向左滾動
  
  // 短暫延遲後恢復自動滾動
  isAutoScrollPaused.value = true;
  setTimeout(() => {
    isAutoScrollPaused.value = false;
    if (!isHovering.value && !isDragging.value) {
      startAutoScroll();
    }
  }, 2000);
};

const handleManualScrollRight = () => {
  stopAutoScroll();
  scrollToNext(); // 修正為向右滾動
  
  // 短暫延遲後恢復自動滾動
  isAutoScrollPaused.value = true;
  setTimeout(() => {
    isAutoScrollPaused.value = false;
    if (!isHovering.value && !isDragging.value) {
      startAutoScroll();
    }
  }, 2000);
};

const handleItemClick = (item, event) => {
  // 防止拖曳後誤觸發點擊
  if (isDragging.value || isTransitioning.value) {
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  
  // 檢查拖曳距離，避免誤觸發
  const dragDistance = Math.abs(scrollContainer.value.scrollLeft - scrollLeft.value);
  if (dragDistance > 10) {
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  
  // 正常處理點擊事件
  console.log('[Carousel] Item clicked:', item);
  emit('itemClick', item);
};

const getItemImage = (item) => {
  if (props.currentCategory === 'games' && item.game_title) {
    return `/images/games/${encodeURIComponent(item.game_title)}.jpg`;
  } else if (item.poster) {
    return item.poster;
  }
  return '/images/default-poster.jpg';
};

const getItemTitle = (item) => {
  return item.game_title || item.animation_title || item.movie_title || 'Untitled';
};

// 測量卡片實際寬度
const measureCardDimensions = () => {
  if (!scrollContainer.value) return;
  
  nextTick(() => {
    const cards = scrollContainer.value.querySelectorAll('.carousel-card');
    if (cards.length > 0) {
      const firstCard = cards[0];
      const style = window.getComputedStyle(firstCard);
      
      // 測量實際寬度和間距
      cardWidth.value = firstCard.offsetWidth;
      cardGap.value = parseInt(style.marginLeft) + parseInt(style.marginRight);
      
      console.log(`[Carousel] Measured card width: ${cardWidth.value}px, gap: ${cardGap.value}px`);
      
      // 根據保存的滾動位置初始化
      initializeScrollPosition();
    }
  });
};

// 初始化滾動位置
const initializeScrollPosition = () => {
  if (!scrollContainer.value) return;
  
  const totalWidth = groupWidth.value;
  if (totalWidth <= 0) return;
  
  // 設置到中間組的開始位置，加上保存的位置
  let targetPosition = totalWidth;
  if (props.savedScrollPosition !== undefined) {
    targetPosition += props.savedScrollPosition;
  }
  
  // 先禁用動畫，設置位置
  scrollContainer.value.style.scrollBehavior = 'auto';
  scrollContainer.value.scrollLeft = targetPosition;
  
  // 恢復動畫設置
  setTimeout(() => {
    scrollContainer.value.style.scrollBehavior = 'smooth';
  }, 100);
};

// 觸摸事件處理
const handleTouchStart = (e) => {
  if (e.touches && e.touches.length === 1) {
    startDrag(e);
  }
};

const handleTouchMove = (e) => {
  if (e.touches && e.touches.length === 1) {
    doDrag(e);
  }
};

const handleTouchEnd = (e) => {
  stopDrag(e);
};

// 初始化
const initializeCarousel = () => {
  // 測量卡片尺寸
  measureCardDimensions();
  
  // 添加滾動事件監聽
  if (scrollContainer.value) {
    scrollContainer.value.addEventListener('scroll', () => {
      if (!isDragging.value && !isTransitioning.value) {
        // 節流滾動事件處理
        if (!scrollContainer.value.scrollThrottle) {
          scrollContainer.value.scrollThrottle = setTimeout(() => {
            checkInfiniteScroll(false);
            scrollContainer.value.scrollThrottle = null;
          }, 100);
        }
      }
    });
  }
  
  // 啟動自動滾動 (確保初始化時立即開始)
  isAutoScrollPaused.value = false;
  startAutoScroll();
};

// 生命週期鉤子
onMounted(() => {
  console.log('[Carousel] Mounted with category:', props.currentCategory);
  initializeCarousel();
  
  // 延遲1秒後強制啟動自動輪播
  setTimeout(() => {
    console.log('[Carousel] Force starting auto-scroll');
    isHovering.value = false;
    isDragging.value = false;
    isAutoScrollPaused.value = false;
    startAutoScroll();
  }, 1000);
});

onUnmounted(() => {
  stopAutoScroll();
  
  // 清理防抖計時器
  if (scrollContainer.value && scrollContainer.value.scrollThrottle) {
    clearTimeout(scrollContainer.value.scrollThrottle);
  }
});

// 監聽 props 變化
watch([() => props.items, () => props.currentCategory, () => props.selectedGenre], 
  ([newItems, newCategory, newGenre]) => {
    console.log('[Carousel] Props updated:', { 
      category: newCategory, 
      genre: newGenre,
      itemCount: newItems.length 
    });
    
    // 重置位置並重新初始化
    nextTick(() => {
      initializeCarousel();
    });
  }, { immediate: false, deep: true });

// 視窗大小變化時重新測量
const handleResize = () => {
  measureCardDimensions();
};

// 監聽視窗大小變化
onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<template>
  <div 
    v-if="displayItems.length > 0" 
    class="horizontal-carousel-container"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <button 
      class="nav-button prev" 
      @click.stop="handleManualScrollLeft"
      aria-label="上一項"
    >❮</button>
    
    <div 
      class="carousel-scroll-container" 
      ref="scrollContainer"
      @mousedown="startDrag"
      @mousemove="doDrag"
      @mouseup="stopDrag"
      @mouseleave="stopDrag"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <div 
        v-for="(item, index) in displayItems" 
        :key="`${item.id || ''}-${index}`" 
        class="carousel-card"
        @click="(e) => handleItemClick(item, e)"
      >
        <div class="card-image-container">
          <img
            :src="getItemImage(item)"
            :alt="getItemTitle(item)"
            class="card-image"
            @error="$event.target.src = '/images/default-poster.jpg'"
            draggable="false"
          />
          <div class="card-overlay">
            <h3 class="card-title">{{ getItemTitle(item) }}</h3>
          </div>
        </div>
      </div>
    </div>
    
    <button 
      class="nav-button next" 
      @click.stop="handleManualScrollRight"
      aria-label="下一項"
    >❯</button>
  </div>
</template>

<style scoped>
.horizontal-carousel-container {
  position: relative;
  width: 100%;
  padding: 20px 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  margin-top: 200px; /* 增加上方間距 150px (原本30px + 150px = 180px) */
}

.carousel-scroll-container {
  display: flex;
  overflow-x: auto;
  scroll-behavior: smooth;
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
  padding: 10px 0;
  flex: 1;
  cursor: grab;
  user-select: none;
  position: relative;
  will-change: transform, scroll-position;
}

.carousel-scroll-container:active {
  cursor: grabbing;
}

/* 隱藏滾動條 */
.carousel-scroll-container::-webkit-scrollbar {
  display: none;
}

.carousel-card {
  flex: 0 0 auto;
  width: 200px;
  height: 300px;
  margin: 0 10px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  pointer-events: auto;
  will-change: transform;
}

.carousel-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.card-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  user-drag: none;
  -webkit-user-drag: none;
}

.carousel-card:hover .card-image {
  transform: scale(1.1);
}

.card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 15px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  transition: background 0.3s ease;
}

.card-title {
  color: white;
  margin: 0;
  font-size: 1rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border: 2px solid white;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
}

.nav-button:hover {
  background-color: rgba(0, 0, 0, 0.8);
  transform: translateY(-50%) scale(1.1);
}

.prev {
  left: 10px;
}

.next {
  right: 10px;
}

@media (max-width: 768px) {
  .carousel-card {
    width: 160px;
    height: 240px;
  }
  
  .card-title {
    font-size: 0.9rem;
  }
  
  .nav-button {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
}
</style>