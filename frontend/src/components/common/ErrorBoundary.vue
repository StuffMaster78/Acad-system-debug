<template>
  <div v-if="hasError" class="error-boundary">
    <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-6 rounded-lg">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <svg class="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="ml-4 flex-1">
          <h3 class="text-lg font-semibold text-red-800 dark:text-red-200">
            {{ title || 'Something went wrong' }}
          </h3>
          <p class="mt-2 text-sm text-red-700 dark:text-red-300">
            {{ errorMessage }}
          </p>
          <div class="mt-4 flex gap-3">
            <button
              @click="handleRetry"
              class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
            >
              {{ retryText || 'Try Again' }}
            </button>
            <button
              v-if="showReload"
              @click="handleReload"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
            >
              Reload Page
            </button>
          </div>
          <details v-if="showDetails && errorDetails" class="mt-4">
            <summary class="text-sm text-red-600 dark:text-red-400 cursor-pointer hover:underline">
              Technical Details
            </summary>
            <pre class="mt-2 text-xs bg-red-100 dark:bg-red-900/30 p-3 rounded overflow-auto">{{ errorDetails }}</pre>
          </details>
        </div>
      </div>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: null
  },
  errorMessage: {
    type: String,
    default: 'An unexpected error occurred. Please try again.'
  },
  retryText: {
    type: String,
    default: null
  },
  showReload: {
    type: Boolean,
    default: true
  },
  showDetails: {
    type: Boolean,
    default: false
  },
  onRetry: {
    type: Function,
    default: null
  }
})

const hasError = ref(false)
const errorDetails = ref(null)

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorDetails.value = {
    message: err.message,
    stack: err.stack,
    componentStack: info
  }
  console.error('ErrorBoundary caught error:', err, info)
  return false // Prevent error from propagating
})

const handleRetry = () => {
  if (props.onRetry) {
    props.onRetry()
  }
  hasError.value = false
  errorDetails.value = null
}

const handleReload = () => {
  window.location.reload()
}
</script>

