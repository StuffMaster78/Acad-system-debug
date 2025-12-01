<template>
  <div class="workload-management space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Workload Management</h1>
        <p class="mt-2 text-gray-600">Manage your current workload and capacity</p>
      </div>
      <button
        @click="fetchWorkload"
        class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        :disabled="loading"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Capacity Overview -->
    <div v-if="workloadData?.current_workload" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Active Tasks"
        :value="workloadData.current_workload.active_tasks_count || 0"
        icon="📝"
        bgColor="bg-blue-100"
        :subtitle="`of ${workloadData.current_workload.max_concurrent_tasks || 0} max`"
      />
      <StatsCard
        name="Available Slots"
        :value="workloadData.current_workload.available_slots || 0"
        icon="✅"
        bgColor="bg-green-100"
      />
      <StatsCard
        name="Capacity"
        :value="`${workloadData.current_workload.capacity_percentage || 0}%`"
        icon="📊"
        :bgColor="getCapacityColor(workloadData.current_workload.capacity_percentage)"
      />
      <StatsCard
        name="Status"
        :value="workloadData.current_workload.is_at_capacity ? 'At Capacity' : 'Available'"
        icon="⚡"
        :bgColor="workloadData.current_workload.is_at_capacity ? 'bg-red-100' : 'bg-green-100'"
      />
    </div>

    <!-- Capacity Gauge -->
    <div v-if="workloadData?.current_workload" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Capacity Overview</h2>
      <div class="flex items-center justify-center py-8">
        <div class="relative w-64 h-64">
          <svg class="transform -rotate-90 w-64 h-64">
            <circle
              cx="128"
              cy="128"
              r="100"
              stroke="#e5e7eb"
              stroke-width="20"
              fill="none"
            />
            <circle
              cx="128"
              cy="128"
              r="100"
              :stroke="getCapacityColor(workloadData.current_workload.capacity_percentage).replace('bg-', '#').replace('-100', '')"
              stroke-width="20"
              fill="none"
              :stroke-dasharray="628"
              :stroke-dashoffset="628 - (628 * workloadData.current_workload.capacity_percentage / 100)"
              class="transition-all duration-500"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="text-center">
              <div class="text-4xl font-bold text-gray-900">
                {{ Math.round(workloadData.current_workload.capacity_percentage) }}%
              </div>
              <div class="text-sm text-gray-500 mt-1">
                {{ workloadData.current_workload.active_tasks_count }} / {{ workloadData.current_workload.max_concurrent_tasks }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Deadline Analysis -->
    <div v-if="workloadData?.deadline_analysis" class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatsCard
        name="Urgent Tasks"
        :value="workloadData.deadline_analysis.urgent_tasks || 0"
        icon="🔴"
        bgColor="bg-red-100"
        subtitle="Due within 24 hours"
      />
      <StatsCard
        name="Overdue Tasks"
        :value="workloadData.deadline_analysis.overdue_tasks || 0"
        icon="⏰"
        bgColor="bg-orange-100"
        subtitle="Past deadline"
      />
      <StatsCard
        name="With Deadlines"
        :value="workloadData.deadline_analysis.total_with_deadlines || 0"
        icon="📅"
        bgColor="bg-blue-100"
      />
    </div>

    <!-- Time Estimates -->
    <div v-if="workloadData?.time_estimates" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Time Estimates</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-600">Estimated Hours Until All Deadlines</div>
          <div class="text-2xl font-bold text-gray-900">
            {{ formatNumber(workloadData.time_estimates.estimated_hours_until_all_deadlines) }}h
          </div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-600">Average Hours Per Task</div>
          <div class="text-2xl font-bold text-gray-900">
            {{ formatNumber(workloadData.time_estimates.average_hours_per_task) }}h
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="workloadData?.recommendations" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Recommendations</h2>
      <div class="space-y-3">
        <div
          v-if="workloadData.recommendations.should_focus_on_urgent"
          class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg"
        >
          <div class="flex items-center">
            <span class="text-yellow-600 text-xl mr-2">⚠️</span>
            <p class="text-yellow-800">
              You have urgent or overdue tasks. Focus on completing these first.
            </p>
          </div>
        </div>
        <div
          v-if="workloadData.recommendations.should_claim_more"
          class="p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <div class="flex items-center">
            <span class="text-green-600 text-xl mr-2">✅</span>
            <p class="text-green-800">
              You can take on {{ workloadData.recommendations.recommended_max_orders }} more task(s).
            </p>
          </div>
        </div>
        <div
          v-if="!workloadData.recommendations.should_claim_more && !workloadData.recommendations.should_focus_on_urgent"
          class="p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <div class="flex items-center">
            <span class="text-blue-600 text-xl mr-2">ℹ️</span>
            <p class="text-blue-800">
              Your workload is balanced. Continue managing your current tasks.
            </p>
          </div>
        </div>
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
import { ref, onMounted } from 'vue'
import editorDashboardAPI from '@/api/editor-dashboard'
import StatsCard from '@/components/dashboard/StatsCard.vue'

const loading = ref(false)
const error = ref(null)
const workloadData = ref(null)

const fetchWorkload = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await editorDashboardAPI.getWorkload()
    workloadData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load workload data'
    console.error('Error fetching workload:', err)
  } finally {
    loading.value = false
  }
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toFixed(2)
}

const getCapacityColor = (percentage) => {
  if (percentage >= 90) return 'bg-red-100'
  if (percentage >= 70) return 'bg-yellow-100'
  if (percentage >= 50) return 'bg-blue-100'
  return 'bg-green-100'
}

onMounted(() => {
  fetchWorkload()
})
</script>

<style scoped>
.workload-management {
  max-width: 1400px;
  margin: 0 auto;
}
</style>

