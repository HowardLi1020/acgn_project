<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user'; // 引入用於處理認證的 Store

const authStore = useUserStore(); // 用於獲取登入狀態和用戶信息

const BASE_URL = import.meta.env.VITE_MemberApi;
const API_URL = `${BASE_URL}reset/`;

// 表單數據
const formData = ref({
    user_email: ''
});

// 錯誤信息
const errors = ref({
    user_email: '',
    general: ''
});

// 表單狀態
const isSubmitting = ref(false);
const isSuccess = ref(false); // 控制成功樣式

// 用戶是否已登入
const isLoggedIn = ref(authStore.isAuthenticated); // 判斷用戶是否登入

// 在已登入情況下初始化電子郵箱
onMounted(() => {
    if (isLoggedIn.value) {
        const userEmail = authStore.user?.user_email; // 獲取用戶的郵箱（儲在 authStore.user）
        if (userEmail) {
            formData.value.user_email = userEmail;
        }
    }
});

// 驗證電子郵件格式
const validateEmail = (email) => {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
};

// 驗證表單
const validateForm = () => {
    let isValid = true;
    errors.value.user_email = '';

    // 驗證電子郵箱
    const emailError = authStore.validateEmail(formData.value.user_email);
    if (emailError) {
      errors.value.user_email = emailError;
      isValid = false;
    }

    if (!isLoggedIn.value) {
        // 如果未登入，用戶必須輸入電子郵箱
        if (!formData.value.user_email) {
            errors.value.user_email = '請輸入電子郵箱';
            isValid = false;
        } else if (!validateEmail(formData.value.user_email)) {
            errors.value.user_email = '請輸入有效的電子郵箱格式';
            isValid = false;
        }
    }

    return isValid;
};

// 提交表單
const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    try {
        isSubmitting.value = true;

        const headers = {
            'Content-Type': 'application/json',
        };
        if (isLoggedIn.value) {
            headers.Authorization = `Bearer ${authStore.accessToken}`;
      }

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
              user_email: formData.value.user_email
            })
        });

        if (!response.ok) {
            // 解析錯誤訊息
            const errorData = await response.json();
            throw new Error(errorData.message || '重置密碼請求失敗');
        }

        errors.value.general = '如果電子郵箱存在，我們會發送重置連結~!';
        isSuccess.value = true;
    } catch (error) {
        errors.value.general = error.message || '發送重置密碼郵件時發生錯誤，請稍後重試';
        isSuccess.value = false;
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<template>
  <div class="page-container">
    <div class="form-section">
      <div class="form-content">
        <div class="text-center mb-4">
          <RouterLink :to="{ name: 'Reset' }" class="app-logo">
            <img class="rounded-circle" src="@/assets/img/acgn-icon.jpg" alt="Logo" width="50" height="50">
            <h2 class="auth-heading text-center mb-4">Forgot Password ／忘記密碼</h2>
          </RouterLink>
        </div>

        <div class="auth-intro mb-4 text-center">
          請於下方輸入您註冊的電子郵箱，我們將發送連結至您的電子郵箱，<br>以便您快速重置密碼。<br>
          Enter your email address below. <br> We'll email you a link to a page <br> where you can easily create a new password.
        </div>

        <div class="auth-form-container text-left">
          <div :class="['alert', isSuccess.valueOf ? 'alert-success' : 'alert-danger']" v-if="errors.general" role="alert">
            {{ errors.general }}
          </div>

          <form class="auth-form resetpass-form" @submit="handleSubmit">
            <div class="email mb-3" v-if="!isLoggedIn">
              <label class="sr-only" for="reset-email">電子郵箱</label>
              <input 
                id="reset-email" 
                v-model="formData.user_email"
                type="email" 
                class="form-control send-email" 
                :class="{ 'is-invalid': errors.user_email }"
                placeholder="電子郵箱" 
                required
              >
              <div v-if="errors.user_email" class="invalid-feedback">
                {{ errors.user_email }}
              </div>
            </div>

            <div v-else>
              <p class="text-muted">已登入的用戶電子郵箱：{{ formData.user_email }}</p>
            </div>

            <div class="text-center">
              <button 
                type="submit" 
                class="btn app-btn-primary w-50 theme-btn mx-auto"
                :disabled="isSubmitting.value"
              >
                {{ isSubmitting.value ? '發送中...' : '確認送出' }}
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
  color: rgb(102, 102, 241);
}

.alert {
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.25rem;
  font-size: 1rem;
  text-align: center;
}

.alert-success {
  color: #155724;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}
</style>