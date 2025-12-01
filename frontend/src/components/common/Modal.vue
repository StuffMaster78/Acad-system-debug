<template>
  <Transition name="modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 overflow-y-auto"
    >
      <!-- Background overlay -->
      <Transition name="modal-backdrop">
        <div
          v-if="visible"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          style="z-index: 40;"
        ></div>
      </Transition>

      <div 
        class="relative z-50 flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
        @click="handleBackdropClick"
      >
        <!-- Center modal -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Modal panel -->
        <Transition name="modal-panel">
          <div
            v-if="visible"
            ref="modalPanelRef"
            @click.stop
            class="relative flex flex-col align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle max-h-[90vh]"
            :class="[
              size === 'sm' ? 'sm:max-w-sm' : '',
              size === 'md' ? 'sm:max-w-md' : '',
              size === 'lg' ? 'sm:max-w-lg' : '',
              size === 'xl' ? 'sm:max-w-xl' : '',
              size === '2xl' ? 'sm:max-w-2xl' : '',
              size === 'full' ? 'sm:max-w-full' : 'sm:max-w-lg',
              'w-full'
            ]"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="title ? 'modal-title' : undefined"
          >
            <!-- Header -->
            <div v-if="title || $slots.header || icon" class="bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 px-4 pt-5 pb-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div v-if="icon" class="text-2xl">{{ icon }}</div>
                  <div>
                    <h3 v-if="title" id="modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">{{ title }}</h3>
                    <p v-if="subtitle" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ subtitle }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <slot name="header"></slot>
                  <button
                    v-if="showClose"
                    @click="close"
                    type="button"
                    class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg p-2 transition-all hover:bg-gray-100 dark:hover:bg-gray-600"
                    aria-label="Close modal"
                  >
                    <span class="sr-only">Close</span>
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Body -->
            <div 
              ref="bodyRef"
              class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 flex-1"
              :class="[
                scrollable ? 'overflow-y-auto modal-body-scrollable' : 'overflow-y-visible',
                showTopShadow ? 'shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)]' : '',
                showBottomShadow ? 'shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]' : ''
              ]"
              :style="scrollable ? { maxHeight: maxHeight } : {}"
            >
              <slot></slot>
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 border-t border-gray-200 dark:border-gray-600">
              <div class="flex flex-col sm:flex-row sm:flex-row-reverse gap-2 sm:gap-3">
                <slot name="footer"></slot>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg, xl, 2xl, full
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl', 'full'].includes(value)
  },
  showClose: {
    type: Boolean,
    default: true
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  closeOnEscape: {
    type: Boolean,
    default: true
  },
  autoFocus: {
    type: Boolean,
    default: true
  },
  scrollable: {
    type: Boolean,
    default: false
  },
  maxHeight: {
    type: String,
    default: '60vh'
  }
})

const emit = defineEmits(['update:visible', 'close'])

const modalPanelRef = ref(null)
const bodyRef = ref(null)
const showTopShadow = ref(false)
const showBottomShadow = ref(false)
const previousActiveElement = ref(null)

const close = () => {
  restoreFocus()
  emit('update:visible', false)
  emit('close')
}

const handleBackdropClick = (event) => {
  // Only close if clicking directly on the backdrop container, not on the modal panel
  // The modal panel has @click.stop which prevents this from firing when clicking inside
  if (props.closeOnBackdrop) {
    close()
  }
}

const handleEscape = (event) => {
  if (props.closeOnEscape && event.key === 'Escape' && props.visible) {
    close()
  }
}

// Scroll shadow management
const updateScrollShadows = () => {
  if (!bodyRef.value || !props.scrollable) {
    showTopShadow.value = false
    showBottomShadow.value = false
    return
  }
  
  const { scrollTop, scrollHeight, clientHeight } = bodyRef.value
  showTopShadow.value = scrollTop > 0
  showBottomShadow.value = scrollTop < scrollHeight - clientHeight - 1
}

