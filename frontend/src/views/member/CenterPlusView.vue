<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router';
import draggable from "vuedraggable";

const router = useRouter()
const route = useRoute(); // 獲取當前路由
const BASE_URL = import.meta.env.VITE_MemberApi
const API_URL = `${BASE_URL}auth/update_info/`
const memberData = ref(null); // 用於存儲當前登入會員的資料
const showVIPBenefitsPopup = ref(false); // 控制顯示升級VIP會員優點彈窗

// 表單數據
const formData = ref({
    password: '',
    personal_like: '未設定',
    vip_status: '0',
    payment_set: '未設定',
    privicy_set: '',
})

onMounted(() => {
    const storedMemberData = JSON.parse(localStorage.getItem('memberData'));
    if (storedMemberData) {
        memberData.value = storedMemberData; // 將資料賦值給 memberData
    } else {
        console.warn('No member data found in localStorage'); // 輸出警告
    }
});

onBeforeUnmount(() => {
    if (!localStorage.getItem('memberData')) {
        console.log('memberData 丟失，防止跳轉錯誤頁面');
    }
});

// 定義狀態
const showPopup = ref(false);
const personalLikes = ref(["討論區(首頁)", "周邊商店", "活動專區", "委託專區", "討論區(電影相關)", "討論區(動漫相關)", "討論區(遊戲相關)"]); // 初始數據
const LikesData = ref({
  personal_like: "", // 存儲用戶選擇的喜好
});

// 刪除項目
const removeItem = (index) => {
  personalLikes.value.splice(index, 1);
};

// 保存排序方法
const saveOrder = () => {
  LikesData.value.personal_like = personalLikes.value.join(", ");
  showPopup.value = false; // 關閉彈窗
  console.log(`排序已保存：${LikesData.value.personal_like}`);
  alert(`排序已保存：${LikesData.value.personal_like}`);
};

// 處理升級VIP會員的邏輯
const handleUpgradeVIP = () => {
    const confirmUpgrade = confirm("您即將離開該頁面，請確認是否要升級VIP會員？");
    if (confirmUpgrade) {
      showVIPBenefitsPopup.value = true;  // 彈窗顯示VIP會員的優點
    }
    
};

