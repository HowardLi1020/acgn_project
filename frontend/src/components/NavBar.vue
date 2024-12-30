<template>
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">ACGN 商城</router-link>
        <ul class="nav-links">
          <li><router-link to="/">首頁</router-link></li>
          <li><router-link to="/store">商店</router-link></li>
          <li><router-link to="/login">登入</router-link></li>
          <li><router-link to="/register">註冊</router-link></li>
        </ul>
      </div>
    </nav>
</template>

<script setup>
// 使用 setup 語法
</script>

<style scoped>
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 60px;
    background-color: #1a1a1a;
    border-bottom: 1px solid #333;
    z-index: 1000;
}

.nav-container {
    position: relative;
    width: 100%;
    height: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand {
    color: #28a745;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
    margin: 0;
    padding: 0;
}

.nav-links li a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}

.nav-links li a:hover {
    color: #28a745;
}

@media (max-width: 768px) {
    .nav-container {
        flex-direction: column;
        padding: 10px 20px;
    }
    
    .navbar {
        height: auto;
    }
    
    .nav-links {
        gap: 1rem;
    }
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 20px;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}
</style>