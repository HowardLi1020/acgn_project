<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'

const route = useRoute(); // 獲取當前路由
const router = useRouter()
const BASE_URL = import.meta.env.VITE_MemberApi
const API_URL = `${BASE_URL}auth/login/`

// 表單數據
const formData = ref({
  user_email: '',
  user_password: '',
  remember_me: false
})

// 錯誤信息
const errors = ref({
  user_email: '',
  user_password: '',
  general: ''
})

onMounted(() => {
  // Get message and type from URL parameters
  const message = route.query.message
  const type = route.query.type

  if (message && type) {
    Swal.fire({
      title: type === 'success' ? '驗證成功！' : '驗證失敗',
      text: message,
      icon: type, // 'success' or 'error'
      confirmButtonText: '確定',
      timer: 3000,
      timerProgressBar: true
    })
  }
})

// 表單狀態
const isSubmitting = ref(false)

// 驗證電子郵箱格式
const validateEmail = (user_email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(user_email)
}

// 驗證密碼強度
const validatePassword = (user_password) => {
  return user_password.length >= 8
}

// 驗證表單
const validateForm = () => {
    let isValid = true
    
    // 重置錯誤信息
    Object.keys(errors.value).forEach(key => errors.value[key] = '')

    // 驗證電子郵箱
    if (!formData.value.user_email) {
        errors.value.user_email = '請輸入電子郵箱'
        isValid = false
    } else if (!validateEmail(formData.value.user_email)) {
        errors.value.user_email = '請輸入有效的郵箱格式'
        isValid = false
    }

    // 驗證密碼
    if (!formData.value.user_password) {
        errors.value.user_password = '請輸入密碼'
        isValid = false
    } else if (!validatePassword(formData.value.user_password)) {
	  errors.value.user_password = '密碼長度至少需要8個字符'
	  isValid = false
    }

    return isValid
}


// 提交表單
const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    try {
        isSubmitting.value = true;

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_email: formData.value.user_email,
                user_password: formData.value.user_password,
                remember_me: formData.value.remember_me,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json(); // 獲取後端詳細錯誤
            throw new Error(errorData.error || '登入失敗，請檢查您的電子郵箱和密碼');
        }

        const memberData = await response.json();
        // 驗證返回數據的完整性
        if (!memberData.tokens || !memberData.tokens.access || !memberData.tokens.refresh) {
            throw new Error('後端未返回正確的 tokens，請聯繫後端檢查問題');
        }
        // 儲存 Token 和用戶信息
        localStorage.setItem('memberData', JSON.stringify(memberData.user));
        localStorage.setItem('access_token', memberData.tokens.access);
        localStorage.setItem('refresh_token', memberData.tokens.refresh);

        // 登入成功，跳轉
        router.push({ name: 'center', params: { user_id: memberData.user.user_id } });
    } catch (error) {
        // 顯示錯誤消息
        errors.value.general = error.message || '登入過程中發生錯誤，請稍後再試';
        console.error('登入失敗:', error);
    } finally {
        isSubmitting.value = false;
    }
};


// 處理忘記密碼
const handleResetPassword = () => {
    router.push({ name: 'ResetPw' })
}
</script>

<template>
  <div class="page-container">
    <!-- 左側表單 -->
    <div class="form-section">
      <div class="form-content">
        <div class="text-center mb-4">
          <RouterLink class="app-logo" :to="{ name: 'login' }">
          <img class="rounded-circle" src="@/assets/img/acgn-icon.jpg" alt="Logo" width="50" height="50">
          <h2 class="auth-heading text-center mb-5">Log in／登入</h2>
          </RouterLink>
        </div>
        
        <!-- 原有表單內容 -->
        <div v-if="errors.general" class="alert alert-danger" role="alert">
          {{ errors.general }}
        </div>

        <form class="auth-form" @submit="handleSubmit">
          <div class="email mb-3">
            <label class="sr-only" for="login-email">電子郵箱</label>
            <input id="login-email" v-model="formData.user_email"type="email" class="form-control login-email" :class="{ 'is-invalid': errors.user_email }" placeholder="電子郵箱" required>
            <div v-if="errors.user_email" class="invalid-feedback">
              {{ errors.user_email }}
            </div>
          </div>

          <div class="password mb-3">
            <label class="sr-only" for="login-password">密碼</label>
            <input id="login-password" v-model="formData.user_password" type="password" class="form-control login-password" :class="{ 'is-invalid': errors.user_password }" placeholder="密碼" required>
            <div v-if="errors.user_password" class="invalid-feedback">
              {{ errors.user_password }}
            </div>

            <div class="extra mt-3 row justify-content-between">
              <div class="col-6">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="RememberPassword" v-model="formData.remember_me">
                  <label class="form-check-label" for="RememberPassword">
                    記住我
                  </label>
                </div>
              </div>
              <div class="col-6">
                <div class="forgot-password text-end">
                  <RouterLink :to="{ name: 'Reset' }" class="app-link">忘記密碼?</RouterLink>
                </div>
			
              </div>
            </div>
          </div>

          <div class="text-center pt-3">
            <button 
              type="submit" 
              class="btn app-btn-primary w-50 theme-btn mx-auto"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '登入中...' : '登入' }}
            </button>
          </div>
        </form>
        <br />
		<!-- 放第三方登入圖示 -->
		<hr />
		<div class="text-center">或使用第三方登入
			<img class="rounded-circle" src="@/assets/img/member/google.png" alt="logo" width="50" height="50">
			<img class="rounded-circle" src="@/assets/img/member/line.png" alt="logo" width="50" height="50">
		  <img class="rounded-circle" src="@/assets/img/member/fb.png" alt="logo" width="50" height="50">
		</div>

        <div class="auth-option text-center pt-5">
          沒有帳號? <RouterLink :to="{ name: 'signup' }" class="app-link">Sign up／註冊</RouterLink>
        </div>
      </div>
    </div>

    <!-- 右側背景 -->
    <!-- <div class="background-section">
      <div class="bg-image"></div>
    </div> -->
</div>
  <!-- </div> -->
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
  max-width: 550px;
  padding: 2rem;
  margin: 0 auto;
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

.rounded-circle {
  border: 2px solid #fff; /* 可選：添加白色邊框 */
}
</style>