<template>
  <div class="max-w-md mx-auto py-10">
    <h1 class="text-2xl font-bold mb-4">Password Reset</h1>
    <p class="text-sm text-gray-600 mb-6">Enter your email and we'll send you a reset link.</p>
    <form @submit.prevent="submit">
      <label class="block text-sm font-medium mb-1">Email</label>
      <input v-model="email" type="email" required class="w-full border rounded px-3 py-2 mb-4" />
      <div v-if="message" class="text-green-600 text-sm mb-3">{{ message }}</div>
      <div v-if="error" class="text-red-600 text-sm mb-3">{{ error }}</div>
      <button :disabled="loading" class="px-4 py-2 bg-primary-600 text-white rounded disabled:opacity-50">
        {{ loading ? 'Sending...' : 'Send Reset Link' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '@/api/auth'

const email = ref('')
const loading = ref(false)
const error = ref('')
const message = ref('')

const submit = async () => {
  error.value = ''
  message.value = ''
  loading.value = true
  try {
    await authAPI.requestPasswordReset(email.value)
    message.value = 'If that email exists, a reset link was sent.'
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to send reset link.'
  } finally {
    loading.value = false
  }
}
</script>
