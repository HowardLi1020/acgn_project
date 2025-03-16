<template>
    <div class="container py-5">
      <button @click="$router.go(-1)" class="btn btn-secondary mb-4">🔙 返回</button>
      <div v-if="item" class="detail-card">
        <img v-if="item.poster" :src="item.poster" class="detail-img" alt="Poster" />
        <div class="detail-info">
          <h2>{{ item.game_title || item.animation_title || item.movie_title }}</h2>
          <p><strong>描述：</strong> {{ item.game_description || item.animation_description || item.movie_description }}</p>
          <p><strong>類別：</strong> {{ item.game_genre || item.animation_genre || item.movie_genre }}</p>
          <p><strong>發行日期：</strong> {{ item.release_date }}</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import { useRoute } from "vue-router";
  import axios from "axios";
  
  const route = useRoute();
  const item = ref(null);
  
  // ✅ 確保 Vue Router 可以獲取 category 和 id
  const fetchDetail = async () => {
    let apiUrl = "";
  
    if (route.params.category === "games") {
      apiUrl = `http://localhost:8000/api/games/${route.params.id}/`;
    } else if (route.params.category === "animations") {
      apiUrl = `http://localhost:8000/api/animations/${route.params.id}/`;
    } else if (route.params.category === "movies") {
      apiUrl = `http://localhost:8000/api/movies/${route.params.id}/`;
    }
  
    try {
      const response = await axios.get(apiUrl);
      item.value = response.data;
    } catch (error) {
      console.error("API 請求失敗:", error);
    }
  };
  
  onMounted(fetchDetail);
  </script>
  