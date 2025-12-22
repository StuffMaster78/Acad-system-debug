<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="handleCancel">
      <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full shadow-2xl transform transition-all">
        <!-- Header with gradient background -->
        <div class="bg-linear-to-r from-red-500 to-red-600 dark:from-red-600 dark:to-red-700 rounded-t-2xl p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border-2 border-white/30">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">{{ title }}</h3>
                <p class="text-sm text-red-100 mt-0.5">{{ subtitle }}</p>
              </div>
            </div>
            <button 
              @click="handleCancel" 
              class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1.5 transition-all"
              :disabled="loading"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6 space-y-5">
          <!-- Warning Message -->
          <div v-if="warningMessage" class="p-4 bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-400 dark:border-amber-500 rounded-lg">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p class="text-sm text-amber-800 dark:text-amber-200 leading-relaxed">{{ warningMessage }}</p>
            </div>
          </div>

          <!-- Username Input (if required) -->
          <div v-if="requireUsername">
            <label for="username" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Username
              </span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <input
                id="username"
                ref="usernameInput"
                v-model="username"
                type="text"
                placeholder="Enter your username"
                class="w-full pl-10 pr-4 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white transition-all"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': error && !password }"
                :disabled="loading"
                @keyup.enter="handleConfirm"
                autocomplete="username"
              />
            </div>
            <!-- Quick-select stored usernames -->
            <div v-if="savedUsernames && savedUsernames.length" class="mt-2 flex flex-wrap gap-2">
              <button
                v-for="name in savedUsernames"
                :key="name"
                type="button"
                class="px-2.5 py-1 rounded-full text-xs font-medium border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/60 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                @click="selectUsername(name)"
                :disabled="loading"
              >
                Use {{ name }}
              </button>
            </div>
          </div>

          <!-- Password Input -->
          <div>
            <label for="password" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Password
                <span class="text-red-500">*</span>
              </span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                ref="passwordInput"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                class="w-full pl-10 pr-12 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white transition-all"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': error }"
                :disabled="loading"
                @keyup.enter="handleConfirm"
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                :disabled="loading"
                title="Toggle password visibility"
              >
                <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
            <p v-if="error" class="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ error }}
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3 pt-2">
            <button
              @click="handleCancel"
              :disabled="loading"
              class="flex-1 px-5 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:border-gray-400 dark:hover:border-gray-500"
            >
              Cancel
            </button>
            <button
              @click="handleConfirm"
              :disabled="loading || !password || (requireUsername && !username)"
              class="flex-1 px-5 py-3 bg-linear-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none"
            >
              <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ loading ? 'Verifying...' : confirmButtonText }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  subtitle: {
    type: String,
    default: 'This action requires password verification'
  },
  warningMessage: {
    type: String,
    default: null
  },
  confirmButtonText: {
    type: String,
    default: 'Confirm'
  },
  loading: {
    type: Boolean,
    default: false
  },
  requireUsername: {
    type: Boolean,
    default: false
  },
  // Optional list of stored admin identities (e.g. username/email) to quick-select
  savedUsernames: {
    type: Array,
    default: () => []
  },
  // Optional default username to pre-fill when modal opens
  defaultUsername: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const passwordInput = ref(null)
const usernameInput = ref(null)

watch(() => props.show, (newVal) => {
  if (newVal) {
    // Pre-fill username from defaultUsername or first savedUsernames entry (if provided)
    if (props.requireUsername && (props.defaultUsername || (props.savedUsernames && props.savedUsernames.length))) {
      username.value = props.defaultUsername || props.savedUsernames[0] || ''
    } else {
      username.value = ''
    }
    password.value = ''
    error.value = ''
    showPassword.value = false
    nextTick(() => {
      if (props.requireUsername) {
        usernameInput.value?.focus()
      } else {
        passwordInput.value?.focus()
      }
    })
  }
})

const handleConfirm = () => {
  if (!password.value) {
    error.value = 'Password is required'
    passwordInput.value?.focus()
    return
  }
  
  if (props.requireUsername && !username.value) {
    error.value = 'Username is required'
    usernameInput.value?.focus()
    return
  }
  
  error.value = ''
  emit('confirm', {
    password: password.value,
    username: props.requireUsername ? username.value : undefined
  })
}

const handleCancel = () => {
  if (props.loading) return
  username.value = ''
  password.value = ''
  error.value = ''
  emit('cancel')
  emit('update:show', false)
}

const setError = (message) => {
  error.value = message
}

const selectUsername = (name) => {
  username.value = name
  error.value = ''
}

defineExpose({
  setError,
  clearPassword: () => {
    username.value = ''
    password.value = ''
    error.value = ''
  }
})
</script>

<style scoped>
/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}

/* Input focus animations */
input:focus {
  animation: pulse-ring 0.3s ease-out;
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  100% {
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0);
  }
}

/* Button hover effects */
button:not(:disabled):hover {
  transition: all 0.2s ease;
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: color, background-color, border-color, transform, box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>
