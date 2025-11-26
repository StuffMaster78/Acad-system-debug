<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Deadline Extension Requests</h1>
        <p class="mt-2 text-gray-600">Request deadline extensions for your orders</p>
      </div>
      <button
        @click="showRequestModal = true; editingRequest = null"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        + New Request
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <p class="text-sm font-medium text-gray-600 mb-1">Total Requests</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6">
        <p class="text-sm font-medium text-yellow-600 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6">
        <p class="text-sm font-medium text-green-600 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.approved || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6">
        <p class="text-sm font-medium text-red-600 mb-1">Rejected</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.rejected || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filterStatus"
            @change="loadRequests"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by order ID..."
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </div>

    <!-- Requests List -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <div v-else-if="filteredRequests.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">No deadline extension requests found.</p>
      <p class="text-gray-400 text-sm mt-2">Create a new request to extend an order deadline.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="request in filteredRequests"
        :key="request.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-3">
                <h3 class="text-lg font-semibold text-gray-900">
                  Order #{{ request.order }}
                </h3>
                <span
                  :class="[
                    'px-3 py-1 rounded-full text-xs font-medium',
                    getStatusBadgeClass(request.approved)
                  ]"
                >
                  {{ getStatusLabel(request.approved) }}
                </span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p class="text-sm text-gray-600 mb-1">Current Deadline</p>
                  <p class="text-sm font-medium text-gray-900">
                    {{ formatDateTime(request.old_deadline) }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-600 mb-1">Requested Deadline</p>
                  <p class="text-sm font-medium text-primary-600">
                    {{ formatDateTime(request.requested_deadline) }}
                  </p>
                </div>
              </div>

              <div v-if="request.reason" class="mb-4">
                <p class="text-sm text-gray-600 mb-1">Reason</p>
                <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg">
                  {{ request.reason }}
                </p>
              </div>

              <div class="flex items-center gap-4 text-sm text-gray-500">
                <span>Requested: {{ formatDateTime(request.requested_at) }}</span>
                <span v-if="request.reviewed_by">
                  Reviewed by: {{ request.reviewed_by }}
                </span>
              </div>
            </div>

            <div class="flex flex-col gap-2 ml-4">
              <router-link
                :to="`/orders/${request.order}`"
                class="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors text-center"
              >
                View Order
              </router-link>
              <button
                v-if="!request.approved && request.approved === null"
                @click="editRequest(request)"
                class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              >
                Edit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Modal -->
    <div
      v-if="showRequestModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingRequest ? 'Edit Request' : 'New Deadline Extension Request' }}
            </h2>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <form @submit.prevent="saveRequest" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Order *</label>
              <select
                v-model="requestForm.order"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                @change="loadOrderDetails"
              >
                <option value="">Select an order</option>
                <option
                  v-for="order in availableOrders"
                  :key="order.id"
                  :value="order.id"
                >
                  Order #{{ order.id }} - {{ order.topic || 'No topic' }} (Due: {{ formatDateTime(order.writer_deadline || order.client_deadline || order.deadline) }})
                </option>
              </select>
            </div>

            <div v-if="selectedOrder" class="bg-gray-50 p-4 rounded-lg">
              <p class="text-sm text-gray-600 mb-2">Current Deadline:</p>
              <p class="text-sm font-medium text-gray-900">
                {{ formatDateTime(selectedOrder.writer_deadline || selectedOrder.client_deadline || selectedOrder.deadline) }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">New Deadline *</label>
              <input
                v-model="requestForm.requested_deadline"
                type="datetime-local"
                required
                :min="minDeadline"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <p class="text-xs text-gray-500 mt-1">The new deadline must be after the current deadline</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Reason *</label>
              <textarea
                v-model="requestForm.reason"
                required
                rows="4"
                placeholder="Please explain why you need a deadline extension..."
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              ></textarea>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : 'Submit Request' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import writerManagementAPI from '@/api/writer-management'
import ordersAPI from '@/api/orders'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import { debounce } from '@/utils/debounce'

const { success: showSuccess, error: showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const requests = ref([])
const availableOrders = ref([])
const selectedOrder = ref(null)
const filterStatus = ref('')
const searchQuery = ref('')
const showRequestModal = ref(false)
const editingRequest = ref(null)

const requestForm = ref({
  order: '',
  old_deadline: '',
  requested_deadline: '',
  reason: '',
})

const stats = computed(() => {
  const total = requests.value.length
  const pending = requests.value.filter(r => r.approved === null || r.approved === false).length
  const approved = requests.value.filter(r => r.approved === true).length
  const rejected = requests.value.filter(r => r.approved === false && r.reviewed_by).length
  
  return { total, pending, approved, rejected }
})

const filteredRequests = computed(() => {
  let filtered = requests.value

  if (filterStatus.value) {
    if (filterStatus.value === 'pending') {
      filtered = filtered.filter(r => r.approved === null || (r.approved === false && !r.reviewed_by))
    } else if (filterStatus.value === 'approved') {
      filtered = filtered.filter(r => r.approved === true)
    } else if (filterStatus.value === 'rejected') {
      filtered = filtered.filter(r => r.approved === false && r.reviewed_by)
    }
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(r => 
      String(r.order).includes(query)
    )
  }

  return filtered.sort((a, b) => new Date(b.requested_at) - new Date(a.requested_at))
})

const minDeadline = computed(() => {
  if (!selectedOrder.value) return ''
  const deadline = selectedOrder.value.writer_deadline || selectedOrder.value.client_deadline || selectedOrder.value.deadline
  if (!deadline) return ''
  const date = new Date(deadline)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
})

const debouncedSearch = debounce(() => {
  // Filtering is handled by computed property
}, 300)

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await writerManagementAPI.listDeadlineExtensionRequests()
    requests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load deadline extension requests:', error)
    showError(getErrorMessage(error, 'Failed to load requests'))
  } finally {
    loading.value = false
  }
}

const loadAvailableOrders = async () => {
  try {
    const response = await ordersAPI.list({
      assigned_writer: true,
      status__in: ['in_progress', 'assigned', 'under_editing'],
      page_size: 100,
    })
    availableOrders.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load available orders:', error)
  }
}

const loadOrderDetails = async () => {
  if (!requestForm.value.order) {
    selectedOrder.value = null
    return
  }
  
  try {
    const response = await ordersAPI.get(requestForm.value.order)
    selectedOrder.value = response.data
    
    // Set old deadline
    const deadline = response.data.writer_deadline || response.data.client_deadline || response.data.deadline
    if (deadline) {
      requestForm.value.old_deadline = deadline
    }
  } catch (error) {
    console.error('Failed to load order details:', error)
    showError(getErrorMessage(error, 'Failed to load order details'))
  }
}

const saveRequest = async () => {
  saving.value = true
  try {
    const data = {
      order: requestForm.value.order,
      old_deadline: requestForm.value.old_deadline,
      requested_deadline: requestForm.value.requested_deadline,
      reason: requestForm.value.reason,
    }

    if (editingRequest.value) {
      await writerManagementAPI.updateDeadlineExtensionRequest(editingRequest.value.id, data)
      showSuccess('Request updated successfully')
    } else {
      await writerManagementAPI.createDeadlineExtensionRequest(data)
      showSuccess('Request submitted successfully')
    }
    
    closeModal()
    await loadRequests()
  } catch (error) {
    console.error('Failed to save request:', error)
    showError(getErrorMessage(error, 'Failed to save request'))
  } finally {
    saving.value = false
  }
}

const editRequest = (request) => {
  editingRequest.value = request
  requestForm.value = {
    order: request.order,
    old_deadline: request.old_deadline,
    requested_deadline: request.requested_deadline ? new Date(request.requested_deadline).toISOString().slice(0, 16) : '',
    reason: request.reason,
  }
  loadOrderDetails()
  showRequestModal.value = true
}

const closeModal = () => {
  showRequestModal.value = false
  editingRequest.value = null
  requestForm.value = {
    order: '',
    old_deadline: '',
    requested_deadline: '',
    reason: '',
  }
  selectedOrder.value = null
}

const getStatusBadgeClass = (approved) => {
  if (approved === true) return 'bg-green-100 text-green-700'
  if (approved === false && approved !== null) return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

const getStatusLabel = (approved) => {
  if (approved === true) return 'Approved'
  if (approved === false && approved !== null) return 'Rejected'
  return 'Pending'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadRequests()
  loadAvailableOrders()
})
</script>

