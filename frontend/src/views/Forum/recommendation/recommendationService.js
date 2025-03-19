// recommendation/recommendationService.js

import apiClient from './api';

// 獲取推薦內容
export const getRecommendations = (searchParams) => {
  // 方便調試，輸出請求參數
  console.log('Recommendation request payload:', searchParams);
  
  // 根據 Django URL 設置正確的路徑
  return apiClient.post('/recommendations/', searchParams).catch(error => {
    // 特別處理 404 錯誤，提供更多信息
    if (error.response && error.response.status === 404) {
      console.error('API 端點無法訪問。請確認後端路由配置正確:', '/api/recommendations/');
      console.error('完整的請求路徑:', apiClient.defaults.baseURL + '/recommendations/');
    }
    throw error;
  });
};

// 獲取可用的內容類型（電影、動畫、遊戲等）
export const getContentTypes = () => {
  return apiClient.get('/content-types/');
};

// 獲取可用的風格/類型列表
export const getGenres = () => {
  return apiClient.get('/genres/');
};

// 檢查系統狀態
export const checkSystemStatus = () => {
  return apiClient.get('/system-status/');
};

// 測試與後端連接的函數 - 用於診斷問題
export const testBackendConnection = () => {
  // 第一步：檢查系統狀態 API
  return checkSystemStatus()
    .then(response => {
      console.log('系統狀態 API 測試成功:', response.data);
      // 第二步：嘗試獲取內容類型
      return getContentTypes();
    })
    .then(response => {
      console.log('內容類型 API 測試成功:', response.data);
      // 第三步：嘗試獲取類型/風格
      return getGenres();
    })
    .then(response => {
      console.log('類型/風格 API 測試成功:', response.data);
      return { success: true, message: '所有 API 測試通過!' };
    })
    .catch(error => {
      console.error('API 連接測試失敗:', error);
      return {
        success: false,
        message: 'API 連接測試失敗',
        error: error.response ? `${error.response.status} - ${error.response.statusText}` : error.message
      };
    });
};