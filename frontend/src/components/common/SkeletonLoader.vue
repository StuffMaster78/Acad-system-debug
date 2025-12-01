<template>
  <div class="skeleton-loader" :class="containerClass">
    <!-- Card Skeleton -->
    <div v-if="type === 'card'" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 animate-pulse">
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
      <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
      <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
      <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
    </div>

    <!-- Table Skeleton -->
    <div v-else-if="type === 'table'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden animate-pulse">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
      </div>
      <div class="p-4 space-y-3">
        <div v-for="i in rows" :key="i" class="flex gap-4">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
        </div>
      </div>
    </div>

    <!-- List Skeleton -->
    <div v-else-if="type === 'list'" class="space-y-3 animate-pulse">
      <div v-for="i in rows" :key="i" class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
        <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
      </div>
    </div>

    <!-- Stats Card Skeleton -->
    <div v-else-if="type === 'stats'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      <div v-for="i in 4" :key="i" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
        <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
      </div>
    </div>

    <!-- Custom Skeleton -->
    <div v-else class="animate-pulse">
      <div v-for="i in rows" :key="i" class="mb-4">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded" :style="{ width: widths[i % widths.length] }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'custom',
    validator: (value) => ['card', 'table', 'list', 'stats', 'custom'].includes(value)
  },
  rows: {
    type: Number,
    default: 3
  },
  widths: {
    type: Array,
    default: () => ['100%', '80%', '90%', '75%']
  },
  containerClass: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

