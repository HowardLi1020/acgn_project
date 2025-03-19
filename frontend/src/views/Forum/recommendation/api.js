// recommendation/api.js

import axios from 'axios';

// 創建一個基本的 axios 實例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',  // 使用完整的 URL 包括域名和端口
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000  // 請求超時時間：10秒
});

// 請求攔截器（可選）
apiClient.interceptors.request.use(
  config => {
    // 在這裡可以添加身份驗證 token 等
    // 例如：const token = localStorage.getItem('token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    console.log('API Request:', config.method.toUpperCase(), config.baseURL + config.url);
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 響應攔截器（可選）
apiClient.interceptors.response.use(
  response => {
    // 可以在這裡統一處理成功的響應
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  error => {
    // 可以在這裡統一處理錯誤
    const errorMessage = error.response?.data?.message || '網絡請求失敗';
    const statusCode = error.response?.status || 'Unknown';
    const url = error.config?.url || 'Unknown URL';
    console.error(`API Error (${statusCode})`, url, errorMessage);
    
    // 輸出更詳細的錯誤信息，幫助調試
    if (error.response) {
      // 服務器回應了請求，但回應了錯誤狀態碼
      console.error('Error Response Data:', error.response.data);
      console.error('Error Response Status:', error.response.status);
      console.error('Error Response Headers:', error.response.headers);
    } else if (error.request) {
      // 請求已發出，但沒有收到回應
      console.error('No response received:', error.request);
    } else {
      // 發送請求時出現了問題
      console.error('Request error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;