<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Performance Analytics</h1>
        <p class="mt-2 text-gray-600">Track your editing performance and metrics</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="dateRange" @change="loadPerformance" class="border rounded px-3 py-2">
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="90">Last 90 Days</option>
          <option value="365">Last Year</option>
        </select>
        <button @click="loadPerformance" :disabled="loading" class="btn btn-secondary">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Performance Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Reviews</p>
            <p class="mt-2 text-3xl font-bold text-blue-600">
              {{ performanceData?.total_orders_reviewed || 0 }}
            </p>
            <p class="text-xs text-gray-500 mt-1">All time</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-lg">
            <span class="text-2xl">📝</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Avg Review Time</p>
            <p class="mt-2 text-3xl font-bold text-green-600">
              {{ formatReviewTime(performanceData?.average_review_time_hours) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">Hours per review</p>
          </div>
          <div class="p-3 bg-green-100 rounded-lg">
            <span class="text-2xl">⏱️</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Quality Score</p>
            <p class="mt-2 text-3xl font-bold text-yellow-600">
              {{ performanceData?.average_quality_score ? performanceData.average_quality_score.toFixed(1) : 'N/A' }}
            </p>
            <p class="text-xs text-gray-500 mt-1">Out of 10</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-lg">
            <span class="text-2xl">⭐</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Approval Rate</p>
            <p class="mt-2 text-3xl font-bold text-purple-600">
              {{ detailedStats?.approval_rate_percent ? detailedStats.approval_rate_percent.toFixed(1) : '0.0' }}%
            </p>
            <p class="text-xs text-gray-500 mt-1">Orders approved</p>
          </div>
          <div class="p-3 bg-purple-100 rounded-lg">
            <span class="text-2xl">✅</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Late Reviews</p>
            <p class="mt-2 text-3xl font-bold text-red-600">
              {{ performanceData?.late_reviews || 0 }}
            </p>
            <p class="text-xs text-gray-500 mt-1">Past deadline</p>
          </div>
          <div class="p-3 bg-red-100 rounded-lg">
            <span class="text-2xl">⚠️</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Revision Rate</p>
            <p class="mt-2 text-3xl font-bold text-orange-600">
              {{ detailedStats?.revision_rate_percent ? detailedStats.revision_rate_percent.toFixed(1) : '0.0' }}%
            </p>
            <p class="text-xs text-gray-500 mt-1">Requiring revision</p>
          </div>
          <div class="p-3 bg-orange-100 rounded-lg">
            <span class="text-2xl">🔄</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Completed (Period)</p>
            <p class="mt-2 text-3xl font-bold text-green-600">
              {{ detailedStats?.completed_tasks || 0 }}
            </p>
            <p class="text-xs text-gray-500 mt-1">In selected period</p>
          </div>
          <div class="p-3 bg-green-100 rounded-lg">
            <span class="text-2xl">📊</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Avg Completion</p>
            <p class="mt-2 text-3xl font-bold text-blue-600">
              {{ formatReviewTime(detailedStats?.average_completion_time_hours) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">Hours per task</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-lg">
            <span class="text-2xl">⏰</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Trends Chart -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h3 class="text-xl font-bold text-gray-900 mb-4">Performance Trends</h3>
      <apexchart
        v-if="performanceTrends && performanceTrends.length"
        type="line"
        height="300"
        :options="{
          chart: { 
            type: 'line', 
            toolbar: { show: false },
            zoom: { enabled: false }
          },
          xaxis: { 
            categories: performanceTrends.map(t => new Date(t.date).toLocaleDateString()),
            labels: { rotate: -45, style: { fontSize: '12px' } }
          },
          yaxis: { 
            title: { text: 'Number of Tasks' },
            min: 0
          },
          dataLabels: { enabled: false },
          stroke: { curve: 'smooth', width: 2 },
          colors: ['#3B82F6', '#10B981', '#F59E0B'],
          legend: {
            position: 'top',
            horizontalAlign: 'right'
          },
          grid: {
            borderColor: '#e5e7eb',
            strokeDashArray: 4
          }
        }"
        :series="[
          { name: 'Completed', data: performanceTrends.map(t => t.completed) },
          { name: 'In Review', data: performanceTrends.map(t => t.in_review) },
          { name: 'Pending', data: performanceTrends.map(t => t.pending) }
        ]"
      ></apexchart>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-4xl mb-2">📊</div>
        <p>{{ loading ? 'Loading performance data...' : 'No performance data available' }}</p>
      </div>
    </div>

    <!-- Task Statistics -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Task Breakdown by Status -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Tasks by Status</h3>
        <apexchart
          v-if="taskBreakdown"
          type="donut"
          height="300"
          :options="{
            chart: { toolbar: { show: false } },
            labels: ['Pending', 'In Review', 'Completed', 'Rejected', 'Unclaimed'],
            colors: ['#F59E0B', '#3B82F6', '#10B981', '#EF4444', '#6B7280'],
            legend: {
              position: 'bottom'
            }
          }"
          :series="[
            taskBreakdown.pending || 0,
            taskBreakdown.in_review || 0,
            taskBreakdown.completed || 0,
            taskBreakdown.rejected || 0,
            taskBreakdown.unclaimed || 0
          ]"
        ></apexchart>
        <div v-else class="text-center py-8 text-gray-500">
          <p>No task data available</p>
        </div>
      </div>

      <!-- Assignment Type Breakdown -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Tasks by Assignment Type</h3>
        <apexchart
          v-if="assignmentBreakdown"
          type="pie"
          height="300"
          :options="{
            chart: { toolbar: { show: false } },
            labels: ['Auto', 'Manual', 'Claimed'],
            colors: ['#3B82F6', '#10B981', '#F59E0B'],
            legend: {
              position: 'bottom'
            }
          }"
          :series="[
            assignmentBreakdown.auto || 0,
            assignmentBreakdown.manual || 0,
            assignmentBreakdown.claimed || 0
          ]"
        ></apexchart>
        <div v-else class="text-center py-8 text-gray-500">
          <p>No assignment data available</p>
        </div>
      </div>
    </div>

    <!-- Recent Reviews Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div class="p-6 border-b">
        <h3 class="text-xl font-bold text-gray-900">Recent Reviews</h3>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quality Score</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Submitted</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="review in recentReviews" :key="review.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ review.order_id || review.order?.id || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span class="font-semibold">{{ review.quality_score || 'N/A' }}</span>
              <span class="text-gray-500">/10</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span v-if="review.is_approved" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Approved</span>
              <span v-else-if="review.requires_revision" class="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">Revision</span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Pending</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(review.submitted_at) }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && recentReviews.length === 0" class="text-center py-12 text-gray-500">
        <p>No recent reviews found</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import editorPerformanceAPI from '@/api/editor-performance'

