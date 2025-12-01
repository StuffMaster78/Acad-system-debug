<template>
  <div class="support-analytics space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Support Analytics</h1>
        <p class="mt-2 text-gray-600">Comprehensive analytics for support operations</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedDays"
          @change="fetchAnalytics"
          class="px-4 py-2 border rounded-lg"
        >
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="180">Last 180 days</option>
        </select>
        <button
          @click="fetchAnalytics"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Performance Summary -->
    <div v-if="performanceData" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Tickets"
        :value="performanceData.total_tickets || 0"
        icon="🎫"
        bgColor="bg-blue-100"
      />
      <StatsCard
        name="Resolved"
        :value="performanceData.resolved_tickets || 0"
        icon="✅"
        bgColor="bg-green-100"
        :subtitle="`${performanceData.resolution_rate || 0}% resolution rate`"
      />
      <StatsCard
        name="Avg Response Time"
        :value="`${formatNumber(performanceData.average_response_time_hours || 0)}h`"
        icon="⏱️"
        bgColor="bg-purple-100"
      />
      <StatsCard
        name="Avg Resolution Time"
        :value="`${formatNumber(performanceData.average_resolution_time_hours || 0)}h`"
        icon="⏰"
        bgColor="bg-orange-100"
      />
    </div>

    <!-- Trends Chart -->
    <ChartWidget
      v-if="trendsSeries.length > 0"
      title="Ticket Trends"
      type="line"
      :series="trendsSeries"
      :options="trendsOptions"
      :loading="loading"
    />

    <!-- Performance Metrics -->
    <div v-if="performanceData" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Performance Metrics</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">First Response Time</span>
            <span class="font-bold text-gray-900">
              {{ formatNumber(performanceData.first_response_time_hours || 0) }}h
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">SLA Compliance Rate</span>
            <span class="font-bold text-green-600">
              {{ formatNumber(performanceData.sla_compliance_rate || 0) }}%
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Customer Satisfaction</span>
            <span class="font-bold text-blue-600">
              {{ formatNumber(performanceData.customer_satisfaction_score || 0) }}/5
            </span>
          </div>
        </div>
      </div>

      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Ticket Breakdown</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Open Tickets</span>
            <span class="font-bold text-yellow-600">{{ performanceData.open_tickets || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">In Progress</span>
            <span class="font-bold text-blue-600">{{ performanceData.in_progress_tickets || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Pending</span>
            <span class="font-bold text-orange-600">{{ performanceData.pending_tickets || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Closed</span>
            <span class="font-bold text-green-600">{{ performanceData.closed_tickets || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Trends Data -->
    <div v-if="trendsData?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Weekly Trends</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Week</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tickets</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resolved</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Response</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Resolution</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="trend in trendsData" :key="trend.week">
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ trend.week }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ trend.total_tickets || 0 }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ trend.resolved_tickets || 0 }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{{ formatNumber(trend.avg_response_time) }}h</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{{ formatNumber(trend.avg_resolution_time) }}h</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="card bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <span class="text-red-600 text-xl mr-2">⚠️</span>
        <p class="text-red-800">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import supportDashboardAPI from '@/api/support-dashboard'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'

const loading = ref(false)
const error = ref(null)
const selectedDays = ref(30)
const performanceData = ref(null)
const trendsData = ref([])

const fetchAnalytics = async () => {
  loading.value = true
  error.value = null
  try {
    const params = { days: selectedDays.value }
    const [performanceResponse, trendsResponse] = await Promise.all([
      supportDashboardAPI.getAnalyticsPerformance(params),
      supportDashboardAPI.getAnalyticsTrends(params)
    ])
    performanceData.value = performanceResponse.data
    trendsData.value = trendsResponse.data?.trends || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load analytics'
    console.error('Error fetching analytics:', err)
  } finally {
    loading.value = false
  }
}

const trendsSeries = computed(() => {
  if (!trendsData.value?.length) return []
  
  return [
    {
      name: 'Total Tickets',
      data: trendsData.value.map(t => t.total_tickets || 0)
    },
    {
      name: 'Resolved',
      data: trendsData.value.map(t => t.resolved_tickets || 0)
    }
  ]
})

const trendsOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: false }
  },
  xaxis: {
    categories: trendsData.value?.map(t => t.week) || []
  },
  stroke: {
    curve: 'smooth'
  },
  colors: ['#3b82f6', '#10b981']
}))

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toFixed(2)
}

onMounted(() => {
  fetchAnalytics()
})
</script>

<style scoped>
.support-analytics {
  max-width: 1400px;
  margin: 0 auto;
}
</style>

