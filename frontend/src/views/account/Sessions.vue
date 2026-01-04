<template>
  <div class="sessions-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Active Sessions</h1>
      <p class="text-gray-600 dark:text-gray-400">Manage your active login sessions across different devices.</p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="relative w-12 h-12 mx-auto mb-4">
          <div class="absolute inset-0 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
        </div>
        <p class="text-gray-600 dark:text-gray-400 font-medium">Loading sessions...</p>
      </div>
    </div>

    <div v-else-if="sessions.length === 0" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-12 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
      <p class="text-gray-500 dark:text-gray-400">No active sessions found</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="session in sessions"
        :key="session.id"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-all duration-200"
        :class="{ 'ring-2 ring-primary-500/30': session.is_current }"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <strong class="text-gray-900 dark:text-white font-semibold">{{ session.device_name || 'Unknown Device' }}</strong>
              <span v-if="session.is_current" class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full text-xs font-bold">Current</span>
            </div>
            <div class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <p class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                IP: {{ session.ip_address }}
              </p>
              <p class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Last active: {{ formatDate(session.last_activity) }}
              </p>
            </div>
          </div>
          <button
            v-if="!session.is_current"
            @click="revokeSession(session.id)"
            class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg font-semibold hover:bg-red-200 dark:hover:bg-red-900/50 transition-all duration-200"
          >
            Revoke
          </button>
        </div>
      </div>
      
      <button 
        v-if="sessions.length > 1" 
        @click="revokeAllSessions" 
        class="w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200"
      >
        Logout All Devices
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import { useToast } from '@/composables/useToast'
import { useRouter } from 'vue-router'

const { error: showError } = useToast()
const router = useRouter()

const sessions = ref([])
const loading = ref(true)

const loadSessions = async () => {
  loading.value = true
  try {
    const response = await authApi.getActiveSessions()
    let sessionsData = response.data
    if (sessionsData && !Array.isArray(sessionsData)) {
      sessionsData = sessionsData.results || sessionsData.sessions || sessionsData.data || []
    }
    sessions.value = Array.isArray(sessionsData) ? sessionsData : []
  } catch (err) {
    console.error('Failed to load sessions:', err)
    sessions.value = []
    showError('Failed to load sessions')
  } finally {
    loading.value = false
  }
}

const revokeSession = async (sessionId) => {
  try {
    // Implement session revocation endpoint call
    await loadSessions()
  } catch (err) {
    console.error('Failed to revoke session:', err)
    showError('Failed to revoke session')
  }
}

const revokeAllSessions = async () => {
  if (!confirm('Are you sure you want to logout from all devices?')) {
    return
  }

  try {
    await authApi.logout(true)
    router.push('/login')
  } catch (err) {
    console.error('Failed to logout all devices:', err)
    showError('Failed to logout all devices')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.sessions-page {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

