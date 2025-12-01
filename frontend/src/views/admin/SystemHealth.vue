<template>
  <div class="system-health p-6">
    <PageHeader title="System Health Monitoring" subtitle="Monitor system performance and health metrics" />
    
    <div v-if="loading" class="mt-6">
      <SkeletonLoader type="stats" />
    </div>
    
    <div v-else-if="error" class="mt-6">
      <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-4 rounded">
        <p class="text-red-800 dark:text-red-200">{{ error }}</p>
        <button @click="loadHealth" class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
          Retry
        </button>
      </div>
    </div>
    
    <div v-else-if="healthData" class="mt-6 space-y-6">
      <!-- Status Overview -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold">System Status</h2>
          <span :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            healthData.status === 'healthy' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
          ]">
            {{ healthData.status.toUpperCase() }}
          </span>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Last updated: {{ formatDate(healthData.timestamp) }}
        </p>
      </div>
      
      <!-- Alerts -->
      <div v-if="healthData.alerts && healthData.alerts.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Alerts</h2>
        <div class="space-y-3">
          <div 
            v-for="(alert, index) in healthData.alerts" 
            :key="index"
            :class="[
              'p-4 rounded-lg border-l-4',
              alert.severity === 'critical' 
                ? 'bg-red-50 dark:bg-red-900/20 border-red-400'
                : alert.severity === 'warning'
                ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400'
                : 'bg-blue-50 dark:bg-blue-900/20 border-blue-400'
            ]"
          >
            <div class="flex items-start justify-between">
              <div>
                <p class="font-medium" :class="[
                  alert.severity === 'critical' 
                    ? 'text-red-800 dark:text-red-200'
                    : alert.severity === 'warning'
                    ? 'text-yellow-800 dark:text-yellow-200'
                    : 'text-blue-800 dark:text-blue-200'
                ]">
                  {{ alert.message }}
                </p>
                <p class="text-sm mt-1" :class="[
                  alert.severity === 'critical' 
                    ? 'text-red-600 dark:text-red-400'
                    : alert.severity === 'warning'
                    ? 'text-yellow-600 dark:text-yellow-400'
                    : 'text-blue-600 dark:text-blue-400'
                ]">
                  {{ alert.action }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Database Health -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Database</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Status</span>
              <span class="font-medium">{{ healthData.database?.status || 'Unknown' }}</span>
            </div>
            <div v-if="healthData.database?.response_time_ms" class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Response Time</span>
              <span class="font-medium">{{ healthData.database.response_time_ms }}ms</span>
            </div>
          </div>
        </div>
        
        <!-- Order Metrics -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Orders</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Total</span>
              <span class="font-medium">{{ formatNumber(healthData.orders?.total || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Last 24h</span>
              <span class="font-medium">{{ formatNumber(healthData.orders?.last_24h || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Overdue</span>
              <span class="font-medium text-red-600">{{ formatNumber(healthData.orders?.overdue || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Stuck</span>
              <span class="font-medium text-yellow-600">{{ formatNumber(healthData.orders?.stuck || 0) }}</span>
            </div>
          </div>
        </div>
        
        <!-- User Metrics -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Users</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Total</span>
              <span class="font-medium">{{ formatNumber(healthData.users?.total || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Active (30d)</span>
              <span class="font-medium">{{ formatNumber(healthData.users?.active_30d || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Suspended</span>
              <span class="font-medium text-red-600">{{ formatNumber(healthData.users?.suspended || 0) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Financial Health -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Financial</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Payments (24h)</span>
              <span class="font-medium">${{ formatCurrency(healthData.financial?.payments_24h?.total || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Payments (7d)</span>
              <span class="font-medium">${{ formatCurrency(healthData.financial?.payments_7d?.total || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Pending Fines</span>
              <span class="font-medium text-yellow-600">${{ formatCurrency(healthData.financial?.pending_fines?.total || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recommendations -->
      <div v-if="healthData.recommendations && healthData.recommendations.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Recommendations</h2>
        <div class="space-y-3">
          <div 
            v-for="(rec, index) in healthData.recommendations" 
            :key="index"
            class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
          >
            <p class="font-medium text-blue-800 dark:text-blue-200 mb-2">{{ rec.message }}</p>
            <ul class="list-disc list-inside text-sm text-blue-700 dark:text-blue-300 space-y-1">
              <li v-for="(action, actionIndex) in rec.actions" :key="actionIndex">{{ action }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import adminManagementAPI from '@/api/admin-management'

const loading = ref(false)
const error = ref(null)
const healthData = ref(null)

const loadHealth = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await adminManagementAPI.getSystemHealth()
    healthData.value = response.data || {}
  } catch (err) {
    // Only set error and log if it's not a 404 (endpoint doesn't exist)
    if (err?.response?.status !== 404) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load system health data'
      console.error('Failed to load system health:', err)
    } else {
      // Endpoint doesn't exist, set empty data
      healthData.value = {}
    }
  } finally {
    loading.value = false
  }
}

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatCurrency = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadHealth()
  // Auto-refresh every 60 seconds
  const interval = setInterval(loadHealth, 60000)
  return () => clearInterval(interval)
})
</script>

