<template>
  <Transition name="modal">
    <div
      v-if="show"
      class="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-50"
      @click.self="stayLoggedIn"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg
              class="h-6 w-6 text-yellow-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-lg font-medium text-gray-900 mb-2">
              Your Session is About to Expire!
            </h3>
            <p class="text-sm text-gray-500 mb-4">
              Your session will be logged out in
              <span class="font-semibold text-gray-900">{{ formattedTime }}</span>.
            </p>
            <div class="mb-4">
              <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>Redirecting in</span>
                <span class="font-semibold">{{ countdownText }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-yellow-600 h-2 rounded-full transition-all duration-1000"
                  :style="{ width: `${progressPercent}%` }"
                ></div>
              </div>
            </div>
            <div class="flex space-x-3">
              <button
                @click="stayLoggedIn"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                Stay Logged In
              </button>
              <button
                @click="logoutNow"
                class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Logout Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import sessionManager from '@/services/sessionManager'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  remainingSeconds: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['stay-logged-in', 'logout-now'])

const countdown = ref(props.remainingSeconds)
const countdownInterval = ref(null)

const formattedTime = computed(() => {
  const minutes = Math.floor(countdown.value / 60)
  const seconds = countdown.value % 60
  return `${minutes}m ${seconds}s`
})

const countdownText = computed(() => {
  const minutes = Math.floor(countdown.value / 60)
  const seconds = countdown.value % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
})

const progressPercent = computed(() => {
  // Assuming 5 minutes (300 seconds) warning period
  const maxTime = 300
  return Math.max(0, (countdown.value / maxTime) * 100)
})

watch(() => props.remainingSeconds, (newVal) => {
  countdown.value = newVal
})

watch(() => props.show, (isShowing) => {
  if (isShowing) {
    startCountdown()
  } else {
    stopCountdown()
  }
})

const startCountdown = () => {
  stopCountdown()
  countdownInterval.value = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      stopCountdown()
      emit('logout-now')
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
}

const stayLoggedIn = async () => {
  stopCountdown()
  await sessionManager.stayLoggedIn()
  emit('stay-logged-in')
}

const logoutNow = async () => {
  stopCountdown()
  await sessionManager.logoutNow()
  emit('logout-now')
}

onMounted(() => {
  if (props.show) {
    startCountdown()
  }
})

onUnmounted(() => {
  stopCountdown()
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
</style>

