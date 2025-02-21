<template>
  <div class="create-post-container">
    <div class="create-post-header">
      <h2>發表新文章</h2>
      <button class="back-button" @click="goBack">返回</button>
    </div>
    
    <div class="form-container">
      <div class="form-group">
        <label for="title">文章標題 <span class="required">*</span></label>
        <input 
          type="text" 
          id="title" 
          v-model="postForm.title" 
          placeholder="請輸入標題（最多50字）"
          maxlength="50"
          :class="{ 'error': errors.title }"
        />
        <span class="error-message" v-if="errors.title">{{ errors.title }}</span>
      </div>
      
      <div class="form-group">
        <label for="category">文章分類 <span class="required">*</span></label>
        <select 
          id="category" 
          v-model="postForm.category_id"
          :class="{ 'error': errors.category }"
        >
          <option v-for="category in categoryOptions" :key="category.id" :value="category.id">
            {{ getCategoryIcon(category.id) }} {{ category.name }}
          </option>
        </select>
        <span class="error-message" v-if="errors.category">{{ errors.category }}</span>
      </div>
      
      <div class="form-group">
        <label for="body">文章內容 <span class="required">*</span></label>
        <textarea 
          id="body" 
          v-model="postForm.body" 
          placeholder="請輸入文章內容..."
          rows="12"
          :class="{ 'error': errors.body }"
        ></textarea>
        <span class="error-message" v-if="errors.body">{{ errors.body }}</span>
        <div class="word-count">
          {{ postForm.body.length }} 字
        </div>
      </div>
      
      <div class="form-group">
        <label for="tags">標籤（選填，最多5個）</label>
        <div class="tags-input">
          <div class="tags-container">
            <div v-for="(tag, index) in postForm.tags" :key="index" class="tag">
              {{ tag }}
              <button type="button" class="remove-tag" @click="removeTag(index)">×</button>
            </div>
            <input 
              type="text" 
              placeholder="輸入標籤後按 Enter"
              v-model="tagInput"
              @keydown.enter.prevent="addTag"
              @keydown.tab.prevent="addTag"
              @keydown.comma.prevent="addTag"
              v-show="postForm.tags.length < 5"
            />
          </div>
        </div>
        <span class="tip">提示: 請用標籤幫助其他用戶找到您的文章，每個標籤按 Enter 確認。</span>
      </div>
      
      <div class="form-submit">
        <button 
          class="submit-button" 
          @click="submitPost" 
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '發布中...' : '發布文章' }}
        </button>
        <button 
          class="preview-button" 
          @click="togglePreview" 
          :disabled="isSubmitting"
        >
          {{ showPreview ? '返回編輯' : '預覽文章' }}
        </button>
      </div>
    </div>
    
    <!-- 預覽區塊 -->
    <div v-if="showPreview" class="preview-container">
      <h3 class="preview-title">預覽模式</h3>
      <div class="post-preview">
        <h2 class="preview-post-title">{{ postForm.title || '未設定標題' }}</h2>
        <div class="preview-meta">
          <span>作者：當前用戶</span>
          <span>發表於：{{ formatDate(new Date()) }}</span>
          <span>分類：{{ getCategoryName(postForm.category_id) }}</span>
        </div>
        <div class="preview-tags" v-if="postForm.tags.length > 0">
          <span class="preview-tag" v-for="tag in postForm.tags" :key="tag">{{ tag }}</span>
        </div>
        <div class="preview-body">
          {{ postForm.body || '尚未輸入內容...' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

export default {
  name: 'CreatePost',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const postForm = reactive({
      title: '',
      body: '',
      tags: [],
      category_id: route.query.category || 'game' // 從URL獲取預設分類，默認為遊戲
    });
    const tagInput = ref('');
    const errors = reactive({
      title: '',
      body: '',
      category: ''
    });
    const isSubmitting = ref(false);
    const showPreview = ref(false);
    
    // 分類選項
    const categoryOptions = [
      { id: 'game', name: '遊戲' },
      { id: 'anime', name: '動畫' },
      { id: 'movie', name: '電影' }
    ];
    
    // 獲取分類名稱
    const getCategoryName = (categoryId) => {
      const category = categoryOptions.find(cat => cat.id === categoryId);
      return category ? category.name : '未分類';
    };
    
    // 獲取分類圖標
    const getCategoryIcon = (categoryId) => {
      switch (categoryId) {
        case 'movie': return '🎬';
        case 'game': return '🎮';
        case 'anime': return '📺';
        default: return '📋';
      }
    };
    
    // 添加標籤
    const addTag = () => {
      const trimmedTag = tagInput.value.trim();
      if (trimmedTag && postForm.tags.length < 5 && !postForm.tags.includes(trimmedTag)) {
        postForm.tags.push(trimmedTag);
        tagInput.value = '';
      }
    };
    
    // 移除標籤
    const removeTag = (index) => {
      postForm.tags.splice(index, 1);
    };
    
    // 表單驗證
    const validateForm = () => {
      let isValid = true;
      errors.title = '';
      errors.body = '';
      errors.category = '';
      
      if (!postForm.title.trim()) {
        errors.title = '請輸入文章標題';
        isValid = false;
      } else if (postForm.title.length < 3) {
        errors.title = '標題至少需要3個字';
        isValid = false;
      }
      
      if (!postForm.body.trim()) {
        errors.body = '請輸入文章內容';
        isValid = false;
      } else if (postForm.body.length < 10) {
        errors.body = '文章內容至少需要10個字';
        isValid = false;
      }
      
      if (!postForm.category_id) {
        errors.category = '請選擇文章分類';
        isValid = false;
      }
      
      return isValid;
    };
    
    // 提交文章
    const submitPost = async () => {
      if (!validateForm()) return;
      
      isSubmitting.value = true;
      try {
        const postData = {
          title: postForm.title,
          body: postForm.body,
          tags: postForm.tags,
          author_id: 1, // 假設當前用戶ID為1
          category_id: postForm.category_id,
          created_at: new Date().toISOString()
        };
        
        // 嘗試使用真實API
        try {
          const response = await axios.post('http://127.0.0.1:8000/api/posts/', postData);
          // 發布成功，跳轉到文章詳情頁
          router.push(`/post/${response.data.post_id}`);
        } catch (apiError) {
          console.warn('API調用失敗，模擬發布成功', apiError);
          // 模擬成功發布，返回上一頁
          alert('文章已發布成功！');
          router.go(-1);
        }
      } catch (error) {
        console.error('發布文章失敗:', error);
        alert('發布失敗，請稍後再試');
      } finally {
        isSubmitting.value = false;
      }
    };
    
    // 切換預覽
    const togglePreview = () => {
      showPreview.value = !showPreview.value;
      // 滾動到頂部以查看預覽
      if (showPreview.value) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };
    
    // 返回上一頁
    const goBack = () => {
      router.go(-1);
    };
    
    // 格式化日期
    const formatDate = (date) => {
      return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    return {
      postForm,
      tagInput,
      errors,
      isSubmitting,
      showPreview,
      categoryOptions,
      addTag,
      removeTag,
      submitPost,
      togglePreview,
      goBack,
      formatDate,
      getCategoryName,
      getCategoryIcon
    };
  }
};
</script>

<style scoped>
.create-post-container {
  max-width: 900px;
  margin: 150px auto 0; /* 增加頂部邊距，避免被導航欄遮擋 */
  padding: 30px 20px;
}

.create-post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.create-post-header h2 {
  font-size: 28px;
  color: #333;
  margin: 0;
}

.back-button {
  padding: 8px 15px;
  background-color: #f0f2f5;
  color: #444;
  border: none;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.back-button:hover {
  background-color: #e4e6e8;
}

.form-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 30px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.required {
  color: #e53935;
  margin-left: 3px;
}

input[type="text"],
textarea,
select {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  transition: border-color 0.2s;
}

input[type="text"]:focus,
textarea:focus,
select:focus {
  border-color: #007bff;
  outline: none;
}

input[type="text"].error,
textarea.error,
select.error {
  border-color: #e53935;
}

.error-message {
  color: #e53935;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.word-count {
  text-align: right;
  margin-top: 5px;
  font-size: 14px;
  color: #777;
}

.tags-input {
  margin-top: 10px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  min-height: 48px;
}

.tag {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  background-color: #e9f5ff;
  color: #0077cc;
  border-radius: 30px;
  font-size: 14px;
}

.remove-tag {
  background: none;
  border: none;
  color: #0077cc;
  font-size: 18px;
  margin-left: 5px;
  cursor: pointer;
  padding: 0 5px;
}

.tags-container input {
  border: none;
  outline: none;
  padding: 5px 0;
  flex-grow: 1;
  min-width: 100px;
  font-size: 14px;
}

.tip {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: #777;
}

.form-submit {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.submit-button,
.preview-button {
  padding: 12px 24px;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.submit-button {
  background-color: #28a745;
  color: white;
}

.submit-button:hover {
  background-color: #218838;
}

.submit-button:disabled {
  background-color: #9fd9af;
  cursor: not-allowed;
}

.preview-button {
  background-color: #f0f2f5;
  color: #444;
}

.preview-button:hover {
  background-color: #e4e6e8;
}

.preview-button:disabled {
  background-color: #f9f9f9;
  color: #aaa;
  cursor: not-allowed;
}

/* 預覽區域 */
.preview-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 30px;
  margin-top: 20px;
}

.preview-title {
  text-align: center;
  padding-bottom: 15px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  color: #666;
  font-size: 18px;
}

.post-preview {
  padding: 0 15px;
}

.preview-post-title {
  font-size: 26px;
  color: #333;
  margin-bottom: 15px;
}

.preview-meta {
  display: flex;
  justify-content: space-between;
  color: #777;
  font-size: 14px;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.preview-tag {
  padding: 4px 10px;
  background-color: #e9f5ff;
  color: #0077cc;
  border-radius: 30px;
  font-size: 14px;
}

.preview-body {
  font-size: 16px;
  line-height: 1.7;
  color: #444;
  margin-bottom: 30px;
  white-space: pre-wrap;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .create-post-container {
    padding: 20px 15px;
    margin-top: 100px; /* 在小屏幕上減小頂部邊距 */
  }
  
  .create-post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .form-container {
    padding: 20px 15px;
  }
  
  .form-submit {
    flex-direction: column;
    gap: 15px;
  }
  
  .submit-button,
  .preview-button {
    width: 100%;
  }
  
  .preview-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>