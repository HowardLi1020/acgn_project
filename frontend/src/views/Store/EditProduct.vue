<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { storeAPI } from "../../utils/api";
import Swal from "sweetalert2";

const apiUrl = import.meta.env.VITE_APIURL;
const router = useRouter();
const route = useRoute();
const productId = route.params.productId;

const formData = ref({
    product_name: "",
    description_text: "",
    category: "",
    brand: "",
    series: "",
    price: "",
    stock: "",
    images: [],
});

const newCategory = ref("");
const newBrand = ref("");
const newSeries = ref("");
const categories = ref([]);
const brands = ref([]);
const series = ref([]);
const imagePreviews = ref([]);
const images = ref([]);
const isSubmitting = ref(false);
const deletedImages = ref([]);

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif"];

// 獲取分類、品牌、系列列表
const fetchCategories = async () => {
    try {
        const response = await fetch(`${apiUrl}/store/categories/`);
        if (response.ok) {
            categories.value = await response.json(); // 確保這裡的數據格式正確
            console.log("Fetched categories:", categories.value); // 添加日誌
        } else {
            console.error("Error fetching categories:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching categories:", error);
    }
};

const fetchBrands = async () => {
    try {
        const response = await fetch(`${apiUrl}/store/brands/`);
        brands.value = await response.json();
    } catch (error) {
        console.error("Error fetching brands:", error);
    }
};

const fetchSeries = async () => {
    try {
        const response = await fetch(`${apiUrl}/store/series/`);
        series.value = await response.json();
    } catch (error) {
        console.error("Error fetching series:", error);
    }
};

// 新增分類、品牌、系列
const addCategory = async () => {
    try {
        const response = await fetch(`${apiUrl}/store/create_category/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name: newCategory.value }),
        });
        if (response.ok) {
            await fetchCategories();
            newCategory.value = "";
        }
    } catch (error) {
        console.error("Error adding category:", error);
    }
};

const addBrand = async () => {
    try {
        const response = await fetch(`${apiUrl}/store/create_brand/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name: newBrand.value }),
        });
        if (response.ok) {
            await fetchBrands();
            newBrand.value = "";
        }
    } catch (error) {
        console.error("Error adding brand:", error);
    }
};

