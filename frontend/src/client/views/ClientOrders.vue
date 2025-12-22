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

    <!-- Overview Stats (client-friendly, similar feel to admin) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Active orders</p>
          <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{{ activeOrdersCount }}</p>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Pending, in progress, under editing, or on revision</p>
        </div>
        <div class="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
          <span class="text-blue-600 dark:text-blue-300 text-lg">📚</span>
        </div>
      </div>

      <div class="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Completed</p>
          <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{{ completedOrdersCount }}</p>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Completed, approved, or closed orders</p>
        </div>
        <div class="w-10 h-10 rounded-full bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center">
          <span class="text-emerald-600 dark:text-emerald-300 text-lg">✅</span>
        </div>
      </div>

      <div class="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">All orders</p>
          <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{{ totalCount || orders.length }}</p>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Across every status</p>
        </div>
        <div class="w-10 h-10 rounded-full bg-gray-50 dark:bg-gray-800/60 flex items-center justify-center">
          <span class="text-gray-600 dark:text-gray-300 text-lg">📊</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 md:p-5 shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="flex flex-col md:flex-row md:items-center gap-4 md:gap-6">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="selectedStatus = status.value"
            class="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs md:text-sm font-medium rounded-full border transition-all"
            :class="selectedStatus === status.value
              ? 'bg-primary-600 text-white border-primary-600 shadow-sm'
              : 'bg-gray-50 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            <span
              class="inline-flex items-center justify-center w-5 h-5 rounded-full text-[11px] font-semibold"
              :class="selectedStatus === status.value
                ? 'bg-white/15 border border-white/40'
                : 'bg-white dark:bg-gray-900/60 border border-gray-200/60 dark:border-gray-600/60 text-gray-600 dark:text-gray-300'"
            >
              {{ getStatusCount(status.value) }}
            </span>
            <span>{{ status.label }}</span>
          </button>
        </div>
        <div class="flex-1" />
        <div class="w-full md:w-64 relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by topic or #ID..."
            class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-900/40 dark:text-white placeholder:text-gray-400"
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

    <div v-else class="bg-white dark:bg-gray-900/40 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <div>
          <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Showing</p>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ filteredOrders.length }} of {{ totalCount || filteredOrders.length }} orders
          </p>
        </div>
        <div class="hidden md:flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span class="inline-flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span> Active
          </span>
          <span class="inline-flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-gray-400"></span> Completed / Closed
          </span>
        </div>
      </div>

      <div class="divide-y divide-gray-100 dark:divide-gray-800">
        <button
          v-for="order in filteredOrders"
          :key="order.id"
          type="button"
          class="w-full text-left px-4 md:px-5 py-4 md:py-5 hover:bg-gray-50 dark:hover:bg-gray-900/60 transition-colors"
          @click="$router.push(`/client/orders/${order.id}`)"
        >
          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3 md:gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1.5">
                <span class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  #{{ order.id }}
                </span>
                <h3 class="text-base md:text-lg font-semibold text-gray-900 dark:text-white truncate">
                  {{ order.topic || 'Untitled Order' }}
                </h3>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 text-xs md:text-sm text-gray-600 dark:text-gray-400">
                <div class="space-y-0.5">
                  <p class="text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Deadline</p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ formatDate(order.client_deadline) }}
                  </p>
                </div>
                <div class="space-y-0.5">
                  <p class="text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Created</p>
                  <p>{{ formatDate(order.created_at) }}</p>
                </div>
                <div class="space-y-0.5">
                  <p class="text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Pages</p>
                  <p>{{ order.number_of_pages || 0 }}</p>
                </div>
                <div class="space-y-0.5">
                  <p class="text-[11px] uppercase tracking-wide text-gray-400 dark:text-gray-500">Total</p>
                  <p class="font-semibold text-gray-900 dark:text-gray-100">
                    ${{ (order.total_price || 0).toFixed(2) }}
                  </p>
                </div>
              </div>
            </div>

            <div class="flex flex-col items-end gap-2 shrink-0">
              <EnhancedStatusBadge
                :status="order.status"
                :show-tooltip="true"
                size="sm"
              />
              <div class="hidden md:flex items-center gap-1.5 text-xs text-primary-600 dark:text-primary-400 font-medium">
                <span>View details</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </button>
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
import EnhancedStatusBadge from '@/components/common/EnhancedStatusBadge.vue'

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
  { label: 'Under Editing', value: 'under_editing' },
  { label: 'Revision Requested', value: 'revision_requested' },
  { label: 'Completed', value: 'completed' },
  { label: 'Approved', value: 'approved' },
  { label: 'On Hold', value: 'on_hold' },
  { label: 'Cancelled', value: 'cancelled' },
  { label: 'Disputed', value: 'disputed' },
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

const getStatusCount = (statusValue) => {
  if (statusValue === 'all') return orders.value.length
  return orders.value.filter(order => order.status === statusValue).length
}

const activeOrdersCount = computed(() => {
  const activeStatuses = [
    'pending',
    'in_progress',
    'under_editing',
    'revision_requested',
    'submitted',
    'on_hold',
    'disputed',
  ]
  return orders.value.filter(order => activeStatuses.includes(order.status)).length
})

const completedOrdersCount = computed(() => {
  const doneStatuses = ['completed', 'approved', 'closed', 'rated', 'reviewed']
  return orders.value.filter(order => doneStatuses.includes(order.status)).length
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

