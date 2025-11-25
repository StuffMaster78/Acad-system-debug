<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Performance Analytics</h1>
        <p class="mt-2 text-gray-600">Track writer performance, rankings, and analytics</p>
      </div>
      <button @click="refreshAnalytics" class="btn btn-secondary" :disabled="loading">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Overall Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Writers</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_writers || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Active Writers</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.active_writers || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Avg Rating</p>
        <p class="text-3xl font-bold text-purple-900">{{ formatRating(stats.avg_rating) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.total_orders || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search Writer</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by username..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Sort By</label>
          <select v-model="filters.ordering" @change="loadSnapshots" class="w-full border rounded px-3 py-2">
            <option value="-composite_score">Composite Score (High to Low)</option>
            <option value="-average_rating">Rating (High to Low)</option>
            <option value="-completed_orders">Orders Completed (High to Low)</option>
            <option value="-amount_paid">Earnings (High to Low)</option>
            <option value="composite_score">Composite Score (Low to High)</option>
            <option value="average_rating">Rating (Low to High)</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Period</label>
          <select v-model="filters.period" @change="loadSnapshots" class="w-full border rounded px-3 py-2">
            <option value="">All Periods</option>
            <option value="recent">Most Recent</option>
            <option value="last_week">Last Week</option>
            <option value="last_month">Last Month</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Writer Performance Table -->
    <div class="card overflow-hidden">
      <div v-if="snapshotsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Writer</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Composite Score</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rating</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Orders</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Completion Rate</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Earnings</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Period</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="(snapshot, index) in snapshots" :key="snapshot.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
              <span v-if="index < 3" class="text-yellow-500">#{{ index + 1 }}</span>
              <span v-else>#{{ index + 1 }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ snapshot.writer_name || snapshot.writer?.user?.username || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getScoreBadgeClass(snapshot.composite_score)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ formatScore(snapshot.composite_score) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <div class="flex items-center">
                <span class="mr-1">{{ formatRating(snapshot.average_rating) }}</span>
                <span class="text-yellow-400">★</span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ snapshot.completed_orders || 0 }} / {{ snapshot.total_orders || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ formatPercentage(snapshot.completion_rate) }}%
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              ${{ formatCurrency(snapshot.amount_paid) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatPeriod(snapshot.period_start, snapshot.period_end) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button @click="viewWriterDetails(snapshot)" class="text-blue-600 hover:text-blue-900">View</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!snapshotsLoading && snapshots.length === 0" class="text-center py-12 text-gray-500">
        No performance data found
      </div>
    </div>

    <!-- Writer Detail Modal -->
    <div v-if="showDetailModal && selectedSnapshot" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">Writer Performance Details</h3>
            <button @click="closeDetailModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h4 class="font-semibold mb-3">Performance Metrics</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Composite Score:</span>
                  <span class="font-medium">{{ formatScore(selectedSnapshot.composite_score) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Average Rating:</span>
                  <span class="font-medium">{{ formatRating(selectedSnapshot.average_rating) }} ⭐</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Completion Rate:</span>
                  <span class="font-medium">{{ formatPercentage(selectedSnapshot.completion_rate) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Lateness Rate:</span>
                  <span class="font-medium text-red-600">{{ formatPercentage(selectedSnapshot.lateness_rate) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Revision Rate:</span>
                  <span class="font-medium">{{ formatPercentage(selectedSnapshot.revision_rate) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Dispute Rate:</span>
                  <span class="font-medium text-red-600">{{ formatPercentage(selectedSnapshot.dispute_rate) }}%</span>
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-semibold mb-3">Order Statistics</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Total Orders:</span>
                  <span class="font-medium">{{ selectedSnapshot.total_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Completed:</span>
                  <span class="font-medium text-green-600">{{ selectedSnapshot.completed_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Late Orders:</span>
                  <span class="font-medium text-red-600">{{ selectedSnapshot.late_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Revised Orders:</span>
                  <span class="font-medium">{{ selectedSnapshot.revised_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Disputed Orders:</span>
                  <span class="font-medium text-red-600">{{ selectedSnapshot.disputed_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Total Pages:</span>
                  <span class="font-medium">{{ selectedSnapshot.total_pages || 0 }}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-semibold mb-3">Earnings</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Amount Paid:</span>
                  <span class="font-medium text-green-600">${{ formatCurrency(selectedSnapshot.amount_paid) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Bonuses:</span>
                  <span class="font-medium">${{ formatCurrency(selectedSnapshot.bonuses) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Tips:</span>
                  <span class="font-medium">${{ formatCurrency(selectedSnapshot.tips) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Client Revenue:</span>
                  <span class="font-medium">${{ formatCurrency(selectedSnapshot.client_revenue) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Profit Contribution:</span>
                  <span class="font-medium text-green-600">${{ formatCurrency(selectedSnapshot.profit_contribution) }}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-semibold mb-3">Additional Metrics</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Better Than:</span>
                  <span class="font-medium">{{ formatPercentage(selectedSnapshot.better_than_percent) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Avg Turnaround:</span>
                  <span class="font-medium">{{ formatHours(selectedSnapshot.average_turnaround_hours) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Preferred Orders:</span>
                  <span class="font-medium">{{ selectedSnapshot.preferred_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">HVO Orders:</span>
                  <span class="font-medium">{{ selectedSnapshot.hvo_orders || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Period:</span>
                  <span class="font-medium">{{ formatPeriod(selectedSnapshot.period_start, selectedSnapshot.period_end) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-4">
            <button @click="closeDetailModal" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { writerPerformanceAPI } from '@/api'

const loading = ref(false)
const stats = ref({})
const snapshots = ref([])
const snapshotsLoading = ref(false)

const showDetailModal = ref(false)
const selectedSnapshot = ref(null)

const filters = ref({
  search: '',
  ordering: '-composite_score',
  period: '',
})

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatRating = (value) => {
  if (!value) return '0.0'
  return parseFloat(value).toFixed(1)
}

const formatScore = (value) => {
  if (!value) return '0.0'
  return parseFloat(value).toFixed(1)
}

const formatPercentage = (value) => {
  if (!value) return '0.0'
  return (parseFloat(value) * 100).toFixed(1)
}

const formatPeriod = (start, end) => {
  if (!start || !end) return 'N/A'
  const startDate = new Date(start).toLocaleDateString()
  const endDate = new Date(end).toLocaleDateString()
  return `${startDate} - ${endDate}`
}

const formatHours = (hours) => {
  if (!hours) return 'N/A'
  const h = parseFloat(hours)
  if (h < 24) return `${h.toFixed(1)} hours`
  return `${(h / 24).toFixed(1)} days`
}

const getScoreBadgeClass = (score) => {
  const s = parseFloat(score) || 0
  if (s >= 80) return 'bg-green-100 text-green-800'
  if (s >= 60) return 'bg-blue-100 text-blue-800'
  if (s >= 40) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

const loadStats = async () => {
  try {
    // Calculate stats from snapshots
    const allSnapshots = snapshots.value
    const uniqueWriters = new Set(allSnapshots.map(s => s.writer))
    const totalOrders = allSnapshots.reduce((sum, s) => sum + (s.total_orders || 0), 0)
    const avgRating = allSnapshots.length > 0
      ? allSnapshots.reduce((sum, s) => sum + (parseFloat(s.average_rating) || 0), 0) / allSnapshots.length
      : 0

    stats.value = {
      total_writers: uniqueWriters.size,
      active_writers: uniqueWriters.size, // Could filter by recent activity
      avg_rating: avgRating,
      total_orders: totalOrders,
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadSnapshots = async () => {
  snapshotsLoading.value = true
  try {
    const params = {
      ordering: filters.value.ordering,
    }
    
    if (filters.value.period === 'recent') {
      // Get most recent snapshot per writer
      // This would need backend support or client-side filtering
    } else if (filters.value.period === 'last_week') {
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      params.period_end__gte = weekAgo.toISOString().split('T')[0]
    } else if (filters.value.period === 'last_month') {
      const monthAgo = new Date()
      monthAgo.setMonth(monthAgo.getMonth() - 1)
      params.period_end__gte = monthAgo.toISOString().split('T')[0]
    }
    
    // Note: The endpoint might need to be adjusted based on actual URL structure
    // Using writers endpoint as fallback if performance snapshots aren't directly accessible
    const response = await writerPerformanceAPI.listSnapshots(params).catch(async () => {
      // Fallback: try to get from writers endpoint
      const writersResponse = await writerPerformanceAPI.listWriters({ page_size: 100 })
      return { data: { results: [] } } // Return empty for now
    })
    
    snapshots.value = response.data.results || response.data || []
    
    // If we have snapshots, calculate stats
    if (snapshots.value.length > 0) {
      await loadStats()
    }
  } catch (error) {
    console.error('Failed to load snapshots:', error)
    // Try alternative approach - get writers and their performance
    try {
      const writersResponse = await writerPerformanceAPI.listWriters({ page_size: 100 })
      snapshots.value = writersResponse.data.results || writersResponse.data || []
    } catch (err) {
      console.error('Failed to load writers:', err)
    }
  } finally {
    snapshotsLoading.value = false
  }
}

let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadSnapshots()
  }, 500)
}

const resetFilters = () => {
  filters.value = {
    search: '',
    ordering: '-composite_score',
    period: '',
  }
  loadSnapshots()
}

const viewWriterDetails = (snapshot) => {
  selectedSnapshot.value = snapshot
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedSnapshot.value = null
}

const refreshAnalytics = async () => {
  loading.value = true
  try {
    await loadSnapshots()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSnapshots()
})
</script>

