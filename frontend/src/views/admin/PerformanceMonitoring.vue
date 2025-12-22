<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Performance Monitoring</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Monitor system performance, query counts, and response times</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="refreshData"
          :disabled="loading"
          class="btn btn-secondary flex items-center gap-2"
        >
          <span>🔄</span>
          <span>Refresh</span>
        </button>
        <button
          @click="clearMetrics"
          class="btn btn-warning flex items-center gap-2"
        >
          <span>🗑️</span>
          <span>Clear Metrics</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Endpoints</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total_endpoints || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Total Requests</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.total_requests || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Slow Endpoints</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ slowEndpoints.length || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-red-50 to-red-100 border border-red-200 dark:from-red-900/20 dark:to-red-800/20 dark:border-red-700">
        <p class="text-sm font-medium text-red-700 dark:text-red-300 mb-1">High Query Endpoints</p>
        <p class="text-3xl font-bold text-red-900 dark:text-red-100">{{ highQueryEndpoints.length || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading performance data...</p>
    </div>

    <!-- All Endpoints Tab -->
    <div v-else-if="activeTab === 'all'" class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Endpoint</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Requests</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Avg Response (ms)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Max Response (ms)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Avg Queries</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Max Queries</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="Object.keys(endpointStats).length === 0" class="text-center">
              <td colspan="6" class="px-6 py-12 text-gray-500 dark:text-gray-400">
                No performance data available
              </td>
            </tr>
            <tr
              v-for="(stat, endpoint) in endpointStats"
              :key="endpoint"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">{{ endpoint }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ stat.total_requests || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm"
                :class="getResponseTimeClass(stat.avg_response_time)"
              >
                {{ formatNumber(stat.avg_response_time) }}ms
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm"
                :class="getResponseTimeClass(stat.max_response_time)"
              >
                {{ formatNumber(stat.max_response_time) }}ms
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm"
                :class="getQueryCountClass(stat.avg_query_count)"
              >
                {{ formatNumber(stat.avg_query_count) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm"
                :class="getQueryCountClass(stat.max_query_count)"
              >
                {{ formatNumber(stat.max_query_count) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Slow Endpoints Tab -->
    <div v-else-if="activeTab === 'slow'" class="space-y-4">
      <div class="card p-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Threshold (ms)
        </label>
        <input
          v-model.number="slowThreshold"
          type="number"
          min="0"
          step="50"
          class="w-full max-w-xs px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadSlowEndpoints"
        />
      </div>
      <div
        v-for="endpoint in slowEndpoints"
        :key="endpoint.endpoint"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ endpoint.endpoint }}
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500 dark:text-gray-400">Avg Response:</span>
                <span class="ml-2 font-semibold text-red-600 dark:text-red-400">
                  {{ formatNumber(endpoint.avg_response_time) }}ms
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Max Response:</span>
                <span class="ml-2 font-semibold text-red-600 dark:text-red-400">
                  {{ formatNumber(endpoint.max_response_time) }}ms
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Requests:</span>
                <span class="ml-2 font-semibold">{{ endpoint.request_count }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Avg Queries:</span>
                <span class="ml-2 font-semibold">{{ formatNumber(endpoint.avg_query_count) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="slowEndpoints.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No slow endpoints found (threshold: {{ slowThreshold }}ms)
      </div>
    </div>

    <!-- High Query Endpoints Tab -->
    <div v-else-if="activeTab === 'queries'" class="space-y-4">
      <div class="card p-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Threshold (queries)
        </label>
        <input
          v-model.number="queryThreshold"
          type="number"
          min="0"
          step="5"
          class="w-full max-w-xs px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadHighQueryEndpoints"
        />
      </div>
      <div
        v-for="endpoint in highQueryEndpoints"
        :key="endpoint.endpoint"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ endpoint.endpoint }}
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500 dark:text-gray-400">Avg Queries:</span>
                <span class="ml-2 font-semibold text-red-600 dark:text-red-400">
                  {{ formatNumber(endpoint.avg_query_count) }}
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Max Queries:</span>
                <span class="ml-2 font-semibold text-red-600 dark:text-red-400">
                  {{ formatNumber(endpoint.max_query_count) }}
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Requests:</span>
                <span class="ml-2 font-semibold">{{ endpoint.request_count }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Avg Response:</span>
                <span class="ml-2 font-semibold">{{ formatNumber(endpoint.avg_response_time) }}ms</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="highQueryEndpoints.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No high query endpoints found (threshold: {{ queryThreshold }} queries)
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import adminManagementAPI from '@/api/admin-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const activeTab = ref('all')
const endpointStats = ref({})
const slowEndpoints = ref([])
const highQueryEndpoints = ref([])
const slowThreshold = ref(500)
const queryThreshold = ref(10)
let refreshInterval = null

const tabs = [
  { id: 'all', label: 'All Endpoints' },
  { id: 'slow', label: 'Slow Endpoints' },
  { id: 'queries', label: 'High Query Count' },
]

const stats = computed(() => {
  const endpoints = Object.keys(endpointStats.value)
  const totalRequests = Object.values(endpointStats.value).reduce((sum, stat) => sum + (stat.total_requests || 0), 0)
  return {
    total_endpoints: endpoints.length,
    total_requests: totalRequests,
  }
})

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(2)
}

const getResponseTimeClass = (time) => {
  if (!time) return 'text-gray-900 dark:text-white'
  if (time > 1000) return 'text-red-600 dark:text-red-400 font-semibold'
  if (time > 500) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-green-600 dark:text-green-400'
}

const getQueryCountClass = (count) => {
  if (!count) return 'text-gray-900 dark:text-white'
  if (count > 20) return 'text-red-600 dark:text-red-400 font-semibold'
  if (count > 10) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-green-600 dark:text-green-400'
}

const loadStats = async () => {
  try {
    const response = await adminManagementAPI.getPerformanceStats()
    endpointStats.value = response.data.endpoints || {}
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadSlowEndpoints = async () => {
  try {
    const response = await adminManagementAPI.getSlowEndpoints(slowThreshold.value)
    slowEndpoints.value = response.data.slow_endpoints || []
  } catch (error) {
    console.error('Error loading slow endpoints:', error)
  }
}

const loadHighQueryEndpoints = async () => {
  try {
    const response = await adminManagementAPI.getHighQueryEndpoints(queryThreshold.value)
    highQueryEndpoints.value = response.data.high_query_endpoints || []
  } catch (error) {
    console.error('Error loading high query endpoints:', error)
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStats(),
      loadSlowEndpoints(),
      loadHighQueryEndpoints(),
    ])
  } catch (error) {
    showError('Failed to refresh performance data')
  } finally {
    loading.value = false
  }
}

const clearMetrics = () => {
  confirm.showDestructive(
    'Clear Performance Metrics',
    'Are you sure you want to clear all performance metrics?',
    'This action cannot be undone. All collected performance data will be permanently deleted.',
    async () => {
      try {
        await adminManagementAPI.clearPerformanceMetrics()
        showSuccess('Performance metrics cleared successfully')
        await refreshData()
      } catch (error) {
        showError('Failed to clear metrics')
      }
    }
  )
}

onMounted(() => {
  refreshData()
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(refreshData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

