<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0
  },
  readonly: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'medium'
  }
})

const emit = defineEmits(['update:modelValue'])

const stars = computed(() => {
  return Array.from({ length: 5 }, (_, i) => ({
    filled: i < props.modelValue,
    value: i + 1
  }))
})

const handleClick = (value) => {
  if (!props.readonly) {
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div 
    class="star-rating" 
    :class="[size, { readonly }]"
  >
    <span
      v-for="star in stars"
      :key="star.value"
      class="star"
      :class="{ filled: star.filled }"
      @click="handleClick(star.value)"
    >
      ★
    </span>
  </div>
</template>

<style scoped>
.star-rating {
  display: inline-flex;
  gap: 4px;
}

.star {
  color: #ddd;
  cursor: pointer;
  transition: color 0.2s;
}

.star.filled {
  color: #ffd700;
}

.star-rating.readonly .star {
  cursor: default;
}

.star-rating.small .star {
  font-size: 1rem;
}

.star-rating.medium .star {
  font-size: 1.5rem;
}

.star-rating.large .star {
  font-size: 2rem;
}
</style>
