<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter()
const route = useRoute(); // 獲取當前路由
const userStore = useUserStore(); // Pinia 用戶狀態

const BASE_URL = import.meta.env.VITE_MemberApi   // 後端 MemberApi 的主機地址
const LOAD_URL = `${BASE_URL}profile/`

const BASIC_URL = "http://127.0.0.1:8000"   // 後端 API 的主機地址
const loadAvatar = ref(`${BASIC_URL}/media/default.png`) // 後端返回的 user_avatar

const selectedFile = ref(null); // 用戶選擇的文件
const avatarURL = computed(() => loadAvatar.value); // 自動更新的完整路徑

const API_URL = `${BASE_URL}auth/update_info/`   // 上傳後端接口地址
const memberData = ref({}) // 用來存當前登入會員的資料
const accessToken = localStorage.getItem("access_token");


// 1. 載入會員資料
const loadData = async () => {
  const userId = userStore.user?.user_id;

  if (!userId) {
    console.error("User ID not found, cannot fetch data.");
    return;
  }

  try {
    const response = await fetch(`${LOAD_URL}${userId}/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${userStore.accessToken}`, // 使用 Pinia 中的 accessToken
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Fetched member data:", data);

    // 更新 Vue Ref 和 Pinia 狀態
    memberData.value = data;
    userStore.updateUser(data);
    loadAvatar.value = data.user_avatar || `${BASIC_URL}/media/default.png`;
  } catch (error) {
    console.error("Error fetching member data:", error.message);
  }
};

loadData();

// 2. 處理上傳的頭像
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    loadAvatar.value = URL.createObjectURL(file); // 頭像預覽
    selectedFile.value = file;
    console.log("選擇的檔案:", selectedFile.value);
    console.log("選擇的檔案名稱:", selectedFile.value.name);
  }
};

// 3. 修改用戶信息
const ChangeInfo = async () => {
  const formData = new FormData();
  const userId = memberData.value.user_id;  // 獲取用戶 ID

  if (selectedFile.value) {
    formData.append("user_avatar", selectedFile.value || ""); // 上傳的檔案
  }
  formData.append("user_email", memberData.value.user_email || "");
  formData.append("user_nickname", memberData.value.user_nickname || "");
  formData.append("user_gender", memberData.value.user_gender || "");
  formData.append("user_birth", memberData.value.user_birth || "");

  try {
    const response = await fetch(`${API_URL}${userId}/`, {
      method: "PUT",
      body: formData,
      headers: {
        Authorization: `Bearer ${userStore.accessToken}`, // 使用 Pinia 中的 Token
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Update failed:", errorText);
      alert("該圖片已存在或重複數據，請檢查後再試");
      return;
    }

    const result = await response.json();
    console.log("Update successful:", result)

    // 更新資料
    memberData.value = { ...memberData.value, ...result };
    userStore.updateUser(memberData.value);
    alert("資料更新成功！");
  } catch (error) {
    console.error("Update error:", error.message);
    alert("儲存過程中出錯！");
  }
};

// 4. 登出處理
const handleLogout = () => {
  const confirmLogout = confirm("您即將登出頁面...請您再次確認~*");

  if (confirmLogout) {
    userStore.logout(); // 清除 Pinia 狀態
    router.push("/login");
  }

  if (confirmLogout === false) {
        console.log("用戶取消登出");
        console.log("取消後 localStorage 狀態:", localStorage.length);
        return;
    }
};


</script>

<template>
  <div class="member-container">
    <div class="content-wrapper">
      <div class="header-section">
        <RouterLink :to="{ name: 'center' }">
            <img class="logo-icon me-2" src="@/assets/img/acgn.png" alt="logo" width="70" height="40">
        </RouterLink>
        <h2>會員中心</h2>
      </div>
      <keep-alive>
      <form class="member-form" method="POST" enctype="multipart/form-data" id="registerForm" v-if="memberData">
        <div class="mb-3">
          <label for="InputName" class="form-label">會員姓名：*</label>
          <input type="text" class="form-control" id="InputName" v-model="memberData.user_name" disabled minlength="2" maxlength="10">
        </div>
        <div class="mb-3">
            <label for="InputPhone" class="form-label">手機：*</label>
            <input type="tel" class="form-control" id="InputPhone" name="phone" v-model="memberData.user_phone" disabled pattern="09[0-9]{8}" maxlength="10">
            <div style="text-align: right;">
                <small><RouterLink :to="{ name: 'PhoneChange' }" class="btn btn-outline-success btn-sm">修改手機</RouterLink></small>
            </div>
        </div>
        <div class="mb-3">
            <label for="InputEmail" class="form-label">電子郵箱：*</label>
            <input type="email" class="form-control" id="InputEmail" name="email" v-model="memberData.user_email" required>
            <div style="text-align: right;">
                <small><RouterLink :to="{ name: 'EmailChange' }" class="btn btn-outline-success btn-sm">修改郵箱</RouterLink></small>
            </div>
        </div>
        <div class="mb-3">
            <label for="usernickname" class="form-label">暱稱</label>
            <input type="text" class="form-control" name="nickname" id="usernickname" v-model="memberData.user_nickname">
        </div>
        <div class="mb-3">
            <label class="form-label">性別</label>
            <select class="form-control" name="usergender" id="usergender" v-model="memberData.user_gender" required>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="prefer_not_to_say">不願透漏</option>
            </select>
        </div>
        <div class="mb-3">
            <label for="InputBirth" class="form-label">生日：*</label>
            <input type="date" class="form-control" id="InputBirth" name="birth" v-model="memberData.user_birth" required>
        </div>
        <div class="mb-3">
            <label for="userphoto" class="form-label">頭像：</label>
            <input class="form-control" type="file" id="userphoto" name="user_avatar" @change="handleFileChange">
            <img id="userphoto" :src="avatarURL" alt="頭像預覽" style="margin-top: 10px; max-width: 100px;">
        </div>
        <div class="text-center mt-4">
          <button type="submit" class="btn btn-outline-primary me-3 btn-sm"  @click.prevent="ChangeInfo">儲存</button>
            <RouterLink :to="{ name: 'center' }" class="btn btn-outline-secondary me-3 btn-sm">會員中心首頁</RouterLink>
            <RouterLink :to="{ name: 'center_plus' }" class="btn btn-outline-secondary me-3 btn-sm">進階設定</RouterLink>
          <button @click.prevent="handleLogout" class="btn btn-outline-danger btn-sm">登出</button>
        </div>
      </form>
    </keep-alive>

      <!-- Alert 提示區域 -->
      <div id="alertMessage" class="alert alert-warning mt-4" style="display: none;"></div>
    </div>
  </div>
</template>

<style scoped>
.member-container {
  padding-top: 50px;  /* 增加上方間距 */
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;     /* 垂直居中 */
  justify-content: center; /* 水平居中 */
}

.content-wrapper {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding-top: 8rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.member-form {
  margin-top: 2rem;
}

.header-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.logo-icon {
  margin: 0;  /* 移除預設的 margin */
}

h2 {
  color: #333;
  font-size: 2rem;
  margin: 0;  /* 移除預設的 margin */
}

.form-label {
  font-weight: 500;
}

.form-text {
  color: #666;
}

/* 響應式調整 */
@media (max-width: 768px) {
  .member-container {
    padding-top: 60px;
    padding: 1rem;
  }

  .content-wrapper {
    padding: 1rem;
  }

  h2 {
    font-size: 1.5rem;
  }
}
</style>