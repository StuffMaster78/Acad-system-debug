<template>
  <div class="min-h-screen bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <RouterView />
    <ToastContainer />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import ToastContainer from '@/components/common/ToastContainer.vue'
</script>
