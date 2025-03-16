<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink, useRouter } from 'vue-router';
import draggable from "vuedraggable";
import { useUserStore } from '@/stores/user';

const router = useRouter()
const userStore = useUserStore(); // Pinia 用戶狀態

const BASE_URL = import.meta.env.VITE_MemberApi
const API_URL = `${BASE_URL}auth/update-likes/`
const memberData = ref(null); // 用於存儲當前登入會員的資料
const showVIPBenefitsPopup = ref(false); // 控制顯示升級VIP會員優點彈窗

// 表單數據
const formData = ref({
    password: '',
    personal_like: '未設定',
    vip_status: '0',
    payment_set: '未設定',
    user_address: '',
    privicy_set: '',
})

// 定義初始數據
const initialPersonalLikes = ["ACGN綜合論壇(首頁)", "周邊商店", "討論區(電影相關)", "討論區(動畫相關)", "討論區(遊戲相關)", "委託專區" ,"會員專區"];
const personalLikes = ref([...initialPersonalLikes]); // 使用初始數據

onMounted(async () => {
    // 同步 Pinia Store 与 localStorage
    userStore.syncWithLocalStorage();

    const userId = userStore.user?.user_id;
    if (!userId) {
      alert("用戶未登入或 ID 丟失");
      console.error("無法加載個人喜好：用戶 ID 不存在");
      router.push('/login'); // 跳轉回登入頁
      return;
    }

    await fetchPersonalLikes(); // 獲取個人喜好

    if (userId) {
        const storedLikes = localStorage.getItem(`personalLikes_${userId}`);
        if (storedLikes) {
            try {
                const parsedLikes = JSON.parse(storedLikes);
                if (Array.isArray(parsedLikes) && parsedLikes.length > 0) {
                  personalLikes.value = parsedLikes; // 從 localStorage 加載排序資料
                  LikesData.value.personal_like = parsedLikes; // 同步到表單數據
                } else {
                  console.warn('存儲的個人喜好資料無效或為空');
                }
            } catch (error) {
              console.error('解析 localStorage 中的資料時發生錯誤', error);
            }
        } else {
            console.warn('未找到會員喜好資料');
        }
    } else {
        console.error("無法加載會員喜好：用户ID不存在");
    }

    // 從 localStorage 加載會員資料
    try {
      const storedMemberData = localStorage.getItem('memberData');
      if (storedMemberData) {
        memberData.value = JSON.parse(storedMemberData); // 賦值給 memberData
      } else {
        console.warn('未找到會員資料');
      }
    } catch (error) {
      console.error('解析 localStorage 中的會員資料時發生錯誤', error);
    }
});

onBeforeUnmount(() => {
    if (!localStorage.getItem('memberData')) {
        console.log('memberData 丟失，防止跳轉錯誤頁面');
    }
});

// 定義狀態
const showPopup = ref(false); // 控制顯示編輯排序彈窗
const LikesData = ref({
  personal_like: "", // 存儲用戶選擇的喜好
});

// 獲取個人喜好資料 (GET)
const fetchPersonalLikes = async () => {
  const userId = userStore.user?.user_id;

  if (!userId) {
    console.error('無法加載個人喜好：用戶ID不存在');
    alert('用戶未登入或ID丟失');
    return;
  }

  try {
    const response = await fetch(`${API_URL}${userId}/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${userStore.accessToken}`, // 加入 JWT Token
      },
    });

    if (!response.ok) {
      const errorResponse = await response.json();
      console.error('獲取個人喜好失敗，HTTP状态碼:', response.status, '錯誤詳情:', errorResponse);
      throw new Error(errorResponse.error || '獲取失敗');
    }

    // 解析後端返回資料
    const responseData = await response.json();
    console.log('獲取個人喜好成功:', responseData);

    // 檢查 personal_likes 是否為陣列
    if (!Array.isArray(responseData.personal_likes)) {
      console.error('personal_likes 的數據格式錯誤:', responseData.personal_likes);
      alert('返回數據格式錯誤，請聯繫後端檢查');
      return;
    }

    // 當 personal_likes 為空陣列時，保持預設值
    if (responseData.personal_likes.length === 0) {
      console.warn('用戶無個人喜好資料，使用預設資料');
      personalLikes.value = ["ACGN綜合論壇(首頁)", "周邊商店", "討論區(電影相關)", "討論區(動畫相關)", "討論區(遊戲相關)", "委託專區" ,"會員專區"];
    } else {
      // 將後端返回的資料映射為字符串陣列
      personalLikes.value = responseData.personal_likes.map(item => item.type_name || '未命名項目');
    }

    LikesData.value.personal_like = [...personalLikes.value]; // 同步到表單數據
  } catch (error) {
    console.error('獲取個人喜好失敗:', error);
    alert('獲取個人喜好失敗，請檢查後端或網絡連線');
  }
};

