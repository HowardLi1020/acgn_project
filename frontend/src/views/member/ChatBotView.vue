<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { marked } from 'marked';

const BASE_URL = import.meta.env.VITE_MemberApi
const LOAD_CHAT = `${BASE_URL}chat-bot/`
const LOAD_Search = `${BASE_URL}search/`

const msg = ref([]);
const inputMessage = ref('');
let sn = 0;
const isOpen = ref(true); // 控制彈窗顯示
const selectedCategory = ref('all'); // 新增：用於存儲選擇的類別
const msgList = ref(null); // 用於引用消息列表

const toggleChat = () => {
  isOpen.value = !isOpen.value;
};

const sendMessage = async () => {
  const message = inputMessage.value;
  if (!message) return;

  // 新增：根據選擇的類別添加前綴
  let fullMessage = message;
  if (selectedCategory.value !== 'all') {
    const categoryText = {
      'movie': '電影',
      'game': '遊戲',
      'anime': '動畫'
    }[selectedCategory.value];
    fullMessage = `[${categoryText}] ${message}`;
  }

  msg.value.push({ content: fullMessage, id: `user_${sn}`, isUser: true });
  sn++;
  inputMessage.value = '';

  // **新增滾動到底部**
  nextTick(() => {
    msgList.value.scrollTop = msgList.value.scrollHeight;
  });

  const payload = {
    session_id: "sess_55663312",
    message: fullMessage,
  };

  try {
    const response = await fetch(LOAD_CHAT, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    // 檢查回應是否為 JSON 格式
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
      const jsonResponse = await response.json();
      if (jsonResponse.type === 'entertainment_filter') {
        msg.value.push({ content: '', id: `ai_${sn}`, isUser: false });
        typeMessage(jsonResponse.message);
        sn++;
        return;
      }
    }

    // 添加 AI 回應的預設消息
    msg.value.push({ content: '', id: `ai_${sn}`, isUser: false });
    
    // 處理流式回應
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let currentResponse = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      
      const text = decoder.decode(value);
      currentResponse += text;
      // 使用 typeMessage 逐字輸出
      typeMessage(currentResponse, null, msg.value.length - 1);
    }

    sn++;

    // 滾動到消息列表底部
    nextTick(() => {
      msgList.value.scrollTop = msgList.value.scrollHeight;
    });


  } catch (error) {
    console.error('Error:', error);
    msg.value.push({ content: '', id: `ai_${sn}`, isUser: false });
    typeMessage('發生錯誤，請稍後再試。');
    sn++;
  }
};

// 修改 typeMessage 函數，添加索引參數
const typeMessage = (text, callback = null, messageIndex = msg.value.length - 1) => {
  let currentText = '';
  const delay = 60; // 每個字的延遲（毫秒）
  let index = 0;

  const interval = setInterval(() => {
    if (index < text.length) {
      currentText += text[index];
      index++;
      msg.value[messageIndex].content = marked.parse(currentText); // 動態更新內容

      // 每次更新都滾動到底部
      nextTick(() => {
        msgList.value.scrollTop = msgList.value.scrollHeight;
      });
      
    } else {
      clearInterval(interval);
      if (callback) callback();
    }
  }, delay);
};

// 在組件加載時發送問候語
onMounted(() => {
  msg.value.push({
    content: '', // 初始化為空字符串
    id: `ai_${sn}`,
    isUser: false,
  });
  sn++;

  // 開始逐字輸出消息
  typeMessage('您好，我是聊天機器人，會嘗試為您推薦或查找相關『電影、遊戲、動畫』資訊，請問今天要問什麼呢~?');
});
</script>

<template>
    <div class="chat-popup" :style="{ display: isOpen ? 'block' : 'none' }">
        <div class="chat-header">
            <h4>聊天機器人</h4>
            <button class="button-8" @click="toggleChat">關閉</button>
        </div>
        <div class="chatroom">
            <ul id="msg" ref="msgList">
                <li v-for="(message, index) in msg" :key="index" :class="{ user: message.isUser }">
                    <div v-html="message.content"></div>
                </li>
            </ul>
            <div class="input-area">
                <div class="input-container">
                    <select v-model="selectedCategory" class="category-select">
                        <option value="all">全部類別</option>
                        <option value="movie">電影</option>
                        <option value="game">遊戲</option>
                        <option value="anime">動畫</option>
                    </select>
                    <textarea v-model="inputMessage" placeholder="請輸入您的訊息"></textarea>
                </div>
                <button class="button-8" @click="sendMessage">送出</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.chat-popup {
  position: fixed;
  bottom: 100px;
  right: 300px;
  width: 1300px; /* 初始寬度 */
  height: 650px; 
  max-height: 1000px; /* 最大高度 */
  border: 1px solid #ccc;
  background-color: rgb(214, 224, 224);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  resize: both; /* 允許用戶調整大小 */
  overflow: auto ; /* 隱藏溢出內容 */
}

.chat-header {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f1f1f1;
  border-bottom: 1px solid #ccc;
}

.chatroom {
  display: flex;
  flex-direction: column;
  height: calc(100% - 50px); /* 扣除 header 高度 */
  padding: 10px;
}

.chatroom li div {
  white-space: pre-line; /* 多行自動換行 */
  font-size: 18px;
  line-height: 1;
  color: #333;
}

ul#msg {
  list-style-type: none;
  margin: 0;
  padding: 10px;
  overflow-y: auto; /* 允許垂直滾動 */
  flex: 1 1 auto; /* 讓消息區域自動佔據剩餘空間 */
  min-height: 0; /* 確保可以正確滾動 */
  max-height: calc(100% - 150px); /* 限制最大高度，預留輸入區域空間 */
}

ul#msg li {
  padding: 5px;
  font-family: 'Times New Roman', Times, serif;
  font-size: 20px;
  display: flex;
  justify-content: flex-start; /* 默認左對齊 */
}

ul#msg li.user {
  justify-content: flex-end; /* 使用者消息右對齊 */
  background-color: #d1ecf1; /* 添加背景色區分用戶訊息 */
}

ul#msg li:not(.user) {
  background-color: #eeeedb; /* 添加背景色區分機器人訊息 */
}

.input-area {
  flex: 0 0 auto; /* 不要縮放 */
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

.input-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.category-select {
  width: 120px;
  height: 40px;
  padding: 5px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  background-color: white;
  cursor: pointer;
}

textarea {
  flex: 1;
  height: 80px;
  min-height: 80px;
  max-height: 80px;
  resize: none;
  font-family: 'Times New Roman', Times, serif;
  font-size: 18px;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.button-8 {
  background-color: #e1ecf4;
  border-radius: 3px;
  border: 1px solid #7aa7c7;
  box-shadow: rgba(255, 255, 255, .7) 0 1px 0 0 inset;
  box-sizing: border-box;
  color: #39739d;
  cursor: pointer;
  display: inline-block;
  font-family: -apple-system,system-ui,"Segoe UI","Liberation Sans",sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.15385;
  margin: 0;
  outline: none;
  padding: 8px .8em;
  position: relative;
  text-align: center;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  vertical-align: baseline;
  white-space: nowrap;
}

.button-8:hover,
.button-8:focus {
  background-color: #b3d3ea;
  color: #2c5777;
}

.button-8:focus {
  box-shadow: 0 0 0 4px rgba(0, 149, 255, .15);
}

.button-8:active {
  background-color: #a0c7e4;
  box-shadow: none;
  color: #2c5777;
}
</style>
