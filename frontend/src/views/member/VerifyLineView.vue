<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import Swal from 'sweetalert2';

const route = useRoute();
const router = useRouter();

const userStore = useUserStore();

const BASE_URL = import.meta.env.VITE_MemberApi
const LINE_URL = `${BASE_URL}auth/line-login/`

const isLoading = ref(true); // 驗證中標誌
const errorMessage = ref(''); // 儲存錯誤訊息

const verifyLineLogin = async () => {
  const code = route.query.code;
  const state = route.query.state;

  if (!code || !state) {
    errorMessage.value = '缺少必要的參數 (code 或 state)';
    console.error(errorMessage.value);
    alert(errorMessage.value);
    return;
  }
  console.log("請求的 body:", { code, state });

  try {
    const response = await fetch(LINE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP Error: ${response.status}`);
    }

    const data = await response.json();
    console.log('驗證成功:', data);

    // 同步用戶數據
    userStore.setUser(data.user, data.tokens.access, data.tokens.refresh);

    // 存儲 用戶數據 到 localStorage
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);

    console.log("資料已同步到 useUserStore:", userStore.user);

    // 跳轉到中心頁面，並傳遞 user_id
    const result = await Swal.fire({
        title: '即將跳轉至會員中心',
        text: '提醒您登入後立即修改密碼與手機號，以便後續登入哦~',
        icon: 'info',
        confirmButtonText: '確定'
    })
    if (result.isConfirmed) {
      router.push({ name: 'center', params: { user_id: data.user.user_id } });
    }
  } catch (err) {
    console.error('驗證失敗:', err.message);
    errorMessage.value = `登入失敗: ${err.message}`;
    alert(errorMessage.value);
  } finally {
    isLoading.value = false; // 結束驗證
  }
};

// 組件掛載時執行驗證
onMounted(() => {
  verifyLineLogin();
});
</script>

<template>
  <div class="verification-container">
    <!-- 驗證中提示 -->
    <div v-if="isLoading" class="loading-indicator">
      正在驗證您的 Line 帳戶，請稍候...
    </div>

    <!-- 錯誤提示 -->
    <div v-else-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>
  </div>
</template>

<style scoped>
.loading-indicator {
  text-align: center;
  margin-top: 20px;
  font-size: 18px;
  color: #555;
}
.alert {
  margin-top: 20px;
  font-size: 16px;
}
</style>