// 刪除項目
const removeItem = (index) => {
  personalLikes.value.splice(index, 1);
};

// 保存排序方法
const saveOrder = () => {
  LikesData.value.personal_like = [...personalLikes.value]; // 保留列表格式
  showPopup.value = false; // 關閉彈窗

  // 更新到 localStorage，使用 user_id 作為鍵的一部分
  const userId = userStore.user?.user_id;
  if (userId) {
    localStorage.setItem(
      `personalLikes_${userId}`,
      JSON.stringify(LikesData.value.personal_like)
    );
  } else {
    console.error('用戶 ID 未找到，無法保存排序');
  }
  console.log(`排序已保存：`, LikesData.value.personal_like);
  alert(`排序已保存：${LikesData.value.personal_like.join(", ")}`);
};

// 恢復初始狀態
const resetToInitial = () => {
    personalLikes.value = [...initialPersonalLikes]; // 重置為初始值
    alert('已重置為初始排序');
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
    const userId = userStore.user?.user_id;

    // 确保 user_id 存在
    if (!userId) {
        console.error('用户ID未找到');
        alert('用户ID未找到，请检查用户信息');
        return;
    }

    try {
        // 構建請求的 payload
        const payload = {
            user_id: userId,
            personal_likes: LikesData.value.personal_like.map((item, index) => ({
                type_name: item,
                sort_order: index + 1
            })),
            user_address: memberData.value.user_address  // 添加地址數據
        };
        console.log('更新請求:', JSON.stringify(payload));

        // 發送請求
        const response = await fetch(`${API_URL}${userId}/`, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${userStore.accessToken}`,
            },
        });
        
        if (!response.ok) {
            const errorResponse = await response.json();
            throw new Error(errorResponse.error || '更新失敗');
        }

        const updatedData = await response.json();
        console.log('更新成功:', updatedData);
        
        // 更新本地數據
        memberData.value.user_address = updatedData.user_address;
        
        alert('資料更新成功！');

    } catch (error) {
        console.error('更新失败:', error);
        alert('更新失敗，請檢查後端或網絡連線');
    }
};

// 4. 登出處理
const handleLogout = async () => {
    const confirmLogout = confirm("您即將登出頁面...請您再次確認~*");
    console.log("用戶確認登出:", confirmLogout);

    if (confirmLogout) {
        try {
            console.log("開始登出流程");
            userStore.logout(); // 調用 Pinia 的 logout 方法
            await router.push({ name: 'login' }); // 導向登入頁面
        } catch (error) {
            console.error("登出過程發生錯誤:", error);
        }
    } else {
        console.log("用戶取消登出");
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
            <button @click..prevent="resetToInitial" class="btn btn-info me-3 btn-sm">網站初始排序</button>
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
            <label for="InputAddress" class="form-label">地址設定</label>
            <input type="text" class="form-control" id="InputAddress" name="privicy" v-model="memberData.user_address" placeholder="台北市大安區復興南路一段390號2樓">
        </div>
        <div class="mb-3">
            <label for="PrivicySet" class="form-label">隱私設定</label>
            <input type="text" class="form-control" id="PrivicySet" name="privicy" v-model="memberData.privicy_set">
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