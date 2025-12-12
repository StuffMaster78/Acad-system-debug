<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <p class="text-red-700 dark:text-red-300">{{ error }}</p>
    </div>

    <!-- Order Content -->
    <div v-else-if="order">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center space-x-3 mb-2">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ order.topic || 'Untitled Order' }}</h1>
            <span
              class="px-3 py-1 text-sm font-semibold rounded-full"
              :class="getStatusClass(order.status)"
            >
              {{ formatStatus(order.status) }}
            </span>
          </div>
          <p class="text-gray-600 dark:text-gray-400">Order #{{ order.id }}</p>
        </div>
        <router-link
          to="/client/orders"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          ← Back to Orders
        </router-link>
      </div>

      <!-- Order Details Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Order Information -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Order Information</h2>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Pages</dt>
              <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ order.number_of_pages || 0 }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Deadline</dt>
              <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ formatDate(order.client_deadline) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Created</dt>
              <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ formatDate(order.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Price</dt>
              <dd class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">${{ (order.total_price || 0).toFixed(2) }}</dd>
            </div>
          </dl>
        </div>

        <!-- Payment Status -->
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Payment Status</h2>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Status</span>
              <span
                class="px-3 py-1 text-xs font-semibold rounded-full"
                :class="order.payment_status === 'paid' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'"
              >
                {{ order.payment_status === 'paid' ? 'Paid' : 'Pending' }}
              </span>
            </div>
            <div v-if="order.payment_status !== 'paid'" class="pt-4">
              <button
                @click="handlePayment"
                class="w-full px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                Pay Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Instructions</h2>
        <div class="prose dark:prose-invert max-w-none">
          <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ order.order_instructions || 'No instructions provided' }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Actions</h2>
        <div class="flex flex-wrap gap-3">
          <router-link
            :to="`/client/messages?order=${order.id}`"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Message Writer
          </router-link>
          <button
            v-if="order.status === 'completed'"
            @click="requestRevision"
            class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            Request Revision
          </button>
          <button
            v-if="['pending', 'in_progress'].includes(order.status)"
            @click="cancelOrder"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Cancel Order
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ordersAPI from '@/api/orders'
import { useConfirmDialog } from '@/composables/useConfirmDialog'

const route = useRoute()
const router = useRouter()
const { confirm } = useConfirmDialog()

const loading = ref(true)
const error = ref('')
const order = ref(null)

const fetchOrder = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await ordersAPI.get(route.params.id)
    order.value = response.data
  } catch (err) {
    console.error('Failed to fetch order:', err)
    error.value = err.response?.data?.detail || 'Failed to load order'
  } finally {
    loading.value = false
  }
}

const formatStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'on_hold': 'On Hold',
    'revision': 'Revision',
    'disputed': 'Disputed'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'on_hold': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    'revision': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'disputed': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const handlePayment = () => {
  router.push(`/client/payments?order=${order.value.id}`)
}

const requestRevision = async () => {
  const confirmed = await confirm({
    title: 'Request Revision',
    message: 'Are you sure you want to request a revision for this order?',
    confirmText: 'Request Revision',
    cancelText: 'Cancel'
  })

  if (!confirmed) return

  try {
    await ordersAPI.requestRevision(order.value.id)
    await fetchOrder()
  } catch (err) {
    console.error('Failed to request revision:', err)
    alert(err.response?.data?.detail || 'Failed to request revision')
  }
}

const cancelOrder = async () => {
  const confirmed = await confirm({
    title: 'Cancel Order',
    message: 'Are you sure you want to cancel this order? This action cannot be undone.',
    confirmText: 'Cancel Order',
    cancelText: 'Keep Order',
    variant: 'danger'
  })

  if (!confirmed) return

  try {
    await ordersAPI.cancel(order.value.id)
    await fetchOrder()
  } catch (err) {
    console.error('Failed to cancel order:', err)
    alert(err.response?.data?.detail || 'Failed to cancel order')
  }
}

onMounted(() => {
  fetchOrder()
})
</script>

