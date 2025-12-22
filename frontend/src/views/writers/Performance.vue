<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Performance Analytics</h1>
        <p class="mt-2 text-gray-600">Track your performance metrics and trends</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="selectedDays" @change="loadPerformance" class="border rounded px-3 py-2">
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="365">Last year</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-4xl mb-2">⏳</div>
      <p class="text-gray-500">Loading performance data...</p>
    </div>

    <!-- Performance Metrics Cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Completion Rate</p>
            <p class="mt-2 text-3xl font-bold text-blue-600">
              {{ performanceData?.completion_rate ? performanceData.completion_rate.toFixed(1) : '0.0' }}%
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ performanceData?.completed_orders || 0 }}/{{ performanceData?.total_orders || 0 }} orders
            </p>
          </div>
          <div class="p-3 bg-blue-100 rounded-lg">
            <span class="text-2xl">✅</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">On-Time Rate</p>
            <p class="mt-2 text-3xl font-bold text-green-600">
              {{ performanceData?.on_time_rate ? performanceData.on_time_rate.toFixed(1) : '0.0' }}%
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ performanceData?.on_time_orders || 0 }} on time
            </p>
          </div>
          <div class="p-3 bg-green-100 rounded-lg">
            <span class="text-2xl">⏰</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Average Rating</p>
            <p class="mt-2 text-3xl font-bold text-yellow-600">
              {{ performanceData?.avg_rating ? performanceData.avg_rating.toFixed(1) : 'N/A' }}
            </p>
            <p class="text-xs text-gray-500 mt-1">Client satisfaction</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-lg">
            <span class="text-2xl">⭐</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Revision Rate</p>
            <p class="mt-2 text-3xl font-bold text-orange-600">
              {{ performanceData?.revision_rate ? performanceData.revision_rate.toFixed(1) : '0.0' }}%
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ performanceData?.revised_orders || 0 }} revised
            </p>
          </div>
          <div class="p-3 bg-orange-100 rounded-lg">
            <span class="text-2xl">📝</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Trends Chart -->
    <div v-if="!loading" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Performance Trends</h2>
      <apexchart
        v-if="performanceData && performanceData.performance_trend && performanceData.performance_trend.length"
        type="line"
        height="350"
        :options="{
          chart: { 
            type: 'line', 
            toolbar: { show: false },
            zoom: { enabled: false }
          },
          xaxis: { 
            categories: performanceData.performance_trend.map(t => new Date(t.date).toLocaleDateString()),
            labels: { rotate: -45, style: { fontSize: '12px' } }
          },
          yaxis: { 
            title: { text: 'Number of Orders' },
            min: 0
          },
          dataLabels: { enabled: false },
          stroke: { curve: 'smooth', width: 2 },
          colors: ['#3B82F6', '#10B981'],
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
          { name: 'Completed Orders', data: performanceData.performance_trend.map(t => t.completed) },
          { name: 'Total Orders', data: performanceData.performance_trend.map(t => t.total) }
        ]"
      ></apexchart>
      <div v-else class="text-center py-12 text-gray-500">
        <div class="text-4xl mb-2">📊</div>
        <p>{{ performanceData ? 'No performance data available for this period' : 'Loading performance data...' }}</p>
      </div>
    </div>

    <!-- Detailed Metrics -->
    <div v-if="!loading" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Order Statistics -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Order Statistics</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Total Orders</span>
            <span class="text-lg font-bold text-gray-900">{{ performanceData?.total_orders || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Completed Orders</span>
            <span class="text-lg font-bold text-green-600">{{ performanceData?.completed_orders || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">On-Time Orders</span>
            <span class="text-lg font-bold text-blue-600">{{ performanceData?.on_time_orders || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Late Orders</span>
            <span class="text-lg font-bold text-yellow-600">{{ performanceData?.late_orders || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Revised Orders</span>
            <span class="text-lg font-bold text-orange-600">{{ performanceData?.revised_orders || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- Quality Metrics -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Quality Metrics</h2>
        <div class="space-y-4">
          <div class="p-4 bg-linear-to-r from-yellow-50 to-yellow-100 rounded-lg border border-yellow-200">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Average Rating</span>
              <span class="text-2xl font-bold text-yellow-600">
                {{ performanceData?.avg_rating ? performanceData.avg_rating.toFixed(1) : 'N/A' }}
              </span>
            </div>
            <div class="text-xs text-gray-600">
              Client reviews
            </div>
          </div>
          <div class="p-4 bg-linear-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Completion Rate</span>
              <span class="text-2xl font-bold text-blue-600">
                {{ performanceData?.completion_rate ? performanceData.completion_rate.toFixed(1) : '0.0' }}%
              </span>
            </div>
            <div class="text-xs text-gray-600">
              Orders completed on time
            </div>
          </div>
          <div class="p-4 bg-linear-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">On-Time Rate</span>
              <span class="text-2xl font-bold text-green-600">
                {{ performanceData?.on_time_rate ? performanceData.on_time_rate.toFixed(1) : '0.0' }}%
              </span>
            </div>
            <div class="text-xs text-gray-600">
              Orders delivered before deadline
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import writerDashboardAPI from '@/api/writer-dashboard'

const authStore = useAuthStore()

// State
const performanceData = ref(null)
const loading = ref(false)
const selectedDays = ref(30)

// Methods
const loadPerformance = async () => {
  if (!authStore.isWriter) return
  
  loading.value = true
  try {
    const response = await writerDashboardAPI.getPerformanceAnalytics(selectedDays.value)
    performanceData.value = response.data
  } catch (error) {
    console.error('Failed to load performance data:', error)
    performanceData.value = null
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadPerformance()
})
</script>


