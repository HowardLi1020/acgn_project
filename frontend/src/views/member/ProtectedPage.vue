<script setup>
import { ref } from 'vue';
import apiClient from '../axios';

// 定義響應式數據
const message = ref("");

// 定義方法
const fetchProtectedData = async () => {
  try {
    const response = await apiClient.get("protected/");
    message.value = response.data.message;
  } catch (error) {
    console.error("Error fetching protected data", error);
    alert("Access denied!");
  }
};
</script>

<template>
    <div>
      <h1>Protected Page</h1>
      <button @click="fetchProtectedData">Fetch Protected Data</button>
      <p v-if="message">{{ message }}</p>
    </div>
  </template>

<style scoped>

  </style>