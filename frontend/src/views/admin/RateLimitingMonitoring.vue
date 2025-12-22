<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Rate Limiting Monitoring</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Monitor API rate limit violations and statistics</p>
      </div>
      <button
        @click="clearStats"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        Clear Stats
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Violations</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total_violations || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-red-50 to-red-100 border border-red-200 dark:from-red-900/20 dark:to-red-800/20 dark:border-red-700">
        <p class="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Unique Endpoints</p>
        <p class="text-3xl font-bold text-red-900 dark:text-red-100">{{ stats.unique_endpoints || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Unique Users</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.unique_users || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Unique IPs</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.unique_ips || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="scopeFilter"
          type="text"
          placeholder="Filter by scope..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedLoadStats"
        />
        <input
          v-model="userIdFilter"
          type="number"
          placeholder="Filter by User ID..."
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedLoadStats"
        />
        <input
          v-model="ipFilter"
          type="text"
          placeholder="Filter by IP..."
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedLoadStats"
        />
        <input
          v-model.number="limitFilter"
          type="number"
          min="1"
          max="1000"
          placeholder="Limit"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedLoadStats"
        />
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'overview'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'overview'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          Overview
        </button>
        <button
          @click="activeTab = 'endpoints'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'endpoints'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          Top Endpoints
        </button>
        <button
          @click="activeTab = 'users'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'users'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          Top Users
        </button>
        <button
          @click="activeTab = 'ips'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'ips'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          Top IPs
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading rate limit data...</p>
    </div>

    <!-- Overview Tab -->
    <div v-else-if="activeTab === 'overview'" class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Violation Statistics</h2>
      <div class="space-y-4">
        <div v-if="overviewData.violations && overviewData.violations.length > 0">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Endpoint</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Scope</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">User ID</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">IP</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Timestamp</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                <tr
                  v-for="(violation, index) in overviewData.violations.slice(0, 50)"
                  :key="index"
                  class="hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ violation.endpoint || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ violation.scope || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ violation.user_id || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ violation.ip || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ formatDate(violation.timestamp) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
          No violations found
        </div>
      </div>
    </div>

    <!-- Top Endpoints Tab -->
    <div v-else-if="activeTab === 'endpoints'" class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Top Endpoints by Violations</h2>
      <div class="space-y-3">
        <div
          v-for="(endpoint, index) in topEndpoints"
          :key="index"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold text-gray-500 dark:text-gray-400">#{{ index + 1 }}</span>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ endpoint.endpoint }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold text-red-600 dark:text-red-400">{{ endpoint.violations }}</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">violations</span>
          </div>
        </div>
        <div v-if="topEndpoints.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No endpoint violations found
        </div>
      </div>
    </div>

    <!-- Top Users Tab -->
    <div v-else-if="activeTab === 'users'" class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Top Users by Violations</h2>
      <div class="space-y-3">
        <div
          v-for="(user, index) in topUsers"
          :key="index"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold text-gray-500 dark:text-gray-400">#{{ index + 1 }}</span>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">User ID: {{ user.user_id }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold text-red-600 dark:text-red-400">{{ user.violations }}</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">violations</span>
          </div>
        </div>
        <div v-if="topUsers.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No user violations found
        </div>
      </div>
    </div>

    <!-- Top IPs Tab -->
    <div v-else-if="activeTab === 'ips'" class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Top IPs by Violations</h2>
      <div class="space-y-3">
        <div
          v-for="(ip, index) in topIPs"
          :key="index"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold text-gray-500 dark:text-gray-400">#{{ index + 1 }}</span>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ ip.ip }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold text-red-600 dark:text-red-400">{{ ip.violations }}</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">violations</span>
          </div>
        </div>
        <div v-if="topIPs.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No IP violations found
        </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import adminManagementAPI from '@/api/admin-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const activeTab = ref('overview')
const stats = ref({})
const overviewData = ref({})
const topEndpoints = ref([])
const topUsers = ref([])
const topIPs = ref([])
const scopeFilter = ref('')
const userIdFilter = ref('')
const ipFilter = ref('')
const limitFilter = ref(100)

const debouncedLoadStats = debounce(() => {
  loadStats()
}, 300)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadStats = async () => {
  loading.value = true
  try {
    const params = {}
    if (scopeFilter.value) params.scope = scopeFilter.value
    if (userIdFilter.value) params.user_id = userIdFilter.value
    if (ipFilter.value) params.ip = ipFilter.value
    if (limitFilter.value) params.limit = limitFilter.value
    
    const [statsResponse, endpointsResponse, usersResponse, ipsResponse] = await Promise.all([
      adminManagementAPI.getRateLimitStats(params),
      adminManagementAPI.getTopRateLimitedEndpoints(limitFilter.value || 10),
      adminManagementAPI.getTopRateLimitedUsers(limitFilter.value || 10),
      adminManagementAPI.getTopRateLimitedIPs(limitFilter.value || 10),
    ])
    
    overviewData.value = statsResponse.data || {}
    topEndpoints.value = endpointsResponse.data?.endpoints || []
    topUsers.value = usersResponse.data?.users || []
    topIPs.value = ipsResponse.data?.ips || []
    
    stats.value = {
      total_violations: overviewData.value.total_violations || 0,
      unique_endpoints: overviewData.value.unique_endpoints || topEndpoints.value.length,
      unique_users: overviewData.value.unique_users || topUsers.value.length,
      unique_ips: overviewData.value.unique_ips || topIPs.value.length,
    }
  } catch (error) {
    showError('Failed to load rate limit statistics')
    console.error('Error loading stats:', error)
  } finally {
    loading.value = false
  }
}

const clearStats = () => {
  confirm.showDestructive(
    'Clear Rate Limit Statistics',
    'Are you sure you want to clear all rate limit monitoring data?',
    'This action cannot be undone. All violation history will be permanently deleted.',
    async () => {
      try {
        await adminManagementAPI.clearRateLimitStats()
        showSuccess('Rate limit statistics cleared successfully')
        loadStats()
      } catch (error) {
        showError('Failed to clear statistics')
      }
    }
  )
}

watch(activeTab, () => {
  if (activeTab.value === 'endpoints' && topEndpoints.value.length === 0) {
    loadTopEndpoints()
  } else if (activeTab.value === 'users' && topUsers.value.length === 0) {
    loadTopUsers()
  } else if (activeTab.value === 'ips' && topIPs.value.length === 0) {
    loadTopIPs()
  }
})

const loadTopEndpoints = async () => {
  try {
    const response = await adminManagementAPI.getTopRateLimitedEndpoints(limitFilter.value || 10)
    topEndpoints.value = response.data?.endpoints || []
  } catch (error) {
    showError('Failed to load top endpoints')
  }
}

const loadTopUsers = async () => {
  try {
    const response = await adminManagementAPI.getTopRateLimitedUsers(limitFilter.value || 10)
    topUsers.value = response.data?.users || []
  } catch (error) {
    showError('Failed to load top users')
  }
}

const loadTopIPs = async () => {
  try {
    const response = await adminManagementAPI.getTopRateLimitedIPs(limitFilter.value || 10)
    topIPs.value = response.data?.ips || []
  } catch (error) {
    showError('Failed to load top IPs')
  }
}

onMounted(() => {
  loadStats()
})
</script>

