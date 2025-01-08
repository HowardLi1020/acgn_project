<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const route = useRoute(); // 獲取當前路由
const router = useRouter(); // 用於路由跳轉

const BASE_URL = import.meta.env.VITE_MemberApi;
const code = route.params.code || localStorage.getItem('resetCode'); // 優先從 URL 提取，否則從 localStorage 獲取
if (!code) {
  alert('修改郵箱連接無效或缺失，請重新登入請求修改郵箱。');
  router.push({ name: 'home' }); // 跳轉到登入主頁
}
const API_URL = `${BASE_URL}email-change/${code}/`;

// 表單數據
const formData = ref({
    new_email: '',
    password: ''
})

// 錯誤信息
const errors = ref({
    new_email: '',
    password: '',
    general: ''
})

const message = ref('');

// 表單狀態
const isSubmitting = ref(false)

// 驗證密碼強度
const validatePassword = (password) => {
    // 檢查密碼長度
    if (password.length < 8) {
        return false;
    }
    // 檢查是否包含至少一個字母和一個數字
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    return hasLetter && hasNumber;
}

// 驗證電子郵箱格式
const validateEmail = (new_email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(new_email)
}

// 驗證表單
const validateForm = () => {
    let isValid = true
    
    // 重置錯誤信息
    Object.keys(errors.value).forEach(key => errors.value[key] = '')

    // 驗證電子郵箱
    if (!formData.value.new_email) {
        errors.value.new_email = '請輸入電子郵箱'
        isValid = false
    } else if (!validateEmail(formData.value.new_email)) {
        errors.value.new_email = '請輸入有效的電子郵箱格式'
        isValid = false
    } else {
          errors.value.new_email = ''; // 清空錯誤信息
    }

    if (!formData.value.password) {
        errors.value.password = '請確認密碼';
        isValid = false;
    } else if (!validatePassword(formData.value.password)) {
      errors.value.password = '密碼長度至少需要8個字符，英文(不分大小寫)+數字'
      isValid = false
    } else {
      errors.value.password = ''; // 清空錯誤信息
    }

    return isValid
}

// 提交表單
const handleResetEmail = async (event) => {
    event.preventDefault()
    
    if (!validateForm()) {
        return
    }

    try {
        isSubmitting.value = true
        
        // 這裡添加實際的 API 調用
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData.value),
          });

        if (response.ok) {
          Swal.fire('成功', '郵箱修改成功，請重新登入確認', 'success').then(() => {
            router.push({ name: 'login' });
          });
        } else {
          const errorData = await response.json();
          throw new Error(errorData.message || '郵箱修改失敗');
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
          <RouterLink :to="{ name: 'EmailReset' }" class="app-logo">
            <img class="rounded-circle" src="@/assets/img/acgn-icon.jpg" alt="Logo" width="50" height="50">
            <h2 class="auth-heading text-center mb-4">Email Reset／電子郵箱修改</h2>
          </RouterLink>
        </div>
        

        <div class="auth-intro mb-4 text-center">
          請於下方輸入您的新郵箱與密碼，以便為您重設。<br>Enter your new email and password below.<br> We'll reset you a new email.
        </div>

        <div class="auth-form-container text-left">
          <!-- 錯誤/成功信息顯示 -->
          <div v-if="errors.general" 
               :class="{'alert alert-danger': errors.general.includes('失敗') || errors.general.includes('錯誤'),
                       'alert alert-success': errors.general.includes('成功')}" 
               role="alert">
            {{ errors.general }}
          </div>

          <form class="auth-form resetpass-form" @submit="handleResetEmail">
            <div class="email mb-3">
              <label class="sr-only" for="newemail">新郵箱</label>
              <input 
                id="newemail" 
                v-model="formData.new_email"
                type="email" 
                class="form-control login-email" 
                :class="{ 'is-invalid': errors.new_email }"
                placeholder="新郵箱" 
                required
              >
              <div v-if="errors.new_email" class="invalid-feedback">
                {{ errors.new_email }}
              </div>
            </div>
            <div class="email mb-3">
              <label class="sr-only" for="password">註冊密碼</label>
              <input 
                id="password" 
                v-model="formData.password"
                type="password" 
                class="form-control login-email" 
                :class="{ 'is-invalid': errors.password }"
                placeholder="註冊密碼" 
                required
              >
              <div v-if="errors.password" class="invalid-feedback">
                {{ errors.password }}
              </div>
            </div>

            <div class="text-center">
              <button
                type="submit" 
                class="btn app-btn-primary w-50 theme-btn mx-auto"
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? '發送中...' : '確認提交修改' }}
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