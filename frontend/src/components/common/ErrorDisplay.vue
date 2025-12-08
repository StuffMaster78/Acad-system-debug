<template>
  <div v-if="error" class="error-display">
    <div
      class="rounded-lg p-4 border-l-4 flex items-start gap-3"
      :class="errorClasses"
    >
      <div class="flex-shrink-0 text-xl">{{ errorIcon }}</div>
      <div class="flex-1 min-w-0">
        <h4 v-if="title" class="font-semibold mb-1 text-sm">{{ title }}</h4>
        <p class="text-sm" v-html="formattedMessage"></p>
        <div v-if="details" class="mt-2 text-xs opacity-75">
          {{ details }}
        </div>
        <div v-if="showStackTrace && stackTrace" class="mt-3">
          <button
            @click="showFullError = !showFullError"
            class="text-xs underline hover:no-underline"
          >
            {{ showFullError ? 'Hide' : 'Show' }} technical details
          </button>
          <div v-if="showFullError" class="mt-2 p-2 bg-black bg-opacity-10 rounded text-xs font-mono overflow-auto max-h-40">
            {{ stackTrace }}
          </div>
        </div>
      </div>
      <button
        v-if="dismissible"
        @click="$emit('dismiss')"
        class="flex-shrink-0 text-current opacity-50 hover:opacity-100 transition-opacity"
        aria-label="Dismiss error"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  error: {
    type: [String, Error, Object],
    default: null
  },
  title: {
    type: String,
    default: 'Error'
  },
  variant: {
    type: String,
    default: 'error', // 'error', 'warning', 'info'
    validator: (value) => ['error', 'warning', 'info'].includes(value)
  },
  dismissible: {
    type: Boolean,
    default: true
  },
  showStackTrace: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['dismiss'])

const showFullError = ref(false)

const errorClasses = computed(() => {
  const classes = {
    error: 'bg-red-50 dark:bg-red-900/20 border-red-500 text-red-800 dark:text-red-200',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500 text-yellow-800 dark:text-yellow-200',
    info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-800 dark:text-blue-200'
  }
  return classes[props.variant] || classes.error
})

const errorIcon = computed(() => {
  const icons = {
    error: '⚠️',
    warning: '⚠️',
    info: 'ℹ️'
  }
  return icons[props.variant] || icons.error
})

const formattedMessage = computed(() => {
  if (!props.error) return ''
  
  if (typeof props.error === 'string') {
    return props.error
  }
  
  if (props.error instanceof Error) {
    return props.error.message || 'An unexpected error occurred'
  }
  
  if (props.error.response?.data) {
    const data = props.error.response.data
    if (data.detail) return data.detail
    if (data.message) return data.message
    if (data.error) return data.error
    if (typeof data === 'string') return data
  }
  
  if (props.error.message) {
    return props.error.message
  }
  
  return 'An unexpected error occurred'
})

const details = computed(() => {
  if (!props.error || typeof props.error === 'string') return null
  
  if (props.error.response?.data) {
    const data = props.error.response.data
    if (data.errors) {
      return Object.entries(data.errors)
        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
        .join('; ')
    }
  }
  
  return null
})

const stackTrace = computed(() => {
  if (!props.error || typeof props.error === 'string') return null
  
  if (props.error instanceof Error && props.error.stack) {
    return props.error.stack
  }
  
  if (props.error.response) {
    return JSON.stringify(props.error.response.data, null, 2)
  }
  
  return null
})
</script>

<style scoped>
.error-display {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

