<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">System Health Monitoring</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Monitor system health, performance, and alerts</p>
      </div>
      <button
        @click="loadHealth"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- Overall Status -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">System Status</h2>
        <span
          :class="[
            'px-4 py-2 rounded-lg font-semibold',
            healthStatus === 'healthy' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
            healthStatus === 'warning' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
            'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
          ]"
        >
          {{ healthStatus.toUpperCase() }}
        </span>
      </div>
      <p v-if="healthData.timestamp" class="text-sm text-gray-500 dark:text-gray-400">
        Last updated: {{ formatDate(healthData.timestamp) }}
      </p>
    </div>

    <!-- Alerts -->
    <div v-if="alerts.length > 0" class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">⚠️ Active Alerts</h2>
      <div class="space-y-3">
        <div
          v-for="(alert, index) in alerts"
          :key="index"
          :class="[
            'p-4 rounded-lg border-l-4',
            alert.severity === 'critical' ? 'bg-red-50 border-red-500 dark:bg-red-900/20 dark:border-red-700' :
            alert.severity === 'warning' ? 'bg-yellow-50 border-yellow-500 dark:bg-yellow-900/20 dark:border-yellow-700' :
            'bg-blue-50 border-blue-500 dark:bg-blue-900/20 dark:border-blue-700'
          ]"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 dark:text-white mb-1">{{ alert.title || 'Alert' }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ alert.message || alert.description }}</p>
              <p v-if="alert.timestamp" class="text-xs text-gray-500 dark:text-gray-500 mt-2">
                {{ formatDate(alert.timestamp) }}
              </p>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-semibold rounded-full',
                alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                alert.severity === 'warning' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
              ]"
            >
              {{ alert.severity?.toUpperCase() || 'INFO' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="recommendations.length > 0" class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">💡 Recommendations</h2>
      <div class="space-y-3">
        <div
          v-for="(rec, index) in recommendations"
          :key="index"
          class="p-4 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-700"
        >
          <h3 class="font-semibold text-gray-900 dark:text-white mb-1">{{ rec.title || 'Recommendation' }}</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ rec.message || rec.description }}</p>
        </div>
      </div>
    </div>

    <!-- Health Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="(metric, key) in healthMetrics"
        :key="key"
        class="card p-4"
      >
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
          {{ formatMetricName(key) }}
        </h3>
        <div class="space-y-2">
          <div v-if="typeof metric === 'object' && metric !== null">
            <div v-for="(value, subKey) in metric" :key="subKey" class="flex justify-between text-sm">
              <span class="text-gray-600 dark:text-gray-400">{{ formatMetricName(subKey) }}:</span>
              <span class="font-semibold text-gray-900 dark:text-white">{{ formatMetricValue(value) }}</span>
            </div>
          </div>
          <div v-else class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatMetricValue(metric) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading system health data...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="card p-6 bg-red-50 border border-red-200 dark:bg-red-900/20 dark:border-red-700">
      <h2 class="text-lg font-semibold text-red-900 dark:text-red-300 mb-2">Error Loading Health Data</h2>
      <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminManagementAPI from '@/api/admin-management'

const { error: showError } = useToast()

const loading = ref(false)
const healthData = ref({})
const error = ref(null)

const healthStatus = computed(() => {
  if (healthData.value.status) return healthData.value.status
  if (alerts.value.some(a => a.severity === 'critical')) return 'critical'
  if (alerts.value.some(a => a.severity === 'warning')) return 'warning'
  return 'healthy'
})

const alerts = computed(() => {
  return healthData.value.alerts || []
})

const recommendations = computed(() => {
  return healthData.value.recommendations || []
})

const healthMetrics = computed(() => {
  const metrics = { ...healthData.value }
  // Remove non-metric fields
  delete metrics.status
  delete metrics.alerts
  delete metrics.recommendations
  delete metrics.timestamp
  delete metrics.error
  return metrics
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatMetricName = (name) => {
  return name
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim()
}

const formatMetricValue = (value) => {
  if (value === null || value === undefined) return 'N/A'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (typeof value === 'number') {
    if (value > 1000000) return `${(value / 1000000).toFixed(2)}M`
    if (value > 1000) return `${(value / 1000).toFixed(2)}K`
    return value.toFixed(2)
  }
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const loadHealth = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await adminManagementAPI.getSystemHealth()
    healthData.value = response.data || {}
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Failed to load system health data'
    showError('Failed to load system health')
    console.error('Error loading health:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHealth()
})
</script>

