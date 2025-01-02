import axios from 'axios'
const apiUrl = import.meta.env.VITE_APIURL;

const api = axios.create({
    baseURL: import.meta.env.VITE_APIURL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

// 請求攔截器
api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => Promise.reject(error)
)

// 響應攔截器
api.interceptors.response.use(
    response => response,
    async error => {
        if (error.response.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
                try {
                    const response = await axios.post('/api/token/refresh/', {
                        refresh: refreshToken
                    })
                    localStorage.setItem('access_token', response.data.access)
                    error.config.headers.Authorization = `Bearer ${response.data.access}`
                    return axios(error.config)
                } catch (e) {
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                    window.location.href = '/login'
                }
            }
        }
        return Promise.reject(error)
    }
)

// 基礎 GET 請求函數，不需要認證
const getPublic = async (endpoint) => {
    const response = await fetch(`${apiUrl}${endpoint}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};

// 需要認證的 GET 請求
const getWithAuth = async (endpoint) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${apiUrl}${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};

// 需要認證的 POST 請求
const postWithAuth = async (endpoint, data) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': data instanceof FormData ? undefined : 'application/json',
        },
        body: data instanceof FormData ? data : JSON.stringify(data),
        credentials: 'include'
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.error || '請求失敗');
    }
    return response.json();
};

// Store API
export const storeAPI = {
    // 公開 API（使用 getPublic）
    getCategories: () => getPublic('/store/categories/'),
    getBrands: () => getPublic('/store/brands/'),
    getSeries: () => getPublic('/store/series/'),
    getAllProducts: (params) => {
        const queryString = new URLSearchParams(params).toString();
        return getPublic(`/store/view_all_products/?${queryString}`);
    },
    getProductDetail: (productId) => getPublic(`/store/products/${productId}/`),
    
    // 需要認證的 API
    createProduct: (formData) => postWithAuth('/store/create_product/', formData),

    checkWishlist: (productId) => getWithAuth(`/store/wishlist/check/${productId}/`),

    toggleWishlist: (productId) => postWithAuth(`/store/wishlist/toggle/${productId}/`),

    getRecommendations: async (productId, type = 'similar') => {
        try {
            const response = await fetch(`${import.meta.env.VITE_APIURL}/store/recommendations/${type}/${productId}/`);
            if (!response.ok) {
                throw new Error('獲取推薦商品失敗');
            }
            return await response.json();
        } catch (error) {
            console.error('獲取推薦商品時發生錯誤:', error);
            throw error;
        }
    },

    getUserProducts: async (userId) => {
        try {
            const response = await api.get('/store/my-products/', {
                params: { user_id: userId }
            });
            return response.data;
        } catch (error) {
            console.error('獲取用戶產品失敗:', error);
            throw error;
        }
    },

    // 刪除商品
    deleteProduct: async (productId) => {
        try {
            const memberData = JSON.parse(localStorage.getItem("memberData"));
            const userId = memberData?.user_id;

            if (!userId) {
                throw new Error("未找到用戶 ID");
            }
            const params = new URLSearchParams({ user_id: userId });
            const response = await api.delete(`/store/delete_product/${productId}/?${params}`);
            return response.data;
        } catch (error) {
            console.error('刪除商品失敗:', error);
            throw error;
        }
    },

    // 更新商品
    updateProduct: (productId, formData) => {
        return api.put(`/store/edit_product/${productId}/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
};

// 購物車相關 API
export const cartAPI = {
    getCart: () => apiClient.get("/cart_api/cart/"), // 獲取用戶購物車
    addToCart: (data) => apiClient.post("/cart_api/cart/add/", data), // 添加商品到購物車
    updateCartItem: (cartItemId, data) =>
      apiClient.put(`/cart_api/cart/update/${cartItemId}/`, data), // 更新購物車商品數量
    deleteCartItem: (cartItemId) =>
      apiClient.delete(`/cart_api/cart/delete/${cartItemId}/`), // 刪除購物車商品
};

  // 訂單相關 API
export const orderAPI = {
    createOrder: (data) => apiClient.post("/cart_api/orders/create/", data), // 提交新訂單
    getUserOrders: () => apiClient.get("/cart_api/orders/"), // 獲取用戶所有訂單
    getOrderDetail: (orderId) =>
      apiClient.get(`/cart_api/orders/${orderId}/`), // 獲取單個訂單詳細信息
};

// 文件上傳 API
export const uploadAPI = {
    uploadFile: (formData) => postWithAuth('/media/', formData)
};

// 修正默認導出
export default {
    storeAPI,
    uploadAPI,
    api,
};
