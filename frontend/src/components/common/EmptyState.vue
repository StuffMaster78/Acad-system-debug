<template>
  <div class="empty-state text-center py-12 px-4">
    <div class="max-w-md mx-auto">
      <div class="text-6xl mb-4">{{ icon || '📭' }}</div>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {{ title || 'No items found' }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        {{ description || 'There are no items to display at this time.' }}
      </p>
      <div v-if="actionLabel && actionHandler" class="flex justify-center gap-3">
        <button
          @click="actionHandler"
          class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm font-medium"
        >
          {{ actionLabel }}
        </button>
        <button
          v-if="secondaryActionLabel && secondaryActionHandler"
          @click="secondaryActionHandler"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
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

