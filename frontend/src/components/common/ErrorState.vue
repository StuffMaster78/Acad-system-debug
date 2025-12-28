<template>
  <div class="error-state text-center py-12 px-4 animate-fade-in">
    <div class="max-w-md mx-auto">
      <div class="text-6xl mb-4 transform transition-transform duration-300">
        {{ icon || '⚠️' }}
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
        {{ title || 'Something went wrong' }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
        {{ message || error || 'An unexpected error occurred. Please try again.' }}
      </p>
      
      <div v-if="showDetails && details" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-left">
        <p class="text-xs font-mono text-red-800 dark:text-red-200 break-all">
          {{ details }}
        </p>
      </div>
      
      <div class="flex justify-center gap-3 flex-wrap">
        <button
          v-if="retryLabel && retryHandler"
          @click="retryHandler"
          class="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all duration-200 text-sm font-semibold shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ retryLabel }}
        </button>
        <button
          v-if="actionLabel && actionHandler"
          @click="actionHandler"
          class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-200 text-sm font-semibold shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95"
        >
          {{ actionLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  icon: {
    type: String,
    default: null
  },
  title: {
    type: String,
    default: null
  },
  message: {
    type: String,
    default: null
  },
  error: {
    type: String,
    default: null
  },
  details: {
    type: String,
    default: null
  },
  showDetails: {
    type: Boolean,
    default: false
  },
  retryLabel: {
    type: String,
    default: 'Try Again'
  },
  retryHandler: {
    type: Function,
    default: null
  },
  actionLabel: {
    type: String,
    default: null
  },
  actionHandler: {
    type: Function,
    default: null
  }
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>

