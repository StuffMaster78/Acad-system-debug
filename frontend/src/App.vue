<template>
  <div class="min-h-dvh bg-white dark:bg-[#0a0a0a] transition-colors duration-300 safe-area-top safe-area-bottom">
    <!-- Temporarily disable NaiveProvider to debug blank screen -->
    <!-- <NaiveProvider> -->
      <RouterView />
      <ToastContainer />
    <!-- </NaiveProvider> -->
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import ToastContainer from '@/components/common/ToastContainer.vue'
// Temporarily disabled to debug
// import NaiveProvider from '@/components/naive/NaiveProvider.vue'
</script>
