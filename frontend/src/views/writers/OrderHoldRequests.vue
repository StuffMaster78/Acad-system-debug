<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Hold Requests</h1>
        <p class="mt-2 text-gray-600">
          Request to pause an order’s deadline while you wait for client action or clarification.
        </p>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        + New Hold Request
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
        <p class="text-sm font-medium text-gray-600 mb-1">Total Requests</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.total }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 border border-yellow-100">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 border border-green-100">
        <p class="text-sm font-medium text-green-700 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.approved }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 border border-red-100">
        <p class="text-sm font-medium text-red-700 mb-1">Rejected</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.rejected }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filterStatus"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by order ID..."
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
    </div>

    <div v-else-if="filteredRequests.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">No hold requests yet.</p>
      <p class="text-gray-400 text-sm mt-2">
        Use hold requests when you’re blocked by the client—deadlines freeze until the client responds.
      </p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="request in filteredRequests"
        :key="request.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
      >
        <div class="p-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <router-link
                :to="`/orders/${request.order}`"
                class="text-lg font-semibold text-gray-900 hover:text-primary-600"
              >
                Order #{{ request.order }}
              </router-link>
              <span
                :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  getStatusBadgeClass(request.approved, request.reviewed_by)
                ]"
              >
                {{ getStatusLabel(request.approved, request.reviewed_by) }}
              </span>
            </div>
            <p class="text-sm text-gray-600 mb-3">
              Requested {{ formatDate(request.requested_at) }}
            </p>
            <div v-if="request.reason" class="bg-gray-50 border border-gray-100 rounded-lg p-4 text-sm text-gray-700">
              {{ request.reason }}
            </div>
          </div>
          <div class="flex flex-col gap-2 w-full md:w-auto">
            <router-link
              :to="`/orders/${request.order}`"
              class="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors text-center"
            >
              View Order
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingRequest ? 'Update Hold Request' : 'New Hold Request' }}
            </h2>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>

          <form class="space-y-4" @submit.prevent="saveRequest">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Order *</label>
              <select
                v-model="form.order"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Select an active order</option>
                <option
                  v-for="order in activeOrders"
                  :key="order.id"
                  :value="order.id"
                >
                  Order #{{ order.id }} — {{ order.topic || 'No topic' }} (Due {{ formatDate(order.writer_deadline || order.client_deadline || order.deadline) }})
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">
                Only orders you’re currently working on can be placed on hold.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Reason *</label>
              <textarea
                v-model="form.reason"
                rows="4"
                required
                placeholder="Explain why you need the order placed on hold (e.g., waiting for client instructions)."
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                {{ saving ? 'Submitting...' : editingRequest ? 'Update Request' : 'Submit Request' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import writerManagementAPI from '@/api/writer-management'
import ordersAPI from '@/api/orders'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { success: showSuccess, error: showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const requests = ref([])
const activeOrders = ref([])
const showModal = ref(false)
const editingRequest = ref(null)
const filterStatus = ref('')
const searchQuery = ref('')

const form = ref({
  order: '',
  reason: '',
})

const stats = computed(() => {
  return {
    total: requests.value.length,
    pending: requests.value.filter(r => r.approved === null || (r.approved === false && !r.reviewed_by)).length,
    approved: requests.value.filter(r => r.approved === true).length,
    rejected: requests.value.filter(r => r.approved === false && r.reviewed_by).length,
  }
})

const filteredRequests = computed(() => {
  let list = [...requests.value]

  if (filterStatus.value === 'pending') {
    list = list.filter(r => r.approved === null || (r.approved === false && !r.reviewed_by))
  } else if (filterStatus.value === 'approved') {
    list = list.filter(r => r.approved === true)
  } else if (filterStatus.value === 'rejected') {
    list = list.filter(r => r.approved === false && r.reviewed_by)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r => String(r.order).includes(q))
  }

  return list.sort((a, b) => new Date(b.requested_at) - new Date(a.requested_at))
})

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await writerManagementAPI.listHoldRequests()
    requests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load hold requests:', error)
    showError(getErrorMessage(error, 'Failed to load hold requests'))
  } finally {
    loading.value = false
  }
}

const loadActiveOrders = async () => {
  try {
    const response = await ordersAPI.list({
      assigned_writer: true,
      status__in: 'in_progress,under_editing,revision_requested,on_hold',
      page_size: 100,
    })
    activeOrders.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load active orders:', error)
    activeOrders.value = []
  }
}

const openModal = (request = null) => {
  editingRequest.value = request
  if (request) {
    form.value = {
      order: request.order,
      reason: request.reason,
    }
  } else {
    form.value = {
      order: '',
      reason: '',
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingRequest.value = null
  form.value = {
    order: '',
    reason: '',
  }
}

const saveRequest = async () => {
  if (!form.value.order || !form.value.reason.trim()) {
    showError('Please select an order and provide a reason.')
    return
  }

  saving.value = true
  try {
    const payload = {
      order: form.value.order,
      reason: form.value.reason.trim(),
    }

    if (editingRequest.value) {
      await writerManagementAPI.updateHoldRequest(editingRequest.value.id, payload)
      showSuccess('Hold request updated successfully')
    } else {
      await writerManagementAPI.createHoldRequest(payload)
      showSuccess('Hold request submitted successfully')
    }

    closeModal()
    await loadRequests()
  } catch (error) {
    console.error('Failed to save hold request:', error)
    showError(getErrorMessage(error, 'Failed to submit hold request'))
  } finally {
    saving.value = false
  }
}

const getStatusLabel = (approved, reviewedBy) => {
  if (approved === true) return 'Approved'
  if (approved === false && reviewedBy) return 'Rejected'
  return 'Pending'
}

const getStatusBadgeClass = (approved, reviewedBy) => {
  if (approved === true) return 'bg-green-100 text-green-700'
  if (approved === false && reviewedBy) return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

watch(showModal, (val) => {
  if (val) {
    loadActiveOrders()
  }
})

onMounted(() => {
  loadRequests()
  loadActiveOrders()
})
</script>

