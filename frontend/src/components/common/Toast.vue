<template>
  <Transition name="toast">
    <div
      v-if="visible"
      class="fixed top-4 right-4 z-50 max-w-sm w-full"
    >
      <div
        class="rounded-lg shadow-lg p-4 flex items-start gap-3 animate-slide-in"
        :class="toastClass"
      >
        <div class="shrink-0 text-xl">{{ icon }}</div>
        <div class="flex-1 min-w-0">
          <div v-if="title" class="font-semibold mb-1 text-sm">{{ title }}</div>
          <div class="text-sm leading-relaxed">{{ message }}</div>
          <div v-if="actionLabel && actionHandler" class="mt-3">
            <button
              @click="handleAction"
              class="text-xs font-medium underline hover:no-underline transition-all"
              :class="actionButtonClass"
            >
              {{ actionLabel }}
            </button>
          </div>
        </div>
        <button
          @click="close"
          class="shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Close notification"
        >
          ✕
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info', // success, error, warning, info
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 5000 // milliseconds, 0 = no auto-close
  },
  actionLabel: {
    type: String,
    default: ''
  },
  actionHandler: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['close'])

const visible = ref(true)

const toastClass = computed(() => {
  const classes = {
    success: 'bg-green-50 border border-green-200 text-green-800',
    error: 'bg-red-50 border border-red-200 text-red-800',
    warning: 'bg-yellow-50 border border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border border-blue-200 text-blue-800',
  }
  return classes[props.type] || classes.info
})

const icon = computed(() => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  }
  return icons[props.type] || icons.info
})

const actionButtonClass = computed(() => {
  const classes = {
    success: 'text-green-700 hover:text-green-800',
    error: 'text-red-700 hover:text-red-800',
    warning: 'text-yellow-700 hover:text-yellow-800',
    info: 'text-blue-700 hover:text-blue-800',
  }
  return classes[props.type] || classes.info
})

const handleAction = () => {
  if (props.actionHandler) {
    props.actionHandler()
  }
  close()
}

const close = () => {
  visible.value = false
  setTimeout(() => {
    emit('close')
  }, 300) // Wait for transition
}

onMounted(() => {
  if (props.duration > 0) {
    setTimeout(() => {
      close()
    }, props.duration)
  }
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slide-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>

