<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-3 sm:px-4 md:px-6 lg:px-8 py-6 sm:py-8 md:py-12">
    <div class="w-full max-w-md sm:max-w-lg md:max-w-md lg:max-w-lg xl:max-w-xl 2xl:max-w-2xl">
      <div class="bg-white rounded-xl sm:rounded-2xl shadow-xl sm:shadow-2xl border border-gray-100 p-4 sm:p-6 md:p-8 lg:p-10">
        <div class="text-center mb-6 sm:mb-8">
          <div class="inline-flex items-center justify-center w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 bg-gradient-to-br from-primary-600 to-primary-800 rounded-xl sm:rounded-2xl shadow-lg mb-3 sm:mb-4 transform hover:scale-105 transition-transform">
            <svg class="w-6 h-6 sm:w-8 sm:h-8 md:w-10 md:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-1 sm:mb-2">
            {{ appName }}
          </h1>
          <p class="text-sm sm:text-base text-gray-600">Create your account</p>
        </div>

        <form @submit.prevent="handleSignup" class="space-y-4 sm:space-y-5 md:space-y-6">
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-xs sm:text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-xs sm:text-sm">
            {{ success }}
          </div>

          <!-- Username -->
          <div>
            <label for="username" class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
              Username <span class="text-red-500">*</span>
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              class="w-full px-3 sm:px-4 py-2 sm:py-2.5 md:py-3 text-sm sm:text-base border border-gray-300 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="johndoe"
              autocomplete="username"
              :class="{ 'border-red-500': errors.username }"
            />
            <p v-if="errors.username" class="mt-1 text-xs sm:text-sm text-red-600">{{ errors.username }}</p>
            <p class="mt-1 text-[10px] sm:text-xs text-gray-500">Unique identifier for your account</p>
          </div>

          <!-- Email -->
          <div>
            <label for="email" class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
              Email Address <span class="text-red-500">*</span>
            </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              class="w-full px-3 sm:px-4 py-2 sm:py-2.5 md:py-3 text-sm sm:text-base border border-gray-300 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="you@example.com"
              autocomplete="email"
              :class="{ 'border-red-500': errors.email }"
            />
            <p v-if="errors.email" class="mt-1 text-xs sm:text-sm text-red-600">{{ errors.email }}</p>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
              Password <span class="text-red-500">*</span>
            </label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              minlength="8"
              class="w-full px-3 sm:px-4 py-2 sm:py-2.5 md:py-3 text-sm sm:text-base border border-gray-300 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
              autocomplete="new-password"
              :class="{ 'border-red-500': errors.password }"
            />
            <p v-if="errors.password" class="mt-1 text-xs sm:text-sm text-red-600">{{ errors.password }}</p>
            <p class="mt-1 text-[10px] sm:text-xs text-gray-500">Must be at least 8 characters long</p>
          </div>

          <!-- Confirm Password -->
          <div>
            <label for="password_confirm" class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
              Confirm Password <span class="text-red-500">*</span>
            </label>
            <input
              id="password_confirm"
              v-model="formData.password_confirm"
              type="password"
              required
              class="w-full px-3 sm:px-4 py-2 sm:py-2.5 md:py-3 text-sm sm:text-base border border-gray-300 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
              autocomplete="new-password"
              :class="{ 'border-red-500': errors.password_confirm }"
            />
            <p v-if="errors.password_confirm" class="mt-1 text-xs sm:text-sm text-red-600">{{ errors.password_confirm }}</p>
          </div>

          <!-- Phone Number (Optional) -->
          <div>
            <label for="phone" class="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
              Phone Number <span class="text-gray-400 text-xs">(Optional)</span>
            </label>
            <input
              id="phone"
              v-model="formData.phone"
              type="tel"
              class="w-full px-3 sm:px-4 py-2 sm:py-2.5 md:py-3 text-sm sm:text-base border border-gray-300 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="+1234567890"
            />
          </div>

          <!-- Terms and Conditions -->
          <div class="flex items-start gap-2 sm:gap-3">
            <input
              id="terms"
              v-model="formData.accept_terms"
              type="checkbox"
              required
              class="mt-0.5 sm:mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 focus:ring-2 cursor-pointer"
            />
            <label for="terms" class="text-[10px] sm:text-xs md:text-sm text-gray-600 leading-relaxed">
              I agree to the
              <router-link to="/terms" class="text-primary-600 hover:text-primary-700 underline underline-offset-2">Terms and Conditions</router-link>
              and
              <router-link to="/account/privacy" class="text-primary-600 hover:text-primary-700 underline underline-offset-2">Privacy Policy</router-link>
            </label>
          </div>

          <button
            type="submit"
            :disabled="loading || !formData.accept_terms"
            class="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-semibold py-2.5 sm:py-3 md:py-3.5 px-4 text-sm sm:text-base rounded-lg sm:rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            <span v-if="!loading">Create Account</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4 sm:h-5 sm:w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="hidden sm:inline">Creating account...</span>
              <span class="sm:hidden">Creating...</span>
            </span>
          </button>
        </form>

        <div class="mt-4 sm:mt-6 text-center">
          <p class="text-xs sm:text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
              Sign in
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'

