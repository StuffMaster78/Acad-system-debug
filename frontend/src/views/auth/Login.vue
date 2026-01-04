<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-3 py-4 sm:px-4 sm:py-6 md:py-8 md:px-6 lg:px-8">
    <!-- Background decorative elements - hidden on mobile for performance -->
    <div class="hidden sm:block absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-60 h-60 sm:w-80 sm:h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 sm:opacity-30 animate-blob"></div>
      <div class="absolute -bottom-40 -left-40 w-60 h-60 sm:w-80 sm:h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 sm:opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-60 h-60 sm:w-80 sm:h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 sm:opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="w-full max-w-[90%] sm:max-w-sm md:max-w-md lg:max-w-lg xl:max-w-md 2xl:max-w-lg relative z-10">
      <!-- Logo/Brand Section -->
      <div class="text-center mb-4 sm:mb-5 md:mb-6">
        <div class="flex items-center justify-center gap-2.5 sm:gap-3 mb-1 sm:mb-1.5">
          <!-- WriteFlow Logo -->
          <div class="inline-flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 bg-gradient-to-br from-primary-600 to-primary-800 rounded-lg shadow-lg transform hover:scale-105 transition-transform flex-shrink-0">
            <svg 
              class="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7" 
              viewBox="0 0 40 40" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id="loginPenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:1" />
                </linearGradient>
                <linearGradient id="loginInkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.9" />
                  <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.7" />
                </linearGradient>
              </defs>
              
              <!-- Ink trail forming "W" shape -->
              <path d="M8 28 Q12 20, 16 24 T24 20 T32 24" stroke="url(#loginInkGradient)" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>
              <path d="M8 28 Q10 24, 12 26" stroke="url(#loginInkGradient)" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.6"/>
              
              <!-- Pen/Quill body -->
              <path d="M28 8 L32 12 L30 16 L26 12 Z" fill="url(#loginPenGradient)" stroke="url(#loginPenGradient)" stroke-width="1"/>
              <path d="M28 8 L24 10 L26 12 L30 12 Z" fill="url(#loginPenGradient)" opacity="0.9"/>
              
              <!-- Pen tip -->
              <circle cx="24" cy="10" r="1.5" fill="#ffffff"/>
              
              <!-- Ink drops -->
              <circle cx="10" cy="26" r="1.5" fill="url(#loginInkGradient)" opacity="0.7"/>
              <circle cx="14" cy="22" r="1" fill="url(#loginInkGradient)" opacity="0.6"/>
            </svg>
          </div>
          <h1 class="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
            {{ appName }}
          </h1>
        </div>
        <p class="text-xs sm:text-sm text-gray-600">Welcome back! Please sign in to continue</p>
      </div>

      <!-- Main Card -->
      <div class="bg-white/80 backdrop-blur-lg rounded-xl shadow-xl border border-white/20 p-4 sm:p-5 md:p-6 lg:p-6 xl:p-7 transition-all hover:shadow-2xl">
        <!-- Success message for registration -->
        <div v-if="$route.query.registered === 'true'" class="mb-4 sm:mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-green-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg sm:rounded-xl flex items-center gap-2 animate-fade-in">
          <svg class="w-4 h-4 sm:w-5 sm:h-5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span class="text-xs sm:text-sm font-medium">Account created successfully! Please sign in.</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-3.5 sm:space-y-4">
          <!-- Error Message -->
          <div v-if="error" class="bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg sm:rounded-xl flex items-start gap-2 animate-shake">
            <svg class="w-4 h-4 sm:w-5 sm:h-5 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <span class="text-xs sm:text-sm font-medium">{{ error }}</span>
          </div>

          <!-- Email Field -->
          <div class="space-y-1.5">
            <label for="email" class="block text-xs sm:text-sm font-semibold text-gray-700">
              Email Address
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none">
                <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                id="email"
                v-model="email"
                type="email"
                required
                class="block w-full pl-8 pr-3 py-2.5 sm:py-2.5 md:py-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white/50 backdrop-blur-sm placeholder-gray-400 min-h-[44px]"
                placeholder="you@example.com"
                autocomplete="email"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div class="space-y-1.5">
            <label for="password" class="block text-xs sm:text-sm font-semibold text-gray-700">
              Password
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none">
                <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="block w-full pl-8 pr-8 py-2.5 sm:py-2.5 md:py-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white/50 backdrop-blur-sm placeholder-gray-400 min-h-[44px]"
                placeholder="••••••••"
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-2.5 sm:pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors min-w-[44px] min-h-[44px] touch-manipulation"
                aria-label="Toggle password visibility"
              >
                <svg v-if="showPassword" class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
            <!-- Stripe-style Remember Me Toggle -->
            <label class="remember-me-toggle flex items-center group cursor-pointer min-h-[44px] touch-manipulation select-none">
              <input
                v-model="rememberMe"
                type="checkbox"
                class="sr-only peer"
                @change="handleRememberMeChange"
              />
              <!-- Custom checkbox container -->
              <div 
                class="remember-checkbox relative w-5 h-5 rounded border-2 transition-all duration-300 ease-out shadow-sm flex-shrink-0"
                :class="rememberMe 
                  ? 'bg-primary-600 border-primary-600 shadow-primary-600/20' 
                  : 'bg-white border-gray-300 group-hover:border-gray-400 group-hover:bg-gray-50 group-hover:shadow-md'">
                <!-- Checkmark icon with smooth animation -->
                <svg 
                  class="absolute inset-0 w-full h-full text-white transition-all duration-300 ease-out pointer-events-none"
                  :class="rememberMe 
                    ? 'opacity-100 scale-100 rotate-0' 
                    : 'opacity-0 scale-75 rotate-12'"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M5 13l4 4L19 7" />
                </svg>
                <!-- Subtle glow effect when checked -->
                <div 
                  v-if="rememberMe"
                  class="absolute inset-0 rounded bg-primary-600 opacity-20 blur-sm -z-10 animate-pulse-slow pointer-events-none"
                ></div>
              </div>
              <span class="ml-2.5 text-xs sm:text-sm font-medium text-gray-700 group-hover:text-gray-900 transition-colors duration-200">
                Remember me on this device
              </span>
            </label>
            <router-link 
              to="/password-reset" 
              class="text-xs sm:text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors min-h-[44px] flex items-center touch-manipulation"
            >
              Forgot password?
            </router-link>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-semibold py-3 sm:py-2.5 md:py-3 px-4 text-sm sm:text-sm md:text-base rounded-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 min-h-[44px] touch-manipulation"
          >
            <span v-if="!loading">Sign In</span>
            <span v-else class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4 sm:h-5 sm:w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="hidden sm:inline">Signing in...</span>
            </span>
          </button>
        </form>

        <!-- Divider -->
        <div class="my-4 flex items-center">
          <div class="flex-1 border-t border-gray-300"></div>
          <span class="px-3 text-xs text-gray-500 bg-white/50">or</span>
          <div class="flex-1 border-t border-gray-300"></div>
        </div>

        <!-- Magic Link Toggle -->
        <div class="text-center">
          <button
            @click="showMagicLink = !showMagicLink"
            class="text-xs sm:text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors inline-flex items-center gap-1 min-h-[44px] touch-manipulation"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {{ showMagicLink ? 'Use password login' : 'Login with magic link' }}
          </button>
        </div>

        <!-- Magic Link Section -->
        <div v-if="showMagicLink" class="mt-4 pt-4 border-t border-gray-200 animate-fade-in">
          <h3 class="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Passwordless Login
          </h3>
          <form @submit.prevent="handleMagicLinkRequest" class="space-y-3">
            <div>
              <label for="magic-email" class="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                Email Address
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-2 sm:pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 sm:h-5 sm:w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
                <input
                  id="magic-email"
                  v-model="magicEmail"
                  type="email"
                  required
                  class="block w-full pl-8 sm:pl-10 pr-3 py-2.5 sm:py-3 md:py-3 text-sm sm:text-sm md:text-base border border-gray-300 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white/50 backdrop-blur-sm placeholder-gray-400 min-h-[44px]"
                  placeholder="you@example.com"
                  autocomplete="email"
                />
              </div>
            </div>
            <div v-if="magicLinkSent" class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-green-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg sm:rounded-xl">
              <p class="font-semibold flex items-center gap-2 text-xs sm:text-sm">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Check your email!
              </p>
              <p class="text-xs sm:text-sm mt-1">We've sent a magic link to <strong>{{ magicEmail }}</strong>. Click the link in the email to sign in.</p>
            </div>
            <div v-if="error && showMagicLink" class="bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg sm:rounded-xl text-xs sm:text-sm">
              {{ error }}
            </div>
            <div class="flex flex-col sm:flex-row gap-2">
              <button
                type="submit"
                :disabled="loading || magicLinkSent"
                class="flex-1 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-semibold py-3 sm:py-2.5 md:py-3 px-4 text-sm sm:text-sm md:text-base rounded-lg sm:rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none min-h-[44px] touch-manipulation"
              >
                <span v-if="!loading && !magicLinkSent">Send Magic Link</span>
                <span v-else-if="loading">Sending...</span>
                <span v-else>Link Sent!</span>
              </button>
              <button
                type="button"
                @click="showMagicLink = false"
                class="px-3 sm:px-4 py-2.5 sm:py-2.5 md:py-3 bg-gray-100 text-gray-700 font-medium text-sm sm:text-sm md:text-base rounded-lg sm:rounded-xl hover:bg-gray-200 transition-colors min-h-[44px] touch-manipulation"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>

        <!-- Footer Links -->
        <div class="mt-5 pt-4 border-t border-gray-200 text-center space-y-2">
          <p class="text-xs text-gray-600">
            Don't have an account?
            <router-link to="/signup" class="font-semibold text-primary-600 hover:text-primary-700 transition-colors">
              Sign up
            </router-link>
          </p>
          <p class="text-[10px] text-gray-500 leading-relaxed">
            By signing in, you agree to our
            <router-link to="/terms" class="text-primary-600 hover:text-primary-700 underline underline-offset-2">
              Terms &amp; Conditions
            </router-link>
            and
            <router-link to="/account/privacy" class="text-primary-600 hover:text-primary-700 underline underline-offset-2">
              Privacy &amp; Security
            </router-link>
            .
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const showMagicLink = ref(false)
const magicEmail = ref('')
const magicLinkSent = ref(false)

