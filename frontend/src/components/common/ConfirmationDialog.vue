<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div 
        v-if="showValue" 
        class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9999] p-4" 
        @click.self="handleCancel"
      >
        <Transition name="dialog-scale">
          <div 
            v-if="showValue" 
            class="glass-strong rounded-2xl shadow-2xl max-w-md w-full mx-4 border border-gray-200/20 dark:border-slate-700/30 overflow-hidden" 
            @click.stop
          >
            <!-- Header with gradient and icon -->
            <div class="relative px-6 pt-6 pb-4 bg-gradient-to-br from-white via-gray-50 to-white dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
              <!-- Decorative gradient overlay -->
              <div 
                class="absolute inset-0 bg-gradient-to-r pointer-events-none"
                :class="{
                  'from-primary-500/5 to-blue-500/5': variantValue === 'default',
                  'from-error-500/10 to-rose-500/10': variantValue === 'danger',
                  'from-warning-500/10 to-amber-500/10': variantValue === 'warning',
                  'from-success-500/10 to-emerald-500/10': variantValue === 'success'
                }"
              ></div>
              
              <div class="relative flex items-start gap-4">
                <!-- Enhanced icon with colored background -->
                <div 
                  v-if="iconValue" 
                  class="flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-xl text-3xl transition-transform hover:scale-110"
                  :class="{
                    'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400': variantValue === 'default',
                    'bg-error-100 text-error-600 dark:bg-error-900/30 dark:text-error-400': variantValue === 'danger',
                    'bg-warning-100 text-warning-600 dark:bg-warning-900/30 dark:text-warning-400': variantValue === 'warning',
                    'bg-success-100 text-success-600 dark:bg-success-900/30 dark:text-success-400': variantValue === 'success'
                  }"
                >
                  {{ iconValue }}
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-xl font-bold text-gray-900 dark:text-slate-100 tracking-tight">
                    {{ titleValue || 'Confirm Action' }}
                  </h3>
                  <p class="text-sm text-gray-600 dark:text-slate-400 mt-2 leading-relaxed">
                    {{ messageValue || 'Are you sure you want to proceed?' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Body content -->
            <div class="px-6 py-4 bg-white dark:bg-slate-900">
              <!-- Details box -->
              <div 
                v-if="detailsValue" 
                class="mb-4 p-4 rounded-lg border text-sm leading-relaxed"
                :class="{
                  'bg-gray-50 border-gray-200 text-gray-700 dark:bg-slate-800/50 dark:border-slate-700 dark:text-slate-300': variantValue === 'default',
                  'bg-error-50 border-error-200 text-error-800 dark:bg-error-900/20 dark:border-error-800 dark:text-error-200': variantValue === 'danger',
                  'bg-warning-50 border-warning-200 text-warning-800 dark:bg-warning-900/20 dark:border-warning-800 dark:text-warning-200': variantValue === 'warning',
                  'bg-success-50 border-success-200 text-success-800 dark:bg-success-900/20 dark:border-success-800 dark:text-success-200': variantValue === 'success'
                }"
              >
                {{ detailsValue }}
              </div>

              <!-- Action buttons -->
              <div class="flex gap-3 justify-end">
                <button
                  @click="handleCancel"
                  class="btn btn-secondary min-w-[100px]"
                >
                  {{ cancelTextValue || 'Cancel' }}
                </button>
                <button
                  @click="handleConfirm"
                  :disabled="loading"
                  class="btn min-w-[100px] relative"
                  :class="{
                    'btn-primary': variantValue === 'default',
                    'btn-danger': variantValue === 'danger',
                    'btn-warning': variantValue === 'warning',
                    'btn-success': variantValue === 'success'
                  }"
                >
                  <!-- Loading spinner -->
                  <svg 
                    v-if="loading"
                    class="animate-spin h-4 w-4 absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" 
                    fill="none" 
                    viewBox="0 0 24 24"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span :class="{ 'opacity-0': loading }">
                    {{ confirmTextValue || 'Confirm' }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch, computed, onUnmounted, ref } from 'vue'

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
    validator: (value) => ['default', 'danger', 'warning', 'success'].includes(value)
  },
  confirmText: {
    type: String,
    default: null
  },
  cancelText: {
    type: String,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const showValue = computed(() => props.show)
const titleValue = computed(() => props.title)
const messageValue = computed(() => props.message)
const detailsValue = computed(() => props.details)
const variantValue = computed(() => props.variant || 'default')
const iconValue = computed(() => props.icon || getDefaultIcon())
const confirmTextValue = computed(() => props.confirmText)
const cancelTextValue = computed(() => props.cancelText)

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

// Get default icon based on variant
function getDefaultIcon() {
  switch (variantValue.value) {
    case 'danger':
      return '⚠️'
    case 'warning':
      return '⚡'
    case 'success':
      return '✓'
    default:
      return '❓'
  }
}

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
    emit('update:show', false)
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
    emit('update:show', false)
  }
}

// Close on Escape key and manage body scroll
let escapeHandler = null

watch(() => showValue.value, (newVal) => {
  if (newVal) {
    // Prevent body scroll when dialog is open
    document.body.style.overflow = 'hidden'
    
    // Add escape key handler
    escapeHandler = (e) => {
      if (e.key === 'Escape' && !props.loading) {
        handleCancel()
      }
    }
    document.addEventListener('keydown', escapeHandler)
  } else {
    // Restore body scroll
    document.body.style.overflow = ''
    
    // Remove escape key handler
    if (escapeHandler) {
      document.removeEventListener('keydown', escapeHandler)
      escapeHandler = null
    }
  }
})

onUnmounted(() => {
  // Cleanup on unmount
  document.body.style.overflow = ''
  if (escapeHandler) {
    document.removeEventListener('keydown', escapeHandler)
    escapeHandler = null
  }
})
</script>

<style scoped>
/* Dialog fade animation */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1), backdrop-filter 0.25s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
  backdrop-filter: blur(0);
}

/* Dialog scale animation */
.dialog-scale-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dialog-scale-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dialog-scale-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

.dialog-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
</style>
