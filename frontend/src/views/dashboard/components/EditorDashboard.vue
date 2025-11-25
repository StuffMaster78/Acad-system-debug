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
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Recent Tasks</h2>
        <router-link to="/editor/tasks" class="text-primary-600 text-sm">View all</router-link>
      </div>
      <div v-if="editorDashboardData && editorDashboardData.tasks && editorDashboardData.tasks.active_tasks && editorDashboardData.tasks.active_tasks.length" class="divide-y divide-gray-200">
        <div v-for="task in editorDashboardData.tasks.active_tasks.slice(0, 5)" :key="task.id" class="py-3 flex items-center justify-between">
          <div class="flex-1">
            <div class="font-medium">Order #{{ task.order_id }} · {{ task.order_topic || 'N/A' }}</div>
            <div class="text-xs text-gray-500 mt-1">
              Status: <span class="capitalize">{{ task.status || 'pending' }}</span>
              <span v-if="task.deadline" class="ml-2">
                · Deadline: {{ new Date(task.deadline).toLocaleDateString() }}
              </span>
            </div>
          </div>
          <router-link :to="`/orders/${task.order_id}`" class="text-primary-600 text-sm hover:underline">View</router-link>
        </div>
      </div>
      <div v-else-if="editorDashboardData" class="text-center py-8 text-gray-500">
        <div class="text-sm">No active tasks</div>
        <router-link to="/editor/available-tasks" class="text-primary-600 text-sm mt-2 inline-block">Browse available tasks →</router-link>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-sm">Loading tasks...</div>
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

