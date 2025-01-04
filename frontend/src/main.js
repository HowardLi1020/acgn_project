import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';

const pinia = createPinia();

// 創建 Vue 應用並掛載 Pinia 和 Router
const app = createApp(App);
app.use(pinia);
app.use(router);
app.mount('#app');

// jQuery 和 owl-carousel 初始化（確保已正確安裝和引入相關資源）
document.addEventListener('DOMContentLoaded', () => {
    if (window.$ && $('.owl-carousel').length) {
        $('.owl-carousel').owlCarousel({
            loop: true,
            margin: 10,
            nav: true,
            items: 1, // 調整顯示的項目數量
        });
    } else {
        console.warn('jQuery 或 owl-carousel 未正確加載');
    }
});
