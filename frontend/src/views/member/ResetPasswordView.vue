<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';
import { useUserStore } from '@/stores/user'; // 引入用於處理認證的 Store

const route = useRoute(); // 獲取當前路由
const router = useRouter(); // 用於路由跳轉
const authStore = useUserStore(); // Pinia 用戶狀態

const BASE_URL = import.meta.env.VITE_MemberApi;
const code = route.params.code || localStorage.getItem('resetCode'); // 優先從 URL 提取，否則從 localStorage 獲取
if (!code) {
  alert('重置密碼鏈接無效或缺失，請重新請求重置密碼。');
  router.push({ name: 'home' }); // 跳轉到主頁
}
const API_URL = `${BASE_URL}reset/${code}/`;

// 表單數據
const formData = ref({
    new_password: '',
    confirm_password: ''
})

// 錯誤信息
const errors = ref({
    new_password: '',
    confirm_password: '',
    general: ''
})

// 表單狀態
const isSubmitting = ref(false)

// 提交表單
const handleResetPassword = async (event) => {
      event.preventDefault();
      let isValid = true

      // 驗證新密碼
      const passwordError = authStore.validatePassword(formData.value.new_password);
      if (passwordError) {
        errors.value.new_password = passwordError;
        isValid = false;
      } else {
        errors.value.new_password = ''; // 清空錯誤信息
      }

      // 驗證確認密碼
      if (!formData.value.confirm_password) {
        errors.value.confirm_password = '請確認密碼';
        isValid = false;
      } else if (formData.value.new_password !== formData.value.confirm_password) {
        errors.value.confirm_password = '兩次輸入的密碼不一致，請再次確認';
        isValid = false;
      } else {
        errors.value.confirm_password = ''; // 清空錯誤信息
      }

      // 如果表單驗證失敗，停止提交
      if (!isValid) return;

      try {
        isSubmitting.value = true;
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData.value),
        });

        if (response.ok) {
          // 密碼重置成功，清空 localStorage 並登出
          authStore.logout(); // 登出並清空 localStorage
          localStorage.clear(); // 清空 localStorage

          Swal.fire('成功', '密碼重置成功，請重新登入', 'success').then(() => {
            router.push({ name: 'login' });
          });
        } else {
          const errorData = await response.json();
          throw new Error(errorData.message || '密碼重置失敗');
        }
      } catch (error) {
        Swal.fire('錯誤', error.message, 'error');
      }
    };

</script>

<template>
  <div class="page-container">
    <!-- 左側表單 -->
    <div class="form-section">
      <div class="form-content">
        <div class="text-center mb-4">	
          <RouterLink :to="{ name: 'ResetPw' }" class="app-logo">
            <img class="rounded-circle" src="@/assets/img/acgn-icon.jpg" alt="Logo" width="50" height="50">
            <h2 class="auth-heading text-center mb-4">Password Reset／密碼重置</h2>
          </RouterLink>
        </div>
        

        <div class="auth-intro mb-4 text-center">
          請於下方輸入您的新密碼，並再次確認密碼，以便為您重置。<br>
					Enter your password below. We'll reset you a new password.<br>
					提醒您，新密碼至少需要8個字符，<br>英文(不分大小寫)+數字所組成。
        </div>

        <div class="auth-form-container text-left">
          <!-- 錯誤/成功信息顯示 -->
          <div v-if="errors.general" 
               :class="{'alert alert-danger': errors.general.includes('失敗') || errors.general.includes('錯誤'),
                       'alert alert-success': errors.general.includes('成功')}" 
               role="alert">
            {{ errors.general }}
          </div>

          <form class="auth-form resetpass-form" @submit="handleResetPassword">
            <div class="email mb-3">
              <label class="sr-only" for="newpassword">新密碼</label>
              <input 
                id="newpassword" 
                v-model="formData.new_password"
                type="password" 
                class="form-control login-email" 
                :class="{ 'is-invalid': errors.new_password }"
                placeholder="新密碼" 
                required
              >
              <div v-if="errors.new_password" class="invalid-feedback">
                {{ errors.new_password }}
              </div>
            </div>
            <div class="email mb-3">
              <label class="sr-only" for="ConfirmPassword">確認密碼</label>
              <input 
                id="ConfirmPassword" 
                v-model="formData.confirm_password"
                type="password" 
                class="form-control login-email" 
                :class="{ 'is-invalid': errors.confirm_password }"
                placeholder="確認密碼" 
                required
              >
              <div v-if="errors.confirm_password" class="invalid-feedback">
                {{ errors.confirm_password }}
              </div>
            </div>

            <div class="text-center">
              <button
                type="submit" 
                class="btn app-btn-primary w-50 theme-btn mx-auto"
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? '發送中...' : '確認送出' }}
              </button>
            </div>
          </form>
          
          <div class="auth-option text-center pt-5">
            <RouterLink :to="{ name: 'login' }" class="app-link">Log in／登入</RouterLink>
            <span class="px-2">|</span>
            <RouterLink :to="{ name: 'signup' }" class="app-link">Sign up／註冊</RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- 右側背景 -->
    <div class="background-section">
      <div class="bg-image"></div>
    </div>   
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  width: 100%;
  min-height: calc(100vh - 56px);
}

.form-section {
  width: 100%;
  display: flex;
  justify-content: center;
  padding-top: 8rem;
}

.form-content {
  width: 100%;
  max-width: 500px;
  padding: 2rem;
  margin: 0 auto;
}

.auth-intro {
  color: #666;
  font-size: 0.875rem;
}

.invalid-feedback {
  display: block;
  text-align: left;
}

.app-btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.app-link {
  color: #15a362;
  text-decoration: none;
}

.app-link:hover {
  text-decoration: underline;
}
</style>