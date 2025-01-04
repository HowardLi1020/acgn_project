<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router';

const router = useRouter()
const route = useRoute(); // 獲取當前路由
const BASE_URL = import.meta.env.VITE_MemberApi   // 後端 MemberApi 的主機地址
const LOAD_URL = `${BASE_URL}profile/`

const BASIC_URL = "http://127.0.0.1:8000"   // 後端 API 的主機地址
const loadAvatar = ref(`${BASIC_URL}/media/default.png`) // 後端返回的 user_avatar


const selectedFile = ref(null); // 用戶選擇的文件
const avatarURL = computed(() => loadAvatar.value); // 自動更新的完整路徑

const API_URL = `${BASE_URL}auth/update_info/`   // 上傳後端接口地址
const memberData = ref({}) // 用來存當前登入會員的資料
const accessToken = localStorage.getItem("access_token");


// 1.載入對應的會員資料
const loadData = async () => {
  // 從 localStorage 中獲取存儲的會員資料
  const storedData = localStorage.getItem("memberData");
  if (!storedData) {
    console.error("No member data found in localStorage!");
    return;
  }

  // 解析 localStorage 中的資料，獲取 user_id
  const user = JSON.parse(storedData); // 解析 JSON 字串成物件
  const userId = user.user_id; // 取得 user_id
  // console.log("Loaded user_id:", userId); // 輸出 user_id 進行確認
  // console.log("Loaded user_avatar:", userAvatar); // 輸出 user_avatar 進行確認

  // 發送帶有 user_id 的 API 請求
  try {
    const response = await fetch(`${LOAD_URL}${userId}/`, {
        method: "GET",
        headers: {
            // "Authorization": `Bearer ${accessToken}`, // 添加 token
            "Content-Type": "application/json",
        },
    });console.log(`${LOAD_URL}${userId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json(); // 解析 API 回傳的資料
    console.log("Fetched member data:", data); // 調試輸出

    // 更新 Vue Ref，存入當前會員資料
    memberData.value = data;
    console.log("Updated member data:", memberData.value);

    // 更新 Vue Ref，將後端返回的頭像路徑存入
    loadAvatar.value = data.user_avatar || `${BASIC_URL}/media/default.png`;
      console.log("Updated Avatar URL:", avatarURL.value);
  } catch (error) {
    console.error("Error fetching member data:", error.message);
  }
};

loadData();

// 2. 顯示並處理將上傳的頭像
const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      // 使用 URL.createObjectURL 生成預覽 URL
      loadAvatar.value = URL.createObjectURL(file);
      selectedFile.value = file;
      console.log("選擇的檔案:", selectedFile.value);
      console.log("選擇的檔案名稱:", selectedFile.value.name);
    }
  };

// 3. 串接後端API - PUT 修改用户信息
const ChangeInfo = async () => {
    const formData = new FormData();

    // 添加檔案和其他資料到 FormData
    if (selectedFile.value) {
        formData.append("user_avatar", selectedFile.value || ""); // 上傳的檔案
    }
    // formData.append("user_name", memberData.value.user_name || "");
    // formData.append("user_phone", memberData.value.user_phone || "");
    formData.append("user_email", memberData.value.user_email || "");
    formData.append("user_nickname", memberData.value.user_nickname || "");
    formData.append("user_gender", memberData.value.user_gender || "");
    formData.append("user_birth", memberData.value.user_birth || "");

    const userId = memberData.value.user_id; // 獲取用戶 ID
    const updateUrl = `${API_URL}${userId}/`; // 拼接 URL

    try {
        const response = await fetch(updateUrl, {
            method: 'PUT',
            body: formData,
        })

        if (!response.ok) {
            // 输出失败的错误信息
            const errorText = await response.text();
            console.error("更新失败：", errorText);
            alert("該圖片已存在或重複數據，請檢查後再試");
            // alert(`更新失败: ${errorText}`);
            return;
        }

        // 成功返回 JSON 数据
        const result = await response.json();
        console.log("更新成功:", result);

        memberData.value = { ...memberData.value, ...result }; // 更新前台資料
        localStorage.setItem('memberData', JSON.stringify(memberData.value));
        alert('資料更新成功！'); // 提示用户更新成功
    } catch (error) {
        console.error('更新發生錯誤:', error);
        alert(error.message || '儲存過程中出錯！');
    }
};

// 4. 登出處理
const handleLogout = async () => {
    const confirmLogout = confirm("您即將登出頁面...請您再次確認~*");
    console.log("用戶確認登出:", confirmLogout);
    console.log("當前 localStorage 狀態:", localStorage.length);

    if (confirmLogout === false) {
        console.log("用戶取消登出");
        console.log("取消後 localStorage 狀態:", localStorage.length);
        return;
    }

     // 用戶確認登出時才執行以下程式碼
     if (confirmLogout === true) {
        try {
            console.log("開始登出流程");
            localStorage.clear();
            await router.push({ name: 'login' });
        } catch (error) {
            console.error("登出過程發生錯誤:", error);
        }
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
        </div>
        <div class="mb-3">
            <label for="InputEmail" class="form-label">電子郵箱：*</label>
            <input type="email" class="form-control" id="InputEmail" name="email" v-model="memberData.user_email" required>
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