<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Dispute Management</h1>
        <p class="mt-2 text-gray-600">Manage and resolve order disputes</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Open Disputes</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.open || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">In Review</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.in_review || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Escalated</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.escalated || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Resolved</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.resolved || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadDisputes" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_review">In Review</option>
            <option value="escalated">Escalated</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadDisputes" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Order ID</label>
          <input
            v-model.number="filters.order_id"
            @input="debouncedSearch"
            type="number"
            placeholder="Search by order ID"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Raised By</label>
          <input
            v-model="filters.raised_by"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by username"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Disputes Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else>
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Raised By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resolution</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="dispute in disputes" :key="dispute.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #{{ dispute.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div>
                  <router-link
                    :to="`/orders/${dispute.order_id || dispute.order?.id}`"
                    class="font-medium text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    Order #{{ dispute.order_id || dispute.order?.id || 'N/A' }}
                  </router-link>
                  <div class="text-xs text-gray-500 truncate max-w-xs" :title="dispute.order_topic || dispute.order?.topic">
                    {{ dispute.order_topic || dispute.order?.topic || 'N/A' }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ dispute.raised_by_username || dispute.raised_by?.username || 'N/A' }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" :title="dispute.reason">
                {{ dispute.reason || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(dispute.dispute_status || dispute.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ formatStatus(dispute.dispute_status || dispute.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="dispute.resolution_outcome" class="capitalize">
                  {{ formatResolutionOutcome(dispute.resolution_outcome) }}
                </span>
                <span v-else class="text-gray-400">Not resolved</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(dispute.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewDispute(dispute)" class="text-blue-600 hover:underline mr-2">View</button>
                <button
                  v-if="(dispute.dispute_status || dispute.status) !== 'resolved'"
                  @click="openResolveModal(dispute)"
                  class="text-green-600 hover:underline"
                >
                  Resolve
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!disputes.length" class="text-center py-12 text-gray-500">
          No disputes found.
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.totalItems > pagination.itemsPerPage" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ ((pagination.currentPage - 1) * pagination.itemsPerPage) + 1 }} to 
          {{ Math.min(pagination.currentPage * pagination.itemsPerPage, pagination.totalItems) }} of 
          {{ pagination.totalItems }} disputes
        </div>
        <div class="flex gap-2">
          <button
            @click="pagination.currentPage--; loadDisputes()"
            :disabled="pagination.currentPage === 1"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="pagination.currentPage++; loadDisputes()"
            :disabled="pagination.currentPage * pagination.itemsPerPage >= pagination.totalItems"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Dispute Detail Modal -->
    <div v-if="viewingDispute" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Dispute Details</h3>
          <button @click="viewingDispute = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-gray-600">Dispute ID:</span>
              <p class="text-gray-900 font-medium">#{{ viewingDispute.id }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <span :class="getStatusClass(viewingDispute.dispute_status || viewingDispute.status)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ formatStatus(viewingDispute.dispute_status || viewingDispute.status) }}
              </span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Order:</span>
              <router-link
                v-if="viewingDispute.order_id || viewingDispute.order?.id"
                :to="`/orders/${viewingDispute.order_id || viewingDispute.order?.id}`"
                class="text-blue-600 hover:text-blue-800 hover:underline font-medium"
              >
                #{{ viewingDispute.order_id || viewingDispute.order?.id }}
              </router-link>
              <p v-else class="text-gray-900">N/A</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Order Topic:</span>
              <p class="text-gray-900">{{ viewingDispute.order_topic || viewingDispute.order?.topic || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Raised By:</span>
              <p class="text-gray-900">{{ viewingDispute.raised_by_username || viewingDispute.raised_by?.username || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Website:</span>
              <p class="text-gray-900">{{ typeof viewingDispute.website === 'object' ? viewingDispute.website?.name : 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Created:</span>
              <p class="text-gray-900">{{ formatDateTime(viewingDispute.created_at) }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Updated:</span>
              <p class="text-gray-900">{{ formatDateTime(viewingDispute.updated_at) }}</p>
            </div>
            <div v-if="viewingDispute.writer_responded">
              <span class="text-sm font-medium text-gray-600">Writer Response:</span>
              <p class="text-green-600 font-medium">Yes</p>
            </div>
            <div v-if="viewingDispute.resolution_outcome">
              <span class="text-sm font-medium text-gray-600">Resolution Outcome:</span>
              <p class="text-gray-900 capitalize">{{ formatResolutionOutcome(viewingDispute.resolution_outcome) }}</p>
            </div>
          </div>

          <div class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Reason:</span>
            <p class="text-gray-700 mt-2 whitespace-pre-wrap">{{ viewingDispute.reason || 'N/A' }}</p>
          </div>

          <div v-if="viewingDispute.resolution_notes" class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Resolution Notes:</span>
            <p class="text-gray-700 mt-2 whitespace-pre-wrap">{{ viewingDispute.resolution_notes }}</p>
          </div>

          <div v-if="viewingDispute.admin_extended_deadline" class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Extended Deadline:</span>
            <p class="text-gray-900">{{ formatDateTime(viewingDispute.admin_extended_deadline) }}</p>
          </div>

          <!-- Actions -->
          <div v-if="(viewingDispute.dispute_status || viewingDispute.status) !== 'resolved'" class="border-t pt-4 flex gap-2">
            <button
              @click="openResolveModal(viewingDispute)"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Resolve Dispute
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Resolve Dispute Modal -->
    <div v-if="showResolveModal && resolvingDispute" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Resolve Dispute</h3>
          <button @click="closeResolveModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <form @submit.prevent="resolveDispute" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Resolution Outcome *</label>
            <select v-model="resolveForm.resolution_outcome" required class="w-full border rounded px-3 py-2">
              <option value="">Select outcome...</option>
              <option value="writer_wins">Writer Wins</option>
              <option value="client_wins">Client Wins</option>
              <option value="extend_deadline">Extend Deadline</option>
              <option value="reassign">Reassign Order</option>
            </select>
          </div>
          <div v-if="resolveForm.resolution_outcome === 'extend_deadline'">
            <label class="block text-sm font-medium mb-1">Extended Deadline</label>
            <input v-model="resolveForm.extended_deadline" type="datetime-local" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Resolution Notes *</label>
            <textarea v-model="resolveForm.resolution_notes" rows="4" required class="w-full border rounded px-3 py-2" placeholder="Enter resolution notes..."></textarea>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeResolveModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">Cancel</button>
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {{ saving ? 'Resolving...' : 'Resolve Dispute' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import disputesAPI from '@/api/disputes'
import adminDisputesAPI from '@/api/admin-disputes'
import apiClient from '@/api/client'

const router = useRouter()
const disputes = ref([])
const websites = ref([])
const loading = ref(false)
const saving = ref(false)
const viewingDispute = ref(null)
const showResolveModal = ref(false)
const resolvingDispute = ref(null)
const pagination = ref({
  currentPage: 1,
  totalItems: 0,
  itemsPerPage: 20
})

const stats = ref({
  open: 0,
  in_review: 0,
  escalated: 0,
  resolved: 0,
})

const filters = ref({
  status: '',
  website: '',
  order_id: '',
  raised_by: '',
})

const resolveForm = ref({
  resolution_outcome: '',
  resolution_notes: '',
  extended_deadline: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadDisputes()
  }, 500)
}

const loadDisputes = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.currentPage,
      page_size: pagination.value.itemsPerPage
    }
    if (filters.value.status) {
      params.dispute_status = filters.value.status
    }
    if (filters.value.website) {
      params.website = filters.value.website
    }
    if (filters.value.order_id) {
      params.order = filters.value.order_id
    }
    if (filters.value.raised_by) {
      params.raised_by__username__icontains = filters.value.raised_by
    }

    const res = await disputesAPI.list(params)
    disputes.value = res.data.results || res.data || []
    
    // Update pagination
    if (res.data.count !== undefined) {
      pagination.value.totalItems = res.data.count
      pagination.value.currentPage = res.data.current_page || res.data.page || 1
    } else {
      pagination.value.totalItems = disputes.value.length
    }
    
    calculateStats()
  } catch (error) {
    showMessage('Failed to load disputes: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const loadDashboard = async () => {
  try {
    const res = await adminDisputesAPI.getDashboard()
    const dashboard = res.data
    
    if (dashboard.summary) {
      // Use dashboard stats which are more accurate (all disputes, not just current page)
      stats.value = {
        open: dashboard.summary.pending_disputes || dashboard.status_breakdown?.open || 0,
        in_review: dashboard.status_breakdown?.in_review || 0,
        escalated: dashboard.status_breakdown?.escalated || 0,
        resolved: dashboard.status_breakdown?.resolved || dashboard.summary.resolved_recent || 0,
      }
    } else if (dashboard.status_breakdown) {
      // Fallback to status breakdown if summary not available
      stats.value = {
        open: dashboard.status_breakdown.open || 0,
        in_review: dashboard.status_breakdown.in_review || 0,
        escalated: dashboard.status_breakdown.escalated || 0,
        resolved: dashboard.status_breakdown.resolved || 0,
      }
    }
  } catch (error) {
    console.error('Failed to load dispute dashboard:', error)
    // Fallback to calculating from disputes list
    calculateStats()
  }
}

const calculateStats = () => {
  // Calculate from current page data (for quick display)
  // The dashboard API provides more accurate stats
  stats.value = {
    open: disputes.value.filter(d => (d.dispute_status || d.status) === 'open').length,
    in_review: disputes.value.filter(d => (d.dispute_status || d.status) === 'in_review').length,
    escalated: disputes.value.filter(d => (d.dispute_status || d.status) === 'escalated').length,
    resolved: disputes.value.filter(d => (d.dispute_status || d.status) === 'resolved').length,
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    website: '',
    order_id: '',
    raised_by: '',
  }
  pagination.value.currentPage = 1
  loadDisputes()
}

const viewDispute = async (dispute) => {
  try {
    const res = await disputesAPI.get(dispute.id)
    viewingDispute.value = res.data
  } catch (error) {
    viewingDispute.value = dispute
    showMessage('Failed to load dispute details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openResolveModal = (dispute) => {
  resolvingDispute.value = dispute
  resolveForm.value = {
    resolution_outcome: dispute.resolution_outcome || '',
    resolution_notes: dispute.resolution_notes || '',
    extended_deadline: dispute.admin_extended_deadline ? new Date(dispute.admin_extended_deadline).toISOString().slice(0, 16) : '',
  }
  showResolveModal.value = true
}

const closeResolveModal = () => {
  showResolveModal.value = false
  resolvingDispute.value = null
  resolveForm.value = {
    resolution_outcome: '',
    resolution_notes: '',
    extended_deadline: '',
  }
}

const resolveDispute = async () => {
  saving.value = true
  try {
    const data = {
      resolution_outcome: resolveForm.value.resolution_outcome,
      resolution_notes: resolveForm.value.resolution_notes,
    }
    
    if (resolveForm.value.resolution_outcome === 'extend_deadline' && resolveForm.value.extended_deadline) {
      data.extended_deadline = resolveForm.value.extended_deadline
    }
    
    await disputesAPI.resolve(resolvingDispute.value.id, data)
    showMessage('Dispute resolved successfully', true)
    closeResolveModal()
    await loadDisputes()
    if (viewingDispute.value?.id === resolvingDispute.value.id) {
      viewingDispute.value = null
    }
  } catch (error) {
    showMessage('Failed to resolve dispute: ' + (error.response?.data?.detail || error.response?.data?.error || error.message), false)
  } finally {
    saving.value = false
  }
}

const getStatusClass = (status) => {
  if (!status) return 'bg-gray-100 text-gray-800'
  if (status === 'resolved') return 'bg-green-100 text-green-800'
  if (status === 'closed') return 'bg-gray-100 text-gray-800'
  if (status === 'escalated') return 'bg-orange-100 text-orange-800'
  if (status === 'in_review') return 'bg-yellow-100 text-yellow-800'
  if (status === 'open') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const formatStatus = (status) => {
  if (!status) return 'N/A'
  return status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatResolutionOutcome = (outcome) => {
  if (!outcome) return 'N/A'
  return outcome.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const message = ref('')
const messageSuccess = ref(false)

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(async () => {
  await Promise.all([
    loadWebsites(),
    loadDashboard(),
    loadDisputes()
  ])
})
</script>

