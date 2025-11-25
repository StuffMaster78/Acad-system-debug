<template>
  <div class="max-w-md mx-auto py-10">
    <h1 class="text-2xl font-bold mb-4">Set New Password</h1>
    <form @submit.prevent="submit">
      <label class="block text-sm font-medium mb-1">Reset Token</label>
      <input v-model="token" type="text" required class="w-full border rounded px-3 py-2 mb-4" />

      <label class="block text-sm font-medium mb-1">New Password</label>
      <input v-model="password" type="password" required class="w-full border rounded px-3 py-2 mb-4" />

      <div v-if="message" class="text-green-600 text-sm mb-3">{{ message }}</div>
      <div v-if="error" class="text-red-600 text-sm mb-3">{{ error }}</div>

      <button :disabled="loading" class="px-4 py-2 bg-primary-600 text-white rounded disabled:opacity-50">
        {{ loading ? 'Saving...' : 'Reset Password' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { authAPI } from '@/api/auth'

const route = useRoute()
const token = ref(route.query.token || '')
const password = ref('')
const loading = ref(false)
const error = ref('')
const message = ref('')

const submit = async () => {
  error.value = ''
  message.value = ''
  loading.value = true
  try {
    await authAPI.confirmPasswordReset(token.value, password.value)
    message.value = 'Password reset successful. You can now log in.'
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to reset password.'
  } finally {
    loading.value = false
  }
}
</script>
