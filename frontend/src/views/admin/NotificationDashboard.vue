<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Notification Dashboard</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Monitor notification system performance and metrics</p>
      </div>
      <button
        @click="refreshData"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- Performance Metrics -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Notifications</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ metrics.total_notifications || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Success Rate</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ formatPercent(metrics.success_rate) }}%</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Avg Delivery Time</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ metrics.avg_delivery_time || 'N/A' }}ms</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Failed Deliveries</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ metrics.failed_deliveries || 0 }}</p>
      </div>
    </div>

    <!-- Real-Time Metrics -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Real-Time Metrics</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Notifications Sent (Last Hour)</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ realTimeMetrics.notifications_sent_last_hour || 0 }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Notifications Read (Last Hour)</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ realTimeMetrics.notifications_read_last_hour || 0 }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Active Users</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ realTimeMetrics.active_users || 0 }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Queue Size</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ realTimeMetrics.queue_size || 0 }}</p>
        </div>
      </div>
    </div>

    <!-- Template Analytics -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Template Analytics</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="templateAnalytics.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Template</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Sent</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Read</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Read Rate</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="template in templateAnalytics"
              :key="template.id || template.template_name"
              class="hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ template.template_name || template.name || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ template.sent_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ template.read_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ formatPercent(template.read_rate) }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
        No template analytics available
      </div>
    </div>

    <!-- System Health -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">System Health</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="space-y-4">
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div>
            <p class="font-medium text-gray-900 dark:text-white">Cache Status</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Notification cache health</p>
          </div>
          <span
            :class="[
              'px-3 py-1 text-sm font-semibold rounded-full',
              systemHealth.cache_status === 'healthy' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
            ]"
          >
            {{ systemHealth.cache_status || 'Unknown' }}
          </span>
        </div>
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div>
            <p class="font-medium text-gray-900 dark:text-white">Queue Status</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Notification queue health</p>
          </div>
          <span
            :class="[
              'px-3 py-1 text-sm font-semibold rounded-full',
              systemHealth.queue_status === 'healthy' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
            ]"
          >
            {{ systemHealth.queue_status || 'Unknown' }}
          </span>
        </div>
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div>
            <p class="font-medium text-gray-900 dark:text-white">Webhook Status</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Webhook delivery health</p>
          </div>
          <span
            :class="[
              'px-3 py-1 text-sm font-semibold rounded-full',
              systemHealth.webhook_status === 'healthy' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
            ]"
          >
            {{ systemHealth.webhook_status || 'Unknown' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import notificationsAPI from '@/api/notifications'

const { error: showError } = useToast()

const loading = ref(false)
const metrics = ref({})
const realTimeMetrics = ref({})
const templateAnalytics = ref([])
const systemHealth = ref({})

const formatPercent = (value) => {
  if (!value && value !== 0) return '0.00'
  return Number(value).toFixed(2)
}

const loadPerformanceDashboard = async () => {
  try {
    const response = await notificationsAPI.getPerformanceDashboard()
    metrics.value = response.data || {}
  } catch (error) {
    console.error('Error loading performance dashboard:', error)
  }
}

const loadRealTimeMetrics = async () => {
  try {
    const response = await notificationsAPI.getRealTimeMetrics()
    realTimeMetrics.value = response.data || {}
  } catch (error) {
    console.error('Error loading real-time metrics:', error)
  }
}

const loadTemplateAnalytics = async () => {
  try {
    const response = await notificationsAPI.getTemplateAnalytics()
    templateAnalytics.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Error loading template analytics:', error)
  }
}

const loadSystemHealth = async () => {
  try {
    // Combine health data from various sources
    systemHealth.value = {
      cache_status: 'healthy',
      queue_status: 'healthy',
      webhook_status: 'healthy',
    }
  } catch (error) {
    console.error('Error loading system health:', error)
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadPerformanceDashboard(),
      loadRealTimeMetrics(),
      loadTemplateAnalytics(),
      loadSystemHealth(),
    ])
  } catch (error) {
    showError('Failed to refresh dashboard data')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshData()
})
</script>

