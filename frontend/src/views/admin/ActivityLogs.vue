<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Activity Logs</h1>
        <p class="mt-2 text-gray-600">View and search system activity logs and admin actions</p>
      </div>
      <button @click="exportLogs" class="btn btn-secondary" :disabled="exporting">
        {{ exporting ? 'Exporting...' : 'Export CSV' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Logs</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_logs || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Today</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.today_logs || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">This Week</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.week_logs || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">This Month</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.month_logs || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Admin Activity Logs Tab -->
    <div v-if="activeTab === 'admin'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Search</label>
            <input
              v-model="adminFilters.search"
              @input="debouncedAdminSearch"
              type="text"
              placeholder="Search actions..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Admin</label>
            <input
              v-model="adminFilters.admin"
              @input="debouncedAdminSearch"
              type="text"
              placeholder="Filter by admin username"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Date Range</label>
            <select v-model="adminFilters.time_range" @change="loadAdminLogs" class="w-full border rounded px-3 py-2">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="last_7d">Last 7 Days</option>
              <option value="this_month">This Month</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetAdminFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Admin Logs Table -->
      <div class="card overflow-hidden">
        <div v-if="adminLogsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Admin</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="log in adminLogs" :key="log.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 font-mono">{{ log.id }}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="shrink-0 h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold text-xs mr-2">
                      {{ getInitials(log.admin_username || log.admin || 'N/A') }}
                    </div>
                    <div class="text-sm text-gray-900">{{ log.admin_username || log.admin || 'N/A' }}</div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md">{{ log.action }}</div>
                  <div v-if="log.details" class="text-xs text-gray-500 mt-1 truncate max-w-md">{{ log.details }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="text-sm text-gray-500">{{ formatDateTime(log.timestamp) }}</div>
                  <div class="text-xs text-gray-400">{{ formatRelativeTime(log.timestamp) }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm font-medium">
                  <button @click="viewAdminLog(log)" class="text-blue-600 hover:text-blue-900 hover:underline">View Details</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!adminLogsLoading && adminLogs.length === 0" class="text-center py-12 text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2 text-sm">No admin activity logs found</p>
        </div>
        
        <!-- Pagination -->
        <div v-if="!adminLogsLoading && adminLogs.length > 0 && (adminPagination.next || adminPagination.previous)" class="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ adminPagination.start }} to {{ adminPagination.end }} of {{ adminPagination.total }} results
          </div>
          <div class="flex gap-2">
            <button 
              @click="loadAdminLogsPage(adminPagination.previous)" 
              :disabled="!adminPagination.previous"
              class="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <button 
              @click="loadAdminLogsPage(adminPagination.next)" 
              :disabled="!adminPagination.next"
              class="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- General Activity Logs Tab -->
    <div v-if="activeTab === 'general'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Search</label>
            <input
              v-model="generalFilters.search"
              @input="debouncedGeneralSearch"
              type="text"
              placeholder="Search description, metadata..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Action Type</label>
            <select v-model="generalFilters.action_type" @change="loadGeneralLogs" class="w-full border rounded px-3 py-2">
              <option value="">All Types</option>
              <option value="ORDER">Order</option>
              <option value="PAYMENT">Payment</option>
              <option value="NOTIFICATION">Notification</option>
              <option value="COMMUNICATION">Communication</option>
              <option value="LOYALTY">Loyalty</option>
              <option value="USER">User</option>
              <option value="SYSTEM">System</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">User</label>
            <input
              v-model="generalFilters.user"
              @input="debouncedGeneralSearch"
              type="text"
              placeholder="Filter by username"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Time Range</label>
            <select v-model="generalFilters.time_range" @change="loadGeneralLogs" class="w-full border rounded px-3 py-2">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="last_24h">Last 24 Hours</option>
              <option value="this_week">This Week</option>
              <option value="last_7d">Last 7 Days</option>
              <option value="this_month">This Month</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetGeneralFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- General Logs Table -->
      <div class="card overflow-hidden">
        <div v-if="generalLogsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="log in generalLogs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ log.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ log.user || 'System' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getActionTypeBadgeClass(log.action_type)" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ log.action_type }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ truncateText(log.description, 60) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ log.website || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDateTime(log.timestamp) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewGeneralLog(log)" class="text-blue-600 hover:text-blue-900">View</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!generalLogsLoading && generalLogs.length === 0" class="text-center py-12 text-gray-500">
          No activity logs found
        </div>
      </div>
    </div>

    <!-- Log Detail Modal -->
    <div v-if="showLogModal && selectedLog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">Activity Log Details</h3>
            <button @click="closeLogModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">ID</label>
              <p class="text-sm text-gray-900">{{ selectedLog.id }}</p>
            </div>
            <div v-if="selectedLog.admin || selectedLog.admin_username">
              <label class="block text-sm font-medium text-gray-700 mb-1">Admin</label>
              <p class="text-sm text-gray-900">{{ selectedLog.admin_username || selectedLog.admin }}</p>
            </div>
            <div v-if="selectedLog.user">
              <label class="block text-sm font-medium text-gray-700 mb-1">User</label>
              <p class="text-sm text-gray-900">{{ selectedLog.user }}</p>
            </div>
            <div v-if="selectedLog.action">
              <label class="block text-sm font-medium text-gray-700 mb-1">Action</label>
              <p class="text-sm text-gray-900 bg-blue-50 p-2 rounded">{{ selectedLog.action }}</p>
            </div>
            <div v-if="selectedLog.details">
              <label class="block text-sm font-medium text-gray-700 mb-1">Details</label>
              <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded border">{{ selectedLog.details }}</p>
            </div>
            <div v-if="selectedLog.action_type">
              <label class="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
              <p class="text-sm text-gray-900">{{ selectedLog.action_type }}</p>
            </div>
            <div v-if="selectedLog.description">
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <p class="text-sm text-gray-900">{{ selectedLog.description }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Timestamp</label>
              <p class="text-sm text-gray-900">{{ formatDateTime(selectedLog.timestamp) }}</p>
            </div>
            <div v-if="selectedLog.metadata">
              <label class="block text-sm font-medium text-gray-700 mb-1">Metadata</label>
              <pre class="text-xs bg-gray-50 p-3 rounded border overflow-auto max-h-60">{{ JSON.stringify(selectedLog.metadata, null, 2) }}</pre>
            </div>
            <div v-if="selectedLog.website">
              <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
              <p class="text-sm text-gray-900">{{ selectedLog.website }}</p>
            </div>
          </div>
          <div class="flex justify-end pt-4">
            <button @click="closeLogModal" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { activityLogsAPI } from '@/api'

const tabs = [
  { id: 'admin', label: 'Admin Activity Logs' },
  { id: 'general', label: 'General Activity Logs' },
]

const componentError = ref(null)
const initialLoading = ref(true)
const activeTab = ref('admin')
const stats = ref({})
const adminLogs = ref([])
const generalLogs = ref([])

const adminLogsLoading = ref(false)
const generalLogsLoading = ref(false)
const exporting = ref(false)

const showLogModal = ref(false)
const selectedLog = ref(null)

const adminPagination = ref({
  count: 0,
  next: null,
  previous: null,
  start: 0,
  end: 0,
  total: 0,
})

const generalPagination = ref({
  count: 0,
  next: null,
  previous: null,
  start: 0,
  end: 0,
  total: 0,
})

const adminFilters = ref({
  search: '',
  admin: '',
  time_range: '',
})

const generalFilters = ref({
  search: '',
  action_type: '',
  user: '',
  time_range: '',
})

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  return formatDate(dateString)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getInitials = (name) => {
  if (!name || name === 'N/A') return '?'
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const truncateText = (text, maxLength) => {
  if (!text) return 'N/A'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const getActionTypeBadgeClass = (actionType) => {
  const classes = {
    ORDER: 'bg-blue-100 text-blue-800',
    PAYMENT: 'bg-green-100 text-green-800',
    NOTIFICATION: 'bg-yellow-100 text-yellow-800',
    COMMUNICATION: 'bg-purple-100 text-purple-800',
    LOYALTY: 'bg-pink-100 text-pink-800',
    USER: 'bg-gray-100 text-gray-800',
    SYSTEM: 'bg-indigo-100 text-indigo-800',
  }
  return classes[actionType] || 'bg-gray-100 text-gray-800'
}

const loadStats = async () => {
  try {
    const now = new Date()
    const today = new Date(now)
    today.setHours(0, 0, 0, 0)
    const weekAgo = new Date(now)
    weekAgo.setDate(weekAgo.getDate() - 7)
    const monthAgo = new Date(now)
    monthAgo.setMonth(monthAgo.getMonth() - 1)
    
    // Load stats with date filters
    const [totalRes, todayRes, weekRes, monthRes] = await Promise.all([
      activityLogsAPI.listAdminLogs({ page_size: 1 }).catch(() => ({ data: { count: 0 } })),
      activityLogsAPI.listAdminLogs({ page_size: 1, timestamp_after: today.toISOString() }).catch(() => ({ data: { count: 0 } })),
      activityLogsAPI.listAdminLogs({ page_size: 1, timestamp_after: weekAgo.toISOString() }).catch(() => ({ data: { count: 0 } })),
      activityLogsAPI.listAdminLogs({ page_size: 1, timestamp_after: monthAgo.toISOString() }).catch(() => ({ data: { count: 0 } })),
    ])
    
    stats.value = {
      total_logs: totalRes.data.count || 0,
      today_logs: todayRes.data.count || 0,
      week_logs: weekRes.data.count || 0,
      month_logs: monthRes.data.count || 0,
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    stats.value = {
      total_logs: 0,
      today_logs: 0,
      week_logs: 0,
      month_logs: 0,
    }
  }
}

const loadAdminLogs = async (url = null) => {
  adminLogsLoading.value = true
  try {
    let response
    if (url) {
      // Load from pagination URL - extract just the path and query
      const urlObj = new URL(url)
      const path = urlObj.pathname + urlObj.search
      const apiClient = (await import('@/api/client')).default
      response = await apiClient.get(path)
    } else {
      const params = {
        page_size: 20, // Show 20 logs per page
      }
      if (adminFilters.value.search) params.search = adminFilters.value.search
      if (adminFilters.value.admin) params.admin = adminFilters.value.admin
      if (adminFilters.value.time_range) {
        // Map time range to date filters
        const now = new Date()
        if (adminFilters.value.time_range === 'today') {
          params.timestamp_after = new Date(now.setHours(0, 0, 0, 0)).toISOString()
        } else if (adminFilters.value.time_range === 'yesterday') {
          const yesterday = new Date(now)
          yesterday.setDate(yesterday.getDate() - 1)
          yesterday.setHours(0, 0, 0, 0)
          const today = new Date(now)
          today.setHours(0, 0, 0, 0)
          params.timestamp_after = yesterday.toISOString()
          params.timestamp_before = today.toISOString()
        } else if (adminFilters.value.time_range === 'last_7d') {
          const weekAgo = new Date(now)
          weekAgo.setDate(weekAgo.getDate() - 7)
          params.timestamp_after = weekAgo.toISOString()
        } else if (adminFilters.value.time_range === 'this_month') {
          const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
          params.timestamp_after = monthStart.toISOString()
        }
      }
      
      response = await activityLogsAPI.listAdminLogs(params)
    }
    
    // Debug: Log the response structure
    console.log('Activity Logs API Response:', {
      hasData: !!response.data,
      dataKeys: response.data ? Object.keys(response.data) : [],
      hasResults: !!response.data?.results,
      resultsLength: response.data?.results?.length,
      hasCount: !!response.data?.count,
      count: response.data?.count,
      fullResponse: response.data,
    })
    
    // Handle both paginated and non-paginated responses
    // If response.data is an array, it's non-paginated
    // If response.data.results exists, it's paginated
    let logs = []
    if (Array.isArray(response.data)) {
      // Non-paginated response - data is directly an array
      logs = response.data
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      // Paginated response - data.results is the array
      logs = response.data.results
    } else if (Array.isArray(response.data)) {
      logs = response.data
    } else {
      // Fallback - try to extract logs from any structure
      logs = response.data || []
    }
    
    adminLogs.value = Array.isArray(logs) ? logs : []
    
    // Update pagination
    if (response.data) {
      const count = response.data.count !== undefined ? response.data.count : adminLogs.value.length
      const pageSize = 20
      
      // Calculate pagination info
      let start = 0
      let end = 0
      if (response.data.count !== undefined) {
        // Paginated response
        const currentPage = response.data.next 
          ? Math.floor((count - adminLogs.value.length) / pageSize) + 1
          : Math.ceil(count / pageSize) || 1
        start = count > 0 ? ((currentPage - 1) * pageSize) + 1 : 0
        end = Math.min(start + adminLogs.value.length - 1, count)
      } else {
        // Non-paginated response
        start = adminLogs.value.length > 0 ? 1 : 0
        end = adminLogs.value.length
      }
      
      adminPagination.value = {
        count: count,
        next: response.data.next || null,
        previous: response.data.previous || null,
        start: start,
        end: end,
        total: count,
      }
    }
    
    // Debug: Log what we're displaying
    console.log('Admin Logs to Display:', {
      count: adminLogs.value.length,
      firstLog: adminLogs.value[0] || null,
      pagination: adminPagination.value,
    })
  } catch (error) {
    console.error('Failed to load admin logs:', error)
    adminLogs.value = []
  } finally {
    adminLogsLoading.value = false
  }
}

const loadAdminLogsPage = async (url) => {
  if (url) {
    await loadAdminLogs(url)
  }
}

const loadGeneralLogs = async () => {
  generalLogsLoading.value = true
  try {
    const params = {}
    if (generalFilters.value.search) params.search = generalFilters.value.search
    if (generalFilters.value.action_type) params.action_type = generalFilters.value.action_type
    if (generalFilters.value.user) params.user = generalFilters.value.user
    if (generalFilters.value.time_range) params.time_range = generalFilters.value.time_range
    
    const response = await activityLogsAPI.list(params)
    generalLogs.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load general logs:', error)
    // If endpoint doesn't exist, show empty state
    generalLogs.value = []
  } finally {
    generalLogsLoading.value = false
  }
}

let adminSearchTimeout = null
const debouncedAdminSearch = () => {
  if (adminSearchTimeout) clearTimeout(adminSearchTimeout)
  adminSearchTimeout = setTimeout(() => {
    loadAdminLogs()
  }, 500)
}

let generalSearchTimeout = null
const debouncedGeneralSearch = () => {
  if (generalSearchTimeout) clearTimeout(generalSearchTimeout)
  generalSearchTimeout = setTimeout(() => {
    loadGeneralLogs()
  }, 500)
}

const resetAdminFilters = () => {
  adminFilters.value = {
    search: '',
    admin: '',
    time_range: '',
  }
  loadAdminLogs()
}

const resetGeneralFilters = () => {
  generalFilters.value = {
    search: '',
    action_type: '',
    user: '',
    time_range: '',
  }
  loadGeneralLogs()
}

const viewAdminLog = async (log) => {
  try {
    const response = await activityLogsAPI.getAdminLog(log.id)
    selectedLog.value = response.data
    showLogModal.value = true
  } catch (error) {
    console.error('Failed to load log details:', error)
    // Fallback to showing the log object directly
    selectedLog.value = log
    showLogModal.value = true
  }
}

const viewGeneralLog = async (log) => {
  try {
    const response = await activityLogsAPI.get(log.id)
    selectedLog.value = response.data
    showLogModal.value = true
  } catch (error) {
    console.error('Failed to load log details:', error)
    // Fallback to showing the log object directly
    selectedLog.value = log
    showLogModal.value = true
  }
}

const closeLogModal = () => {
  showLogModal.value = false
  selectedLog.value = null
}

const exportLogs = async () => {
  exporting.value = true
  try {
    // Get all logs (or current filtered set)
    const logs = activeTab.value === 'admin' ? adminLogs.value : generalLogs.value
    
    // Convert to CSV
    const headers = activeTab.value === 'admin' 
      ? ['ID', 'Admin', 'Action', 'Timestamp']
      : ['ID', 'User', 'Action Type', 'Description', 'Website', 'Timestamp']
    
    const rows = logs.map(log => {
      if (activeTab.value === 'admin') {
        return [
          log.id,
          log.admin_username || log.admin || '',
          log.action || '',
          formatDateTime(log.timestamp),
        ]
      } else {
        return [
          log.id,
          log.user || '',
          log.action_type || '',
          log.description || '',
          log.website || '',
          formatDateTime(log.timestamp),
        ]
      }
    })
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `activity-logs-${activeTab.value}-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export logs:', error)
    alert('Failed to export logs')
  } finally {
    exporting.value = false
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'admin') {
    loadAdminLogs()
  } else if (newTab === 'general') {
    loadGeneralLogs()
  }
})

onMounted(async () => {
  try {
    await Promise.all([
      loadStats(),
      loadAdminLogs()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing ActivityLogs:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

