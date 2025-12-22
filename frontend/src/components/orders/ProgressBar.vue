<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Order Progress</span>
        <span 
          class="px-2.5 py-0.5 rounded-full text-xs font-bold"
          :class="getProgressBadgeClass(progressPercentage)"
        >
          {{ progressPercentage }}%
        </span>
      </div>
      <div v-if="lastUpdate" class="text-xs text-gray-500 dark:text-gray-400">
        Updated {{ formatRelativeTime(lastUpdate) }}
      </div>
    </div>
    
    <!-- Modern Progress Bar -->
    <div class="relative">
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden shadow-inner">
        <div
          class="h-full rounded-full transition-all duration-700 ease-out relative overflow-hidden"
          :class="getProgressBarClass(progressPercentage)"
          :style="{ width: `${Math.min(progressPercentage, 100)}%` }"
        >
          <!-- Animated shine effect -->
          <div class="absolute inset-0 bg-linear-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
          
          <!-- Progress segments for visual feedback -->
          <div 
            v-if="progressPercentage > 0"
            class="absolute inset-0 flex items-center justify-end pr-2"
          >
            <div class="w-2 h-2 bg-white rounded-full opacity-80"></div>
          </div>
        </div>
      </div>
      
      <!-- Milestone markers -->
      <div class="absolute inset-0 flex justify-between items-center pointer-events-none px-1">
        <div 
          v-for="milestone in [0, 25, 50, 75, 100]"
          :key="milestone"
          class="flex flex-col items-center"
        >
          <div 
            class="w-1 h-1 rounded-full"
            :class="progressPercentage >= milestone ? 'bg-white' : 'bg-gray-400 dark:bg-gray-500'"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- Progress status message -->
    <div class="flex items-center gap-2 text-xs">
      <span :class="getStatusIconClass(progressPercentage)">{{ getStatusIcon(progressPercentage) }}</span>
      <span :class="getStatusTextClass(progressPercentage)">{{ getStatusMessage(progressPercentage) }}</span>
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

const formatRelativeTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

const getProgressBarClass = (percentage) => {
  if (percentage === 0) return 'bg-gray-300 dark:bg-gray-600'
  if (percentage < 25) return 'bg-linear-to-r from-red-500 to-orange-500'
  if (percentage < 50) return 'bg-linear-to-r from-orange-500 to-yellow-500'
  if (percentage < 75) return 'bg-linear-to-r from-yellow-500 to-blue-500'
  if (percentage < 100) return 'bg-linear-to-r from-blue-500 to-indigo-500'
  return 'bg-linear-to-r from-green-500 to-emerald-500'
}

const getProgressBadgeClass = (percentage) => {
  if (percentage === 0) return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
  if (percentage < 25) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  if (percentage < 50) return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
  if (percentage < 75) return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
  if (percentage < 100) return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400'
  return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
}

const getStatusIcon = (percentage) => {
  if (percentage === 0) return '⏸️'
  if (percentage < 25) return '🚀'
  if (percentage < 50) return '📝'
  if (percentage < 75) return '⚡'
  if (percentage < 100) return '🎯'
  return '✅'
}

const getStatusIconClass = (percentage) => {
  if (percentage === 0) return 'text-gray-500'
  if (percentage < 25) return 'text-red-500'
  if (percentage < 50) return 'text-orange-500'
  if (percentage < 75) return 'text-blue-500'
  if (percentage < 100) return 'text-indigo-500'
  return 'text-green-500'
}

const getStatusTextClass = (percentage) => {
  if (percentage === 0) return 'text-gray-600 dark:text-gray-400'
  if (percentage < 25) return 'text-red-600 dark:text-red-400'
  if (percentage < 50) return 'text-orange-600 dark:text-orange-400'
  if (percentage < 75) return 'text-blue-600 dark:text-blue-400'
  if (percentage < 100) return 'text-indigo-600 dark:text-indigo-400'
  return 'text-green-600 dark:text-green-400'
}

const getStatusMessage = (percentage) => {
  if (percentage === 0) return 'Not started'
  if (percentage < 25) return 'Getting started'
  if (percentage < 50) return 'In progress'
  if (percentage < 75) return 'More than halfway'
  if (percentage < 100) return 'Almost done'
  return 'Completed'
}
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
</style>

