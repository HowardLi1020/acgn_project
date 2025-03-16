<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { ref, watchEffect, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { useUserStore } from '@/stores/user'; // 引入 pinia 用戶狀態

const authStore = useUserStore();  // Pinia 用戶狀態
const route = useRoute(); // 獲取當前路由
const router = useRouter()
const BASE_URL = import.meta.env.VITE_MemberApi
const REG_URL = `${BASE_URL}auth/register/`
const TermsPrivacyPopup = ref(false); // 控制顯示服務條款彈窗

// 表單數據
const formData = ref({
  user_name: '',
  user_email: '',
  user_phone: '',
  user_gender: 'prefer_not_to_say', // 設置默認值
  user_password: '',
  confirm_password: '',
  agreeToTerms: false
})

// 錯誤信息
const errors = ref({
  user_name: '',
  user_email: '',
  user_phone: '',
  user_password: '',
  confirm_password: '',
  agreeToTerms: '',
  general: ''
})

const LINE_CLIENT_ID = "2006769537"; // 自己的 client_id
const LINE_REDIRECT_URI = encodeURIComponent("http://localhost:5173/verify-line/"); // 自己的 callback url
const LINE_SCOPE = "openid%20profile%20email";   
const LINE_STATE = "abcde"; // 可改為動態生成的隨機字串

const LineLoginUrl = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${LINE_CLIENT_ID}&redirect_uri=${LINE_REDIRECT_URI}&state=${LINE_STATE}&scope=${LINE_SCOPE}`;

// 第三方登入 - 導向 LINE 授權頁面
const handleLineLogin = () => {
    window.location.href = LineLoginUrl;
};

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

// 驗證表單
const validateForm = () => {
  const validationErrors = authStore.validateForm(formData.value);
  errors.value = { ...validationErrors };
  return Object.keys(validationErrors).length === 0; // 沒有錯誤時返回 true
};

// 顯示"服務條款與隱私政策"
const handleTermsPrivacy = async (event) => {
    event.preventDefault()
    const result = await Swal.fire({
      title: '服務條款和隱私政策',
      text: '請仔細閱讀以下條款和隱私政策，點擊同意後即可註冊。',
      icon: 'info',
      showCancelButton: true,
      confirmButtonText: '同意',
      cancelButtonText: '取消',
      showLoaderOnConfirm: true,
      preConfirm: () => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve()
          }, 2000)
        })
      }
    })

    if (result.isConfirmed) {
    TermsPrivacyPopup.value = true;
  }
};

// 關閉彈窗時自動勾選同意
const closeTermsPrivacyPopup = () => {
    console.log("關閉彈窗觸發");
    TermsPrivacyPopup.value = false; // 隱藏彈窗
    console.log("彈窗狀態:", TermsPrivacyPopup.value);
    formData.value.agreeToTerms = true;    // 自動勾選同意條款
    console.log("條款同意狀態:", formData.value.agreeToTerms);
};


// 提交表單
const handleSubmit = async (event) => {
  event.preventDefault()
  
  if (!validateForm()) {
    return
  }

  try {
    isSubmitting.value = true
    
    // 這裡添加實際的 API 調用
    const response = await fetch(REG_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_name: formData.value.user_name,
        user_email: formData.value.user_email,
        user_phone: formData.value.user_phone,
        user_password: formData.value.user_password
      })
    })

    if (!response.ok) {
      const errorData = await response.json();
      if (errorData.message) {
        Swal.fire('錯誤', errorData.message, 'error');
      }
      Object.keys(errorData).forEach((key) => {
        if (key in errors.value) {
          errors.value[key] = errorData[key];
        }
      });
      throw new Error("註冊失敗，請檢查輸入的資料");
    }

    const responseData = await response.json();
    console.log('註冊成功:', responseData);
    localStorage.setItem('formData', JSON.stringify(formData.value));
    
    // 註冊成功，顯示提示並跳轉到登入頁面
    await Swal.fire({
      title: '註冊成功，請查看您的郵箱並點擊驗證連結以啟動帳號！~*！',
      text: '您將被重定向到登入頁面。',
      icon: 'success',
      timer: 4000,
      showCancelButton: false,
      showConfirmButton: false,
      willClose: () => {
        router.push({ name: 'login' }); // 跳轉到登入頁面
      }
    });

  } catch (error) {
    errors.value.general = error.message || '註冊過程中發生錯誤，請稍後重試'
    console.error('錯誤:', error);
  } finally {
    isSubmitting.value = false
  }
}

watchEffect(() =>{
  localStorage.setItem("formData", JSON.stringify(formData.value))
})
</script>

<template>
  <div class="page-container">
    <!-- 左側表單 -->
    <div class="form-section">
      <div class="form-content">
        <div class="text-center mb-4">
          <RouterLink :to="{ name: 'signup' }" class="app-logo">
            <img class="rounded-circle" src="@/assets/img/acgn-icon.jpg" alt="Logo" width="50" height="50">
            <h2 class="auth-heading text-center mb-5">Sign up／註冊</h2>
          </RouterLink>
        </div>
        
        <!-- 原有表單內容 -->
        <div v-if="errors.general" class="alert alert-danger" role="alert">
          {{ errors.general }}
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="name mb-3">
            <label class="sr-only" for="InputName">姓名</label>
            <input id="InputName" v-model="formData.user_name" type="name" class="form-control signup-name" :class="{ 'is-invalid': errors.user_name }"
              placeholder="姓名" required minlength="2" maxlength="10">
            <small class="form-text text-muted">請輸入2-10個字符</small>
            <div v-if="errors.user_name" class="invalid-feedback">
              {{ errors.user_name }}
            </div>
          </div>
          <div class="email mb-3">
            <label class="sr-only" for="InputEmail">電子郵箱</label>
            <input id="InputEmail" v-model="formData.user_email" type="email" class="form-control signup-email" :class="{ 'is-invalid': errors.user_email }" placeholder="電子郵箱" required>
            <small class="form-text text-muted">請輸入有效的電子郵箱地址</small>
            <div v-if="errors.user_email" class="invalid-feedback">
              {{ errors.user_email }}
            </div>
          </div>
          <div class="phone mb-3">
            <label class="sr-only" for="InputPhone">手機</label>
            <input id="InputPhone" v-model="formData.user_phone" type="phone" class="form-control signup-phone" :class="{ 'is-invalid': errors.user_phone }" placeholder="09開頭的10位數字" required pattern="09[0-9]{8}" maxlength="10">
            <small class="form-text text-muted">請輸入10位數字的手機號碼</small>
            <div v-if="errors.user_phone" class="invalid-feedback">
              {{ errors.user_phone }}
            </div>
          </div>
          <div class="password mb-3">
            <label class="sr-only" for="InputPassword">密碼</label>
            <input id="InputPassword" v-model="formData.user_password" type="password" class="form-control signup-password" :class="{ 'is-invalid': errors.user_password }" placeholder="輸入密碼" required minlength="8">
            <small class="form-text text-muted">密碼至少需要8個字符，英文(不分大小寫)+數字</small>
            <div v-if="errors.user_password" class="invalid-feedback">
              {{ errors.user_password }}
            </div>
          </div>
          <div class="password mb-3">
            <label class="sr-only" for="ConfirmPassword">確認密碼</label>
            <input id="ConfirmPassword" v-model="formData.confirm_password" type="password" class="form-control signup-password" :class="{ 'is-invalid': errors.confirm_password }" placeholder="確認密碼" minlength="8" required>
            <div v-if="errors.confirm_password" class="invalid-feedback">
              {{ errors.confirm_password }}
            </div>
          </div>

          <div class="extra mb-3">
            <div class="form-check">
              <input class="form-check-input" :class="{ 'is-invalid': errors.agreeToTerms }" type="checkbox" 
                id="signupAgreement" v-model="formData.agreeToTerms">
              <label class="form-check-label" for="signupAgreement">
                我同意 <a @click.prevent="handleTermsPrivacy" class="app-link">服務條款和隱私政策</a>
              </label>
              <div v-if="errors.agreeToTerms" class="invalid-feedback">
                {{ errors.agreeToTerms }}
              </div>
            </div>
          </div>

          <!-- 彈窗顯示服務條款和隱私政策 -->
        <div v-if="TermsPrivacyPopup" class="popup-overlay">
            <div class="popup-content">
              <small>
              <h5>第一部分：服務條款</h5>
              <p>1. 服務範圍<br>我們提供的服務包括但不限於ACGN相關的資訊、<br>社群互動、活動參與及其他相關功能。<br>本服務僅供符合當地法規的用戶使用。</p>
              <p>2. 用戶註冊</p>
              <ul>
                <li>2.1 用戶需提供真實、準確、完整的註冊資料。</li>
                <li>2.2 用戶需為其帳戶安全負責，包括但不限於密碼保護及帳戶使用。</li>
                <li>2.3 若發現未經授權的使用或其他安全問題，應立即通知我們。</li>
              </ul>
              <p>3. 用戶行為<br>用戶不得利用本服務進行以下行為：</p>
              <ul>
                  <li>發布違法、淫穢、侮辱或侵權內容。</li>
                  <li>侵害他人權利，包括但不限於知識產權、隱私權等。</li>
                  <li>未經授權的廣告、垃圾郵件或欺詐行為。</li>
              </ul>
              <p>4. 服務中斷與終止<br>我們有權在以下情況下中止或終止服務：</p>
              <ul>
                  <li>用戶違反服務條款。</li>
                  <li>因不可抗力或其他原因導致服務無法繼續。</li>
              </ul>
              <p>5. 責任限制<br>我們對因服務中斷、數據丟失或其他非主觀過失造成的損失不承擔責任。</p>
              <hr>
              <h5>第二部分：隱私政策</h5>
              <p>1. 信息收集<br>我們可能收集以下類型的信息：</p>
              <ul>
                  <li>用戶主動提供的信息，如註冊資料、社群發言內容。</li>
                  <li>自動收集的信息，如設備資訊、瀏覽紀錄。</li>
              </ul>
              <p>2. 信息使用<br>我們將收集的信息用於以下用途：</p>
              <ul>
                  <li>提供、維護和改善服務。</li>
                  <li>用於統計與分析，提升用戶體驗。</li>
                  <li>符合法律要求的用途。</li>
              </ul>
              <p>3. 信息分享<br>除非經用戶同意或法律要求，我們不會將用戶信息分享給第三方。</p>

              <p>4. 數據安全<br>我們採取合理的技術措施保護用戶數據，
                <br>但無法保證100%安全。如有數據洩漏風險，我們將及時通知用戶。</p>

              <p>5. 用戶權利<br>用戶有權查詢、更正或刪除其個人信息。
                <br>相關請求可通過我們的客服聯繫方式提交。</p>
            </small>
              <hr>
              <h5>聯繫我們</h5>
              <small>
              <p>如對本服務條款與隱私政策有任何疑問，請通過以下方式聯繫我們：</p>
              <ul>
                  <li>電子郵件：<a href="mailto:support@acgnplatform.com">support@acgnplatform.com</a></li>
                  <li>客服電話：123-456-7890</li>
              </ul>
              <p>我們保留隨時修改本條款與政策的權利，修改後將以公告或其他適當方式通知用戶。</p>

              <p>感謝您的支持，祝您使用愉快！</p>
                <button @click.prevent="closeTermsPrivacyPopup" class="btn btn-secondary btn-sm">關閉</button>
              </small>
            </div>
        </div>

          <div class="text-center">
            <button 
              type="submit" 
              class="btn app-btn-primary w-50 theme-btn mx-auto"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '註冊中...' : '註冊' }}
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
          已有帳號? <RouterLink :to="{ name: 'login' }" class="app-link">Log in／登入</RouterLink>
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
  cursor: pointer;
  color: #15a362;
  text-decoration: none;
}

.app-link:hover {
  text-decoration: underline;
  color: rgb(102, 102, 241);
}

.popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5); /* 半透明背景 */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000; /* 確保位於頂層 */
  }

  .popup-content {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 90%;
    max-width: 600px;
    max-height: 50%; /* 設置最大高度 */
    overflow-y: auto; /* 當內容超出時啟用垂直滾動條 */
    text-align: center;
  }

  .popup-content button {
    margin-top: 20px;
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