const ChangeInfo = async(event) => {
    event.preventDefault();

    // 確保個人喜好有加到 memberData
    memberData.value.personal_like = LikesData.value.personal_like; 

    // 确保 user_id 存在
    if (!memberData.value.user_id) {
        console.error('用户ID未找到');
        alert('用户ID未找到，请检查用户信息');
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: JSON.stringify(memberData.value), // 更新的资料，包括 user_id 和個人喜好
            headers: {
                'Content-Type': 'application/json',
            },
        });
        console.log('请求体:', JSON.stringify(memberData.value));

        if (!response.ok) {
            throw new Error('更新失敗，請檢查您的資料');
        }

        const result = await response.json();
        console.log('更新成功:', result);
        // 更新前台資料
        memberData.value = { ...memberData.value, ...result };
    } catch (error) {
        console.error('更新失败:', error);
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
        <RouterLink :to="{ name: 'center_plus' }">
            <img class="logo-icon me-2" src="@/assets/img/acgn.png" alt="logo" width="70" height="40">
        </RouterLink>
        <h2>會員進階設定</h2>
      </div>
      
      <form class="member-form" method="POST" enctype="multipart/form-data" id="registerForm" v-if="memberData">
        <input type="hidden" name="user_id" :value="memberData.user_id">
        <div class="mb-3">
            <label for="InputPassword" class="form-label">密碼 *</label>
            <input type="password" class="form-control" id="InputPassword" name="password" placeholder="*******" disabled minlength="8">
            <div style="text-align: right;">
                <small><RouterLink :to="{ name: 'Reset' }" class="btn btn-outline-success btn-sm">重置密碼</RouterLink></small>
            </div>
        </div>
        <div class="mb-3">
            <label for="PersonalLike" class="form-label d-flex justify-content-between align-items-center">網站個人喜好
              <button class="btn btn-outline-info btn-sm" @click.prevent="showPopup = true">編輯排序</button>
            </label>
            <input class="form-control" id="PersonalLike" name="personal_like" v-model="LikesData.personal_like" disabled>
        </div>
        <!-- 彈窗區域 -->
        <div v-if="showPopup" class="popup-overlay">
          <div class="popup-content">
            <h2>拖放排序您的喜好</h2>
            <small>-也可刪除您較不感興趣喜好</small>
            <draggable v-model="personalLikes" class="drag-area" animation="200" :itemKey="element => element">
            <template #item="{ element, index }">
              <div class="drag-item d-flex justify-content-between">
                <span>{{ element }}</span>
                <button class="btn bg-danger rounded-pill border-0" @click.stop="removeItem(index)">X</button>
              </div>
            </template>
            </draggable>


            <button @click="saveOrder" class="btn btn-success me-3 btn-sm">保存排序</button>
            <button @click="showPopup = false" class="btn btn-secondary me-3 btn-sm">取消</button>
          </div>
        </div>

        <div class="mb-3">
          <label for="VipStatus" class="form-label ">會員等級</label>
          <input type="text" class="form-control" id="VipStatus" v-model="memberData.vip_status" disabled>
          <div style="text-align: right;">
            <small>
                <button @click.prevent="handleUpgradeVIP" class="btn btn-outline-success btn-sm">升級VIP會員</button>
            </small>
          </div>
        </div>

        <!-- 彈窗顯示VIP會員的優點 -->
        <div v-if="showVIPBenefitsPopup" class="popup-overlay">
            <div class="popup-content">
                <h5><i class="bi bi-award-fill">升級VIP會員的優點：</i></h5>
                <ul>
                    <li>專屬優惠和折扣</li>
                    <li>優先參加活動</li>
                    <li>獲得專屬客服支持</li>
                    <li>更多的個性化設置選項</li>
                </ul>
                <button @click="showVIPBenefitsPopup = false" class="btn btn-secondary btn-sm">關閉</button>
            </div>
        </div>

        <div class="mb-3">
            <label for="PaymentSet" class="form-label">支付設定</label>
            <select class="form-control" name="payment" id="PaymentSet" v-model="memberData.payment_set">
                <option value="信用卡">信用卡</option>
                <option value="銀行帳號">銀行帳號</option>
            </select>
        </div>
        <div class="mb-3">
            <label for="PrivicySet" class="form-label">隱私設定</label>
            <input type="password" class="form-control" id="PrivicySet" name="privicy" v-model="memberData.privicy_set">
        </div>

        <div class="text-center mt-4">
          <button type="submit" class="btn btn-outline-primary me-3 btn-sm" @click.prevent="ChangeInfo">儲存</button>
            <RouterLink :to="{ name: 'center' }" class="btn btn-outline-secondary me-3 btn-sm">會員中心首頁</RouterLink>
            <RouterLink :to="{ name: 'center_plus' }" class="btn btn-outline-secondary me-3 btn-sm">進階設定</RouterLink>
            <button @click.prevent="handleLogout" class="btn btn-outline-danger btn-sm">登出</button>
        </div>
      </form>

      <!-- Alert 提示區域 -->
      <div id="alertMessage" class="alert alert-warning mt-4" style="display: none;"></div>
    </div>
  </div>
</template>

<style scoped>
.member-container {
  padding-top: 50px;  /* 增加上方間距 */
  min-height: calc(50vh - 56px);
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
  z-index: 9999;
}

.popup-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.drag-area {
  margin: 20px 0;
  border: 1px dashed #ddd;
  border-radius: 5px;
  padding: 10px;
}

.drag-item {
  padding: 10px;
  background: #f9f9f9;
  margin-bottom: 5px;
  border: 1px solid #ddd;
  border-radius: 3px;
  cursor: grab;
}

.drag-item:hover {
  background: #f7d6d6;
}

.btn-danger {
  margin-left: 10px;
}

.vip-benefits {
    margin-top: 20px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #f9f9f9;
}
</style>