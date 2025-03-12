import { defineStore } from 'pinia';
import api from '@/utils/api';

const BASE_URL = import.meta.env.VITE_MemberApi;
const API_URL = `${BASE_URL}auth/update-likes/`;

export const fetchPersonalLikes = async () => {
  const userStore = useUserStore();
  const userId = userStore.user?.user_id;

  if (!userId) {
    console.error('無法加載個人喜好：用戶ID不存在');
    alert('用戶未登入或ID丟失');
    return [];
  }

  try {
    const response = await fetch(`${API_URL}${userId}/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${userStore.accessToken}`,
      },
    });

    if (!response.ok) {
      console.error('獲取個人喜好失敗:', response.status);
      return [];
    }

    const responseData = await response.json();
    console.log('獲取個人喜好成功:', responseData);

    return responseData.personal_likes ?? [];
  } catch (error) {
    console.error('獲取個人喜好失敗:', error);
    return [];
  }
};

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null, // 用戶資料
    accessToken: null, // 存放 access_token
    refreshToken: null, // 存放 refresh_token
    isAuthenticated: false, // 登入狀態
    personalLikes: [], // 用戶的個人喜好
  }),
  getters: {
    // 檢查是否已登入
    isLoggedIn(state) {
      return !!state.accessToken && state.isAuthenticated;
    },
  },
  actions: {
    setUser(userData, accessToken, refreshToken) {
      this.user = userData;
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      this.isAuthenticated = true;
    },

    // 登入
    login(userData, accessToken, refreshToken) {
      console.log("Login called");
      // 儲存到狀態
      this.user = userData;
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      this.isAuthenticated = true;

      // 同步到 localStorage
      localStorage.setItem('memberData', JSON.stringify(userData));
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      localStorage.setItem('isAuthenticated', 'true');
    },

    // 登出
    logout() {
      console.log("Logout called");
      const userId = this.user?.user_id;
      // 清空狀態
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.isAuthenticated = false;
      this.personalLikes = []; // 清空個人喜好

      // 同步清空 localStorage
      localStorage.removeItem('memberData');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isAuthenticated');

      // 删除特定的 personalLikes 项目
      if (userId) {
        localStorage.removeItem(`personalLikes_${userId}`);
      }
      localStorage.removeItem('personalLikes');
    },

    // 同步狀態與 localStorage
    syncWithLocalStorage() {
      try {
        const userData = localStorage.getItem('memberData');
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        // const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  
        if (userData && accessToken && refreshToken) {
          this.user = JSON.parse(userData);
          this.accessToken = accessToken;
          this.refreshToken = refreshToken;
          this.isAuthenticated = true;

          // 同步个人喜好
          const userId = this.user?.user_id;
          if (userId) {
            const storedLikes = localStorage.getItem(`personalLikes_${userId}`);
            if (storedLikes) {
              this.personalLikes = JSON.parse(storedLikes);
            }
          }
        } else {
          this.logout(); // 同步失敗時清空狀態
        }
      }catch (error) {
            console.error('Error syncing with localStorage:', error);
            this.logout(); // 清空狀態
          }
        },

    // 更新用戶資料
    updateUser(updatedData) {
      // 合併更新用戶資料
      this.user = { ...this.user, ...updatedData };

      // 同步到 localStorage
      localStorage.setItem('memberData', JSON.stringify(this.user));
    },

    // 更新用戶個人喜好
    updatePersonalLikes(updatedLikes) {
      this.personalLikes = [...updatedLikes];
      const userId = this.user?.user_id;
      if (userId) {
        localStorage.setItem(`personalLikes_${userId}`, JSON.stringify(this.personalLikes));
      } else {
        console.error('无法更新个人喜好：用户 ID 不存在');
      }
    },

    // 檢查 Token 是否有效
    async fetchProtectedData(endpoint) {
      try {
        // 直接使用封裝的 api 發送請求
        const response = await api.get(endpoint);
        return response.data;
      } catch (error) {
        console.error('Error fetching protected data:', error);
        throw error;
      }
    },

    // 刷新 Token
    async refreshTokenIfNeeded() {
      const refreshToken = this.refreshToken || localStorage.getItem('refresh_token');
      if (!refreshToken) {
        console.error("Refresh Token 不存在，無法刷新");
        return false;
      }
      try {
        const response = await fetch('http://127.0.0.1:8000/member_api/auth/refresh_token/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: this.refreshToken }),
        });

        if (!response.ok) {
          console.error('刷新 Token 失敗:', response.status);
          this.logout(); // 如果需要登出邏輯
          return false;
        }

        const data = await response.json();
        this.accessToken = data.access;
        localStorage.setItem('access_token', data.access);
        console.log('Token 刷新成功:', data.access);
        return true;
      } catch (error) {
        console.error('刷新 Token 發生錯誤:', error.message);
        this.logout(); // 如果需要登出邏輯
        return false;
      }
    },

    // 驗證電子郵箱格式
    validateEmail(email) {
      if (!email) return '請輸入電子郵箱';
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email) ? null : '請輸入有效的電子郵箱格式';
    },

    // 驗證手機號碼格式
    validatePhone(phone) {
      if (!phone) return '請輸入手機號碼';
      const phoneRegex = /^09\d{8}$/;
      return phoneRegex.test(phone) ? null : '請輸入有效的手機號碼格式';
    },

    // 驗證密碼強度
    validatePassword(password) {
      if (!password) return '請輸入密碼';
      if (password.length < 8) return '密碼長度至少為8個字符';
      if (!/[a-zA-Z]/.test(password)) return '密碼必須包含至少一個字母';
      if (!/\d/.test(password)) return '密碼必須包含至少一個數字';
      return null; // 無錯誤時返回 null     
    },

    // 驗證姓名
    validateName(name) {
      if (!name) return '請輸入姓名';
      if (name.length < 2 || name.length > 10) return '姓名請輸入2-10個字符';
      return null; // 無錯誤時返回 null
    },

    // 統一驗證方法
    validateForm(formData) {
      const errors = {};

      // 驗證各個字段
      const nameError = this.validateName(formData.user_name);
      if (nameError) errors.user_name = nameError;

      const emailError = this.validateEmail(formData.user_email);
      if (emailError) errors.user_email = emailError;

      const phoneError = this.validatePhone(formData.user_phone);
      if (phoneError) errors.user_phone = phoneError;

      const passwordError = this.validatePassword(formData.user_password);
      if (passwordError) errors.user_password = passwordError;

      // 驗證確認密碼
      if (!formData.confirm_password) {
        errors.confirm_password = '請確認密碼';
      } else if (formData.user_password !== formData.confirm_password) {
        errors.confirm_password = '兩次輸入的密碼不一致';
      }

      // 驗證服務條款
      if (!formData.agreeToTerms) {
        errors.agreeToTerms = '請同意服務條款';
      }

      return errors; // 返回所有錯誤信息
    },
  },
});