const loading = ref(false)
const dateRange = ref('30')
const performanceData = ref(null)
const detailedStats = ref(null)
const taskBreakdown = ref(null)
const assignmentBreakdown = ref(null)
const recentReviews = ref([])
const performanceTrends = ref([])

const loadPerformance = async () => {
  loading.value = true
  try {
    // Load performance metrics
    const performanceResponse = await editorPerformanceAPI.getPerformance()
    performanceData.value = performanceResponse.data.results?.[0] || performanceResponse.data[0] || performanceResponse.data || null
    
    // Load detailed stats
    const statsResponse = await editorPerformanceAPI.getDetailedStats({ days: dateRange.value })
    detailedStats.value = statsResponse.data || null
    
    // Load dashboard stats for additional data
    const dashboardResponse = await editorPerformanceAPI.getDashboardStats({ days: dateRange.value })
    const dashboardData = dashboardResponse.data || {}
    
    taskBreakdown.value = dashboardData.tasks?.breakdown_by_status || null
    assignmentBreakdown.value = dashboardData.tasks?.breakdown_by_assignment_type || null
    recentReviews.value = dashboardData.recent_reviews || []
    
    // Generate performance trends (simplified - you might want to enhance this with actual time-series data)
    if (dashboardData.tasks?.active_tasks) {
      performanceTrends.value = generateTrends(dashboardData, parseInt(dateRange.value))
    }
  } catch (error) {
    console.error('Failed to load performance data:', error)
  } finally {
    loading.value = false
  }
}

const generateTrends = (dashboardData, days) => {
  // Simplified trend generation - in production, you'd want actual time-series data
  const trends = []
  const now = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    trends.push({
      date: date.toISOString(),
      completed: Math.floor(Math.random() * 5) + 1, // Placeholder - replace with actual data
      in_review: Math.floor(Math.random() * 3) + 1,
      pending: Math.floor(Math.random() * 2) + 1,
    })
  }
  
  return trends
}

const formatReviewTime = (hours) => {
  if (!hours && hours !== 0) return 'N/A'
  if (hours < 1) {
    const minutes = Math.round(hours * 60)
    return `${minutes}m`
  }
  return `${hours.toFixed(1)}h`
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadPerformance()
})
</script>

