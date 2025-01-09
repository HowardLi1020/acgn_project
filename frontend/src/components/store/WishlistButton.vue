<script setup>
import { ref, onMounted } from 'vue';
import { defineProps } from 'vue';
import Swal from 'sweetalert2';

const props = defineProps({
  productId: {
    type: [String, Number],
    required: true
  },
  isIcon: {
    type: Boolean,
    default: false
  }
});

const isInWishlist = ref(false);
const isLoading = ref(false);

const apiUrl = import.meta.env.VITE_APIURL;

// 檢查是否已收藏
const checkWishlistStatus = async () => {
  try {
    const token = localStorage.getItem('access_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

        const response = await fetch(`${apiUrl}/store/wishlist/check/${props.productId}/`, {
            credentials: 'include',
            headers
        });

    if (!response.ok) throw new Error('檢查收藏狀態失敗');

    const data = await response.json();
    isInWishlist.value = data.is_in_wishlist;
  } catch (error) {
    console.error('檢查收藏狀態失敗:', error);
  }
};

// 切換收藏狀態
const toggleWishlist = async () => {
    try {
        isLoading.value = true;
        const token = localStorage.getItem('access_token');

        if (!token) {
            Swal.fire({
                title: '請先登入',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: '前往登入',
                cancelButtonText: '取消'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/login';
                }
            });
            return;
        }

        const response = await fetch(`${apiUrl}/store/wishlist/toggle/${props.productId}/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('操作失敗');

        const data = await response.json();
        isInWishlist.value = data.is_in_wishlist;

        Swal.fire({
            icon: 'success',
            title: isInWishlist.value ? '已加入收藏' : '已取消收藏',
            showConfirmButton: false,
            timer: 1500
        });

    } catch (error) {
        console.error('切換收藏狀態失敗:', error);
        Swal.fire({
            icon: 'error',
            title: '操作失敗',
            text: '請稍後再試'
        });
    } finally {
        isLoading.value = false;
    }
};

onMounted(checkWishlistStatus);
</script>

<template>
  <!-- 圖標版本 -->
  <div v-if="isIcon" 
       class="wishlist-icon"
       @click="toggleWishlist"
       :class="{ active: isInWishlist, loading: isLoading }">
    <i class="fas" :class="isInWishlist ? 'fa-star' : 'fa-star-o'"></i>
  </div>
  
  <!-- 按鈕版本 -->
  <button v-else
    class="wishlist-btn"
    :class="{ active: isInWishlist }"
    @click="toggleWishlist"
    :disabled="isLoading"
  >
    <i class="fas" :class="isInWishlist ? 'fa-heart' : 'fa-heart-o'"></i>
    {{ isInWishlist ? '已收藏' : '收藏' }}
  </button>
</template>

<style scoped>
.wishlist-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.wishlist-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  cursor: pointer;
  z-index: 1;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.wishlist-icon i {
  color: #666;
  font-size: 1.2rem;
}

.wishlist-icon.active i {
  color: #ffd700;
}

.wishlist-icon:hover {
  transform: scale(1.1);
}

.wishlist-btn:hover {
  border-color: #15a362;
  color: #15a362;
}

.wishlist-btn.active {
  background: #15a362;
  border-color: #15a362;
  color: white;
}

.wishlist-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

i {
  font-size: 1.2rem;
}
</style>