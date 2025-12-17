<template>
  <div v-if="showValue" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="handleCancel">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="p-6">
        <div class="flex items-start">
          <div v-if="iconValue" class="flex-shrink-0 mr-4 text-4xl">{{ iconValue }}</div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ titleValue || 'Confirm Action' }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
              {{ messageValue || 'Are you sure you want to proceed?' }}
            </p>
            <div v-if="detailsValue" class="mb-6 p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm text-gray-700 dark:text-gray-300">
              {{ detailsValue }}
            </div>
            <div class="flex gap-3 justify-end">
              <button
                @click="handleCancel"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
              >
                {{ cancelTextValue || 'Cancel' }}
              </button>
              <button
                @click="handleConfirm"
                :class="[
                  'px-4 py-2 rounded-md transition-colors text-sm font-medium',
                  variantValue === 'danger'
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : variantValue === 'warning'
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                    : 'bg-primary-600 text-white hover:bg-primary-700'
                ]"
              >
                {{ confirmTextValue || 'Confirm' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch, computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: null
  },
  message: {
    type: String,
    default: null
  },
  details: {
    type: String,
    default: null
  },
  icon: {
    type: String,
    default: null
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'danger', 'warning'].includes(value)
  },
  confirmText: {
    type: String,
    default: null
  },
  cancelText: {
    type: String,
    default: null
  }
})

// Props are now unwrapped before being passed, so we can use them directly
const showValue = computed(() => props.show)
const titleValue = computed(() => props.title)
const messageValue = computed(() => props.message)
const detailsValue = computed(() => props.details)
const variantValue = computed(() => props.variant || 'default')
const iconValue = computed(() => props.icon)
const confirmTextValue = computed(() => props.confirmText)
const cancelTextValue = computed(() => props.cancelText)

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

const handleConfirm = () => {
  emit('confirm')
  emit('update:show', false)
}

const handleCancel = () => {
  emit('cancel')
  emit('update:show', false)
}

// Close on Escape key
watch(() => showValue.value, (newVal) => {
  if (newVal) {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        handleCancel()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }
})
</script>

