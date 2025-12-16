<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Assignment Analytics</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Comprehensive metrics and insights for order assignments</p>
      </div>
      <div class="flex items-center gap-2">
        <input
          v-model="dateRange.start"
          type="date"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
        />
        <span class="self-center text-gray-500 text-xs uppercase tracking-wide">to</span>
        <input
          v-model="dateRange.end"
          type="date"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
        />
        <NaiveButton
          type="primary"
          size="small"
          :loading="loading"
          class="ml-2"
          @click="loadAnalytics"
        >
          <template #icon>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </template>
          Refresh
        </NaiveButton>
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Assignments</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(dashboard?.success_rates?.total_assignments || 0) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">All time</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Success Rate</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ (dashboard?.success_rates?.success_rate || 0).toFixed(1) }}%</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {{ dashboard?.success_rates?.accepted || 0 }} accepted / {{ dashboard?.success_rates?.rejected || 0 }} rejected
        </p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Avg. Acceptance Time</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">
          {{ dashboard?.acceptance_times?.average_hours ? formatHours(dashboard.acceptance_times.average_hours) : 'N/A' }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Median: {{ dashboard?.acceptance_times?.median_hours ? formatHours(dashboard.acceptance_times.median_hours) : 'N/A' }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active Writers</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ dashboard?.writer_performance?.total_writers || 0 }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">With assignment history</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Success Rates Tab -->
    <div v-if="activeTab === 'success'" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Assignment Success Rates</h2>
        </div>
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center">
              <div class="text-4xl font-bold text-green-600 dark:text-green-400 mb-2">
                {{ (dashboard?.success_rates?.success_rate || 0).toFixed(1) }}%
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ dashboard?.success_rates?.accepted || 0 }} accepted
              </p>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold text-red-600 dark:text-red-400 mb-2">
                {{ (dashboard?.success_rates?.rejection_rate || 0).toFixed(1) }}%
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Rejection Rate</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ dashboard?.success_rates?.rejected || 0 }} rejected
              </p>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold text-yellow-600 dark:text-yellow-400 mb-2">
                {{ (dashboard?.success_rates?.pending_rate || 0).toFixed(1) }}%
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Pending</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ dashboard?.success_rates?.pending || 0 }} awaiting response
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Acceptance Times Tab -->
    <div v-if="activeTab === 'times'" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Acceptance Time Distribution</h2>
        </div>
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="p-6">
          <div class="mb-6">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Average: {{ dashboard?.acceptance_times?.average_hours ? formatHours(dashboard.acceptance_times.average_hours) : 'N/A' }}</span>
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Median: {{ dashboard?.acceptance_times?.median_hours ? formatHours(dashboard.acceptance_times.median_hours) : 'N/A' }}</span>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <p class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">Under 1 Hour</p>
              <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {{ dashboard?.acceptance_times?.distribution?.under_1_hour || 0 }}
              </p>
            </div>
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
              <p class="text-sm font-medium text-green-900 dark:text-green-100 mb-1">1-6 Hours</p>
              <p class="text-2xl font-bold text-green-600 dark:text-green-400">
                {{ dashboard?.acceptance_times?.distribution?.['1_to_6_hours'] || 0 }}
              </p>
            </div>
            <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
              <p class="text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-1">6-24 Hours</p>
              <p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {{ dashboard?.acceptance_times?.distribution?.['6_to_24_hours'] || 0 }}
              </p>
            </div>
            <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
              <p class="text-sm font-medium text-red-900 dark:text-red-100 mb-1">Over 24 Hours</p>
              <p class="text-2xl font-bold text-red-600 dark:text-red-400">
                {{ dashboard?.acceptance_times?.distribution?.over_24_hours || 0 }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rejection Reasons Tab -->
    <div v-if="activeTab === 'rejections'" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Top Rejection Reasons</h2>
        </div>
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="p-4">
          <NaiveDataTable
            :items="rejectionReasons"
            :columns="rejectionColumns"
            :loading="loading"
            :striped="true"
            :bordered="false"
            :pagination="false"
            empty-message="No rejection data available"
          >
            <template #reason="{ row }">
              <div class="text-sm text-gray-900 dark:text-gray-100">
                {{ row.reason || 'No reason provided' }}
              </div>
            </template>
            <template #percentage="{ row }">
              <div class="flex items-center">
                <div class="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                  <div
                    class="bg-red-600 h-2 rounded-full"
                    :style="{ width: `${row.percentage}%` }"
                  ></div>
                </div>
                <span class="text-sm text-gray-900 dark:text-gray-100">
                  {{ row.percentage }}%
                </span>
              </div>
            </template>
          </NaiveDataTable>
        </div>
      </div>
    </div>

    <!-- Writer Performance Tab -->
    <div v-if="activeTab === 'writers'" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Writer Performance Metrics</h2>
        </div>
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="p-4">
          <NaiveDataTable
            :items="writerPerformance"
            :columns="writerColumns"
            :loading="loading"
            :striped="true"
            :bordered="false"
            :pagination="true"
            :page-size="10"
            empty-message="No writer performance data available"
          >
            <template #writer="{ row }">
              <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ row.writer_username }}
              </div>
            </template>
            <template #acceptance_rate="{ row }">
              <div class="flex items-center">
                <div class="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                  <div
                    class="bg-green-600 h-2 rounded-full"
                    :style="{ width: `${row.acceptance_rate}%` }"
                  ></div>
                </div>
                <span class="text-sm text-gray-900 dark:text-gray-100">
                  {{ row.acceptance_rate }}%
                </span>
              </div>
            </template>
          </NaiveDataTable>
        </div>
      </div>
    </div>

    <!-- Trends Tab -->
    <div v-if="activeTab === 'trends'" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Assignment Trends</h2>
            <select
              v-model="trendGroupBy"
              @change="loadTrends"
              class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
            >
              <option value="day">By Day</option>
              <option value="week">By Week</option>
              <option value="month">By Month</option>
            </select>
          </div>
        </div>
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="!trends.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
          <p class="text-sm font-medium">No trend data available</p>
        </div>
        <div v-else class="p-6">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Period</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Accepted</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Rejected</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Success Rate</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="trend in trends" :key="trend.period" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ formatDate(trend.period) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ trend.total }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400">
                    {{ trend.accepted }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600 dark:text-red-400">
                    {{ trend.rejected }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                        <div
                          class="bg-green-600 h-2 rounded-full"
                          :style="{ width: `${trend.success_rate}%` }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-900 dark:text-gray-100">{{ trend.success_rate }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import assignmentAnalyticsAPI from '@/api/assignment-analytics'
import { useToast } from '@/composables/useToast'
import NaiveButton from '@/components/naive/NaiveButton.vue'
import NaiveDataTable from '@/components/naive/NaiveDataTable.vue'

const loading = ref(false)
const activeTab = ref('success')
const dashboard = ref(null)
const rejectionReasons = ref([])
const writerPerformance = ref([])
const trends = ref([])
const trendGroupBy = ref('day')

const dateRange = ref({
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0],
})

const tabs = [
  { id: 'success', label: 'Success Rates' },
  { id: 'times', label: 'Acceptance Times' },
  { id: 'rejections', label: 'Rejection Reasons' },
  { id: 'writers', label: 'Writer Performance' },
  { id: 'trends', label: 'Trends' },
]

const loadAnalytics = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
    }
    
    // Load dashboard data
    const dashboardRes = await assignmentAnalyticsAPI.getDashboard(params)
    dashboard.value = dashboardRes.data
    
    // Load rejection reasons
    const rejectionRes = await assignmentAnalyticsAPI.getRejectionReasons(params)
    rejectionReasons.value = rejectionRes.data || []
    
    // Load writer performance
    const writerRes = await assignmentAnalyticsAPI.getWriterPerformance(params)
    writerPerformance.value = writerRes.data?.writers || []
    
    // Load trends
    await loadTrends()
  } catch (error) {
    console.error('Failed to load analytics:', error)
    showError('Failed to load analytics: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadTrends = async () => {
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
      group_by: trendGroupBy.value,
    }
    
    const trendsRes = await assignmentAnalyticsAPI.getTrends(params)
    trends.value = trendsRes.data || []
  } catch (error) {
    console.error('Failed to load trends:', error)
    showError('Failed to load trends: ' + (error.response?.data?.detail || error.message))
  }
}

