<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Approval Queue</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Review and approve special orders and express class inquiries</p>
      </div>
      <button
        @click="loadAllQueues"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm font-medium flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-6 bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border border-yellow-200 dark:border-yellow-800">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Special Orders</p>
            <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.specialOrders || 0 }}</p>
          </div>
          <div class="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
            <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
      </div>
      <div class="card p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Express Classes</p>
            <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.expressClasses || 0 }}</p>
          </div>
          <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
      </div>
      <div class="card p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Pending</p>
            <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total || 0 }}</p>
          </div>
          <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <svg class="w-8 h-8 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        </div>
      </div>
      <div class="card p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Reviewed Today</p>
            <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.reviewedToday || 0 }}</p>
          </div>
          <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
          <span
            v-if="tab.count !== undefined"
            :class="[
              'ml-2 py-0.5 px-2 rounded-full text-xs font-medium',
              activeTab === tab.id
                ? 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
            ]"
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Content -->
    <div v-if="loading && items.length === 0" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading approval queue...</p>
      </div>
    </div>

    <div v-else-if="items.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No items pending approval</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">All items have been reviewed.</p>
    </div>

    <div v-else class="space-y-4">
      <!-- Special Orders -->
      <div v-for="item in items" :key="`${item.type}-${item.id}`" class="card p-6 hover:shadow-lg transition-shadow">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <span
                :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  item.type === 'special_order'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                ]"
              >
                {{ item.type === 'special_order' ? 'Special Order' : 'Express Class' }}
              </span>
              <span
                :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  getStatusClass(item.status)
                ]"
              >
                {{ getStatusLabel(item.status) }}
              </span>
            </div>
            
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ item.type === 'special_order' ? `Order #${item.id}` : `Class #${item.id}` }}
            </h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Client</p>
                <p class="font-medium text-gray-900 dark:text-white">{{ item.client_username || item.client_email || 'N/A' }}</p>
              </div>
              <div v-if="item.type === 'special_order'">
                <p class="text-sm text-gray-500 dark:text-gray-400">Order Type</p>
                <p class="font-medium text-gray-900 dark:text-white capitalize">{{ item.order_type || 'N/A' }}</p>
              </div>
              <div v-if="item.type === 'express_class'">
                <p class="text-sm text-gray-500 dark:text-gray-400">Course</p>
                <p class="font-medium text-gray-900 dark:text-white">{{ item.course || 'N/A' }}</p>
              </div>
              <div v-if="item.budget">
                <p class="text-sm text-gray-500 dark:text-gray-400">Budget</p>
                <p class="font-medium text-gray-900 dark:text-white">${{ parseFloat(item.budget).toFixed(2) }}</p>
              </div>
            </div>

            <div v-if="item.inquiry_details || item.instructions" class="mb-4">
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Details</p>
              <p class="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                {{ item.inquiry_details || item.instructions || 'No details provided' }}
              </p>
            </div>

            <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ formatDate(item.created_at) }}
            </div>
          </div>

          <div class="flex flex-col gap-2 ml-4">
            <button
              @click="viewItem(item)"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              View Details
            </button>
            <button
              v-if="item.type === 'special_order'"
              @click="approveSpecialOrder(item.id)"
              :disabled="processing"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors text-sm font-medium"
            >
              Approve
            </button>
            <button
              v-if="item.type === 'express_class'"
              @click="reviewExpressClass(item.id)"
              :disabled="processing"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors text-sm font-medium"
            >
              Review Scope
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div
      v-if="selectedItem"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="selectedItem = null"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ selectedItem.type === 'special_order' ? 'Special Order' : 'Express Class' }} Details
            </h2>
            <button
              @click="selectedItem = null"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <!-- Detail content would go here -->
          <div class="space-y-4">
            <p class="text-gray-600 dark:text-gray-400">Full details for {{ selectedItem.type === 'special_order' ? 'Order' : 'Class' }} #{{ selectedItem.id }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import specialOrdersAPI from '@/api/special-orders'
import expressClassesAPI from '@/api/express-classes'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { showToast } = useToast()

const loading = ref(false)
const processing = ref(false)
const items = ref([])
const selectedItem = ref(null)
const activeTab = ref('all')

const tabs = computed(() => [
  { id: 'all', label: 'All', count: items.value.length },
  { id: 'special_orders', label: 'Special Orders', count: items.value.filter(i => i.type === 'special_order').length },
  { id: 'express_classes', label: 'Express Classes', count: items.value.filter(i => i.type === 'express_class').length },
])

const stats = computed(() => ({
  specialOrders: items.value.filter(i => i.type === 'special_order').length,
  expressClasses: items.value.filter(i => i.type === 'express_class').length,
  total: items.value.length,
  reviewedToday: 0, // TODO: Implement
}))

const filteredItems = computed(() => {
  if (activeTab.value === 'all') return items.value
  if (activeTab.value === 'special_orders') return items.value.filter(i => i.type === 'special_order')
  if (activeTab.value === 'express_classes') return items.value.filter(i => i.type === 'express_class')
  return items.value
})

const loadAllQueues = async () => {
  loading.value = true
  try {
    const [specialOrdersRes, expressClassesRes] = await Promise.all([
      specialOrdersAPI.getApprovalQueue().catch(() => ({ data: { results: [] } })),
      expressClassesAPI.getApprovalQueue().catch(() => ({ data: { results: [] } })),
    ])

    const specialOrders = (specialOrdersRes.data?.results || specialOrdersRes.data || []).map(item => ({
      ...item,
      type: 'special_order',
    }))

    const expressClasses = (expressClassesRes.data?.results || expressClassesRes.data || []).map(item => ({
      ...item,
      type: 'express_class',
    }))

    items.value = [...specialOrders, ...expressClasses].sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    )
  } catch (error) {
    console.error('Error loading approval queue:', error)
    showToast('Failed to load approval queue', 'error')
  } finally {
    loading.value = false
  }
}

const viewItem = (item) => {
  if (item.type === 'special_order') {
    router.push(`/admin/special-orders/${item.id}`)
  } else {
    router.push(`/admin/express-classes/${item.id}`)
  }
}

const approveSpecialOrder = async (id) => {
  processing.value = true
  try {
    await specialOrdersAPI.approve(id)
    showToast('Special order approved successfully', 'success')
    await loadAllQueues()
  } catch (error) {
    console.error('Error approving special order:', error)
    showToast('Failed to approve special order', 'error')
  } finally {
    processing.value = false
  }
}

const reviewExpressClass = (id) => {
  router.push(`/admin/express-classes/${id}`)
}

const getStatusClass = (status) => {
  const classes = {
    inquiry: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    awaiting_approval: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    scope_review: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const getStatusLabel = (status) => {
  const labels = {
    inquiry: 'Inquiry',
    awaiting_approval: 'Awaiting Approval',
    scope_review: 'Scope Review',
  }
  return labels[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadAllQueues()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
