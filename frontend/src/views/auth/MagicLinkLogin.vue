<template>
  <div class="magic-link-login min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-2xl font-bold mb-6 text-center">Passwordless Login</h1>

      <!-- Request Magic Link Form -->
      <div v-if="!linkSent">
        <p class="text-gray-600 mb-6 text-center">
          Enter your email address and we'll send you a magic link to log in instantly.
        </p>

        <form @submit.prevent="requestMagicLink" class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              placeholder="your@email.com"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Sending...' : 'Send Magic Link' }}
          </button>
        </form>

        <div class="mt-4 text-center">
          <button
            @click="$emit('switch-to-password')"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            Use password instead
          </button>
        </div>

        <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>
      </div>

      <!-- Magic Link Sent Confirmation -->
      <div v-else class="text-center">
        <div class="mb-4">
          <svg class="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>
        <h2 class="text-xl font-semibold mb-2">Check Your Email</h2>
        <p class="text-gray-600 mb-4">
          We've sent a magic link to <strong>{{ email }}</strong>
        </p>
        <p class="text-sm text-gray-500 mb-6">
          Click the link in the email to log in. The link will expire in {{ expiresIn }} minutes.
        </p>
        <button
          @click="resetForm"
          class="text-sm text-blue-600 hover:text-blue-700"
        >
          Send to a different email
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import magicLinkAPI from '@/api/magic-link'

const emit = defineEmits(['switch-to-password'])

const router = useRouter()
const email = ref('')
const loading = ref(false)
const linkSent = ref(false)
const error = ref('')
const expiresIn = ref(15)

const requestMagicLink = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await magicLinkAPI.requestMagicLink(email.value)
    linkSent.value = true
    expiresIn.value = Math.floor(response.data.expires_in / 60)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to send magic link. Please try again.'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  linkSent.value = false
  email.value = ''
  error.value = ''
}

// Handle magic link verification if token is in URL
const checkMagicLinkToken = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const token = urlParams.get('token')
  
  if (token) {
    verifyMagicLink(token)
  }
}

const verifyMagicLink = async (token) => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await magicLinkAPI.verifyMagicLink(token)
    
    // Store tokens
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    
    // Redirect to dashboard
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Invalid or expired magic link.'
    linkSent.value = false
  } finally {
    loading.value = false
  }
}

// Check for token on mount
import { onMounted } from 'vue'
onMounted(() => {
  checkMagicLinkToken()
})
</script>