// Focus management
const focusFirstInput = async () => {
  if (!props.autoFocus || !props.visible) return
  
  // Save the previously focused element
  previousActiveElement.value = document.activeElement
  
  await nextTick()
  if (modalPanelRef.value) {
    // Find first focusable element (input, textarea, select, button)
    const focusableElements = modalPanelRef.value.querySelectorAll(
      'input:not([disabled]), textarea:not([disabled]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    if (focusableElements.length > 0) {
      // Small delay to ensure modal is fully rendered
      setTimeout(() => {
        focusableElements[0].focus()
      }, 100)
    }
  }
}

// Restore focus to previous element
const restoreFocus = () => {
  if (previousActiveElement.value && previousActiveElement.value.focus) {
    try {
      previousActiveElement.value.focus()
    } catch (e) {
      // Element might not be focusable anymore
      console.warn('Could not restore focus:', e)
    }
  }
}

// Trap focus inside modal
const trapFocus = (event) => {
  if (!props.visible || !modalPanelRef.value) return
  
  const focusableElements = modalPanelRef.value.querySelectorAll(
    'input:not([disabled]), textarea:not([disabled]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )
  
  if (focusableElements.length === 0) return
  
  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]
  
  if (event.key === 'Tab') {
    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        event.preventDefault()
        lastElement.focus()
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        event.preventDefault()
        firstElement.focus()
      }
    }
  }
}

// Prevent body scroll when modal is open (more robust)
const preventBodyScroll = () => {
  // Save current scroll position
  const scrollY = window.scrollY
  document.body.style.position = 'fixed'
  document.body.style.top = `-${scrollY}px`
  document.body.style.width = '100%'
  document.body.style.overflow = 'hidden'
}

const restoreBodyScroll = () => {
  const scrollY = document.body.style.top
  document.body.style.position = ''
  document.body.style.top = ''
  document.body.style.width = ''
  document.body.style.overflow = ''
  if (scrollY) {
    window.scrollTo(0, parseInt(scrollY || '0') * -1)
  }
}

// Watch for scrollable body changes
watch(() => [props.scrollable, props.visible], async ([scrollable, visible]) => {
  if (visible && scrollable && bodyRef.value) {
    await nextTick()
    bodyRef.value.addEventListener('scroll', updateScrollShadows)
    updateScrollShadows()
  } else if (bodyRef.value) {
    bodyRef.value.removeEventListener('scroll', updateScrollShadows)
  }
}, { immediate: true })

// Prevent body scroll when modal is open
watch(() => props.visible, async (newVal) => {
  if (newVal) {
    preventBodyScroll()
    // Add keyboard listeners
    document.addEventListener('keydown', handleEscape)
    document.addEventListener('keydown', trapFocus)
    // Focus first input after a short delay
    await nextTick()
    focusFirstInput()
  } else {
    restoreBodyScroll()
    // Remove keyboard listeners
    document.removeEventListener('keydown', handleEscape)
    document.removeEventListener('keydown', trapFocus)
    // Clean up scroll listener
    if (bodyRef.value) {
      bodyRef.value.removeEventListener('scroll', updateScrollShadows)
    }
  }
})

onUnmounted(() => {
  restoreBodyScroll()
  restoreFocus()
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('keydown', trapFocus)
  if (bodyRef.value) {
    bodyRef.value.removeEventListener('scroll', updateScrollShadows)
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-backdrop-enter-active,
.modal-backdrop-leave-active {
  transition: opacity 0.3s ease;
}

.modal-backdrop-enter-from,
.modal-backdrop-leave-to {
  opacity: 0;
}

.modal-panel-enter-active,
.modal-panel-leave-active {
  transition: all 0.3s ease;
}

.modal-panel-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.modal-panel-leave-to {
  opacity: 0;
  transform: scale(0.98) translateY(10px);
}

/* Smooth scrollbar styling for scrollable modals */
.modal-body-scrollable::-webkit-scrollbar {
  width: 8px;
}

.modal-body-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body-scrollable::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.modal-body-scrollable::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

.dark .modal-body-scrollable::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.dark .modal-body-scrollable::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>