const router = useRouter()

const appName = import.meta.env.VITE_APP_NAME || 'Writing System'

const formData = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  phone: '',
  accept_terms: false,
})

const errors = reactive({})
const error = ref('')
const success = ref('')
const loading = ref(false)

const validateForm = () => {
  // Clear previous errors
  Object.keys(errors).forEach(key => delete errors[key])
  error.value = ''

  // Username validation
  if (!formData.username.trim()) {
    errors.username = 'Username is required'
    return false
  }

  if (formData.username.trim().length < 3) {
    errors.username = 'Username must be at least 3 characters'
    return false
  }

  // Username should be alphanumeric and underscores
  const usernameRegex = /^[a-zA-Z0-9_]+$/
  if (!usernameRegex.test(formData.username)) {
    errors.username = 'Username can only contain letters, numbers, and underscores'
    return false
  }

  // Email validation
  if (!formData.email.trim()) {
    errors.email = 'Email is required'
    return false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.email)) {
    errors.email = 'Please enter a valid email address'
    return false
  }

  // Password validation
  if (!formData.password) {
    errors.password = 'Password is required'
    return false
  }

  if (formData.password.length < 8) {
    errors.password = 'Password must be at least 8 characters long'
    return false
  }

  // Confirm password validation
  if (!formData.password_confirm) {
    errors.password_confirm = 'Please confirm your password'
    return false
  }

  if (formData.password !== formData.password_confirm) {
    errors.password_confirm = 'Passwords do not match'
    return false
  }

  return true
}

const handleSignup = async () => {
  if (!validateForm()) {
    return
  }

  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await authAPI.signup({
      username: formData.username.trim(),
      email: formData.email.trim().toLowerCase(),
      password: formData.password,
    })
    
    if (response && response.data) {
      const message = response.data.message || 'Account created successfully!'
      success.value = message + ' Redirecting to login...'
      
      // Redirect to login after 1.5 seconds
      setTimeout(() => {
        router.push({ name: 'Login', query: { registered: 'true' } })
      }, 1500)
    } else {
      error.value = 'Unexpected response from server'
    }
  } catch (err) {
    // Handle validation errors from backend
    if (err.response?.data) {
      const data = err.response.data
      
      if (data.email) {
        errors.email = Array.isArray(data.email) ? data.email[0] : data.email
      }
      if (data.password) {
        errors.password = Array.isArray(data.password) ? data.password[0] : data.password
      }
      if (data.username) {
        errors.username = Array.isArray(data.username) ? data.username[0] : data.username
      }
      if (data.phone) {
        errors.phone = Array.isArray(data.phone) ? data.phone[0] : data.phone
      }
      if (data.message || data.error) {
        error.value = data.message || data.error || 'Registration failed'
      }
    } else {
      // Handle network errors and other non-response errors
      const errorMessage = err.message || 'An error occurred during registration'
      if (errorMessage.includes('Network error') || errorMessage.includes('connect')) {
        error.value = 'Unable to connect to the server. Please ensure the backend is running and check your connection.'
      } else {
        error.value = errorMessage
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Responsive optimizations */
@media (max-width: 640px) {
  /* Mobile optimizations */
  .min-h-screen {
    min-height: 100vh;
    min-height: -webkit-fill-available; /* iOS Safari fix */
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  /* Tablet optimizations */
  .max-w-md {
    max-width: 28rem;
  }
}

@media (min-width: 1280px) {
  /* Small laptop/desktop */
  .max-w-lg {
    max-width: 32rem;
  }
}

@media (min-width: 1440px) {
  /* Standard desktop (Full HD) */
  .max-w-xl {
    max-width: 36rem;
  }
}

@media (min-width: 1920px) {
  /* Large screens */
  .max-w-2xl {
    max-width: 42rem;
  }
}
</style>
