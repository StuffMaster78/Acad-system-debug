<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Orders</h1>
        <p class="mt-2 text-gray-600">Manage your assigned orders and track deadlines</p>
      </div>
      <button @click="loadOrders" :disabled="loading" class="btn btn-secondary">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.in_progress || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Due Soon</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.due_soon || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Submitted</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.submitted || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Active</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.total_active || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            @change="loadOrders"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="in_progress">In Progress</option>
            <option value="submitted">Submitted</option>
            <option value="under_editing">Under Editing</option>
            <option value="revision_requested">Revision Requested</option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
            <option value="approved">Approved</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            v-model="sortBy"
            @change="loadOrders"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="deadline_asc">Deadline (Earliest First)</option>
            <option value="deadline_desc">Deadline (Latest First)</option>
            <option value="created_desc">Newest First</option>
            <option value="created_asc">Oldest First</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by topic or order ID..."
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </div>

    <!-- Orders List -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <div v-else-if="orders.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">No orders found.</p>
      <p class="text-gray-400 text-sm mt-2">Check the order queue to find available orders.</p>
      <router-link to="/writer/queue" class="mt-4 inline-block btn btn-primary">
        View Order Queue
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="order in orders"
        :key="order.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">
                  Order #{{ order.id }}
                </h3>
                <span
                  :class="getStatusBadgeClass(order.status)"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ formatStatus(order.status) }}
                </span>
                <span
                  v-if="isDueSoon(order.writer_deadline || order.client_deadline || order.deadline)"
                  class="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700"
                >
                  Due Soon
                </span>
              </div>
              
              <p class="text-gray-900 font-medium mb-2">{{ order.topic || 'No topic' }}</p>
              
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
                <div>
                  <span class="text-gray-500">Pages:</span>
                  <span class="ml-2 font-medium text-gray-900">{{ order.pages || order.number_of_pages || 'N/A' }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Service:</span>
                  <span class="ml-2 font-medium text-gray-900">
                    {{ order.service_type?.name || order.service_type || 'N/A' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500">Deadline:</span>
                  <span
                    class="ml-2 font-medium"
                    :class="getDeadlineClass(order.writer_deadline || order.client_deadline || order.deadline)"
                  >
                    {{ formatDeadline(order.writer_deadline || order.client_deadline || order.deadline) }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500">Price:</span>
                  <span class="ml-2 font-medium text-green-600">${{ formatCurrency(order.total_price) }}</span>
                </div>
              </div>
            </div>

            <div class="flex flex-col gap-2 ml-4">
              <router-link
                :to="`/orders/${order.id}`"
                class="btn btn-secondary text-sm whitespace-nowrap"
              >
                View Details
              </router-link>
              <button
                v-if="canSubmit(order)"
                @click="submitOrder(order)"
                :disabled="submittingOrder === order.id"
                class="btn btn-primary text-sm whitespace-nowrap"
              >
                {{ submittingOrder === order.id ? 'Submitting...' : 'Submit Order' }}
              </button>
              <button
                v-if="order.status === 'revision_requested'"
                @click="viewRevision(order)"
                class="btn btn-warning text-sm whitespace-nowrap"
              >
                View Revision
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination && pagination.total_pages > 1" class="flex items-center justify-between bg-white rounded-lg shadow-sm p-4">
      <div class="text-sm text-gray-700">
        Showing {{ pagination.start_index || 1 }} to {{ pagination.end_index || orders.length }} of {{ pagination.total_count || orders.length }} orders
      </div>
      <div class="flex gap-2">
        <button
          @click="loadOrders(pagination.current_page - 1)"
          :disabled="!pagination.has_previous || loading"
          class="btn btn-secondary text-sm"
        >
          Previous
        </button>
        <button
          @click="loadOrders(pagination.current_page + 1)"
          :disabled="!pagination.has_next || loading"
          class="btn btn-secondary text-sm"
        >
          Next
        </button>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ordersAPI from '@/api/orders'
import { debounce } from '@/utils/debounce'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const router = useRouter()
const { error: showError, success: showSuccess } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const orders = ref([])
const pagination = ref(null)
const submittingOrder = ref(null)

const filters = ref({
  status: '',
})

const sortBy = ref('deadline_asc')
const searchQuery = ref('')

const stats = computed(() => {
  const inProgress = orders.value.filter(o => o.status === 'in_progress').length
  const submitted = orders.value.filter(o => o.status === 'submitted' || o.status === 'under_editing').length
  const dueSoon = orders.value.filter(o => {
    const deadline = o.writer_deadline || o.client_deadline || o.deadline
    return deadline && isDueSoon(deadline)
  }).length
  
  return {
    in_progress: inProgress,
    submitted: submitted,
    due_soon: dueSoon,
    total_active: orders.value.filter(o => 
      ['in_progress', 'submitted', 'under_editing', 'revision_requested', 'on_hold'].includes(o.status)
    ).length,
  }
})

const loadOrders = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      assigned_writer: true, // Only get orders assigned to current writer
    }

    if (filters.value.status) {
      params.status = filters.value.status
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    // Handle sorting
    if (sortBy.value === 'deadline_asc') {
      params.ordering = 'writer_deadline,client_deadline,deadline'
    } else if (sortBy.value === 'deadline_desc') {
      params.ordering = '-writer_deadline,-client_deadline,-deadline'
    } else if (sortBy.value === 'created_desc') {
      params.ordering = '-created_at'
    } else if (sortBy.value === 'created_asc') {
      params.ordering = 'created_at'
    }

    const response = await ordersAPI.list(params)
    
    if (response.data.results) {
      orders.value = response.data.results
      pagination.value = {
        current_page: response.data.current_page || page,
        total_pages: response.data.total_pages || 1,
        total_count: response.data.count || response.data.results.length,
        has_next: response.data.next !== null,
        has_previous: response.data.previous !== null,
        start_index: ((response.data.current_page || page) - 1) * (response.data.page_size || 20) + 1,
        end_index: Math.min((response.data.current_page || page) * (response.data.page_size || 20), response.data.count || response.data.results.length),
      }
    } else {
      orders.value = Array.isArray(response.data) ? response.data : []
      pagination.value = null
    }
  } catch (error) {
    console.error('Failed to load orders:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load orders. Please try again.')
    showError(errorMsg)
    orders.value = []
  } finally {
    loading.value = false
  }
}

const submitOrder = async (order) => {
  const confirmed = await confirm.showDialog(
    `Are you sure you want to submit Order #${order.id}? This will mark it as completed and send it for editing.`,
    'Submit Order',
    {
      variant: 'default',
      icon: '📤',
      confirmText: 'Submit',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return

  submittingOrder.value = order.id
  try {
    await ordersAPI.executeAction(order.id, 'submit_order')
    showSuccess('Order submitted successfully!')
    await loadOrders(pagination.value?.current_page || 1)
  } catch (error) {
    console.error('Failed to submit order:', error)
    const errorMsg = getErrorMessage(error, 'Failed to submit order. Please try again.')
    showError(errorMsg)
  } finally {
    submittingOrder.value = null
  }
}

const viewRevision = (order) => {
  router.push(`/orders/${order.id}`)
}

const canSubmit = (order) => {
  return order.status === 'in_progress' || order.status === 'on_hold'
}

const formatStatus = (status) => {
  const statusMap = {
    'in_progress': 'In Progress',
    'submitted': 'Submitted',
    'under_editing': 'Under Editing',
    'revision_requested': 'Revision Requested',
    'on_hold': 'On Hold',
    'completed': 'Completed',
    'approved': 'Approved',
  }
  return statusMap[status] || status
}

const getStatusBadgeClass = (status) => {
  const classes = {
    'in_progress': 'bg-blue-100 text-blue-700',
    'submitted': 'bg-yellow-100 text-yellow-700',
    'under_editing': 'bg-purple-100 text-purple-700',
    'revision_requested': 'bg-orange-100 text-orange-700',
    'on_hold': 'bg-gray-100 text-gray-700',
    'completed': 'bg-green-100 text-green-700',
    'approved': 'bg-green-100 text-green-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline'
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  if (diffMs < 0) {
    return `Overdue (${date.toLocaleDateString()})`
  } else if (diffDays === 0) {
    return `Today (${diffHours}h remaining)`
  } else if (diffDays === 1) {
    return `Tomorrow (${diffHours}h remaining)`
  } else if (diffDays < 7) {
    return `${diffDays} days (${date.toLocaleDateString()})`
  } else {
    return date.toLocaleDateString()
  }
}

const getDeadlineClass = (deadline) => {
  if (!deadline) return 'text-gray-500'
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMs < 0) {
    return 'text-red-600 font-bold'
  } else if (diffDays <= 1) {
    return 'text-red-600'
  } else if (diffDays <= 3) {
    return 'text-orange-600'
  } else {
    return 'text-gray-900'
  }
}

const isDueSoon = (deadline) => {
  if (!deadline) return false
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  return diffDays <= 2 && diffMs > 0
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const debouncedSearch = debounce(() => {
  loadOrders(1)
}, 500)

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

