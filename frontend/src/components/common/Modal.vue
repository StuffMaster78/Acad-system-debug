<template>
  <Transition name="modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="handleBackdropClick"
    >
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <Transition name="modal-backdrop">
          <div
            v-if="visible"
            class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          ></div>
        </Transition>

        <!-- Center modal -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Modal panel -->
        <Transition name="modal-panel">
          <div
            v-if="visible"
            class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle"
            :class="[
              size === 'sm' ? 'sm:max-w-sm' : '',
              size === 'md' ? 'sm:max-w-md' : '',
              size === 'lg' ? 'sm:max-w-lg' : '',
              size === 'xl' ? 'sm:max-w-xl' : '',
              size === '2xl' ? 'sm:max-w-2xl' : '',
              size === 'full' ? 'sm:max-w-full' : 'sm:max-w-lg',
              'w-full'
            ]"
          >
            <!-- Header -->
            <div v-if="title || $slots.header" class="bg-white px-4 pt-5 pb-4 sm:p-6 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 v-if="title" class="text-lg font-medium text-gray-900">{{ title }}</h3>
                <slot name="header"></slot>
                <button
                  v-if="showClose"
                  @click="close"
                  class="text-gray-400 hover:text-gray-500 focus:outline-none"
                >
                  <span class="sr-only">Close</span>
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Body -->
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
              <slot></slot>
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t border-gray-200">
              <slot name="footer"></slot>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
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
  }
})

const emit = defineEmits(['update:visible', 'close'])

const close = () => {
  emit('update:visible', false)
  emit('close')
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    close()
  }
}

// Prevent body scroll when modal is open
watch(() => props.visible, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
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
  transform: scale(0.95) translateY(-20px);
}

.modal-panel-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-20px);
}
</style>

