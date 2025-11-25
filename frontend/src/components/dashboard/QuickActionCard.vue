<template>
  <router-link :to="to" class="card hover:shadow-md transition-shadow p-4 text-center">
    <div class="text-3xl mb-2">{{ icon }}</div>
    <div class="font-semibold">{{ title }}</div>
    <div class="text-sm text-gray-500">{{ description }}</div>
  </router-link>
</template>

<script setup>
defineProps({
  to: {
    type: [String, Object],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1rem;
  border: 1px solid #e5e7eb;
  display: block;
  text-decoration: none;
  color: inherit;
}
</style>

