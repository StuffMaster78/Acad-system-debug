<template>
  <div class="session-management">
    <div class="card p-6">
      <h2 class="text-2xl font-bold mb-4">Active Sessions</h2>
      <p class="text-sm text-gray-600 mb-6">
        Manage your active sessions across different devices. You can revoke access for any device you don't recognize.
      </p>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="sessions.length === 0" class="text-center py-12">
        <p class="text-gray-500">No active sessions found.</p>
      </div>

      <div v-else class="space-y-4">
        <template v-for="session in sessions" :key="session?.id || Math.random()">
          <div
            v-if="session"
            class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            :class="{ 'border-primary-500 bg-primary-50': session?.is_current }"
          >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <div class="text-2xl">
                  {{ getDeviceIcon(session.device_type) }}
                </div>
                <div>
                  <div class="font-semibold text-gray-900">
                    {{ session.device_name || 'Unknown Device' }}
                    <span v-if="session.is_current" class="ml-2 text-xs px-2 py-1 bg-primary-600 text-white rounded">
                      Current Session
                    </span>
                  </div>
                  <div class="text-sm text-gray-600">
                    {{ session.browser || 'Unknown Browser' }} on {{ session.os || 'Unknown OS' }}
                  </div>
                </div>
              </div>
              
              <div class="text-xs text-gray-500 space-y-1">
                <div>IP Address: {{ session.ip_address || 'N/A' }}</div>
                <div>Location: {{ session.location || 'Unknown' }}</div>
                <div>Last Active: {{ formatDate(session.last_activity) }}</div>
                <div>Created: {{ formatDate(session.created_at) }}</div>
              </div>
            </div>

            <button
              v-if="!session.is_current"
              @click="revokeSession(session.id)"
              :disabled="revoking === session.id"
              class="px-4 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ revoking === session.id ? 'Revoking...' : 'Revoke' }}
            </button>
          </div>
        </div>
        </template>
      </div>

      <!-- Revoke All Button -->
      <div v-if="sessions.length > 1" class="mt-6 pt-6 border-t border-gray-200">
        <button
          @click="revokeAllSessions"
          :disabled="revokingAll"
          class="px-4 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ revokingAll ? 'Revoking All...' : 'Revoke All Other Sessions' }}
        </button>
        <p class="text-xs text-gray-500 mt-2">
          This will log you out from all devices except this one.
        </p>
      </div>

      <!-- Security Notice -->
      <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 class="font-semibold text-yellow-900 mb-2">Security Tips</h4>
        <ul class="text-sm text-yellow-800 space-y-1 list-disc list-inside">
          <li>Review your active sessions regularly</li>
          <li>Revoke access for devices you don't recognize</li>
          <li>Use strong, unique passwords</li>
          <li>Enable two-factor authentication for added security</li>
        </ul>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authAPI } from '@/api/auth'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const sessions = ref([])
const loading = ref(true)
const revoking = ref(null)
const revokingAll = ref(false)

const getDeviceIcon = (deviceType) => {
  const icons = {
    desktop: '🖥️',
    mobile: '📱',
    tablet: '📱',
    unknown: '💻'
  }
  return icons[deviceType?.toLowerCase()] || icons.unknown
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadSessions = async () => {
  loading.value = true
  try {
    // Assuming there's an endpoint for fetching sessions
    // This would need to be implemented in the backend
    const response = await authAPI.getSessions()
    // Filter out any null or invalid sessions
    sessions.value = (response.data || []).filter(session => session && session.id)
  } catch (error) {
    console.error('Failed to load sessions:', error)
    // For now, use empty array if API is not available
    sessions.value = []
  } finally {
    loading.value = false
  }
}

const revokeSession = async (sessionId) => {
  const confirmed = await confirm.showDialog(
    'Are you sure you want to revoke this session?',
    'Revoke Session',
    {
      details: 'This will log out the device from this session. The user will need to log in again.',
      variant: 'warning',
      icon: '🔒',
      confirmText: 'Revoke',
      cancelText: 'Cancel'
    }
  )

  if (!confirmed) return

  revoking.value = sessionId
  try {
    await authAPI.revokeSession(sessionId)
    await loadSessions()
    showSuccess('Session revoked successfully')
  } catch (error) {
    console.error('Failed to revoke session:', error)
    showError('Failed to revoke session. Please try again.')
  } finally {
    revoking.value = null
  }
}

const revokeAllSessions = async () => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to revoke all other sessions?',
    'Revoke All Sessions',
    {
      details: 'You will be logged out from all devices except this one. This action cannot be undone.',
      icon: '🔒'
    }
  )

  if (!confirmed) return

  revokingAll.value = true
  try {
    await authAPI.revokeAllSessions()
    await loadSessions()
    showSuccess('All other sessions revoked successfully')
  } catch (error) {
    console.error('Failed to revoke all sessions:', error)
    showError('Failed to revoke sessions. Please try again.')
  } finally {
    revokingAll.value = false
  }
}

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.session-management {
  width: 100%;
}
</style>

