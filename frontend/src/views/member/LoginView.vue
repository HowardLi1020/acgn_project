<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { useUserStore } from '@/stores/user';
import { fetchPersonalLikes } from '@/stores/user'; // 引用 API 方法
import api from '@/utils/api'; // 你的 Axios 實例

const route = useRoute(); // 獲取當前路由
const router = useRouter()
const userStore = useUserStore(); // Pinia 用戶狀態

const BASE_URL = import.meta.env.VITE_MemberApi
const API_URL = `${BASE_URL}auth/login/`

const LINE_CLIENT_ID = "2006769537"; // 自己的 client_id
const LINE_REDIRECT_URI = encodeURIComponent("http://localhost:5173/verify-line/"); // 自己的 callback url
const LINE_SCOPE = "openid%20profile%20email";   
const LINE_STATE = "abcde"; // 可改為動態生成的隨機字串

// LINE_STATE 動態生成的隨機字串
// function generateRandomState(length = 16) {
//   const array = new Uint8Array(length);
//   window.crypto.getRandomValues(array);
//   return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
// }

// const LINE_STATE = generateRandomState();
// localStorage.setItem("line_state", LINE_STATE);
// console.log("Generated LINE_STATE:", LINE_STATE);

const LineLoginUrl = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${LINE_CLIENT_ID}&redirect_uri=${LINE_REDIRECT_URI}&state=${LINE_STATE}&scope=${LINE_SCOPE}`;

// 第三方登入 - 導向 LINE 授權頁面
const handleLineLogin = () => {
    window.location.href = LineLoginUrl;
};

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

// 表單狀態
const isSubmitting = ref(false)

// 驗證表單
const validateForm = () => {
    let isValid = true
    
    // 重置錯誤信息
    Object.keys(errors.value).forEach(key => errors.value[key] = '')

    // 驗證電子郵箱
    const emailError = userStore.validateEmail(formData.value.user_email);
    if (emailError) {
      errors.value.user_email = emailError;
      isValid = false;
    }

    // 驗證密碼
    const passwordError = userStore.validatePassword(formData.value.user_password);
    if (passwordError) {
      errors.value.user_password = passwordError;
      isValid = false;
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

        const data = await response.json();
        console.log("Login Response:", data);  // 打印 API 響應

        const { user, tokens } = data;

        // 使用 Pinia 儲存用戶資料
        userStore.login(user, tokens.access, tokens.refresh);
        
        // 調用 fetchPersonalLikes() 獲取個人喜好
        const personalLikes = await fetchPersonalLikes();

        if (personalLikes.length > 0) {
          // 提取第一個喜好的 type_name
          const firstPersonalLike = personalLikes[0].type_name;

          Swal.fire({
            title: '登入成功',
            text: `即將為您跳轉到 ${firstPersonalLike || '未知項目'}`,
            icon: 'success',
            confirmButtonText: '確定',
            timer: 3000,
            timerProgressBar: true,
            willClose: () => {
              // 根據個人喜好進行跳轉
              const routesMap = {
                "ACGN綜合論壇(首頁)": '/',
                "周邊商店": '/store',
                "討論區(電影相關)": '/Forum?category=movies',
                "討論區(動畫相關)": '/Forum?category=animations',
                "討論區(遊戲相關)": '/Forum?category=games',
                "委託專區": '/commission',
                "會員專區": '/center/:user_id',
              };

              const targetRoute = routesMap[firstPersonalLike] || '/'; // 默認跳轉到首頁
              router.push(targetRoute);
            }
          });
        } else {
          // 如果沒有個人喜好，則進入會員中心
          router.push({ name: 'center', params: { user_id: user.user_id } });
        }

    } catch (error) {
        errors.value.general =
          error.response?.data?.error || '登入失敗，請檢查您的電子郵箱和密碼';
        console.error('登入失敗:', error);
    } finally {
        isSubmitting.value = false;
    }
};

onMounted( async() => {
  // 頁面載入提示信息
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
  // 滾動到頁面頂部
  window.scrollTo({
      top: 0,
      behavior: 'smooth'
  });
});
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
		<div class="text-center">或使用第三方登入/註冊
      <button>
        <img class="rounded-circle img-float" src="@/assets/img/member/google.png" alt="logo" width="50" height="50">
      </button>
			<button @click.prevent="handleLineLogin">
        <img class="rounded-circle img-float" src="@/assets/img/member/line.png" alt="logo" width="50" height="50">
      </button>
      <button>
        <img class="rounded-circle img-float" src="@/assets/img/member/fb.png" alt="logo" width="50" height="50">
      </button>
		</div>

        <div class="auth-option text-center pt-5">
          沒有帳號? <RouterLink :to="{ name: 'signup' }" class="app-link">Sign up／註冊</RouterLink>
        </div>
      </div>
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
  color: rgb(102, 102, 241);
}

.rounded-circle {
  border: 2px solid #fff; /* 可選：添加白色邊框 */
}

button {
  border: none;        /* 移除圖片邊框 */
  outline: none;       /* 移除點擊方框 */
}

.img-float:hover {
  transform: translateY(-10px);
  transition: all 0.3s ease-in-out;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3); /* 加陰影 */
}
</style>