<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
    <div class="max-w-md w-full">
      <div class="card">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            {{ appName }}
          </h1>
          <p class="text-gray-600">Create your account</p>
        </div>

        <form @submit.prevent="handleSignup" class="space-y-6">
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {{ error }}
          </div>

          <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {{ success }}
          </div>

          <!-- Username -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              Username <span class="text-red-500">*</span>
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              class="input"
              placeholder="johndoe"
              autocomplete="username"
              :class="{ 'border-red-500': errors.username }"
            />
            <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
            <p class="mt-1 text-xs text-gray-500">Unique identifier for your account</p>
          </div>

          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email Address <span class="text-red-500">*</span>
            </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              class="input"
              placeholder="you@example.com"
              autocomplete="email"
              :class="{ 'border-red-500': errors.email }"
            />
            <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password <span class="text-red-500">*</span>
            </label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              minlength="8"
              class="input"
              placeholder="••••••••"
              autocomplete="new-password"
              :class="{ 'border-red-500': errors.password }"
            />
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
            <p class="mt-1 text-xs text-gray-500">Must be at least 8 characters long</p>
          </div>

          <!-- Confirm Password -->
          <div>
            <label for="password_confirm" class="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password <span class="text-red-500">*</span>
            </label>
            <input
              id="password_confirm"
              v-model="formData.password_confirm"
              type="password"
              required
              class="input"
              placeholder="••••••••"
              autocomplete="new-password"
              :class="{ 'border-red-500': errors.password_confirm }"
            />
            <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-600">{{ errors.password_confirm }}</p>
          </div>

          <!-- Phone Number (Optional) -->
          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
              Phone Number <span class="text-gray-400">(Optional)</span>
            </label>
            <input
              id="phone"
              v-model="formData.phone"
              type="tel"
              class="input"
              placeholder="+1234567890"
            />
          </div>

          <!-- Terms and Conditions -->
          <div class="flex items-start">
            <input
              id="terms"
              v-model="formData.accept_terms"
              type="checkbox"
              required
              class="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label for="terms" class="ml-2 text-sm text-gray-600">
              I agree to the
              <a href="#" class="text-primary-600 hover:text-primary-700">Terms and Conditions</a>
              and
              <a href="#" class="text-primary-600 hover:text-primary-700">Privacy Policy</a>
            </label>
          </div>

          <button
            type="submit"
            :disabled="loading || !formData.accept_terms"
            class="w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!loading">Create Account</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating account...
            </span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
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
    console.log('Attempting registration with:', {
      username: formData.username.trim(),
      email: formData.email.trim().toLowerCase(),
    })
    
    const response = await authAPI.signup({
      username: formData.username.trim(),
      email: formData.email.trim().toLowerCase(),
      password: formData.password,
    })

    console.log('Registration response:', response)
    
    if (response && response.data) {
      const message = response.data.message || 'Account created successfully!'
      success.value = message + ' Redirecting to login...'
      
      console.log('✅ Registration successful, redirecting to login...')
      
      // Redirect to login after 1.5 seconds (shorter delay)
      setTimeout(() => {
        router.push({ name: 'Login', query: { registered: 'true' } })
      }, 1500)
    } else {
      console.error('❌ Unexpected response format:', response)
      error.value = 'Unexpected response from server'
    }
  } catch (err) {
    console.error('Registration error:', err)
    console.error('Error response:', err.response)
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

