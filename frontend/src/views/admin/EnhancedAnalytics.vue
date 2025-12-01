<template>
  <div class="enhanced-analytics p-6">
    <PageHeader 
      title="Enhanced Analytics" 
      subtitle="Deep insights and performance trends"
      :show-refresh="true"
      @refresh="loadAnalytics"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="mt-6">
      <SkeletonLoader type="stats" />
    </div>
    
    <!-- Error State -->
    <ErrorBoundary v-else-if="error" :error-message="error" @retry="loadAnalytics" />
    
    <!-- Analytics Content -->
    <div v-else-if="analyticsData" class="mt-6 space-y-6">
      <!-- Insights Cards -->
      <div v-if="analyticsData.insights && analyticsData.insights.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="(insight, index) in analyticsData.insights"
          :key="index"
          :class="[
            'p-4 rounded-lg border-l-4',
            insight.type === 'positive' 
              ? 'bg-green-50 dark:bg-green-900/20 border-green-400'
              : insight.type === 'warning'
              ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400'
              : 'bg-blue-50 dark:bg-blue-900/20 border-blue-400'
          ]"
        >
          <h3 class="font-semibold mb-2">{{ insight.title }}</h3>
          <p class="text-sm mb-2">{{ insight.message }}</p>
          <p class="text-xs font-medium">{{ insight.action }}</p>
        </div>
      </div>
      
      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Client Retention</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Retention Rate</span>
              <span class="font-medium">{{ analyticsData.client_metrics?.retention_rate || 0 }}%</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Active Clients</span>
              <span class="font-medium">{{ analyticsData.client_metrics?.total_active_clients || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Avg Orders/Client</span>
              <span class="font-medium">{{ analyticsData.client_metrics?.avg_orders_per_client || 0 }}</span>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Predictions</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Next Week Revenue</span>
              <span class="font-medium">${{ formatCurrency(analyticsData.predictions?.predicted_revenue_next_week || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Confidence</span>
              <span class="font-medium capitalize">{{ analyticsData.predictions?.confidence || 'N/A' }}</span>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Top Writers</h3>
          <div class="space-y-2">
            <div
              v-for="(writer, index) in analyticsData.writer_performance?.slice(0, 3)"
              :key="index"
              class="flex justify-between text-sm"
            >
              <span class="truncate">{{ writer.writer_username }}</span>
              <span class="font-medium">{{ writer.completed_orders }} orders</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Revenue Trends Chart Placeholder -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Revenue Trends</h3>
        <div class="h-64 flex items-center justify-center text-gray-500">
          Chart visualization would go here (integrate Chart.js or similar)
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import adminManagementAPI from '@/api/admin-management'
import { getErrorMessage } from '@/utils/errorHandler'

const loading = ref(false)
const error = ref(null)
const analyticsData = ref(null)

const loadAnalytics = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await adminManagementAPI.getEnhancedAnalytics(30)
    analyticsData.value = response.data
  } catch (err) {
    error.value = getErrorMessage(err, 'Failed to load analytics')
    console.error('Failed to load analytics:', err)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num)
}

onMounted(() => {
  loadAnalytics()
})
</script>

