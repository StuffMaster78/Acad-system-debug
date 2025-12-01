<template>
  <div class="security-activity">
    <div class="max-w-6xl mx-auto p-6">
      <h1 class="text-3xl font-bold mb-6">Security Activity</h1>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-500">Recent Logins</p>
          <p class="text-2xl font-bold">{{ summary.total_logins }}</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-500">Failed Attempts</p>
          <p class="text-2xl font-bold text-orange-600">{{ summary.failed_attempts }}</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-500">Suspicious Activity</p>
          <p class="text-2xl font-bold text-red-600">{{ summary.suspicious_activities }}</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-500">Security Score</p>
          <p class="text-2xl font-bold text-green-600">{{ securityScore }}/100</p>
        </div>
      </div>

      <!-- Activity Timeline -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold">Recent Activity</h2>
          <div class="flex gap-2">
            <select
              v-model="filters.event_type"
              @change="loadActivity"
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="">All Events</option>
              <option value="login">Logins</option>
              <option value="login_failed">Failed Logins</option>
              <option value="password_change">Password Changes</option>
              <option value="2fa_enabled">2FA Changes</option>
            </select>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="filters.suspicious_only"
                @change="loadActivity"
                class="mr-2"
              />
              <span class="text-sm">Suspicious Only</span>
            </label>
          </div>
        </div>

        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>

        <div v-else-if="events.length === 0" class="text-center py-8 text-gray-500">
          No security events found
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="event in events"
            :key="event.id"
            class="flex items-start p-4 border border-gray-200 rounded-lg"
            :class="{
              'bg-red-50 border-red-200': event.is_suspicious,
              'bg-yellow-50 border-yellow-200': event.severity === 'high',
            }"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-medium">{{ formatEventType(event.event_type) }}</span>
                <span
                  v-if="event.is_suspicious"
                  class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded"
                >
                  Suspicious
                </span>
                <span
                  v-if="event.severity === 'high'"
                  class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded"
                >
                  High Severity
                </span>
              </div>
              <p class="text-sm text-gray-500 mt-1">
                {{ formatDate(event.created_at) }}
                <span v-if="event.location"> • {{ event.location }}</span>
                <span v-if="event.device"> • {{ event.device }}</span>
              </p>
              <p v-if="event.ip_address" class="text-xs text-gray-400 mt-1">
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

const summary = ref({
  total_logins: 0,
  failed_attempts: 0,
  password_changes: 0,
  suspicious_activities: 0,
  device_changes: 0
})
const events = ref([])
const loading = ref(false)
const securityScore = ref(0)
const filters = ref({
  event_type: '',
  suspicious_only: false
})

onMounted(async () => {
  await loadSummary()
  await loadActivity()
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
    'account_locked': 'Account Locked',
    'account_unlocked': 'Account Unlocked'
  }
  return labels[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}
</script>

