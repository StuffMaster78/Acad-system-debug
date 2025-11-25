<template>
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">{{ title }}</h1>
      <p v-if="subtitle" class="text-sm text-gray-600 mt-1">{{ subtitle }}</p>
    </div>
    <div class="flex gap-2">
      <slot name="actions"></slot>
      <button 
        v-if="showRefresh"
        @click="$emit('refresh')"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        :title="refreshTitle"
      >
        🔄 Refresh
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  refreshTitle: {
    type: String,
    default: 'Refresh data'
  }
})

defineEmits(['refresh'])
</script>

