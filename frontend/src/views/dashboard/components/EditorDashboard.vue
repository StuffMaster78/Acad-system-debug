<template>
  <div class="space-y-6">
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <QuickActionCard
        to="/editor/tasks"
        icon="📋"
        title="My Tasks"
        description="Review assigned orders"
      />
      <QuickActionCard
        to="/editor/available-tasks"
        icon="🎯"
        title="Available Tasks"
        description="Claim new tasks"
      />
      <QuickActionCard
        to="/editor/performance"
        icon="📊"
        title="Performance"
        description="View your stats"
      />
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Active Tasks"
        :value="editorStats.activeTasks"
        icon="📋"
      />
      <StatsCard
        name="Completed Reviews"
        :value="editorStats.completedReviews"
        icon="✅"
      />
      <StatsCard
        name="Pending Tasks"
        :value="editorStats.pendingTasks"
        icon="⏳"
      />
      <StatsCard
        name="Average Score"
        :value="editorStats.averageScore"
        icon="⭐"
      />
    </div>

    <!-- Recent Tasks -->
    <div class="card bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
      <div class="bg-linear-to-r from-purple-50 to-indigo-50 border-b-2 border-purple-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Recent Tasks
          </h2>
          <router-link to="/editor/tasks" class="text-purple-600 hover:text-purple-800 text-sm font-semibold flex items-center gap-1 transition-colors">
            View all
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
      <div v-if="!editorDashboardData" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
      <div v-else-if="editorDashboardData && editorDashboardData.tasks && editorDashboardData.tasks.active_tasks && editorDashboardData.tasks.active_tasks.length" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200" style="min-width: 1000px;">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Order ID</th>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Topic</th>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Status</th>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Deadline</th>
              <th class="px-6 py-3 text-center text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="task in editorDashboardData.tasks.active_tasks.slice(0, 5)" :key="task.id" class="hover:bg-purple-50/50 transition-all duration-150">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-linear-to-br from-purple-400 to-indigo-500 flex items-center justify-center text-white text-xs font-bold">
                    #
                  </div>
                  <span class="text-sm font-semibold text-gray-900">#{{ task.order_id }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 max-w-md truncate" :title="task.order_topic">
                  {{ task.order_topic || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold shadow-sm capitalize"
                      :class="getTaskStatusClass(task.status)">
                  {{ task.status || 'pending' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="task.deadline" class="text-sm text-gray-900">{{ formatDate(task.deadline) }}</div>
                <div v-else class="text-sm text-gray-400">N/A</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <router-link 
                  :to="`/orders/${task.order_id}`" 
                  class="inline-flex items-center px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-xs font-semibold shadow-sm"
                >
                  View Task
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-12 text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="mt-2 text-sm font-medium">No active tasks</p>
        <router-link to="/editor/available-tasks" class="mt-2 inline-block text-purple-600 hover:text-purple-800 text-sm font-medium">
          Browse available tasks →
        </router-link>
      </div>
    </div>

    <!-- Performance Summary -->
    <div v-if="editorDashboardData && editorDashboardData.performance" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Performance Summary</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Total Orders Reviewed</div>
              <div class="text-2xl font-bold text-blue-600">{{ editorDashboardData.performance.total_orders_reviewed || 0 }}</div>
            </div>
            <span class="text-3xl">📝</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Average Review Time</div>
              <div class="text-2xl font-bold text-green-600">{{ editorDashboardData.performance.average_review_time_hours ? `${editorDashboardData.performance.average_review_time_hours.toFixed(1)}h` : 'N/A' }}</div>
            </div>
            <span class="text-3xl">⏱️</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Average Quality Score</div>
              <div class="text-2xl font-bold text-yellow-600">{{ editorDashboardData.performance.average_quality_score ? editorDashboardData.performance.average_quality_score.toFixed(1) : 'N/A' }}</div>
            </div>
            <span class="text-3xl">⭐</span>
          </div>
        </div>
      </div>
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Review Statistics</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Revisions Requested</div>
              <div class="text-2xl font-bold text-orange-600">{{ editorDashboardData.performance.revisions_requested_count || 0 }}</div>
            </div>
            <span class="text-3xl">📝</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Approvals</div>
              <div class="text-2xl font-bold text-green-600">{{ editorDashboardData.performance.approvals_count || 0 }}</div>
            </div>
            <span class="text-3xl">✅</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-red-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Late Reviews</div>
              <div class="text-2xl font-bold text-red-600">{{ editorDashboardData.performance.late_reviews || 0 }}</div>
            </div>
            <span class="text-3xl">⚠️</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Charts -->
    <div v-if="editorDashboardData && editorDashboardData.performance" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Review Trends Chart -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Review Trends (Last 30 Days)</h2>
        <div v-if="loading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
        <apexchart
          v-else-if="reviewTrendsSeries.length > 0"
          type="line"
          height="300"
          :options="reviewTrendsOptions"
          :series="reviewTrendsSeries"
        ></apexchart>
        <div v-else class="h-64 flex items-center justify-center text-gray-500">
          No review data available
        </div>
      </div>

      <!-- Review Breakdown Chart -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Review Breakdown</h2>
        <div v-if="loading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
        <apexchart
          v-else-if="reviewBreakdownSeries.length > 0"
          type="donut"
          height="300"
          :options="reviewBreakdownOptions"
          :series="reviewBreakdownSeries"
        ></apexchart>
        <div v-else class="h-64 flex items-center justify-center text-gray-500">
          No breakdown data available
        </div>
      </div>
    </div>

    <!-- Task Status Distribution -->
    <div v-if="editorDashboardData && editorDashboardData.tasks" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Task Status Distribution</h2>
      <div v-if="loading" class="flex items-center justify-center h-64">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
      <apexchart
        v-else-if="taskStatusSeries.length > 0"
        type="bar"
        height="300"
        :options="taskStatusOptions"
        :series="taskStatusSeries"
      ></apexchart>
      <div v-else class="h-64 flex items-center justify-center text-gray-500">
        No task data available
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import QuickActionCard from '@/components/dashboard/QuickActionCard.vue'

const props = defineProps({
  editorDashboardData: Object,
  loading: Boolean
})

// Chart Series
const reviewTrendsSeries = computed(() => {
  // Mock data structure - adjust based on actual API response
  if (!props.editorDashboardData?.performance) return []
  
  // If API provides trend data, use it; otherwise create mock from available data
  const performance = props.editorDashboardData.performance
  return [
    {
      name: 'Reviews Completed',
      data: [performance.approvals_count || 0, performance.revisions_requested_count || 0, performance.total_orders_reviewed || 0]
    }
  ]
})

const reviewBreakdownSeries = computed(() => {
  if (!props.editorDashboardData?.performance) return []
  
  const perf = props.editorDashboardData.performance
  return [
    perf.approvals_count || 0,
    perf.revisions_requested_count || 0,
    perf.late_reviews || 0
  ]
})

const taskStatusSeries = computed(() => {
  if (!props.editorDashboardData?.tasks?.breakdown_by_status) return []
  
  const breakdown = props.editorDashboardData.tasks.breakdown_by_status
  return [
    {
      name: 'Tasks',
      data: [
        breakdown.pending || 0,
        breakdown.in_review || 0,
        breakdown.completed || 0
      ]
    }
  ]
})

// Chart Options
const reviewTrendsOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: false }
  },
  xaxis: {
    categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4']
  },
  yaxis: {
    title: { text: 'Count' }
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  colors: ['#8b5cf6'],
  markers: {
    size: 4
  }
}))

