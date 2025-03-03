<script setup>
import { computed } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore(); // Pinia 用戶狀態

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 動態計算路由
const computedRoute = computed(() => {
      if (userStore.user) {
        // 已登入，跳轉到會員專區
        return { name: 'center', params: { user_id: userStore.user.user_id } };
      } else {
        // 未登入，跳轉到登入頁面
        return { name: 'login' };
      }
    });
</script>

<template>
    <!-- Navbar start -->
    <div class="container-fluid fixed-top">
        <div class="container topbar bg-primary d-none d-lg-block">
            <div class="d-flex justify-content-between">
                <div class="top-info ps-2">
                    <small class="me-3"><i class="fas fa-map-marker-alt me-2 text-secondary"></i> <a href="#" class="text-white">123 Street, New York</a></small>
                    <small class="me-3"><i class="fas fa-envelope me-2 text-secondary"></i><a href="#" class="text-white">ACGN666@gmail.com</a></small>
                </div>
                <div class="top-link pe-2">
                    <a href="#" class="text-white"><small class="text-white mx-2">隱私政策</small>/</a>
                    <a href="#" class="text-white"><small class="text-white mx-2">服務條款</small>/</a>
                    <a href="#" class="text-white"><small class="text-white ms-2">關於我們</small></a>
                </div>
            </div>
        </div>
        <div class="container px-0">
            <nav class="navbar navbar-light bg-white navbar-expand-xl">
                <router-link to="/" class="navbar-brand" @click="scrollToTop"><h1 class="text-primary display-6">ACGN 綜合論壇</h1></router-link>
                <button class="navbar-toggler py-2 px-3" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
                    <span class="fa fa-bars text-primary"></span>
                </button>
                <div class="collapse navbar-collapse bg-white" id="navbarCollapse">
                    <div class="navbar-nav mx-auto">
                        <router-link to="/" class="nav-item nav-link active" @click="scrollToTop">首頁</router-link>
                        <router-link to="/Forum" class="nav-item nav-link" @click="scrollToTop">討論區</router-link>
                        <router-link to="/store" class="nav-item nav-link" @click="scrollToTop">周邊商店</router-link>
                        <router-link to="/commission" class="nav-item nav-link" @click="scrollToTop">委託專區</router-link>
                        <router-link :to="computedRoute" class="nav-item nav-link" @click="scrollToTop">會員專區</router-link>
                        <div class="nav-item dropdown">
                            <a href="#" class="nav-link dropdown-toggle" data-bs-toggle="dropdown">列表</a>
                            <div class="dropdown-menu m-0 bg-secondary rounded-0">
                                <router-link to="/Fruitables" class="nav-item nav-link active" @click="scrollToTop">首頁</router-link>
                                <router-link to="/store" class="nav-item nav-link" @click="scrollToTop">商店</router-link>
                                <router-link to="/commission" class="nav-item nav-link" @click="scrollToTop">委託專區</router-link>
                                <router-link :to="computedRoute" class="nav-item nav-link" @click="scrollToTop">會員專區</router-link>
                                <router-link to="/chat-bot" class="nav-item nav-link" @click="scrollToTop">聊天室</router-link>
                                
                            </div>
                        </div>
                        
                    </div>
                    <div class="d-flex m-3 me-0">
                        <button class="btn-search btn border border-secondary btn-md-square rounded-circle bg-white me-4" data-bs-toggle="modal" data-bs-target="#searchModal"><i class="fas fa-search text-primary"></i></button>
                        <router-link to="/shoppingcart" class="position-relative me-4 my-auto">
                            <i class="fa fa-shopping-bag fa-2x"></i>
                        </router-link>
                        <router-link :to="computedRoute" class="my-auto">
                            <i class="fas fa-user fa-2x"></i>
                        </router-link>
                    </div>
                </div>
            </nav>
        </div>
    </div>
    <!-- Navbar End -->
</template>

<style lang="css" scoped>

</style>