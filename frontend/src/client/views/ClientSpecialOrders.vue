<template>
  <div class="space-y-6">
    <!-- Breadcrumbs -->
    <nav class="flex items-center gap-2 text-xs sm:text-sm overflow-x-auto whitespace-nowrap" aria-label="Breadcrumb">
      <router-link to="/dashboard" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Dashboard
      </router-link>
      <span class="text-gray-400 dark:text-gray-600">/</span>
      <span class="text-gray-900 dark:text-gray-100 font-medium truncate max-w-[60vw] sm:max-w-none">Special Orders</span>
    </nav>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">My Special Orders</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and track your custom orders</p>
      </div>
      <router-link
        to="/orders/special/new"
        class="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-md"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Request Special Order</span>
      </router-link>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Total</p>
        <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20 p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-yellow-700 dark:text-yellow-400">Awaiting Approval</p>
        <p class="mt-2 text-2xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.awaiting_approval || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-blue-700 dark:text-blue-400">In Progress</p>
        <p class="mt-2 text-2xl font-bold text-blue-900 dark:text-blue-100">{{ stats.in_progress || 0 }}</p>
      </div>
      <div class="rounded-2xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-green-700 dark:text-green-400">Completed</p>
        <p class="mt-2 text-2xl font-bold text-green-900 dark:text-green-100">{{ stats.completed || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="selectedStatus = status.value"
            class="px-3.5 py-1.5 text-sm font-medium rounded-full border transition-all"
            :class="selectedStatus === status.value
              ? 'bg-primary-600 text-white border-primary-600'
              : 'bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            {{ status.label }}
          </button>
        </div>
        <div class="flex-1" />
        <div class="w-full md:w-64 relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by ID or details..."
            class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-900/40 dark:text-white"
          />
          <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading special orders...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredOrders.length === 0" class="bg-white dark:bg-gray-800 rounded-lg p-12 text-center shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="text-6xl mb-4">⭐</div>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Special Orders Yet</h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">Get started by requesting a custom order tailored to your needs</p>
      <router-link
        to="/orders/special/new"
        class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Request Special Order
      </router-link>
    </div>

    <!-- Orders List -->
    <div v-else class="space-y-4">
      <div
        v-for="order in filteredOrders"
        :key="order.id"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow cursor-pointer"
        @click="viewOrder(order.id)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Special Order #{{ order.id }}
              </h3>
              <span
                class="px-3 py-1 text-xs font-semibold rounded-full"
                :class="getStatusClass(order.status)"
              >
                {{ getStatusLabel(order.status) }}
              </span>
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'"
              >
                {{ order.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
              </span>
            </div>
            <p v-if="order.inquiry_details" class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
              {{ order.inquiry_details }}
            </p>
            <div class="flex flex-wrap items-center gap-4 text-sm">
              <div class="flex items-center gap-1">
                <span class="text-gray-500 dark:text-gray-400">💰</span>
                <span class="font-medium text-gray-900 dark:text-white">
                  ${{ formatCurrency(order.total_cost || 0) }}
                </span>
                <span v-if="order.budget" class="text-gray-500 dark:text-gray-400">
                  (Budget: ${{ formatCurrency(order.budget) }})
                </span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-gray-500 dark:text-gray-400">⏱️</span>
                <span class="text-gray-700 dark:text-gray-300">{{ order.duration_days || 0 }} days</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-gray-500 dark:text-gray-400">📅</span>
                <span class="text-gray-700 dark:text-gray-300">{{ formatDate(order.created_at) }}</span>
              </div>
              <div v-if="order.writer" class="flex items-center gap-1">
                <span class="text-gray-500 dark:text-gray-400">✍️</span>
                <span class="text-gray-700 dark:text-gray-300">Writer: {{ order.writer_username || order.writer?.username || 'Assigned' }}</span>
              </div>
            </div>
          </div>
          <div class="ml-4">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.total_pages > 1" class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div class="text-sm text-gray-700 dark:text-gray-300">
        Showing {{ pagination.start_index }} to {{ pagination.end_index }} of {{ pagination.total_count }} results
      </div>
      <div class="flex gap-2">
        <button
          @click="goToPage(pagination.current_page - 1)"
          :disabled="pagination.current_page === 1"
          class="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Previous
        </button>
        <span class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300">
          Page {{ pagination.current_page }} of {{ pagination.total_pages }}
        </span>
        <button
          @click="goToPage(pagination.current_page + 1)"
          :disabled="pagination.current_page >= pagination.total_pages"
          class="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import specialOrdersAPI from '@/api/special-orders'

const router = useRouter()

const loading = ref(true)
const orders = ref([])
const stats = ref({
  total: 0,
  awaiting_approval: 0,
  in_progress: 0,
  completed: 0
})
const selectedStatus = ref('')
const searchQuery = ref('')
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  start_index: 1,
  end_index: 1
})

const statusFilters = [
  { value: '', label: 'All' },
  { value: 'inquiry', label: 'Inquiry' },
  { value: 'awaiting_approval', label: 'Awaiting Approval' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' }
]

const filteredOrders = computed(() => {
  let filtered = orders.value

  if (selectedStatus.value) {
    filtered = filtered.filter(order => order.status === selectedStatus.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(order => {
      return (
        order.id.toString().includes(query) ||
        (order.inquiry_details && order.inquiry_details.toLowerCase().includes(query))
      )
    })
  }

  return filtered
})

const loadOrders = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: 20
    }

    if (selectedStatus.value) {
      params.status = selectedStatus.value
    }

    const response = await specialOrdersAPI.list(params)
    const results = response.data.results || response.data || []
    
    orders.value = results

    // Calculate stats
    stats.value = {
      total: response.data.count || results.length,
      awaiting_approval: results.filter(o => o.status === 'awaiting_approval').length,
      in_progress: results.filter(o => o.status === 'in_progress').length,
      completed: results.filter(o => o.status === 'completed').length
    }

    // Set pagination
    if (response.data) {
      pagination.value = {
        current_page: response.data.current_page || page,
        total_pages: response.data.total_pages || 1,
        total_count: response.data.count || results.length,
        start_index: ((response.data.current_page || page) - 1) * 20 + 1,
        end_index: Math.min((response.data.current_page || page) * 20, response.data.count || results.length)
      }
    }
  } catch (error) {
    console.error('Failed to load special orders:', error)
    orders.value = []
  } finally {
    loading.value = false
  }
}

const debouncedSearch = useDebounceFn(() => {
  loadOrders(1)
}, 300)

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    loadOrders(page)
  }
}

const viewOrder = (id) => {
  router.push(`/client/special-orders/${id}`)
}

const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'awaiting_approval': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'inquiry': 'Inquiry',
    'awaiting_approval': 'Awaiting Approval',
    'in_progress': 'In Progress',
    'completed': 'Completed'
  }
  return labels[status] || status
}

const formatCurrency = (value) => {
  return parseFloat(value || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

watch(selectedStatus, () => {
  loadOrders(1)
})

watch(searchQuery, () => {
  debouncedSearch()
})

onMounted(() => {
  loadOrders()
})
</script>
