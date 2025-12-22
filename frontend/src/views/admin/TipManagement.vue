<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Tip Management & Earnings</h1>
        <p class="mt-2 text-gray-600">Track tip earnings, writer payouts, and platform profit</p>
      </div>
      <div class="flex gap-2">
        <select v-model="daysFilter" @change="loadDashboard" class="border rounded px-3 py-2">
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="365">Last year</option>
        </select>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="dashboardData && dashboardData.summary" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4">
      <div class="card p-5 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-2">Total Tips</p>
        <p class="text-2xl sm:text-3xl font-bold text-purple-900 break-words">{{ dashboardData.summary?.total_tips || 0 }}</p>
      </div>
      <div class="card p-5 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-2">Total Amount</p>
        <p class="text-2xl sm:text-3xl font-bold text-blue-900 break-words">${{ formatCurrency(dashboardData.summary?.total_tip_amount) }}</p>
      </div>
      <div class="card p-5 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-2">Writer Earnings</p>
        <p class="text-2xl sm:text-3xl font-bold text-green-900 break-words">${{ formatCurrency(dashboardData.summary?.total_writer_earnings) }}</p>
      </div>
      <div class="card p-5 bg-linear-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-2">Platform Profit</p>
        <p class="text-2xl sm:text-3xl font-bold text-indigo-900 break-words">${{ formatCurrency(dashboardData.summary?.total_platform_profit) }}</p>
      </div>
      <div class="card p-5 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-2">Avg Tip</p>
        <p class="text-2xl sm:text-3xl font-bold text-yellow-900 break-words">${{ formatCurrency(dashboardData.summary?.avg_tip_amount) }}</p>
      </div>
      <div class="card p-5 bg-linear-to-br from-pink-50 to-pink-100 border border-pink-200">
        <p class="text-sm font-medium text-pink-700 mb-2">Avg Writer %</p>
        <p class="text-2xl sm:text-3xl font-bold text-pink-900 break-words">{{ (dashboardData.summary?.avg_writer_percentage || 0).toFixed(1) }}%</p>
      </div>
    </div>

    <!-- Recent Summary -->
    <div v-if="dashboardData && dashboardData.recent_summary" class="card p-6 bg-linear-to-r from-purple-500 to-indigo-600 text-white">
      <h2 class="text-xl font-bold mb-4">Last {{ dashboardData.recent_summary.days }} Days Summary</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <p class="text-sm opacity-90 mb-2">Tips</p>
          <p class="text-2xl sm:text-3xl font-bold break-words">{{ dashboardData.recent_summary.total_tips }}</p>
        </div>
        <div>
          <p class="text-sm opacity-90 mb-2">Total Amount</p>
          <p class="text-2xl sm:text-3xl font-bold break-words">${{ formatCurrency(dashboardData.recent_summary.total_tip_amount) }}</p>
        </div>
        <div>
          <p class="text-sm opacity-90 mb-2">Writer Earnings</p>
          <p class="text-2xl sm:text-3xl font-bold break-words">${{ formatCurrency(dashboardData.recent_summary.total_writer_earnings) }}</p>
        </div>
        <div>
          <p class="text-sm opacity-90 mb-2">Platform Profit</p>
          <p class="text-2xl sm:text-3xl font-bold break-words">${{ formatCurrency(dashboardData.recent_summary.total_platform_profit) }}</p>
        </div>
      </div>
    </div>

    <!-- Payment Status Cards -->
    <div v-if="dashboardData && dashboardData.payment_status" class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="card p-5 bg-green-50 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-2">Completed</p>
        <p class="text-2xl font-bold text-green-900 break-words">{{ dashboardData.payment_status.completed || 0 }}</p>
      </div>
      <div class="card p-5 bg-yellow-50 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-2">Pending</p>
        <p class="text-2xl font-bold text-yellow-900 break-words">{{ dashboardData.payment_status.pending || 0 }}</p>
      </div>
      <div class="card p-5 bg-blue-50 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-2">Processing</p>
        <p class="text-2xl font-bold text-blue-900 break-words">{{ dashboardData.payment_status.processing || 0 }}</p>
      </div>
      <div class="card p-5 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-2">Failed</p>
        <p class="text-2xl font-bold text-red-900 break-words">{{ dashboardData.payment_status.failed || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
          <span v-if="tab.badge" class="ml-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">
            {{ tab.badge }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Tips List Tab -->
    <div v-if="activeTab === 'tips'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-6 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Tip Type</label>
            <select v-model="filters.tip_type" @change="loadTips" class="w-full border rounded px-3 py-2">
              <option value="">All Types</option>
              <option value="direct">Direct</option>
              <option value="order">Order-Based</option>
              <option value="class">Class-Based</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Payment Status</label>
            <select v-model="filters.payment_status" @change="loadTips" class="w-full border rounded px-3 py-2">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Writer ID</label>
            <input
              v-model.number="filters.writer_id"
              @input="debouncedSearch"
              type="number"
              placeholder="Writer ID"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Client ID</label>
            <input
              v-model.number="filters.client_id"
              @input="debouncedSearch"
              type="number"
              placeholder="Client ID"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Date From</label>
            <input
              v-model="filters.date_from"
              @change="loadTips"
              type="date"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <div v-if="tipsSummary" class="grid grid-cols-3 gap-4">
        <div class="card p-4 bg-blue-50">
          <p class="text-sm text-blue-700 mb-1">Total Tip Amount</p>
          <p class="text-2xl font-bold text-blue-900">${{ formatCurrency(tipsSummary.total_tip_amount) }}</p>
        </div>
        <div class="card p-4 bg-green-50">
          <p class="text-sm text-green-700 mb-1">Writer Earnings</p>
          <p class="text-2xl font-bold text-green-900">${{ formatCurrency(tipsSummary.total_writer_earnings) }}</p>
        </div>
        <div class="card p-4 bg-indigo-50">
          <p class="text-sm text-indigo-700 mb-1">Platform Profit</p>
          <p class="text-2xl font-bold text-indigo-900">${{ formatCurrency(tipsSummary.total_platform_profit) }}</p>
        </div>
      </div>

      <!-- Tips Table -->
      <div class="card overflow-hidden">
        <div v-if="loadingTips" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tip Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer Earned</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Platform Profit</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer %</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="tip in tips" :key="tip.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  #{{ tip.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span class="px-2 py-1 text-xs rounded" :class="getTypeBadgeClass(tip.tip_type)">
                    {{ tip.tip_type_display || tip.tip_type }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ tip.writer_username || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ tip.client_username || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  ${{ formatCurrency(tip.full_tip_amount || tip.tip_amount) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                  ${{ formatCurrency(tip.amount_received || tip.writer_earning) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                  {{ formatCurrency((tip.full_tip_amount || tip.tip_amount) - (tip.amount_received || tip.writer_earning)) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ tip.writer_percentage_display || (tip.writer_percentage ? tip.writer_percentage + '%' : 'N/A') }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span class="px-2 py-1 text-xs rounded" :class="getStatusBadgeClass(tip.payment_status)">
                    {{ tip.payment_status || 'pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(tip.sent_at) }}
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="tips.length === 0" class="text-center py-12 text-gray-500">
            No tips found
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="space-y-4">
      <div v-if="loadingAnalytics" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="analyticsData" class="space-y-6">
        <!-- Top Performers -->
        <div class="grid grid-cols-2 gap-6">
          <div class="card p-6">
            <h3 class="text-lg font-bold mb-4">Top Writers by Earnings</h3>
            <div class="space-y-3">
              <div
                v-for="(writer, index) in analyticsData.top_performers?.writers || []"
                :key="writer.writer__id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded"
              >
                <div class="flex items-center gap-3">
                  <span class="text-lg font-bold text-gray-400">#{{ index + 1 }}</span>
                  <div>
                    <p class="font-medium">{{ writer.writer__username }}</p>
                    <p class="text-sm text-gray-500">{{ writer.tip_count }} tips</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-bold text-green-600">${{ formatCurrency(writer.total_received) }}</p>
                  <p class="text-xs text-gray-500">Avg: ${{ formatCurrency(writer.avg_tip) }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card p-6">
            <h3 class="text-lg font-bold mb-4">Top Clients by Tips Sent</h3>
            <div class="space-y-3">
              <div
                v-for="(client, index) in analyticsData.top_performers?.clients || []"
                :key="client.client__id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded"
              >
                <div class="flex items-center gap-3">
                  <span class="text-lg font-bold text-gray-400">#{{ index + 1 }}</span>
                  <div>
                    <p class="font-medium">{{ client.client__username }}</p>
                    <p class="text-sm text-gray-500">{{ client.tip_count }} tips</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-bold text-blue-600">${{ formatCurrency(client.total_sent) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Breakdowns -->
        <div class="grid grid-cols-2 gap-6">
          <div class="card p-6">
            <h3 class="text-lg font-bold mb-4">Breakdown by Type</h3>
            <div class="space-y-3">
              <div
                v-for="item in analyticsData.breakdowns?.by_type || []"
                :key="item.tip_type"
                class="flex items-center justify-between p-3 bg-gray-50 rounded"
              >
                <div>
                  <p class="font-medium capitalize">{{ item.tip_type }}</p>
                  <p class="text-sm text-gray-500">{{ item.count }} tips</p>
                </div>
                <div class="text-right">
                  <p class="font-bold">${{ formatCurrency(item.total_amount) }}</p>
                  <p class="text-xs text-gray-500">
                    Writer: ${{ formatCurrency(item.writer_earnings) }} | 
                    Platform: ${{ formatCurrency(item.platform_profit) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card p-6">
            <h3 class="text-lg font-bold mb-4">Breakdown by Level</h3>
            <div class="space-y-3">
              <div
                v-for="item in analyticsData.breakdowns?.by_level || []"
                :key="item.writer_level__name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded"
              >
                <div>
                  <p class="font-medium">{{ item.writer_level__name }}</p>
                    <p class="text-sm text-gray-500">{{ item.tip_count }} tips ({{ (item.avg_percentage || 0).toFixed(1) }}% avg)</p>
                </div>
                <div class="text-right">
                  <p class="font-bold">${{ formatCurrency(item.total_tips) }}</p>
                  <p class="text-xs text-gray-500">
                    Writer: ${{ formatCurrency(item.total_writer_earnings) }} | 
                    Platform: ${{ formatCurrency(item.total_platform_profit) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Earnings Tab -->
    <div v-if="activeTab === 'earnings'" class="space-y-4">
      <div v-if="loadingEarnings" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="earningsData" class="space-y-6">
        <!-- Overall Earnings -->
        <div v-if="earningsData && earningsData.overall" class="card p-6 bg-linear-to-r from-indigo-500 to-purple-600 text-white">
          <h3 class="text-xl font-bold mb-4">Overall Earnings Summary</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p class="text-sm opacity-90 mb-2">Total Tips</p>
              <p class="text-xl sm:text-2xl font-bold break-words">{{ earningsData.overall?.total_tips || 0 }}</p>
            </div>
            <div>
              <p class="text-sm opacity-90 mb-2">Total Amount</p>
              <p class="text-xl sm:text-2xl font-bold break-words">${{ formatCurrency(earningsData.overall?.total_tip_amount) }}</p>
            </div>
            <div>
              <p class="text-sm opacity-90 mb-2">Writer Earnings</p>
              <p class="text-xl sm:text-2xl font-bold break-words">${{ formatCurrency(earningsData.overall?.total_writer_earnings) }}</p>
            </div>
            <div>
              <p class="text-sm opacity-90 mb-2">Platform Profit</p>
              <p class="text-xl sm:text-2xl font-bold break-words">${{ formatCurrency(earningsData.overall?.total_platform_profit) }}</p>
              <p class="text-xs sm:text-sm opacity-75 mt-1">({{ (earningsData.overall?.platform_profit_percentage || 0).toFixed(1) }}%)</p>
            </div>
          </div>
        </div>

        <!-- Earnings by Level -->
        <div class="card p-6">
          <h3 class="text-lg font-bold mb-4">Earnings by Writer Level</h3>
          <div class="space-y-3">
            <div
              v-for="item in earningsData.by_level || []"
              :key="item.writer_level__name"
              class="flex items-center justify-between p-4 bg-gray-50 rounded"
            >
              <div>
                <p class="font-medium text-lg">{{ item.writer_level__name }}</p>
                <p class="text-sm text-gray-500">{{ item.tip_count }} tips | Avg: {{ (item.avg_percentage || 0).toFixed(1) }}%</p>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold">${{ formatCurrency(item.total_tips) }}</p>
                <p class="text-sm text-gray-500">
                  Writer: ${{ formatCurrency(item.writer_earnings) }} | 
                  Platform: ${{ formatCurrency(item.platform_profit) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Earnings by Type -->
        <div class="card p-6">
          <h3 class="text-lg font-bold mb-4">Earnings by Tip Type</h3>
          <div class="grid grid-cols-3 gap-4">
            <div
              v-for="item in earningsData.by_type || []"
              :key="item.tip_type"
              class="p-4 bg-gray-50 rounded"
            >
              <p class="font-medium capitalize mb-2">{{ item.tip_type }}</p>
              <p class="text-sm text-gray-500 mb-2">{{ item.tip_count }} tips</p>
              <p class="text-lg font-bold mb-1">${{ formatCurrency(item.total_tips) }}</p>
              <p class="text-xs text-gray-500">
                Writer: ${{ formatCurrency(item.writer_earnings) }}
              </p>
              <p class="text-xs text-gray-500">
                Platform: ${{ formatCurrency(item.platform_profit) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { adminTipsAPI } from '@/api'

const dashboardData = ref(null)
const tips = ref([])
const tipsSummary = ref(null)
const analyticsData = ref(null)
const earningsData = ref(null)
const loadingDashboard = ref(false)
const loadingTips = ref(false)
const loadingAnalytics = ref(false)
const loadingEarnings = ref(false)
const activeTab = ref('tips')
const daysFilter = ref(30)

const tabs = [
  { id: 'tips', label: 'All Tips' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'earnings', label: 'Earnings' }
]

const filters = ref({
  tip_type: '',
  payment_status: '',
  writer_id: '',
  client_id: '',
  date_from: '',
  date_to: ''
})

let searchTimeout = null

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getTypeBadgeClass = (type) => {
  const classes = {
    direct: 'bg-purple-100 text-purple-800',
    order: 'bg-blue-100 text-blue-800',
    class: 'bg-green-100 text-green-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusBadgeClass = (status) => {
  const classes = {
    completed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    failed: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const response = await adminTipsAPI.getDashboard({ days: daysFilter.value })
    dashboardData.value = response.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadTips = async () => {
  loadingTips.value = true
  try {
    const params = {
      limit: 100,
      ...Object.fromEntries(
        Object.entries(filters.value).filter(([_, v]) => v !== '')
      )
    }
    const response = await adminTipsAPI.listTips(params)
    tips.value = response.data.results || []
    tipsSummary.value = response.data.summary || null
  } catch (error) {
    console.error('Error loading tips:', error)
  } finally {
    loadingTips.value = false
  }
}

const loadAnalytics = async () => {
  loadingAnalytics.value = true
  try {
    const response = await adminTipsAPI.getAnalytics({ days: 90 })
    analyticsData.value = response.data
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loadingAnalytics.value = false
  }
}

const loadEarnings = async () => {
  loadingEarnings.value = true
  try {
    const response = await adminTipsAPI.getEarnings()
    earningsData.value = response.data
  } catch (error) {
    console.error('Error loading earnings:', error)
  } finally {
    loadingEarnings.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadTips()
  }, 500)
}

const resetFilters = () => {
  filters.value = {
    tip_type: '',
    payment_status: '',
    writer_id: '',
    client_id: '',
    date_from: '',
    date_to: ''
  }
  loadTips()
}

watch(activeTab, (newTab) => {
  if (newTab === 'analytics' && !analyticsData.value) {
    loadAnalytics()
  } else if (newTab === 'earnings' && !earningsData.value) {
    loadEarnings()
  }
})

onMounted(() => {
  loadDashboard()
  loadTips()
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  min-width: 0; /* Prevents flex/grid items from overflowing */
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  font-weight: 500;
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #d1d5db;
}

/* Ensure numbers wrap properly and don't overflow */
.break-words {
  word-break: break-word;
  overflow-wrap: break-word;
}

/* Responsive font sizing for large numbers */
@media (max-width: 640px) {
  .card p.text-2xl,
  .card p.text-3xl {
    font-size: 1.5rem;
    line-height: 1.75rem;
  }
}

/* Better number formatting for very large values */
@media (min-width: 1024px) {
  .card p.text-2xl,
  .card p.text-3xl {
    font-size: clamp(1.5rem, 2.5vw, 2.25rem);
  }
}
</style>