const appName = import.meta.env.VITE_APP_NAME || 'WriteFlow'

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const result = await authStore.login(email.value, password.value, rememberMe.value)
    
    if (result.success) {
      const redirect = route.query.redirect || '/dashboard'
      router.push(redirect)
    } else {
      error.value = result.error || 'Invalid email or password'
    }
  } catch (err) {
    error.value = err.message || 'An error occurred during login'
  } finally {
    loading.value = false
  }
}

const handleMagicLinkRequest = async () => {
  error.value = ''
  loading.value = true
  magicLinkSent.value = false

  try {
    const { authAPI } = await import('@/api/auth')
    await authAPI.requestMagicLink(magicEmail.value)
    magicLinkSent.value = true
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to send magic link. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleRememberMeChange = () => {
  // Smooth animation trigger - the checkbox state change will trigger CSS animations
  // This function can be used for any additional logic if needed
}
</script>

<style scoped>
@keyframes blob {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

.animate-shake {
  animation: shake 0.5s;
}

/* Responsive optimizations for all screen sizes */

/* Extra small devices (phones, 320px and up) */
@media (min-width: 320px) {
  .min-h-screen {
    min-height: 100vh;
    min-height: -webkit-fill-available; /* iOS Safari fix */
  }
}

/* Small devices (landscape phones, 480px and up) */
@media (min-width: 480px) {
  /* Slightly larger on small landscape phones */
}

/* Medium devices (tablets, 640px and up) */
@media (min-width: 640px) {
  .max-w-md {
    max-width: 26rem;
  }
}

/* Large devices (small laptops, 768px and up) */
@media (min-width: 768px) {
  .max-w-md {
    max-width: 28rem;
  }
}

/* Extra large devices (laptops, 1024px and up) */
@media (min-width: 1024px) {
  .max-w-md {
    max-width: 26rem;
  }
}

/* 2XL devices (desktops, 1280px and up) */
@media (min-width: 1280px) {
  .max-w-lg {
    max-width: 28rem;
  }
}

/* 3XL devices (large desktops, 1536px and up) */
@media (min-width: 1536px) {
  .max-w-lg {
    max-width: 30rem;
  }
}

/* 4XL devices (extra large desktops, 1920px and up) */
@media (min-width: 1920px) {
  .max-w-lg {
    max-width: 32rem;
  }
}

/* Touch device optimizations */
@media (hover: none) and (pointer: coarse) {
  /* Ensure all interactive elements are touch-friendly */
  button,
  a,
  input[type="checkbox"],
  input[type="radio"],
  label {
    min-height: 44px;
    min-width: 44px;
  }
  
  /* Larger tap targets on mobile */
  input[type="text"],
  input[type="email"],
  input[type="password"] {
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  /* Ensure crisp rendering on retina displays */
  .bg-white\/80 {
    backdrop-filter: blur(12px);
  }
}

/* Landscape orientation optimizations */
@media (orientation: landscape) and (max-height: 600px) {
  .min-h-screen {
    min-height: auto;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .text-center {
    margin-bottom: 1rem;
  }
}

/* Stripe-style Remember Me Toggle */
.remember-me-toggle {
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.remember-me-toggle input:focus ~ .remember-checkbox,
.remember-me-toggle input:focus-visible ~ .remember-checkbox {
  outline: 2px solid rgba(59, 130, 246, 0.4);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.remember-me-toggle:active .remember-checkbox {
  transform: scale(0.92);
}

/* Smooth checkbox transitions with hardware acceleration */
.remember-checkbox {
  will-change: transform, background-color, border-color, box-shadow;
  transform: translateZ(0);
  backface-visibility: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.remember-checkbox svg {
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}

/* Subtle pulse animation for checked state */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.15;
  }
  50% {
    opacity: 0.25;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Enhanced hover state */
.remember-me-toggle:hover .remember-checkbox {
  transition-duration: 200ms;
}

/* Smooth check animation when toggled */
.remember-me-toggle input:checked ~ .remember-checkbox {
  animation: checkbox-check 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes checkbox-check {
  0% {
    transform: scale(1) translateZ(0);
  }
  30% {
    transform: scale(1.15) translateZ(0);
  }
  60% {
    transform: scale(0.95) translateZ(0);
  }
  100% {
    transform: scale(1) translateZ(0);
  }
}

/* Smooth uncheck animation */
.remember-me-toggle input:not(:checked) ~ .remember-checkbox {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Print styles */
@media print {
  .bg-gradient-to-br,
  .backdrop-blur-lg,
  .shadow-xl,
  button,
  .animate-blob {
    display: none;
  }
  
  .bg-white\/80 {
    background: white;
  }
}
</style>