const addSeries = async () => {
    try {
        // 驗證輸入
        if (!newSeries.value.trim()) {
            Swal.fire({
                title: "錯誤",
                text: "系列名稱不能為空",
                icon: "error",
            });
            return;
        }

        const response = await fetch(`${apiUrl}/store/create_series/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name: newSeries.value.trim() }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "創建系列失敗");
        }

        // 成功處理
        await fetchSeries(); // 重新獲取系列列表
        newSeries.value = ""; // 清空輸入框

        Swal.fire({
            title: "成功",
            text: "系列創建成功",
            icon: "success",
        });
    } catch (error) {
        console.error("Error adding series:", error);
        Swal.fire({
            title: "錯誤",
            text: error.message || "創建系列失敗",
            icon: "error",
        });
    }
};

// 獲取商品數據
const fetchProductData = async () => {
    try {
        const response = await storeAPI.getProductDetail(productId);

        // 填充表單數據
        formData.value = {
            product_name: response.product_name,
            description_text: response.description_text,
            category: response.category,
            brand: response.brand,
            series: response.series,
            price: response.price,
            stock: response.stock,
        };

        // 處理圖片預覽
        if (response.images && response.images.length > 0) {
            // 直接使用完整的圖片URL
            imagePreviews.value = response.images.map(img => {
                // 檢查 image_url 是否已經是完整的 URL
                if (img.image_url.startsWith('http')) {
                    return img.image_url;
                }
                // 如果不是完整 URL，則添加 API URL 前綴
                return `${apiUrl}${img.image_url}`;
            });
        }

        console.log("商品數據加載成功:", response);
    } catch (error) {
        console.error("獲取商品數據失敗:", error);
        Swal.fire({
            title: "錯誤",
            text: "獲取商品數據失敗",
            icon: "error",
        });
    }
};

// 修改提交處理函數
const handleSubmit = async (event) => {
    event.preventDefault();
    isSubmitting.value = true;

    try {
        // 計算實際剩餘的圖片數量
        // 原有圖片數量 (imagePreviews.value.length - images.value.length) - 被標記刪除的數量 (deletedImages.value.length) + 新上傳的圖片數量 (images.value.length)
        const remainingImagesCount = imagePreviews.value.length;

        if (remainingImagesCount < 1) {
            await Swal.fire({
                title: "錯誤",
                text: "至少需要一張圖片",
                icon: "error",
            });
            return;
        }

        const formDataToSend = new FormData();
        formDataToSend.append("product_name", formData.value.product_name);
        formDataToSend.append("description_text", formData.value.description_text);
        formDataToSend.append("category", formData.value.category);
        formDataToSend.append("brand", formData.value.brand);
        formDataToSend.append("series", formData.value.series);
        formDataToSend.append("price", formData.value.price);
        formDataToSend.append("stock", formData.value.stock);

        // 添加要刪除的圖片列表
        if (deletedImages.value.length > 0) {
            formDataToSend.append("deleted_images", JSON.stringify(deletedImages.value));
        }

        // 添加新上傳的圖片
        images.value.forEach((image) => {
            formDataToSend.append("image_url", image);  // 修改為 image_url 以匹配後端
        });

        const response = await fetch(
            `${apiUrl}/store/edit_product/${productId}/`,
            {
                method: "PUT",
                body: formDataToSend,
            }
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "更新商品失敗");
        }

        await Swal.fire({
            title: "成功",
            text: "商品已成功更新",
            icon: "success",
        });

        router.push("/store/my-products");
    } catch (error) {
        console.error("Error:", error);
        await Swal.fire({
            title: "錯誤",
            text: error.message || "更新商品失敗",
            icon: "error",
        });
    } finally {
        isSubmitting.value = false;
    }
};

// File handling
const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const remainingSlots = 5 - images.value.length;

    // 只取剩餘槽位數量的圖片
    const newFiles = files.slice(0, remainingSlots);

    // 驗證文件大小和類型
    const validFiles = newFiles.filter((file) => {
        if (file.size > MAX_FILE_SIZE) {
            message.value = "圖片大小不能超過 5MB";
            return false;
        }
        if (!ALLOWED_TYPES.includes(file.type)) {
            message.value = "只支持 JPG、PNG 和 GIF 格式";
            return false;
        }
        return true;
    });

    // 添加新的圖片到現有的圖片中
    images.value = [...images.value, ...validFiles];
    formData.value.images = images.value;

    // 更新預覽
    validFiles.forEach((file) => {
        const url = URL.createObjectURL(file);
        imagePreviews.value.push(url);
    });

    // 重置 input
    event.target.value = "";
};

const removeImage = (index) => {
    // 計算原始圖片數量（從伺服器載入的圖片）
    const originalImagesCount = imagePreviews.value.length - images.value.length;

    // 計算刪除後的總圖片數量
    const totalImagesAfterDelete = imagePreviews.value.length - 1;

    // 檢查刪除後是否還有圖片
    if (totalImagesAfterDelete < 1) {
        Swal.fire({
            title: "錯誤",
            text: "至少需要保留一張商品圖片",
            icon: "error",
        });
        return;
    }

    // 如果是原有圖片（從伺服器載入的）
    if (index < originalImagesCount) {
        const imageUrl = imagePreviews.value[index];
        deletedImages.value.push(imageUrl);
    } else {
        // 如果是新上傳的圖片
        const newImageIndex = index - originalImagesCount;
        images.value.splice(newImageIndex, 1);
    }

    // 從預覽中移除
    imagePreviews.value.splice(index, 1);
};

onMounted(async () => {
    if (productId) {
        await fetchProductData();
    }
    await fetchCategories();
    await fetchBrands();
    await fetchSeries();
});
</script>

<template>
    <div class="create-product-container">
        <h1>編輯商品</h1>
        <form @submit.prevent="handleSubmit" class="create-product-form">
            <div class="form-group">
                <label for="product_name">商品名稱</label>
                <input
                    id="product_name"
                    v-model="formData.product_name"
                    type="text"
                    class="form-control"
                    required
                />
            </div>

            <div class="form-group">
                <label for="description">商品描述</label>
                <textarea
                    id="description"
                    v-model="formData.description_text"
                    class="form-control"
                    rows="3"
                    required
                ></textarea>
            </div>

            <div class="form-group">
                <label for="category">分類</label>
                <select
                    id="category"
                    v-model="formData.category"
                    class="form-control"
                    required
                >
                    <option
                        v-for="category in categories"
                        :key="category.category_id"
                        :value="category.category_id"
                    >
                        {{ category.category_name }}
                    </option>
                </select>

                <!-- 新增分類 -->
                <div class="add-new-item">
                    <input
                        v-model="newCategory"
                        type="text"
                        class="form-control"
                        placeholder="新增分類"
                    />
                    <button
                        type="button"
                        @click="addCategory"
                        class="btn btn-secondary"
                    >
                        新增
                    </button>
                </div>
            </div>

            <div class="form-group">
                <label for="brand">品牌</label>
                <select
                    id="brand"
                    v-model="formData.brand"
                    class="form-control"
                    required
                >
                    <option
                        v-for="brand in brands"
                        :key="brand.brand_id"
                        :value="brand.brand_id"
                    >
                        {{ brand.brand_name }}
                    </option>
                </select>

                <!-- 新增品牌 -->
                <div class="add-new-item">
                    <input
                        v-model="newBrand"
                        type="text"
                        class="form-control"
                        placeholder="新增品牌"
                    />
                    <button
                        type="button"
                        @click="addBrand"
                        class="btn btn-secondary"
                    >
                        新增
                    </button>
                </div>
            </div>

            <div class="form-group">
                <label for="series">類別</label>
                <select
                    id="series"
                    v-model="formData.series"
                    class="form-control"
                    required
                >
                    <option
                        v-for="series in series"
                        :key="series.series_id"
                        :value="series.series_id"
                    >
                        {{ series.series_name }}
                    </option>
                </select>

                <!-- 新增類別 -->
                <div class="add-new-item">
                    <input
                        v-model="newSeries"
                        type="text"
                        class="form-control"
                        placeholder="新增類別"
                    />
                    <button
                        type="button"
                        @click="addSeries"
                        class="btn btn-secondary"
                    >
                        新增
                    </button>
                </div>
            </div>

            <div class="form-group">
                <label>價格:</label>
                <input
                    type="number"
                    v-model="formData.price"
                    min="0"
                    step="0.01"
                    required
                />
            </div>

            <div class="form-group">
                <label for="stock">庫存</label>
                <input
                    id="stock"
                    v-model="formData.stock"
                    type="number"
                    class="form-control"
                    min="0"
                    required
                />
            </div>

            <div class="form-group">
                <label>商品圖片:</label>
                <div class="image-grid">
                    <!-- 已上傳的圖片槽位 -->
                    <div
                        v-for="(preview, index) in imagePreviews"
                        :key="'preview-' + index"
                        class="image-slot filled"
                    >
                        <img 
                            :src="preview" 
                            :alt="`Image Preview ${index + 1}`" 
                            @error="$event.target.src = '/placeholder.png'"
                        />
                        <span v-if="index === 0" class="cover-label">封面</span>
                        <button
                            type="button"
                            @click="removeImage(index)"
                            class="remove-button"
                        >
                            ×
                        </button>
                    </div>

                    <!-- 空的上傳槽位 -->
                    <div
                        v-for="n in 5 - imagePreviews.length"
                        :key="'empty-' + n"
                        class="image-slot empty"
                        @click="$refs.fileInput.click()"
                    >
                        <span class="add-icon">+</span>
                    </div>
                </div>
                <input
                    ref="fileInput"
                    type="file"
                    multiple
                    accept="image/*"
                    class="hidden"
                    @change="handleFileUpload"
                />
            </div>

            <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSubmitting"
            >
                {{ isSubmitting ? "更新中..." : "更新商品" }}
            </button>
        </form>
    </div>
</template>

<style scoped>
.create-product-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
    padding-top: 150px;
}

.create-product-form {
    background: #fff;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

.add-new-item {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
}

.btn-primary {
    width: 100%;
    margin-top: 1rem;
}
.image-upload-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.upload-button {
    padding: 0.75rem 1.5rem;
    background-color: #f3f4f6;
    border: 2px dashed #e5e7eb;
    border-radius: 6px;
    color: #4b5563;
    cursor: pointer;
    transition: all 0.2s;
}

.upload-button:hover {
    background-color: #e5e7eb;
}

.upload-hint {
    font-size: 0.875rem;
    color: #6b7280;
}

.image-upload-container {
    margin: 1rem 0;
}

.image-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
}

.image-slot {
    position: relative;
    width: 100%;
    height: 100px; /* 調整高度 */
    border: 2px dashed #ccc;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.add-icon {
    font-size: 2rem;
    color: #ccc;
}

.image-slot img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
}

.remove-button {
    position: absolute;
    top: 5px;
    right: 5px;
    background: red;
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
}
.hidden {
    display: none !important;  /* 使用 !important 確保一定會被隱藏 */
}
</style>
