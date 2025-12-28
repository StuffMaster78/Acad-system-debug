<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Class Orders Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage class bundle orders and purchases</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="dashboardData" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 border border-blue-200 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Bundles</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ dashboardData.summary?.total_bundles || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900 dark:to-yellow-800 border border-yellow-200 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending Deposit</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ dashboardData.summary?.pending_deposit || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 border border-green-200 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ dashboardData.summary?.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 border border-purple-200 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Completed</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ dashboardData.summary?.completed || 0 }}</p>
      </div>
    </div>

    <!-- Quick Action Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 mb-4">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Bundles List -->
    <div class="card bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      <div v-if="loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading class bundles...</p>
      </div>
      
      <div v-else-if="bundles.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
        <p>No class bundles found.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Client</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Bundle Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Price</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="bundle in bundles" :key="bundle.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">#{{ bundle.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ bundle.client?.username || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ bundle.bundle_name || bundle.name || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 text-xs rounded-full" :class="getStatusClass(bundle.status)">
                  {{ getStatusLabel(bundle.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                ${{ formatCurrency(bundle.total_price || bundle.price || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(bundle.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="viewClassOrder(bundle)"
                  class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 hover:underline"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import classManagementAPI from '@/api/class-management'
import adminClassBundlesAPI from '@/api/admin-class-bundles'

const router = useRouter()

const loading = ref(false)
const dashboardData = ref(null)
const bundles = ref([])
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: 'All Bundles' },
  { key: 'pending_deposit', label: 'Pending Deposit' },
  { key: 'active', label: 'Active' },
  { key: 'completed', label: 'Completed' },
]

const loadDashboard = async () => {
  try {
    const res = await adminClassBundlesAPI.getDashboard()
    dashboardData.value = res.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  }
}

const loadBundles = async () => {
  loading.value = true
  try {
    const params = {}
    
    if (activeTab.value === 'pending_deposit') {
      const res = await adminClassBundlesAPI.getDepositPending()
      bundles.value = res.data.results || res.data || []
      return
    } else if (activeTab.value === 'active') {
      params.status = 'active'
    } else if (activeTab.value === 'completed') {
      params.status = 'completed'
    }
    
    const res = await classManagementAPI.listBundles(params)
    bundles.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading class bundles:', error)
  } finally {
    loading.value = false
  }
}

const getStatusClass = (status) => {
  const classes = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'active': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': 'Pending',
    'active': 'Active',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
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

const viewClassOrder = (bundle) => {
  router.push({ name: 'AdminClassOrderDetail', params: { id: bundle.id } })
}

watch(activeTab, () => {
  loadBundles()
})

onMounted(() => {
  loadDashboard()
  loadBundles()
})
</script>