const reviewBreakdownOptions = computed(() => ({
  chart: {
    type: 'donut',
    toolbar: { show: false }
  },
  labels: ['Approvals', 'Revisions Requested', 'Late Reviews'],
  colors: ['#10b981', '#f59e0b', '#ef4444'],
  legend: {
    position: 'bottom'
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => `${Math.round(val)}%`
  }
}))

const taskStatusOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false }
  },
  xaxis: {
    categories: ['Pending', 'In Review', 'Completed']
  },
  yaxis: {
    title: { text: 'Number of Tasks' }
  },
  colors: ['#8b5cf6'],
  dataLabels: {
    enabled: true
  }
}))

const editorStats = computed(() => {
  if (!props.editorDashboardData) {
    return {
      activeTasks: '0',
      completedReviews: '0',
      pendingTasks: '0',
      averageScore: '0.0'
    }
  }
  
  const data = props.editorDashboardData
  const summary = data.summary || {}
  const performance = data.performance || {}
  const tasks = data.tasks || {}
  const taskBreakdown = tasks.breakdown_by_status || {}
  
  return {
    activeTasks: summary.active_tasks_count || (taskBreakdown.pending || 0) + (taskBreakdown.in_review || 0) || 0,
    completedReviews: summary.recent_completions || taskBreakdown.completed || performance.total_orders_reviewed || 0,
    pendingTasks: summary.pending_tasks_count || taskBreakdown.pending || 0,
    averageScore: (performance.average_quality_score || 0).toFixed(1)
  }
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getTaskStatusClass = (status) => {
  const statusMap = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'in_review': 'bg-blue-100 text-blue-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800',
  }
  return statusMap[status?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>

