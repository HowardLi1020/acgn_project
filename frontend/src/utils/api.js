import axios from "axios";
const apiUrl = import.meta.env.VITE_APIURL;

export const api = axios.create({
    baseURL: import.meta.env.VITE_APIURL,
    withCredentials: true,
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
    },
});
// 請求攔截器
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);
// 響應攔截器
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response && error.response.status === 401) {
            const refreshToken = localStorage.getItem("refresh_token");
            if (refreshToken) {
                try {
                    const response = await axios.post(
                        "/member_api/auth/refresh_token/",
                        {
                            refresh: refreshToken,
                        }
                    );
                    localStorage.setItem("access_token", response.data.access);
                    error.config.headers.Authorization = `Bearer ${response.data.access}`;
                    return axios(error.config);
                } catch (refreshError) {
                    console.error("刷新 Token 失敗:", refreshError);
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    window.location.href = "/login";
                }
            }
        }
        return Promise.reject(error);
    }
);
const parseJwt = (token) => {
    try {
        const base64Url = token.split(".")[1];
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split("")
                .map(function (c) {
                    return (
                        "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2)
                    );
                })
                .join("")
        );

        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("Error parsing JWT:", e);
        return null;
    }
};
// 獲取當前用戶ID的函數
export const getCurrentUserId = () => {
    const token = localStorage.getItem("access_token");
    if (!token) return null;

    const decodedToken = parseJwt(token);
    return decodedToken ? decodedToken.user_id : null;
};
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
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${apiUrl}${endpoint}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};
// 需要認證的 POST 請求
const postWithAuth = async (endpoint, data) => {
    const token = localStorage.getItem("access_token"); // 改為 access_token
    if (!token) {
        throw new Error("未登入，請先登入");
    }

    const response = await fetch(`${apiUrl}${endpoint}`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
            ...(!(data instanceof FormData) && {
                "Content-Type": "application/json",
            }),
        },
        body: data instanceof FormData ? data : JSON.stringify(data),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.error || "請求失敗");
    }
    return response.json();
};
// Store API
export const storeAPI = {
    // 公開 API（使用 getPublic）
    getCategories: () => getPublic("/store/categories/"),
    getBrands: () => getPublic("/store/brands/"),
    getSeries: () => getPublic("/store/series/"),
    getAllProducts: (params) => {
        const queryString = new URLSearchParams(params).toString();
        return getPublic(`/store/?${queryString}`);
    },
    getProductDetail: (productId) => getPublic(`/store/products/${productId}/`),

    createCategory: async (data) => {
        try {
            const response = await api.post("/store/create_category/", data);
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(error.response?.data?.detail || "創建分類失敗");
        }
    },
    
    createBrand: async (data) => {
        try {
            const response = await api.post("/store/create_brand/", data);
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(error.response?.data?.detail || "創建品牌失敗");
        }
    },
    
    createSeries: async (data) => {
        try {
            const response = await api.post("/store/create_series/", data);
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(error.response?.data?.detail || "創建系列失敗");
        }
    },

    // 需要認證的 API
    createProduct: async (formData) => {
        try {
            const response = await api.post(
                "/store/create_product/",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(error.response?.data?.detail || "創建商品失敗");
        }
    },

    checkWishlist: (productId) =>
        getWithAuth(`/store/wishlist/check/${productId}/`),

    toggleWishlist: (productId) =>
        postWithAuth(`/store/wishlist/toggle/${productId}/`),

    // 獲取用戶收藏的商品
    getWishlist: async () => {
        try {
            const response = await api.get("/store/wishlist/list/");
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(error.response?.data?.detail || "獲取收藏商品失敗");
        }
    },

    getRecommendations: async (productId, type = "similar") => {
        try {
            const response = await fetch(
                `${
                    import.meta.env.VITE_APIURL
                }/store/recommendations/${type}/${productId}/`
            );
            if (!response.ok) {
                throw new Error("獲取推薦商品失敗");
            }
            return await response.json();
        } catch (error) {
            console.error("獲取推薦商品時發生錯誤:", error);
            throw error;
        }
    },

    getUserProducts: async () => {
        try {
            const token = localStorage.getItem("access_token");
            if (!token) {
                throw new Error("未登入，請先登入");
            }

            const response = await api.get("/store/my-products/");

            // 確保返回的數據結構正確
            if (!response.data || !response.data.products) {
                throw new Error("無效的響應數據");
            }

            return response.data;
        } catch (error) {
            console.error("獲取產品列表錯誤:", error);
            if (error.response?.status === 401) {
                throw new Error("未登入或登入已過期，請重新登入");
            }
            throw new Error(error.response?.data?.detail || "獲取產品列表失敗");
        }
    },

    // 刪除商品
    deleteProduct: async (productId) => {
        try {
            // 使用配置好的 api 實例而不是 axios
            const response = await api.delete(
                `/store/delete_product/${productId}/`
            );
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            } else if (error.response?.status === 403) {
                throw new Error("您沒有權限刪除此商品");
            }
            throw new Error(error.response?.data?.detail || "刪除商品失敗");
        }
    },

    // 更新商品
    updateProduct: (productId, formData) => {
        return api.put(`/store/edit_product/${productId}/`, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
    },

    // 獲取購買紀錄
    getPurchasedProducts: async () => {
        try {
            const response = await api.get("/store/purchased-products/");
            return response;
        } catch (error) {
            console.error("獲取購買紀錄失敗:", error);
            throw error;
        }
    },

    // 獲取商品評論
    getProductReviews: async (productId) => {
        try {
            const response = await api.get(
                `/store/products/${productId}/reviews/`
            );
            return response.data; // 直接返回 data
        } catch (error) {
            console.error("獲取評論失敗:", error);
            return { reviews: [] }; // 發生錯誤時返回空評論列表
        }
    },

    // 提交商品評論
    submitReview: async (productId, reviewData) => {
        try {
            const response = await api.post(
                `/store/products/${productId}/reviews/`,
                reviewData
            );
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("請先登入");
            } else if (error.response?.status === 403) {
                throw new Error("您尚未購買此商品，無法評論");
            } else if (error.response?.status === 400) {
                throw new Error(error.response.data.detail || "評論提交失敗");
            }
            throw new Error("提交評論時發生錯誤");
        }
    },

    // 檢查是否可以評論
    checkCanReview: async (productId) => {
        try {
            const response = await api.get(
                `/store/products/${productId}/can-review/`
            );
            return response.data; // 直接返回 data
        } catch (error) {
            console.error("檢查評論權限失敗:", error);
            return { can_review: false };
        }
    },

    // 更新商品評論
    updateReview: async (productId, reviewId, reviewData) => {
        try {
            const response = await api.put(
                `/store/products/${productId}/reviews/${reviewId}/`,
                reviewData
            );
            return response.data;
        } catch (error) {
            console.error("更新評論失敗:", error);
            throw error;
        }
    },

    // 刪除評論
    deleteReview: async (productId, reviewId) => {
        try {
            const response = await api.delete(
                `/store/products/${productId}/reviews/${reviewId}/`
            );
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("請先登入");
            } else if (error.response?.status === 403) {
                throw new Error("您沒有權限刪除此評論");
            }
            throw new Error("刪除評論時發生錯誤");
        }
    },
};

