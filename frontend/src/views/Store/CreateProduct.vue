<script setup>
import { ref, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { storeAPI } from '@/utils/api';
import Swal from "sweetalert2";

const apiUrl = import.meta.env.VITE_APIURL;
const router = useRouter();


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


const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif"];

// 獲取分類、品牌、系列列表
const fetchCategories = async () => {
    try {
        const response = await storeAPI.getCategories();
        categories.value = response;
        console.log("Fetched categories:", categories.value);
    } catch (error) {
        console.error("Error fetching categories:", error);
    }
};

const fetchBrands = async () => {
    try {
        const response = await storeAPI.getBrands();
        brands.value = response;
    } catch (error) {
        console.error("Error fetching brands:", error);
    }
};

const fetchSeries = async () => {
    try {
        const response = await storeAPI.getSeries();
        series.value = response;
    } catch (error) {
        console.error("Error fetching series:", error);
    }
};

// 新增分類、品牌、系列
const addCategory = async () => {
    try {
        // 驗證輸入
        if (!newCategory.value.trim()) {
            Swal.fire({
                title: "錯誤",
                text: "分類名稱不能為空",
                icon: "error"
            });
            return;
        }

        await storeAPI.createCategory({ name: newCategory.value.trim() });
        await fetchCategories();
        newCategory.value = "";
        
        Swal.fire({
            title: "成功",
            text: "分類創建成功",
            icon: "success"
        });
    } catch (error) {
        console.error("Error adding category:", error);
        Swal.fire({
            title: "錯誤",
            text: error.message || "創建分類失敗",
            icon: "error"
        });
    }
};

const addBrand = async () => {
    try {
        // 驗證輸入
        if (!newBrand.value.trim()) {
            Swal.fire({
                title: "錯誤",
                text: "品牌名稱不能為空",
                icon: "error"
            });
            return;
        }

        await storeAPI.createBrand({ name: newBrand.value.trim() });
        await fetchBrands();
        newBrand.value = "";
        
        Swal.fire({
            title: "成功",
            text: "品牌創建成功",
            icon: "success"
        });
    } catch (error) {
        console.error("Error adding brand:", error);
        Swal.fire({
            title: "錯誤",
            text: error.message || "創建品牌失敗",
            icon: "error"
        });
    }
};

const addSeries = async () => {
    try {
        // 驗證輸入
        if (!newSeries.value.trim()) {
            Swal.fire({
                title: "錯誤",
                text: "系列名稱不能為空",
                icon: "error"
            });
            return;
        }

        await storeAPI.createSeries({ name: newSeries.value.trim() });
        await fetchSeries();
        newSeries.value = "";
        
        Swal.fire({
            title: "成功",
            text: "系列創建成功",
            icon: "success"
        });
    } catch (error) {
        console.error("Error adding series:", error);
        Swal.fire({
            title: "錯誤",
            text: error.message || "創建系列失敗",
            icon: "error"
        });
    }
};

// 提交表單
const handleSubmit = async (event) => {
    event.preventDefault();
    isSubmitting.value = true;

    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('請先登入');
        }

        const formDataToSend = new FormData();
        formDataToSend.append('product_name', formData.value.product_name);
        formDataToSend.append('description_text', formData.value.description_text);
        formDataToSend.append('category', formData.value.category);
        formDataToSend.append('brand', formData.value.brand);
        formDataToSend.append('series', formData.value.series);
        formDataToSend.append('price', formData.value.price);
        formDataToSend.append('stock', formData.value.stock);

        images.value.forEach((image) => {
            formDataToSend.append('images', image);
        });

        // 使用 storeAPI 創建商品
        const response = await storeAPI.createProduct(formDataToSend);
        
        await Swal.fire({
            title: "成功",
            text: "商品已成功創建",
            icon: "success",
        });

        // 清空表單
        formData.value = {
            product_name: '',
            description_text: '',
            category: '',
            brand: '',
            series: '',
            price: '',
            stock: '',
            images: [],
        };
        images.value = [];
        imagePreviews.value = [];

        router.push("/store");
    } catch (error) {
        console.error("Error:", error);
        if (error.message.includes('請先登入') || error.message.includes('登入已過期')) {
            await Swal.fire({
                title: "錯誤",
                text: error.message,
                icon: "error",
                confirmButtonText: "前往登入"
            });
            router.push('/login');
            return;
        }
        Swal.fire({
            title: "錯誤",
            text: error.message,
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
    validFiles.forEach(file => {
        const url = URL.createObjectURL(file);
        imagePreviews.value.push(url);
    });
    

    // 重置 input
    event.target.value = "";
};

const removeImage = (index) => {
    images.value.splice(index, 1);
    imagePreviews.value.splice(index, 1);
};

// 返回商店頁面
const backToStore = () => {
  router.push('/store');
};

onMounted(async () => {
    await nextTick(); // 確保 DOM 更新

    await fetchCategories();
    await fetchBrands();
    await fetchSeries();
});
</script>

<template>
    <div class="create-product-container">
        <h1>創建新商品</h1>
        <button @click="backToStore" class="back-button">返回商店</button>
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
                <label for="series">系列</label>
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
                        <img :src="preview" alt="Image Preview" />
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
                {{ isSubmitting ? "創建中..." : "創建商品" }}
            </button>
        </form>
    </div>
</template>

<style scoped>
.create-product-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
    padding-top: 150PX;
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

.back-button {
  margin-bottom: 20px;
  padding: 8px 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.back-button:hover {
  background-color: #45a049;
}
</style>
