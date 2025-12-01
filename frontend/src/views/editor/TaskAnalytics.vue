<template>
  <div class="task-analytics space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Task Analytics</h1>
        <p class="mt-2 text-gray-600">Comprehensive analytics for your editing tasks</p>
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

    <!-- Summary Cards -->
    <div v-if="analyticsData?.summary" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Tasks"
        :value="analyticsData.summary.total_tasks || 0"
        icon="📝"
        bgColor="bg-blue-100"
      />
      <StatsCard
        name="Completed Tasks"
        :value="analyticsData.summary.completed_tasks || 0"
        icon="✅"
        bgColor="bg-green-100"
        :subtitle="`${analyticsData.summary.completion_rate || 0}% completion rate`"
      />
      <StatsCard
        name="Pending Tasks"
        :value="analyticsData.summary.pending_tasks || 0"
        icon="⏳"
        bgColor="bg-yellow-100"
      />
      <StatsCard
        name="In Review"
        :value="analyticsData.summary.in_review_tasks || 0"
        icon="👀"
        bgColor="bg-purple-100"
      />
    </div>

    <!-- Performance Metrics -->
    <div v-if="analyticsData?.performance" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Avg Review Time"
        :value="`${formatNumber(analyticsData.performance.average_review_time_hours || 0)}h`"
        icon="⏱️"
        bgColor="bg-indigo-100"
      />
      <StatsCard
        name="Quality Score"
        :value="formatNumber(analyticsData.performance.average_quality_score || 0)"
        icon="⭐"
        bgColor="bg-orange-100"
        subtitle="Out of 5.0"
      />
      <StatsCard
        name="Approvals"
        :value="analyticsData.performance.approvals_count || 0"
        icon="✅"
        bgColor="bg-green-100"
      />
      <StatsCard
        name="Revisions Requested"
        :value="analyticsData.performance.revisions_requested_count || 0"
        icon="🔄"
        bgColor="bg-red-100"
      />
    </div>

    <!-- Task Trends Chart -->
    <ChartWidget
      v-if="taskTrendsSeries.length > 0"
      title="Task Completion Trends"
      type="line"
      :series="taskTrendsSeries"
      :options="taskTrendsOptions"
      :loading="loading"
    />

    <!-- Task Breakdown by Status -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Task Breakdown by Status</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>
      <div v-else-if="analyticsData?.status_breakdown" class="space-y-3">
        <div
          v-for="(count, status) in analyticsData.status_breakdown"
          :key="status"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div>
            <div class="font-medium text-gray-900 capitalize">{{ status.replace(/_/g, ' ') }}</div>
            <div class="text-sm text-gray-500">{{ count }} tasks</div>
          </div>
          <div class="text-lg font-bold text-primary-600">
            {{ count }}
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div v-if="analyticsData?.recent_assignments?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Recent Assignments</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned At</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="assignment in analyticsData.recent_assignments" :key="assignment.id">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="font-medium text-gray-900">#{{ assignment.order_id || 'N/A' }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ assignment.order_topic || 'N/A' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span
                  :class="getStatusColor(assignment.review_status)"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ assignment.review_status || 'N/A' }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(assignment.assigned_at) }}
              </td>
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
import editorDashboardAPI from '@/api/editor-dashboard'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'

const loading = ref(false)
const error = ref(null)
const selectedDays = ref(30)
const analyticsData = ref(null)

const fetchAnalytics = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await editorDashboardAPI.getTaskAnalytics(selectedDays.value)
    analyticsData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load task analytics'
    console.error('Error fetching task analytics:', err)
  } finally {
    loading.value = false
  }
}

const taskTrendsSeries = computed(() => {
  if (!analyticsData.value?.task_trends?.length) return []
  
  return [{
    name: 'Tasks Completed',
    data: analyticsData.value.task_trends.map(t => t.count || 0)
  }]
})

const taskTrendsOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: false }
  },
  xaxis: {
    categories: analyticsData.value?.task_trends?.map(t => t.date) || []
  },
  stroke: {
    curve: 'smooth'
  },
  colors: ['#3b82f6']
}))

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getStatusColor = (status) => {
  const colors = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'in_review': 'bg-blue-100 text-blue-800',
    'completed': 'bg-green-100 text-green-800',
    'unclaimed': 'bg-gray-100 text-gray-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  fetchAnalytics()
})
</script>

<style scoped>
.task-analytics {
  max-width: 1400px;
  margin: 0 auto;
}
</style>

