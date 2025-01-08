import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useUserStore } from './stores/user';

const app = createApp(App);

const pinia = createPinia(); // 創建 Pinia 實例
app.use(pinia); // 使用 Pinia

// 在應用啟動時同步用戶狀態
const userStore = useUserStore();
userStore.syncWithLocalStorage(); // 同步 LocalStorage 資料到 Pinia

app.use(router); // 使用路由
app.mount('#app');

// 加上這段可以讓死去的輪播功能稍微活一半
$(document).ready(function() {
    // 確保 jQuery 和 owl.carousel 已經加載
    $('.owl-carousel').owlCarousel({
        loop: true,
        margin: 10,
        nav: true,
        items: 1 // 根據需要調整顯示的項目數量
    });
});
