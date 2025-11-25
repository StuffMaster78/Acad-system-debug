<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between text-sm">
      <span class="font-medium text-gray-700">Progress</span>
      <span class="text-gray-600">{{ progressPercentage }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500 ease-out"
        :style="{ width: `${progressPercentage}%` }"
      >
        <div class="h-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
      </div>
    </div>
    <div v-if="lastUpdate" class="text-xs text-gray-500">
      Last update: {{ formatDate(lastUpdate) }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  progressPercentage: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  lastUpdate: {
    type: String,
    default: null
  }
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}
</script>

