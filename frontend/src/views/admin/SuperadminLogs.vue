<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Superadmin Logs</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Audit trail of all superadmin actions</p>
      </div>
      <button
        @click="loadLogs"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Logs</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || logs.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Today</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.today || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">This Week</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.this_week || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Unique Admins</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.unique_admins || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by superadmin username or action..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="actionTypeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadLogs"
        >
          <option value="">All Action Types</option>
          <option value="user_manage">User Management</option>
          <option value="payment">Payment Override</option>
          <option value="report_access">Report Access</option>
          <option value="settings_change">Settings Modification</option>
          <option value="promotion">User Promotion/Demotion</option>
          <option value="suspension">User Suspension</option>
          <option value="probation">User Probation</option>
          <option value="blacklist">User Blacklisting</option>
          <option value="dispute_resolution">Dispute Resolution</option>
          <option value="admin_tracking">Admin Tracking</option>
          <option value="override">System Override</option>
        </select>
        <input
          v-model="dateFrom"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadLogs"
        />
        <input
          v-model="dateTo"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadLogs"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading superadmin logs...</p>
    </div>

    <!-- Logs Table -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Timestamp</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Superadmin</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Action Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Action</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Details</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="log in logs"
              :key="log.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ formatDate(log.formatted_timestamp || log.timestamp) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ log.superadmin || 'Unknown' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    getActionTypeColor(log.action_type)
                  ]"
                >
                  {{ formatActionType(log.action_type) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                {{ log.action || 'N/A' }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400 max-w-md">
                <div class="truncate" :title="log.action_details">
                  {{ log.action_details || 'No details' }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="logs.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No logs found
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination && pagination.next" class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'
import superadminManagementAPI from '@/api/superadmin-management'

const { error: showError } = useToast()

const loading = ref(false)
const loadingMore = ref(false)
const logs = ref([])
const stats = ref({})
const searchQuery = ref('')
const actionTypeFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const pagination = ref(null)

const debouncedSearch = debounce(() => {
  loadLogs()
}, 300)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatActionType = (type) => {
  if (!type) return 'Unknown'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getActionTypeColor = (type) => {
  const colors = {
    'user_manage': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'payment': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'report_access': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'settings_change': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'promotion': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    'suspension': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'probation': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'blacklist': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'dispute_resolution': 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
    'admin_tracking': 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    'override': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
  }
  return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
}

const loadLogs = async (append = false) => {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  
  try {
    const params = {}
    if (actionTypeFilter.value) params.action_type = actionTypeFilter.value
    if (dateFrom.value) params.timestamp__gte = dateFrom.value
    if (dateTo.value) params.timestamp__lte = dateTo.value
    if (searchQuery.value) params.search = searchQuery.value
    if (pagination.value?.next) params.cursor = pagination.value.next
    
    const response = await superadminManagementAPI.listLogs(params)
    const data = response.data
    
    if (append && Array.isArray(data)) {
      logs.value = [...logs.value, ...data]
    } else if (Array.isArray(data)) {
      logs.value = data
    } else if (data.results) {
      logs.value = append ? [...logs.value, ...data.results] : data.results
      pagination.value = {
        next: data.next,
        previous: data.previous,
      }
    } else {
      logs.value = []
    }
    
    // Calculate stats
    const today = new Date().toISOString().split('T')[0]
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    
    stats.value = {
      total: logs.value.length,
      today: logs.value.filter(l => {
        const logDate = l.formatted_timestamp || l.timestamp
        return logDate && logDate.startsWith(today)
      }).length,
      this_week: logs.value.filter(l => {
        const logDate = l.formatted_timestamp || l.timestamp
        return logDate && logDate >= weekAgo
      }).length,
      unique_admins: new Set(logs.value.map(l => l.superadmin)).size,
    }
  } catch (error) {
    showError('Failed to load superadmin logs')
    console.error('Error loading logs:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  loadLogs(true)
}

onMounted(() => {
  loadLogs()
})
</script>

