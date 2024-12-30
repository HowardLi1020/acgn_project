<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const route = useRoute(); // 獲取當前路由
const router = useRouter(); // 用於路由跳轉
const isVerificationPopupVisible = ref(false);

const BASE_URL = import.meta.env.VITE_MemberApi;
const code = route.params.code; // 提取 URL 中的令牌
const status = route.query.status; // 提取 URL 中的查询参数
const API_URL = `${BASE_URL}reset/${code}/`;

// 處理 URL 中的 status 參數
const handleStatusResponse = () => {
  if (status === 'success') {
    isVerificationPopupVisible.value = true; // 顯示成功彈窗
  } else if (status === 'invalid') {
    Swal.fire('驗證失敗', '您的驗證鏈接無效', 'error');
  } else if (status === 'expired') {
    Swal.fire('驗證失敗', '您的驗證鏈接已過期', 'error');
  } else {
    Swal.fire('錯誤', '無法驗證電子郵件，請稍後再試', 'error');
  }
};

// 向後端發送請求驗證
const handleBackendVerification = async () => {
  try {
    const response = await fetch(API_URL); // 調用後端 API
    const data = await response.json(); // 獲取 JSON 數據
    if (data.message === 'success') {
      isVerificationPopupVisible.value = true; // 顯示成功彈窗
    } else {
      Swal.fire('驗證失敗', '您的驗證鏈接無效或已過期', 'error');
    }
  } catch (error) {
    console.error('API 調用失敗:', error);
    Swal.fire('錯誤', '無法驗證電子郵件，請稍後再試', 'error');
  }
};

// 跳轉到登入頁
const RouterPushToLogin = () => {
  isVerificationPopupVisible.value = false; // 關閉彈窗
  router.push({ name: 'ResetPw' }) // 假設 Vue Router 已配置登入路徑
};

// 組件掛載後執行邏輯
onMounted(async () => {
  if (code) {
    localStorage.setItem('resetCode', code); // 保存 code 到 localStorage
  }

  if (status) {
    handleStatusResponse(); // 如果有 status，處理 URL 中的驗證結果
  } else {
    await handleBackendVerification(); // 如果無 status，調用後端驗證
  }
});

</script>
  
  <template>
    <div v-if="isVerificationPopupVisible" class="popup-overlay">
      <div class="popup-content">
        <h2>驗證成功</h2>
        <p>您的重置密碼連結已成功驗證！即將進入重置密碼。</p>
        <button @click="RouterPushToLogin" class="btn btn-primary btn-sm">前往重置密碼頁面</button>
      </div>
    </div>
  </template>


  <style scoped>
  .verify-email {
    text-align: center;
    font-size: 18px;
    margin-top: 50px;
  }

  .popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.popup-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.popup-content h2 {
  margin-bottom: 10px;
}

.popup-content button {
  margin-top: 15px;
}
  </style>
  