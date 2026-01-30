<template>
  <Transition name="modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 overflow-y-auto"
    >
      <!-- Background overlay with blur -->
      <Transition name="modal-backdrop">
        <div
          v-if="visible"
          class="fixed inset-0 bg-black/50 backdrop-blur-sm transition-all"
          style="z-index: 40;"
          @click="closeOnBackdrop ? close() : null"
        ></div>
      </Transition>

      <div 
        class="relative z-50 flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
        @click="handleBackdropClick"
      >
        <!-- Center modal -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Modal panel with enhanced styling -->
        <Transition name="modal-panel">
          <div
            v-if="visible"
            ref="modalPanelRef"
            @click.stop
            class="relative flex flex-col align-bottom glass-strong rounded-xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle max-h-[90vh] border border-gray-200/20 dark:border-slate-700/30"
            :class="[
              size === 'xs' ? 'sm:max-w-xs' : '',
              size === 'sm' ? 'sm:max-w-sm' : '',
              size === 'md' ? 'sm:max-w-md' : '',
              size === 'lg' ? 'sm:max-w-lg' : '',
              size === 'xl' ? 'sm:max-w-xl' : '',
              size === '2xl' ? 'sm:max-w-2xl' : '',
              size === '3xl' ? 'sm:max-w-3xl' : '',
              size === '4xl' ? 'sm:max-w-4xl' : '',
              size === '5xl' ? 'sm:max-w-5xl' : '',
              size === 'full' ? 'sm:max-w-full sm:mx-4' : 'sm:max-w-lg',
              'w-full'
            ]"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="title ? 'modal-title' : undefined"
          >
            <!-- Enhanced Header with gradient -->
            <div 
              v-if="title || $slots.header || icon" 
              class="relative bg-gradient-to-br from-white via-gray-50 to-white dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-6 py-4 border-b border-gray-200/50 dark:border-slate-700/50"
            >
              <!-- Decorative gradient overlay -->
              <div class="absolute inset-0 bg-gradient-to-r from-primary-500/5 via-transparent to-primary-500/5 pointer-events-none"></div>
              
              <div class="relative flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <!-- Enhanced icon with background -->
                  <div 
                    v-if="icon" 
                    class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-2xl"
                  >
                    {{ icon }}
                  </div>
                  <div>
                    <h3 
                      v-if="title" 
                      id="modal-title" 
                      class="text-xl font-bold text-gray-900 dark:text-slate-100 tracking-tight"
                    >
                      {{ title }}
                    </h3>
                    <p v-if="subtitle" class="text-sm text-gray-500 dark:text-slate-400 mt-0.5">
                      {{ subtitle }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <slot name="header"></slot>
                  <button
                    v-if="showClose"
                    @click="close"
                    type="button"
                    class="group p-2 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg transition-all hover:bg-gray-100 dark:hover:bg-slate-700/50 hover:scale-110 active:scale-95"
                    aria-label="Close modal"
                  >
                    <span class="sr-only">Close</span>
                    <svg class="h-5 w-5 transition-transform group-hover:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Body with improved scrolling -->
            <div 
              ref="bodyRef"
              class="bg-white dark:bg-slate-900 px-6 py-5 flex-1 relative"
              :class="[
                scrollable ? 'overflow-y-auto modal-body-scrollable' : 'overflow-y-visible',
                showTopShadow ? 'shadow-[inset_0_8px_8px_-8px_rgba(0,0,0,0.1)]' : '',
                showBottomShadow ? 'shadow-[inset_0_-8px_8px_-8px_rgba(0,0,0,0.1)]' : ''
              ]"
              :style="scrollable ? { maxHeight: maxHeight } : {}"
            >
              <slot></slot>
            </div>

            <!-- Enhanced Footer -->
            <div 
              v-if="$slots.footer" 
              class="bg-gray-50/50 dark:bg-slate-800/50 px-6 py-4 border-t border-gray-200/50 dark:border-slate-700/50 backdrop-blur-sm"
            >
              <slot name="footer"></slot>
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
    default: 'md', // xs, sm, md, lg, xl, 2xl, 3xl, 4xl, 5xl, full
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', 'full'].includes(value)
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
  
  previousActiveElement.value = document.activeElement
  
  await nextTick()
  if (modalPanelRef.value) {
    const focusableElements = modalPanelRef.value.querySelectorAll(
      'input:not([disabled]), textarea:not([disabled]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    if (focusableElements.length > 0) {
      setTimeout(() => {
        focusableElements[0].focus()
      }, 100)
    }
  }
}

const restoreFocus = () => {
  if (previousActiveElement.value && previousActiveElement.value.focus) {
    try {
      previousActiveElement.value.focus()
    } catch (e) {
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
      if (document.activeElement === firstElement) {
        event.preventDefault()
        lastElement.focus()
      }
    } else {
      if (document.activeElement === lastElement) {
        event.preventDefault()
        firstElement.focus()
      }
    }
  }
}

// Prevent body scroll when modal is open
const preventBodyScroll = () => {
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
    document.addEventListener('keydown', handleEscape)
    document.addEventListener('keydown', trapFocus)
    await nextTick()
    focusFirstInput()
  } else {
    restoreBodyScroll()
    document.removeEventListener('keydown', handleEscape)
    document.removeEventListener('keydown', trapFocus)
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
/* Modal animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-backdrop-enter-active,
.modal-backdrop-leave-active {
  transition: opacity 0.25s ease, backdrop-filter 0.25s ease;
}

.modal-backdrop-enter-from,
.modal-backdrop-leave-to {
  opacity: 0;
  backdrop-filter: blur(0);
}

.modal-panel-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-panel-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-panel-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

.modal-panel-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

/* Enhanced scrollbar styling */
.modal-body-scrollable::-webkit-scrollbar {
  width: 10px;
}

.modal-body-scrollable::-webkit-scrollbar-track {
  @apply bg-gray-100/50 dark:bg-slate-800/50;
  border-radius: 10px;
  margin: 4px;
}

.modal-body-scrollable::-webkit-scrollbar-thumb {
  @apply bg-gray-300 hover:bg-gray-400 dark:bg-slate-600 dark:hover:bg-slate-500;
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

/* Fade scrollbar when not hovering */
.modal-body-scrollable::-webkit-scrollbar-thumb {
  transition: background-color 0.2s ease;
}
</style>
