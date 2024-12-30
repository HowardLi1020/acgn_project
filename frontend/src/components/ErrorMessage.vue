<template>
  <div class="error-message">
    <i class="fas fa-exclamation-circle"></i>
    <slot></slot>
  </div>
</template>

<style scoped>
.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

i {
  font-size: 1.2rem;
}
</style>
