<template>
  <div class="security-activity">
    <div class="max-w-6xl mx-auto page-shell">
      <h1 class="page-title mb-6 dark:text-white">Security Activity</h1>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">Recent Logins</p>
          <p class="text-2xl font-bold dark:text-white">{{ summary.total_logins }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">Failed Attempts</p>
          <p class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ summary.failed_attempts }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">Suspicious Activity</p>
          <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ summary.suspicious_activities }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">Security Score</p>
          <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ securityScore }}/100</p>
        </div>
      </div>

      <!-- Active Sessions Section -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold dark:text-white">Active Sessions & Devices</h2>
          <button
            v-if="sessions.length > 1"
            @click="revokeAllSessions"
            :disabled="revokingAll"
            class="px-4 py-2 text-sm text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ revokingAll ? 'Signing Out...' : 'Sign Out All Devices' }}
          </button>
        </div>

        <div v-if="loadingSessions" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>

        <div v-else-if="sessions.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No active sessions found
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            :class="{
              'border-blue-500 dark:border-blue-600 bg-blue-50 dark:bg-blue-900/20': session.is_current
            }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <div class="text-2xl">
                    {{ getDeviceIcon(session.device_type) }}
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <input
                        v-if="!session.is_current && !editingDevice[session.id]"
                        v-model="session.device_name"
                        @blur="updateDeviceName(session.id, session.device_name)"
                        @keyup.enter="updateDeviceName(session.id, session.device_name)"
                        class="font-semibold text-gray-900 dark:text-white bg-transparent border-none p-0 focus:outline-none focus:ring-0"
                        placeholder="Name this device..."
                      />
                      <span
                        v-else
                        class="font-semibold text-gray-900 dark:text-white"
                      >
                        {{ session.device_name || 'Unnamed Device' }}
                      </span>
                      <span
                        v-if="session.is_current"
                        class="ml-2 text-xs px-2 py-1 bg-blue-600 dark:bg-blue-500 text-white rounded"
                      >
                        Current Session
                      </span>
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">
                      {{ session.browser || 'Unknown Browser' }} on {{ session.os || 'Unknown OS' }}
                    </div>
                  </div>
                </div>
                
                <div class="text-xs text-gray-500 dark:text-gray-500 space-y-1 mt-2">
                  <div>IP Address: {{ session.ip_address || 'N/A' }}</div>
                  <div v-if="session.location">Location: {{ session.location }}</div>
                  <div>Last Active: {{ formatDate(session.last_activity || session.logged_in_at) }}</div>
                  <div>Logged In: {{ formatDate(session.logged_in_at) }}</div>
                </div>
              </div>

              <div class="flex gap-2 ml-4">
                <button
                  v-if="!session.is_current"
                  @click="startEditingDevice(session.id)"
                  :disabled="editingDevice[session.id] || updatingDevice === session.id"
                  class="px-3 py-1 text-xs text-blue-600 dark:text-blue-400 border border-blue-300 dark:border-blue-700 rounded hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors disabled:opacity-50"
                >
                  {{ editingDevice[session.id] ? 'Editing...' : '✏️ Name' }}
                </button>
                <button
                  v-if="!session.is_current"
                  @click="reportSuspicious(session.id)"
                  :disabled="reportingSuspicious === session.id"
                  class="px-3 py-1 text-xs text-orange-600 dark:text-orange-400 border border-orange-300 dark:border-orange-700 rounded hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors disabled:opacity-50"
                >
                  {{ reportingSuspicious === session.id ? 'Reporting...' : '🚨 This Wasn\'t Me' }}
                </button>
                <button
                  v-if="!session.is_current"
                  @click="revokeSession(session.id)"
                  :disabled="revoking === session.id"
                  class="px-3 py-1 text-xs text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50"
                >
                  {{ revoking === session.id ? 'Revoking...' : 'Revoke' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Timeline -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold dark:text-white">Recent Activity</h2>
          <div class="flex gap-2">
            <select
              v-model="filters.event_type"
              @change="loadActivity"
              class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Events</option>
              <option value="login">Logins</option>
              <option value="login_failed">Failed Logins</option>
              <option value="password_change">Password Changes</option>
              <option value="2fa_enabled">2FA Changes</option>
              <option value="suspicious_session_reported">Suspicious Sessions</option>
            </select>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="filters.suspicious_only"
                @change="loadActivity"
                class="mr-2"
              />
              <span class="text-sm dark:text-gray-300">Suspicious Only</span>
            </label>
          </div>
        </div>

        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>

        <div v-else-if="events.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No security events found
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="event in events"
            :key="event.id"
            class="flex items-start p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
            :class="{
              'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800': event.is_suspicious,
              'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800': event.severity === 'high',
            }"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-medium dark:text-white">{{ formatEventType(event.event_type) }}</span>
                <span
                  v-if="event.is_suspicious"
                  class="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-xs rounded"
                >
                  Suspicious
                </span>
                <span
                  v-if="event.severity === 'high'"
                  class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded"
                >
                  High Severity
                </span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ formatDate(event.created_at) }}
                <span v-if="event.location"> • {{ event.location }}</span>
                <span v-if="event.device"> • {{ event.device }}</span>
              </p>
              <p v-if="event.ip_address" class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                IP: {{ event.ip_address }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import securityActivityAPI from '@/api/security-activity'
import { authAPI } from '@/api/auth'

const summary = ref({
  total_logins: 0,
  failed_attempts: 0,
  password_changes: 0,
  suspicious_activities: 0,
  device_changes: 0
})
const events = ref([])
const sessions = ref([])
const loading = ref(false)
const loadingSessions = ref(false)
const securityScore = ref(0)
const revoking = ref(null)
const revokingAll = ref(false)
const updatingDevice = ref(null)
const editingDevice = ref({})
const reportingSuspicious = ref(null)
const filters = ref({
  event_type: '',
  suspicious_only: false
})

onMounted(async () => {
  await Promise.all([
    loadSummary(),
    loadActivity(),
    loadSessions()
  ])
})

const loadSummary = async () => {
  try {
    const response = await securityActivityAPI.getSummary()
    summary.value = response.data.last_30_days
    securityScore.value = response.data.security_score
  } catch (error) {
    console.error('Failed to load security summary:', error)
  }
}

const loadActivity = async () => {
  loading.value = true
  try {
    const params = {
      limit: 50,
      days: 30
    }
    if (filters.value.event_type) {
      params.event_type = filters.value.event_type
    }
    if (filters.value.suspicious_only) {
      params.suspicious_only = true
    }
    
    const response = await securityActivityAPI.getActivityFeed(params)
    events.value = response.data.events
  } catch (error) {
    console.error('Failed to load security activity:', error)
  } finally {
    loading.value = false
  }
}

const loadSessions = async () => {
  loadingSessions.value = true
  try {
    const response = await authAPI.getLoginSessions()
    const data = response.data || {}

    // Backend can return either a plain list or an object wrapper.
    // Normalize to an array of sessions before filtering.
    let rawSessions
    if (Array.isArray(data)) {
      rawSessions = data
    } else if (Array.isArray(data.sessions)) {
      rawSessions = data.sessions
    } else if (Array.isArray(data.results)) {
      rawSessions = data.results
    } else if (Array.isArray(data.current_sessions)) {
      rawSessions = data.current_sessions
    } else {
      rawSessions = []
    }

    // Filter out any null or invalid session objects
    sessions.value = rawSessions.filter(s => s && s.id)
  } catch (error) {
    console.error('Failed to load sessions:', error)
    sessions.value = []
  } finally {
    loadingSessions.value = false
  }
}

const revokeSession = async (sessionId) => {
  if (!confirm('Are you sure you want to revoke this session? The device will be logged out.')) return

  revoking.value = sessionId
  try {
    await authAPI.revokeLoginSession(sessionId)
    await loadSessions()
    await loadActivity() // Refresh activity to show the revocation
  } catch (error) {
    console.error('Failed to revoke session:', error)
    alert('Failed to revoke session. Please try again.')
  } finally {
    revoking.value = null
  }
}

const revokeAllSessions = async () => {
  if (!confirm('Are you sure you want to sign out from all other devices? You will remain logged in on this device.')) return

  revokingAll.value = true
  try {
    await authAPI.revokeAllLoginSessions(true) // Keep current session
    await loadSessions()
    await loadActivity()
  } catch (error) {
    console.error('Failed to revoke all sessions:', error)
    alert('Failed to revoke sessions. Please try again.')
  } finally {
    revokingAll.value = false
  }
}

const startEditingDevice = (sessionId) => {
  editingDevice.value[sessionId] = true
}

const updateDeviceName = async (sessionId, deviceName) => {
  if (!deviceName || deviceName.trim() === '') {
    editingDevice.value[sessionId] = false
    return
  }

  updatingDevice.value = sessionId
  try {
    await authAPI.updateDeviceName(sessionId, deviceName.trim())
    editingDevice.value[sessionId] = false
    await loadSessions()
  } catch (error) {
    console.error('Failed to update device name:', error)
    alert('Failed to update device name. Please try again.')
  } finally {
    updatingDevice.value = null
  }
}

const reportSuspicious = async (sessionId) => {
  if (!confirm('This will report this session as suspicious, log a security event, and immediately revoke the session. Continue?')) return

  reportingSuspicious.value = sessionId
  try {
    await authAPI.reportSuspiciousSession(sessionId, 'This wasn\'t me')
    await loadSessions()
    await loadActivity() // Refresh to show the security event
    alert('Suspicious session reported and revoked. A security event has been logged.')
  } catch (error) {
    console.error('Failed to report suspicious session:', error)
    alert('Failed to report suspicious session. Please try again.')
  } finally {
    reportingSuspicious.value = null
  }
}

const getDeviceIcon = (deviceType) => {
  const icons = {
    desktop: '🖥️',
    mobile: '📱',
    tablet: '📱',
    unknown: '💻'
  }
  return icons[deviceType?.toLowerCase()] || icons.unknown
}

const formatEventType = (type) => {
  const labels = {
    'login': 'Login',
    'login_failed': 'Failed Login',
    'logout': 'Logout',
    'password_change': 'Password Changed',
    'password_reset': 'Password Reset',
    '2fa_enabled': '2FA Enabled',
    '2fa_disabled': '2FA Disabled',
    'magic_link_used': 'Magic Link Used',
    'device_trusted': 'Device Trusted',
    'device_revoked': 'Device Revoked',
    'suspicious_activity': 'Suspicious Activity',
    'suspicious_session_reported': 'Suspicious Session Reported',
    'account_locked': 'Account Locked',
    'account_unlocked': 'Account Unlocked'
  }
  return labels[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.security-activity {
  min-height: 100vh;
  background-color: #f9fafb;
}

.dark .security-activity {
  background-color: #111827;
}
</style>