// Cart API
export const cartAPI = {
    // 獲取購物車內容
    getCartItems: async () => {
        try {
            const response = await api.get("/cart_api/cart/");
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(
                error.response?.data?.detail || "無法獲取購物車內容"
            );
        }
    },

    // 添加商品到購物車
    addCartItem: async (data) => {
        try {
            const response = await api.post("/cart_api/cart/", data);
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(
                error.response?.data?.detail || "無法添加商品到購物車"
            );
        }
    },

    // 更新購物車內商品數量
    updateCartItem: async (data) => {
        try {
            // 假設 data 格式為 { product_id: number, action: 'increment' | 'decrement' }
            const response = await api.put("/cart_api/cart/", data);
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(
                error.response?.data?.detail || "無法更新購物車內容"
            );
        }
    },

    // 刪除購物車中的商品
    deleteCartItem: async (productId) => {
        try {
            const response = await api.delete("/cart_api/cart/", {
                data: { product_id: productId },
            });
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("登入已過期，請重新登入");
            }
            throw new Error(
                error.response?.data?.detail || "無法刪除購物車中的商品"
            );
        }
    },
};

// Order API
export const orderAPI = {
    submitOrder: async (orderdata) => {
        try {
            const response = await api.post(
                "/cart_api/create_order/",
                orderdata
            );
            return response.data; // 返回訂單數據
        } catch (error) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.message || "訂單提交失敗");
            } else {
                throw new Error("無法連接到伺服器，請稍後再試");
            }
        }
    },
    payOrder: async (orderId) => {
        try {
            const response = await api.post(`/cart_api/ecpay/${orderId}/`);
            console.log("ECPay 付款 API 回應:", response.data);
            return response.data;
        } catch (err) {
            console.error(
                "取得付款連結失敗:",
                err.response?.data || err.message
            );
            throw err;
        }
    },
    async getOrderList() {
        try {
            const response = await api.get("/cart_api/order_list/"); // 後端的 API 路徑
            return response.data; // 返回訂單清單數據
        } catch (error) {
            throw new Error(
                error.response?.data?.message || "無法獲取訂單清單"
            );
        }
    },
};

// Coupon API
export const couponAPI = {
    // 獲取用戶可用的優惠券
    getUserCoupons: async () => {
        try {
            const response = await api.get("/member_api/usercoupons/");
            return response.data;
        } catch (error) {
            console.error("無法獲取用戶優惠券：", error);
            throw error;
        }
    },
    // 手動兌換優惠券
    redeemCoupon: async (couponCode) => {
        try {
            const response = await api.post("/member_api/usercoupons/redeem/", {
                coupon_code: couponCode,
            });
            return response.data;
        } catch (error) {
            console.error("兌換優惠券時發生錯誤：", error);
            throw error;
        }
    },
};

// 文件上傳 API
export const uploadAPI = {
    uploadFile: (formData) => postWithAuth("/media/", formData),
};

// 修正默認導出
export default {
    storeAPI,
    uploadAPI,
    cartAPI,
    couponAPI,
    orderAPI,
    api,
};
