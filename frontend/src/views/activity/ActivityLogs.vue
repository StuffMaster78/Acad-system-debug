<template>
  <div class="space-y-6 p-6">
    <!-- Breadcrumb -->
    <nav class="text-sm text-gray-600 mb-4">
      <span class="hover:text-gray-900 cursor-pointer" @click="$router.push('/dashboard')">Dashboard</span>
      <span class="mx-2">/</span>
      <span class="text-gray-900 font-medium">User Activity</span>
    </nav>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">User Activity</h1>
      <div class="flex items-center space-x-3">
        <!-- Auto-refresh Toggle -->
        <button
          @click="toggleAutoRefresh"
          :class="[
            'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
            autoRefreshEnabled
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
          :title="autoRefreshEnabled ? 'Auto-refresh enabled (30s)' : 'Enable auto-refresh'"
        >
          <span class="flex items-center space-x-1">
            <svg 
              v-if="autoRefreshEnabled" 
              class="w-4 h-4 animate-spin" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg 
              v-else 
              class="w-4 h-4" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{{ autoRefreshEnabled ? 'Auto' : 'Manual' }}</span>
          </span>
        </button>
        
        <!-- Refresh Button -->
        <button 
          @click="refreshActivities" 
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
          :disabled="loading"
          title="Refresh now"
        >
          <svg 
            :class="['w-4 h-4', loading ? 'animate-spin' : '']" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{{ loading ? 'Loading...' : 'Refresh' }}</span>
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="p-4 rounded-lg bg-red-50 text-red-700 border border-red-200">
      <p class="font-medium">Error loading activity logs</p>
      <p class="text-sm mt-1">{{ error }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !activities.length" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Activity Timeline -->
    <div v-else-if="activities.length" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div class="space-y-4">
        <div 
          v-for="(activity, index) in activities" 
          :key="activity.id"
          class="flex items-start space-x-4 relative"
        >
          <!-- Timeline Line -->
          <div 
            v-if="index < activities.length - 1"
            class="absolute left-5 top-12 bottom-0 w-0.5 bg-gray-200"
          ></div>

          <!-- Icon -->
          <div class="shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center border-2 border-white relative z-10" aria-label="Activity">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <!-- User Role Badge and Email -->
                <div class="flex items-center space-x-2 mb-1">
                  <span 
                    :class="getRoleBadgeClass(activity.user_role)"
                    class="px-2 py-0.5 rounded text-xs font-medium"
                  >
                    {{ activity.user_role || 'user' }}
                  </span>
                  <span class="text-sm text-gray-600">({{ activity.user_email || 'N/A' }})</span>
                </div>

                <!-- Description -->
                <p class="text-gray-900 text-sm leading-relaxed">
                  {{ activity.display_description || activity.description || 'No description' }}
                </p>
              </div>

              <!-- Timestamp -->
              <div class="shrink-0 ml-4 text-right">
                <span class="text-sm text-gray-500 font-medium">
                  {{ activity.formatted_timestamp || formatTimestamp(activity.timestamp) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination && pagination.count > 0" class="mt-6 flex items-center justify-between border-t border-gray-200 pt-4">
        <div class="flex items-center text-sm text-gray-700">
          <span>
            Showing {{ ((currentPage - 1) * pageSize) + 1 }} to 
            {{ Math.min(currentPage * pageSize, pagination.count) }} of 
            {{ pagination.count }} results
          </span>
        </div>
        
        <div class="flex items-center space-x-2">
          <!-- Previous Button -->
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="!pagination.previous || loading"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          <!-- Page Numbers -->
          <div class="flex items-center space-x-1">
            <template v-for="page in visiblePages" :key="page">
              <button
                v-if="page !== '...'"
                @click="goToPage(page)"
                :disabled="loading"
                :class="[
                  'px-3 py-2 text-sm font-medium rounded-md',
                  page === currentPage
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50',
                  loading ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                {{ page }}
              </button>
              <span v-else class="px-2 text-gray-500">...</span>
            </template>
          </div>
          
          <!-- Next Button -->
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="!pagination.next || loading"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No activities</h3>
      <p class="mt-1 text-sm text-gray-500">No activity logs found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import activityAPI from '@/api/activity-logs'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const activities = ref([])
const error = ref('')
const pagination = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const autoRefreshEnabled = ref(false)
const autoRefreshInterval = ref(null)
const refreshInterval = 30000 // 30 seconds

// Compute visible page numbers for pagination
const visiblePages = computed(() => {
  if (!pagination.value) return []
  
  const totalPages = Math.ceil(pagination.value.count / pageSize.value)
  const pages = []
  const maxVisible = 7 // Show max 7 page numbers
  
  if (totalPages <= maxVisible) {
    // Show all pages if total is less than max
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i)
    }
  } else {
    // Show pages around current page
    const start = Math.max(1, currentPage.value - 3)
    const end = Math.min(totalPages, currentPage.value + 3)
    
    if (start > 1) {
      pages.push(1)
      if (start > 2) pages.push('...')
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    
    if (end < totalPages) {
      if (end < totalPages - 1) pages.push('...')
      pages.push(totalPages)
    }
  }
  
  return pages
})

const loadActivities = async (page = 1) => {
  loading.value = true
  error.value = ''
  currentPage.value = page
  
  try {
    const params = {
      page: page,
      page_size: pageSize.value,
    }
    
    const isAdmin = ['admin', 'superadmin'].includes(authStore.userRole)
    const res = isAdmin
      ? await activityAPI.list(params)
      : await activityAPI.listUserFeed(params)
    
    // Handle paginated response from DRF
    if (res.data?.results && Array.isArray(res.data.results)) {
      activities.value = res.data.results
      pagination.value = {
        count: res.data.count || 0,
        next: res.data.next || null,
        previous: res.data.previous || null,
      }
    } else if (Array.isArray(res.data)) {
      // Fallback for non-paginated response
      activities.value = res.data
      pagination.value = {
        count: res.data.length,
        next: null,
        previous: null,
      }
    } else {
      activities.value = []
      pagination.value = {
        count: 0,
        next: null,
        previous: null,
      }
    }
    
    // Update URL query parameter
    router.replace({ query: { ...route.query, page } })
    
  } catch (e) {
    console.error('Failed to load activities:', e)
    error.value = e?.response?.data?.detail || e.message || 'Failed to load activity logs'
    activities.value = []
    pagination.value = null
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page < 1 || loading.value) return
  const totalPages = pagination.value ? Math.ceil(pagination.value.count / pageSize.value) : 1
  if (page > totalPages) return
  loadActivities(page)
}

const refreshActivities = () => {
  loadActivities(currentPage.value)
}

const toggleAutoRefresh = () => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
  
  if (autoRefreshEnabled.value) {
    // Start auto-refresh
    startAutoRefresh()
  } else {
    // Stop auto-refresh
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh() // Clear any existing interval
  
  autoRefreshInterval.value = setInterval(() => {
    if (!loading.value) {
      loadActivities(currentPage.value)
    }
  }, refreshInterval)
}

const stopAutoRefresh = () => {
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = null
  }
}

const formatTimestamp = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const day = date.getDate()
  const month = date.toLocaleDateString('en-US', { month: 'short' })
  const year = date.getFullYear()
  return `${hours}:${minutes} ${day}, ${month} ${year}`
}

const getRoleBadgeClass = (role) => {
  const classes = {
    admin: 'bg-red-100 text-red-700',
    superadmin: 'bg-purple-100 text-purple-700',
    client: 'bg-blue-100 text-blue-700',
    writer: 'bg-green-100 text-green-700',
    editor: 'bg-indigo-100 text-indigo-700',
    support: 'bg-yellow-100 text-yellow-700',
    user: 'bg-gray-100 text-gray-700',
  }
  return classes[role?.toLowerCase()] || 'bg-gray-100 text-gray-700'
}

onMounted(() => {
  // Get page from URL query parameter, default to 1
  const page = parseInt(route.query.page) || 1
  loadActivities(page)
  
  // Optionally start auto-refresh by default (uncomment if desired)
  // autoRefreshEnabled.value = true
  // startAutoRefresh()
})

onUnmounted(() => {
  // Clean up auto-refresh interval when component is unmounted
  stopAutoRefresh()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
