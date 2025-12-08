<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="handleCancel">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {{ title || 'Input Required' }}
        </h3>
        <p v-if="message" class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ message }}
        </p>
        
        <div class="mb-4">
          <label v-if="label" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ label }}
          </label>
          <textarea
            v-if="multiline"
            v-model="inputValue"
            :placeholder="placeholder"
            :rows="rows"
            class="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
            @keydown.enter.exact.prevent="handleSubmit"
            @keydown.enter.shift.exact="inputValue += '\n'"
          ></textarea>
          <input
            v-else
            v-model="inputValue"
            type="text"
            :placeholder="placeholder"
            class="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
            @keydown.enter.exact.prevent="handleSubmit"
          />
          <p v-if="hint" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ hint }}
          </p>
        </div>
        
        <div class="flex gap-3 justify-end">
          <button
            @click="handleCancel"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
          >
            {{ cancelText || 'Cancel' }}
          </button>
          <button
            @click="handleSubmit"
            :disabled="required && !inputValue.trim()"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ confirmText || 'Submit' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

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
  label: {
    type: String,
    default: null
  },
  placeholder: {
    type: String,
    default: 'Enter value...'
  },
  hint: {
    type: String,
    default: null
  },
  multiline: {
    type: Boolean,
    default: false
  },
  rows: {
    type: Number,
    default: 4
  },
  required: {
    type: Boolean,
    default: true
  },
  defaultValue: {
    type: String,
    default: ''
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

const emit = defineEmits(['submit', 'cancel', 'update:show'])

// Ensure we only work with string values
const safeDefaultValue = computed(() => {
  const val = props.defaultValue
  if (typeof val === 'string') return val
  if (val === null || val === undefined) return ''
  // If it's an object, return empty string instead of [object Object]
  return ''
})

const inputValue = ref(safeDefaultValue.value)

// Watch for show prop changes
watch(() => props.show, (newVal) => {
  if (newVal) {
    // Use safe defaultValue
    inputValue.value = safeDefaultValue.value
    // Focus input when modal opens
    setTimeout(() => {
      const input = document.querySelector('textarea, input[type="text"]')
      if (input) input.focus()
    }, 100)
    
    // Close on Escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        handleCancel()
      }
    }
    document.addEventListener('keydown', handleEscape)
    
    // Cleanup function will be called when watcher stops
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  } else {
    // Clear input when modal closes
    inputValue.value = ''
  }
}, { immediate: false })

watch(() => props.defaultValue, () => {
  if (props.show) {
    // Use safe defaultValue
    inputValue.value = safeDefaultValue.value
  }
})

const handleSubmit = () => {
  if (props.required && !inputValue.value.trim()) {
    return
  }
  emit('submit', inputValue.value.trim())
  emit('update:show', false)
  inputValue.value = ''
}

const handleCancel = () => {
  emit('cancel')
  emit('update:show', false)
  inputValue.value = ''
}
</script>

