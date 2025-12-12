<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">My Orders</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and manage all your orders</p>
      </div>
      <router-link
        to="/client/orders/create"
        class="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-md"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Place New Order</span>
      </router-link>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="selectedStatus = status.value"
            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
            :class="selectedStatus === status.value
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'"
          >
            {{ status.label }}
          </button>
        </div>
        <div class="flex-1"></div>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search orders..."
            class="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          />
          <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Orders List -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    </div>

    <div v-else-if="filteredOrders.length === 0" class="bg-white dark:bg-gray-800 rounded-lg p-12 text-center shadow-sm border border-gray-200 dark:border-gray-700">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">No orders found</h3>
      <p class="text-gray-500 mb-6">{{ searchQuery ? 'Try adjusting your search or filters' : 'Get started by placing your first order' }}</p>
      <router-link
        to="/client/orders/create"
        class="inline-flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Place New Order</span>
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="order in filteredOrders"
        :key="order.id"
        class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push(`/client/orders/${order.id}`)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ order.topic || 'Untitled Order' }}</h3>
              <span
                class="px-3 py-1 text-xs font-semibold rounded-full"
                :class="getStatusClass(order.status)"
              >
                {{ formatStatus(order.status) }}
              </span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <span class="font-medium">Pages:</span> {{ order.number_of_pages || 0 }}
              </div>
              <div>
                <span class="font-medium">Deadline:</span> {{ formatDate(order.client_deadline) }}
              </div>
              <div>
                <span class="font-medium">Created:</span> {{ formatDate(order.created_at) }}
              </div>
              <div>
                <span class="font-medium">Total:</span> ${{ (order.total_price || 0).toFixed(2) }}
              </div>
            </div>
          </div>
          <div class="ml-4">
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center space-x-2">
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        Previous
      </button>
      <span class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ordersAPI from '@/api/orders'

const loading = ref(true)
const orders = ref([])
const searchQuery = ref('')
const selectedStatus = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

const statusFilters = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'On Hold', value: 'on_hold' },
  { label: 'Revision', value: 'revision' },
  { label: 'Cancelled', value: 'cancelled' }
]

const filteredOrders = computed(() => {
  let filtered = orders.value

  // Filter by status
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(order => order.status === selectedStatus.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(order =>
      order.topic?.toLowerCase().includes(query) ||
      order.id?.toString().includes(query)
    )
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(totalCount.value / pageSize.value)
})

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: '-created_at'
    }
    if (selectedStatus.value !== 'all') {
      params.status = selectedStatus.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const response = await ordersAPI.list(params)
    const data = response.data
    orders.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
    totalCount.value = data?.count || orders.value.length
  } catch (err) {
    console.error('Failed to fetch orders:', err)
    orders.value = []
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
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

watch([selectedStatus, currentPage], () => {
  fetchOrders()
})

watch(searchQuery, () => {
  // Debounce search
  clearTimeout(searchQuery.timeout)
  searchQuery.timeout = setTimeout(() => {
    currentPage.value = 1
    fetchOrders()
  }, 500)
})

onMounted(() => {
  fetchOrders()
})
</script>

