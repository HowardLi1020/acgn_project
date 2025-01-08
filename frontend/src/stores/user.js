import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null, // 用戶資料
    accessToken: null, // 存放 access_token
    refreshToken: null, // 存放 refresh_token
  }),
  actions: {
    login(userData, accessToken, refreshToken) {
      console.log("Login called");
      // 儲存到狀態
      this.user = userData;
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;

      // 同步到 localStorage
      localStorage.setItem('memberData', JSON.stringify(userData));
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    },
    logout() {
      console.log("Logout called");
      // 清空狀態
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;

      // 同步清空 localStorage
      localStorage.removeItem('memberData');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    syncWithLocalStorage() {
      try {
        const userData = localStorage.getItem('memberData');
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
  
        if (userData && accessToken && refreshToken) {
          this.user = JSON.parse(userData);
          this.accessToken = accessToken;
          this.refreshToken = refreshToken;
        }
      } catch (error) {
        console.error('Error syncing with localStorage:', error);
      }
    },
    updateUser(updatedData) {
      // 合併更新用戶資料
      this.user = { ...this.user, ...updatedData };

      // 同步到 localStorage
      localStorage.setItem('memberData', JSON.stringify(this.user));
    },
  },
});