const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat().format(num)
}

const formatHours = (hours) => {
  if (!hours) return 'N/A'
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`
  } else if (hours < 24) {
    return `${hours.toFixed(1)}h`
  } else {
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    return `${days}d ${remainingHours.toFixed(0)}h`
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

// Naive DataTable column configs
const rejectionColumns = computed(() => [
  {
    key: 'reason',
    label: 'Reason',
    ellipsis: false,
  },
  {
    key: 'count',
    label: 'Count',
    width: 100,
    align: 'right',
  },
  {
    key: 'percentage',
    label: 'Percentage',
    width: 200,
  },
])

const writerColumns = computed(() => [
  {
    key: 'writer',
    label: 'Writer',
    ellipsis: false,
  },
  {
    key: 'total_assignments',
    label: 'Total Assignments',
    width: 140,
    align: 'right',
  },
  {
    key: 'accepted',
    label: 'Accepted',
    width: 110,
    align: 'right',
  },
  {
    key: 'rejected',
    label: 'Rejected',
    width: 110,
    align: 'right',
  },
  {
    key: 'acceptance_rate',
    label: 'Acceptance Rate',
    width: 200,
  },
  {
    key: 'average_response_hours',
    label: 'Avg. Response Time',
    width: 180,
    render: (row) => formatHours(row.average_response_hours),
  },
])

onMounted(() => {
  loadAnalytics()
})
</script>

