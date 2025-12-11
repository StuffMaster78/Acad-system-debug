<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Workload Tracker</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track support staff workload, capacity, and assignments</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Tickets</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total_tickets || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Total Disputes</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.total_disputes || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.total_orders || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Active Agents</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.active_agents || 0 }}</p>
      </div>
    </div>

    <!-- Search -->
    <div class="card p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search by support staff name or email..."
        class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
        @input="debouncedSearch"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading workload data...</p>
    </div>

    <!-- Workload Table -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Support Staff</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Tickets Handled</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Disputes Handled</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Orders Managed</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Last Activity</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Workload</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="workloads.length === 0" class="text-center">
              <td colspan="6" class="px-6 py-12 text-gray-500 dark:text-gray-400">
                No workload data found
              </td>
            </tr>
            <tr
              v-for="workload in workloads"
              :key="workload.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ workload.support_staff_name || workload.support_staff || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ workload.tickets_handled || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ workload.disputes_handled || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ workload.orders_managed || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ formatDate(workload.last_activity) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="getWorkloadClass(workload)">
                  {{ getTotalWorkload(workload) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'
import supportManagementAPI from '@/api/support-management'

const { error: showError } = useToast()

const loading = ref(false)
const workloads = ref([])
const stats = ref({})
const searchQuery = ref('')

const debouncedSearch = debounce(() => {
  loadWorkloads()
}, 300)

const getTotalWorkload = (workload) => {
  return (workload.tickets_handled || 0) + (workload.disputes_handled || 0) + (workload.orders_managed || 0)
}

const getWorkloadClass = (workload) => {
  const total = getTotalWorkload(workload)
  if (total > 100) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
  if (total > 50) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
  return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
}

const formatDate = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

const loadWorkloads = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await supportManagementAPI.listWorkloadTrackers(params)
    workloads.value = response.data.results || response.data || []
    
    // Calculate stats
    stats.value = {
      total_tickets: workloads.value.reduce((sum, w) => sum + (w.tickets_handled || 0), 0),
      total_disputes: workloads.value.reduce((sum, w) => sum + (w.disputes_handled || 0), 0),
      total_orders: workloads.value.reduce((sum, w) => sum + (w.orders_managed || 0), 0),
      active_agents: workloads.value.filter(w => w.last_activity).length,
    }
  } catch (error) {
    showError('Failed to load workload data')
    console.error('Error loading workloads:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadWorkloads()
})
</script>

