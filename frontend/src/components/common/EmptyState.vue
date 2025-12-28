<template>
  <div class="empty-state text-center py-16 px-4 animate-fade-in">
    <div class="max-w-md mx-auto">
      <div class="text-7xl mb-6 transform transition-transform duration-300 hover:scale-110 inline-block">
        {{ icon || '📭' }}
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">
        {{ title || 'No items found' }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
        {{ description || 'There are no items to display at this time.' }}
      </p>
      <div v-if="actionLabel && actionHandler" class="flex justify-center gap-3 flex-wrap">
        <button
          @click="actionHandler"
          class="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:from-primary-700 hover:to-primary-800 transition-all duration-200 text-sm font-semibold shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95"
        >
          {{ actionLabel }}
        </button>
        <button
          v-if="secondaryActionLabel && secondaryActionHandler"
          @click="secondaryActionHandler"
          class="px-6 py-3 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-all duration-200 text-sm font-semibold shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95"
        >
          {{ secondaryActionLabel }}
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
  description: {
    type: String,
    default: null
  },
  actionLabel: {
    type: String,
    default: null
  },
  actionHandler: {
    type: Function,
    default: null
  },
  secondaryActionLabel: {
    type: String,
    default: null
  },
  secondaryActionHandler: {
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

