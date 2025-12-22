<template>
  <div class="space-y-6 p-4 md:p-6" v-if="!componentError && !initialLoading">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Dispute Management</h1>
        <p class="mt-2 text-sm md:text-base text-gray-600 dark:text-gray-400">Manage and resolve order disputes</p>
      </div>
      <button 
        @click="loadDashboard" 
        :disabled="loading"
        class="w-full sm:w-auto px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm font-medium"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border border-yellow-200 dark:border-yellow-800">
        <p class="text-xs sm:text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending Disputes</p>
        <p class="text-2xl sm:text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.summary?.pending_disputes || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-800">
        <p class="text-xs sm:text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Disputes</p>
        <p class="text-2xl sm:text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.summary?.total_disputes || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-800">
        <p class="text-xs sm:text-sm font-medium text-green-700 dark:text-green-300 mb-1">Resolved (30d)</p>
        <p class="text-2xl sm:text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.summary?.resolved_recent || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border border-orange-200 dark:border-orange-800">
        <p class="text-xs sm:text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Awaiting Response</p>
        <p class="text-2xl sm:text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.summary?.awaiting_response || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
      <nav class="-mb-px flex space-x-4 sm:space-x-8 min-w-max">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm transition-colors',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Pending Disputes Tab -->
    <div v-if="activeTab === 'pending'" class="space-y-4">
    <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
            <select 
              v-model="filters.status" 
              @change="loadPendingDisputes" 
              class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm"
            >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div>
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website</label>
            <select 
              v-model="filters.website" 
              @change="loadPendingDisputes" 
              class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm"
            >
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
          <div class="sm:col-span-2">
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
          <input
              v-model="filters.search"
            @input="debouncedSearch"
            type="text"
              placeholder="Order ID, client, topic..."
              class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm"
          />
        </div>
      </div>
    </div>

    <!-- Disputes Table -->
      <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      
      <div v-else>
          <!-- Mobile Card View -->
          <div class="block sm:hidden space-y-4 p-4">
            <div
              v-for="dispute in filteredDisputes"
              :key="dispute.id"
              @click="viewDispute(dispute)"
              class="border dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div class="flex items-start justify-between mb-2">
                <div>
                  <p class="font-semibold text-gray-900 dark:text-white">Order #{{ dispute.order?.id || dispute.order_id }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ dispute.order?.topic || 'N/A' }}</p>
                </div>
                <span 
                  :class="getStatusClass(dispute.dispute_status || dispute.status)" 
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ dispute.dispute_status || dispute.status }}
                </span>
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p><strong>Raised by:</strong> {{ dispute.raised_by?.username || dispute.raised_by || 'N/A' }}</p>
                <p><strong>Created:</strong> {{ formatDate(dispute.created_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Desktop Table View -->
          <div class="hidden sm:block overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">ID</th>
                  <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Order</th>
                  <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Raised By</th>
                  <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                  <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Created</th>
                  <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                <tr 
                  v-for="dispute in filteredDisputes" 
                  :key="dispute.id" 
                  class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <td class="px-4 lg:px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    #{{ dispute.id }}
                  </td>
                  <td class="px-4 lg:px-6 py-4 text-sm text-gray-900 dark:text-white">
                    <div>
                      <p class="font-medium">Order #{{ dispute.order?.id || dispute.order_id }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-xs">
                        {{ dispute.order?.topic || 'N/A' }}
                      </p>
                    </div>
                  </td>
                  <td class="px-4 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {{ dispute.raised_by?.username || dispute.raised_by || 'N/A' }}
              </td>
                  <td class="px-4 lg:px-6 py-4 whitespace-nowrap">
                    <span 
                      :class="getStatusClass(dispute.dispute_status || dispute.status)" 
                      class="px-2 py-1 rounded-full text-xs font-medium"
                    >
                      {{ dispute.dispute_status || dispute.status }}
                </span>
              </td>
                  <td class="px-4 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(dispute.created_at) }}
              </td>
                  <td class="px-4 lg:px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                      @click="viewDispute(dispute)" 
                      class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300"
                >
                      View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
          </div>
          
          <div v-if="!filteredDisputes.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <p class="text-lg">No disputes found</p>
            <p class="text-sm mt-2">All disputes have been resolved</p>
          </div>
        </div>
        </div>
      </div>
      
    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="space-y-4">
      <div class="card p-4 md:p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Dispute Analytics</h3>
        <div v-if="analyticsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
        <div v-else class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Average Resolution Time</h4>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ analytics.avg_resolution_days ? analytics.avg_resolution_days.toFixed(1) : 'N/A' }} days
              </p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Resolution Outcomes</h4>
              <div class="space-y-2">
                <div 
                  v-for="(count, outcome) in analytics.outcome_breakdown" 
                  :key="outcome"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-gray-600 dark:text-gray-400 capitalize">{{ outcome || 'N/A' }}</span>
                  <span class="font-semibold text-gray-900 dark:text-white">{{ count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dispute Detail Modal -->
    <div 
      v-if="viewingDispute" 
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto"
      @click.self="viewingDispute = null"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full my-auto p-4 md:p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">Dispute Details</h3>
          <button 
            @click="viewingDispute = null" 
            class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-2xl"
          >
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Dispute ID:</span>
              <p class="text-gray-900 dark:text-white font-medium">#{{ viewingDispute.id }}</p>
            </div>
            <div>
              <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Status:</span>
              <span 
                :class="getStatusClass(viewingDispute.dispute_status || viewingDispute.status)" 
                class="px-3 py-1 rounded-full text-xs font-medium"
              >
                {{ viewingDispute.dispute_status || viewingDispute.status }}
              </span>
            </div>
            <div>
              <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Order:</span>
              <p class="text-gray-900 dark:text-white">
                #{{ viewingDispute.order?.id || viewingDispute.order_id }}
              </p>
            </div>
            <div>
              <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Raised By:</span>
              <p class="text-gray-900 dark:text-white">
                {{ viewingDispute.raised_by?.username || viewingDispute.raised_by || 'N/A' }}
              </p>
            </div>
            <div>
              <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Created:</span>
              <p class="text-gray-900 dark:text-white">{{ formatDateTime(viewingDispute.created_at) }}</p>
            </div>
            <div v-if="viewingDispute.resolved_by">
              <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Resolved By:</span>
              <p class="text-gray-900 dark:text-white">
                {{ typeof viewingDispute.resolved_by === 'object' ? viewingDispute.resolved_by?.username : viewingDispute.resolved_by }}
              </p>
            </div>
          </div>

          <div v-if="viewingDispute.dispute_reason">
            <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Reason:</span>
            <p class="text-gray-900 dark:text-white mt-1">{{ viewingDispute.dispute_reason }}</p>
          </div>

          <div v-if="viewingDispute.resolution_notes">
            <span class="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400">Resolution Notes:</span>
            <p class="text-gray-900 dark:text-white mt-1">{{ viewingDispute.resolution_notes }}</p>
          </div>

          <!-- Resolve Dispute Form -->
          <div v-if="(viewingDispute.dispute_status || viewingDispute.status) === 'open'" class="border-t dark:border-gray-700 pt-4 mt-4">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Resolve Dispute</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Resolution Outcome</label>
                <select 
                  v-model="resolveForm.resolution_outcome" 
                  class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm"
                >
                  <option value="">Select outcome</option>
                  <option value="favor_client">Favor Client</option>
                  <option value="favor_writer">Favor Writer</option>
                  <option value="partial">Partial Resolution</option>
                  <option value="dismissed">Dismissed</option>
                </select>
              </div>
              <div>
                <label class="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Resolution Notes</label>
                <textarea 
                  v-model="resolveForm.resolution_notes" 
                  rows="4"
                  class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm"
                  placeholder="Enter resolution details..."
                ></textarea>
          </div>
              <div class="flex flex-col sm:flex-row gap-2">
                <button 
                  @click="resolveDispute" 
                  :disabled="resolving || !resolveForm.resolution_outcome"
                  class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
                >
                  {{ resolving ? 'Resolving...' : 'Resolve Dispute' }}
                </button>
            <button
                  @click="viewingDispute = null" 
                  class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
            >
                  Cancel
            </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="componentError" class="card p-6 text-center">
      <p class="text-red-600 dark:text-red-400">{{ componentError }}</p>
      <button @click="loadDashboard" class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
        Retry
            </button>
    </div>
  </div>

  <!-- Loading State -->
  <div v-if="initialLoading" class="flex items-center justify-center min-h-screen">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminDisputesAPI from '@/api/admin-disputes'
import disputesAPI from '@/api/disputes'
import { useDebounceFn } from '@vueuse/core'

const { success: showSuccess, error: showError } = useToast()

// State
const loading = ref(false)
const initialLoading = ref(true)
const componentError = ref(null)
const activeTab = ref('pending')
const disputes = ref([])
const stats = ref({ summary: {} })
const analytics = ref({})
const analyticsLoading = ref(false)
const viewingDispute = ref(null)
const resolving = ref(false)
const websites = ref([])

const tabs = [
  { id: 'pending', label: 'Pending Disputes' },
  { id: 'analytics', label: 'Analytics' },
]

const filters = ref({
  status: '',
  website: '',
  search: '',
})

const resolveForm = ref({
  resolution_outcome: '',
  resolution_notes: '',
  extended_deadline: null,
})

// Computed
const filteredDisputes = computed(() => {
  let result = disputes.value

  if (filters.value.status) {
    result = result.filter(d => (d.dispute_status || d.status) === filters.value.status)
  }

  if (filters.value.website) {
    result = result.filter(d => {
      const websiteId = typeof d.website === 'object' ? d.website?.id : d.website
      return websiteId === parseInt(filters.value.website)
    })
  }

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(d => {
      const orderId = d.order?.id || d.order_id
      const topic = d.order?.topic || ''
      const raisedBy = d.raised_by?.username || d.raised_by || ''
      return (
        orderId?.toString().includes(search) ||
        topic.toLowerCase().includes(search) ||
        raisedBy.toLowerCase().includes(search)
      )
    })
  }

  return result
})

// Methods
const loadDashboard = async () => {
  loading.value = true
  componentError.value = null
  try {
    const response = await adminDisputesAPI.getDashboard()
    stats.value = response.data
    await loadPendingDisputes()
  } catch (error) {
    componentError.value = error.response?.data?.detail || error.message || 'Failed to load dashboard'
    showError(componentError.value)
  } finally {
    loading.value = false
    initialLoading.value = false
  }
}

const loadPendingDisputes = async () => {
  loading.value = true
  try {
    const response = await adminDisputesAPI.getPendingDisputes()
    disputes.value = response.data.disputes || []
  } catch (error) {
    showError(error.response?.data?.detail || error.message || 'Failed to load disputes')
  } finally {
    loading.value = false
  }
}

const loadAnalytics = async () => {
  analyticsLoading.value = true
  try {
    const response = await adminDisputesAPI.getAnalytics()
    analytics.value = response.data
  } catch (error) {
    showError(error.response?.data?.detail || error.message || 'Failed to load analytics')
  } finally {
    analyticsLoading.value = false
  }
}

const viewDispute = async (dispute) => {
  try {
    const response = await disputesAPI.get(dispute.id)
    viewingDispute.value = response.data
  resolveForm.value = {
    resolution_outcome: '',
    resolution_notes: '',
      extended_deadline: null,
    }
  } catch (error) {
    showError(error.response?.data?.detail || error.message || 'Failed to load dispute details')
  }
}

const resolveDispute = async () => {
  if (!resolveForm.value.resolution_outcome) {
    showError('Please select a resolution outcome')
    return
  }

  resolving.value = true
  try {
    await disputesAPI.resolveDispute(viewingDispute.value.id, {
      resolution_outcome: resolveForm.value.resolution_outcome,
      resolution_notes: resolveForm.value.resolution_notes,
      extended_deadline: resolveForm.value.extended_deadline,
    })
    showSuccess('Dispute resolved successfully')
      viewingDispute.value = null
    await loadDashboard()
  } catch (error) {
    showError(error.response?.data?.detail || error.message || 'Failed to resolve dispute')
  } finally {
    resolving.value = false
  }
}

const getStatusClass = (status) => {
  const classes = {
    'open': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'resolved': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'closed': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  }
  return classes[status?.toLowerCase()] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const debouncedSearch = useDebounceFn(() => {
  // Search is handled by computed property
}, 300)

// Watch active tab
import { watch } from 'vue'
watch(activeTab, (newTab) => {
  if (newTab === 'analytics') {
    loadAnalytics()
  }
})

// Lifecycle
onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem; /* rounded-lg */
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border-gray-200 */
}

.dark .card {
  background-color: #1f2937; /* dark:bg-gray-800 */
  border-color: #374151; /* dark:border-gray-700 */
}
</style>

