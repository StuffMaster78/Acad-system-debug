<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Workload & Capacity</h1>
        <p class="mt-2 text-gray-600">Track your current workload vs capacity</p>
      </div>
      <button @click="loadWorkload" :disabled="loading" class="btn btn-secondary">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <div v-else-if="workloadData" class="space-y-6">
      <!-- Capacity Overview -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Capacity Overview</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Capacity Gauge -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Current Capacity</span>
              <span
                :class="[
                  'text-lg font-bold',
                  workloadData.capacity.is_at_capacity ? 'text-red-600' :
                  workloadData.capacity.is_near_capacity ? 'text-orange-600' :
                  'text-green-600'
                ]"
              >
                {{ workloadData.capacity.capacity_percentage }}%
              </span>
            </div>
            
            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-8 mb-4">
              <div
                :class="[
                  'h-8 rounded-full flex items-center justify-center text-sm font-medium text-white transition-all',
                  workloadData.capacity.is_at_capacity ? 'bg-red-600' :
                  workloadData.capacity.is_near_capacity ? 'bg-orange-600' :
                  'bg-green-600'
                ]"
                :style="{ width: `${Math.min(workloadData.capacity.capacity_percentage, 100)}%` }"
              >
                {{ workloadData.capacity.current_orders }} / {{ workloadData.capacity.max_orders }}
              </div>
            </div>
            
            <div class="grid grid-cols-3 gap-4 text-center">
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ workloadData.capacity.current_orders }}</p>
                <p class="text-xs text-gray-600">Current</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ workloadData.capacity.max_orders }}</p>
                <p class="text-xs text-gray-600">Max</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-green-600">{{ workloadData.capacity.available_slots }}</p>
                <p class="text-xs text-gray-600">Available</p>
              </div>
            </div>
          </div>

          <!-- Status Indicators -->
          <div class="space-y-4">
            <div
              :class="[
                'p-4 rounded-lg border-2',
                workloadData.capacity.is_at_capacity
                  ? 'bg-red-50 border-red-200'
                  : workloadData.capacity.is_near_capacity
                  ? 'bg-orange-50 border-orange-200'
                  : 'bg-green-50 border-green-200'
              ]"
            >
              <div class="flex items-center gap-2 mb-2">
                <span class="text-2xl">
                  {{ workloadData.capacity.is_at_capacity ? '⚠️' : workloadData.capacity.is_near_capacity ? '⚡' : '✅' }}
                </span>
                <span class="font-semibold text-gray-900">
                  {{ workloadData.capacity.is_at_capacity ? 'At Capacity' : workloadData.capacity.is_near_capacity ? 'Near Capacity' : 'Capacity Available' }}
                </span>
              </div>
              <p class="text-sm text-gray-600">
                {{ workloadData.capacity.is_at_capacity
                  ? 'You have reached your maximum order limit. Complete existing orders before taking new ones.'
                  : workloadData.capacity.is_near_capacity
                  ? 'You are approaching your capacity limit. Consider completing orders before taking more.'
                  : 'You have available capacity to take on more orders.' }}
              </p>
            </div>

            <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xl">📊</span>
                <span class="font-semibold text-gray-900">Writer Level</span>
              </div>
              <p class="text-sm text-gray-600">
                <span class="font-medium">{{ workloadData.writer_level.name }}</span>
                (Max: {{ workloadData.writer_level.max_orders }} orders)
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Breakdown -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Orders by Status</h2>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div
            v-for="(count, status) in workloadData.status_breakdown"
            :key="status"
            class="text-center p-4 border rounded-lg"
          >
            <p class="text-2xl font-bold text-gray-900">{{ count }}</p>
            <p class="text-xs text-gray-600 capitalize">{{ status.replace('_', ' ') }}</p>
          </div>
        </div>
      </div>

      <!-- Workload Estimate -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Workload Estimate</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-3xl font-bold text-blue-900">{{ workloadData.workload_estimate.total_pages }}</p>
            <p class="text-sm text-gray-600 mt-1">Total Pages</p>
          </div>
          <div class="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p class="text-3xl font-bold text-purple-900">{{ workloadData.workload_estimate.estimated_hours }}h</p>
            <p class="text-sm text-gray-600 mt-1">Estimated Hours</p>
          </div>
          <div class="text-center p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <p class="text-3xl font-bold text-indigo-900">{{ workloadData.workload_estimate.estimated_days }}d</p>
            <p class="text-sm text-gray-600 mt-1">Estimated Days</p>
            <p class="text-xs text-gray-500 mt-1">(8-hour workday)</p>
          </div>
        </div>
      </div>

      <!-- Upcoming Deadlines -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Upcoming Deadlines</h2>
        <div v-if="workloadData.upcoming_deadlines.length === 0" class="text-center py-8 text-gray-500">
          No upcoming deadlines
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="deadline in workloadData.upcoming_deadlines"
            :key="deadline.id"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <router-link
                  :to="`/orders/${deadline.id}`"
                  class="font-medium text-gray-900 hover:text-primary-600"
                >
                  Order #{{ deadline.id }}
                </router-link>
                <span class="text-sm text-gray-500">{{ deadline.topic }}</span>
              </div>
              <div class="text-sm text-gray-600 mt-1">
                {{ deadline.pages }} pages • {{ formatDeadline(deadline.deadline) }}
              </div>
            </div>
            <div class="text-right">
              <div
                :class="[
                  'text-sm font-semibold',
                  deadline.hours_remaining <= 24 ? 'text-red-600' :
                  deadline.hours_remaining <= 48 ? 'text-orange-600' :
                  'text-gray-600'
                ]"
              >
                {{ formatTimeRemaining(deadline.hours_remaining) }}
              </div>
              <div class="text-xs text-gray-500">remaining</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const { error: showError } = useToast()

const loading = ref(false)
const workloadData = ref(null)

const loadWorkload = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getWorkload()
    workloadData.value = response.data
  } catch (error) {
    console.error('Failed to load workload:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load workload data. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const formatDeadline = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatTimeRemaining = (hours) => {
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`
  } else if (hours < 24) {
    return `${Math.round(hours)}h`
  } else {
    const days = Math.floor(hours / 24)
    const remainingHours = Math.round(hours % 24)
    return `${days}d ${remainingHours}h`
  }
}

onMounted(() => {
  loadWorkload()
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

