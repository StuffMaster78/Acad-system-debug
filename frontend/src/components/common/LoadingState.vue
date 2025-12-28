<template>
  <div class="loading-state flex flex-col items-center justify-center py-12 px-4" :class="containerClass">
    <div v-if="type === 'spinner'" class="relative">
      <div 
        class="animate-spin rounded-full border-4 border-gray-200 dark:border-gray-700"
        :class="spinnerSizeClass"
        style="border-top-color: currentColor;"
      >
      </div>
      <div 
        v-if="showPulse"
        class="absolute inset-0 rounded-full animate-ping opacity-75"
        :class="spinnerSizeClass"
        style="background-color: currentColor;"
      ></div>
    </div>
    
    <div v-else-if="type === 'dots'" class="flex space-x-2">
      <div 
        v-for="i in 3" 
        :key="i"
        class="w-3 h-3 rounded-full bg-current animate-bounce"
        :style="{ animationDelay: `${(i - 1) * 0.15}s` }"
      ></div>
    </div>
    
    <div v-else-if="type === 'skeleton'" class="w-full space-y-3">
      <div 
        v-for="i in (lines || 3)" 
        :key="i"
        class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
        :class="i === lines ? 'w-3/4' : 'w-full'"
      ></div>
    </div>
    
    <p v-if="message" class="mt-4 text-sm font-medium text-gray-600 dark:text-gray-400 animate-pulse">
      {{ message }}
    </p>
    <p v-if="subMessage" class="mt-2 text-xs text-gray-500 dark:text-gray-500">
      {{ subMessage }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'spinner', // 'spinner', 'dots', 'skeleton'
    validator: (value) => ['spinner', 'dots', 'skeleton'].includes(value)
  },
  size: {
    type: String,
    default: 'medium', // 'small', 'medium', 'large'
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  message: {
    type: String,
    default: null
  },
  subMessage: {
    type: String,
    default: null
  },
  showPulse: {
    type: Boolean,
    default: false
  },
  lines: {
    type: Number,
    default: 3
  },
  fullScreen: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: ''
  }
})

const spinnerSizeClass = computed(() => {
  const sizes = {
    small: 'w-6 h-6',
    medium: 'w-12 h-12',
    large: 'w-16 h-16'
  }
  return sizes[props.size] || sizes.medium
})

const containerClasses = computed(() => {
  let classes = props.containerClass
  if (props.fullScreen) {
    classes += ' fixed inset-0 bg-white dark:bg-gray-900 z-50'
  }
  return classes
})
</script>

<style scoped>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>

