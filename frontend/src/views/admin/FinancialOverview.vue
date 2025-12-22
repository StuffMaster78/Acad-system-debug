<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Financial Overview</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Comprehensive financial analytics and reporting</p>
      </div>
      <div class="flex gap-2">
        <input
          v-model="dateFrom"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadOverview"
        />
        <input
          v-model="dateTo"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadOverview"
        />
        <button
          @click="loadOverview"
          :disabled="loading"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Total Revenue</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">${{ formatCurrency(summary.total_revenue) }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-red-50 to-red-100 border border-red-200 dark:from-red-900/20 dark:to-red-800/20 dark:border-red-700">
        <p class="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Total Expenses</p>
        <p class="text-3xl font-bold text-red-900 dark:text-red-100">${{ formatCurrency(summary.total_expenses) }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Net Revenue</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">${{ formatCurrency(summary.net_revenue) }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Profit Margin</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ formatNumber(summary.profit_margin) }}%</p>
      </div>
    </div>

    <!-- Revenue Breakdown -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Revenue Breakdown</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Orders</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(revenueBreakdown.orders) }}</p>
        </div>
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Special Orders</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(revenueBreakdown.special_orders) }}</p>
        </div>
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Classes</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(revenueBreakdown.classes) }}</p>
        </div>
      </div>
    </div>

    <!-- Expenses Breakdown -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Expenses Breakdown</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Writer Payments</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(expensesBreakdown.writer_payments) }}</p>
        </div>
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Tips</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(expensesBreakdown.tips) }}</p>
        </div>
      </div>
    </div>

    <!-- Period Breakdown Chart -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Monthly Breakdown (Last 12 Months)</h2>
      <div class="space-y-4">
        <div
          v-for="period in periodBreakdown"
          :key="period.period"
          class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-900 dark:text-white">{{ period.month }}</h3>
            <div class="text-right">
              <p class="text-sm text-gray-500 dark:text-gray-400">Net Revenue</p>
              <p class="text-lg font-bold" :class="period.net_revenue >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                ${{ formatCurrency(period.net_revenue) }}
              </p>
            </div>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p class="text-gray-500 dark:text-gray-400">Orders</p>
              <p class="font-semibold text-gray-900 dark:text-white">${{ formatCurrency(period.revenue.orders) }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Special</p>
              <p class="font-semibold text-gray-900 dark:text-white">${{ formatCurrency(period.revenue.special_orders) }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Classes</p>
              <p class="font-semibold text-gray-900 dark:text-white">${{ formatCurrency(period.revenue.classes) }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Expenses</p>
              <p class="font-semibold text-gray-900 dark:text-white">${{ formatCurrency(period.expenses.total) }}</p>
            </div>
          </div>
        </div>
        <div v-if="periodBreakdown.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No period data available
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading financial data...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminManagementAPI from '@/api/admin-management'

const { error: showError } = useToast()

const loading = ref(false)
const overviewData = ref({})
const dateFrom = ref('')
const dateTo = ref('')

const summary = computed(() => {
  return overviewData.value.summary || {
    total_revenue: 0,
    total_expenses: 0,
    net_revenue: 0,
    profit_margin: 0,
  }
})

const revenueBreakdown = computed(() => {
  return summary.value.revenue_breakdown || {
    orders: 0,
    special_orders: 0,
    classes: 0,
  }
})

const expensesBreakdown = computed(() => {
  return summary.value.expenses_breakdown || {
    writer_payments: 0,
    tips: 0,
  }
})

const periodBreakdown = computed(() => {
  return overviewData.value.period_breakdown || []
})

const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '0.00'
  return Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(2)
}

const loadOverview = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    
    const response = await adminManagementAPI.getFinancialOverview(params)
    overviewData.value = response.data || {}
  } catch (error) {
    showError('Failed to load financial overview')
    console.error('Error loading overview:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Set default date range to last 30 days
  const today = new Date()
  const thirtyDaysAgo = new Date(today)
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  
  dateTo.value = today.toISOString().split('T')[0]
  dateFrom.value = thirtyDaysAgo.toISOString().split('T')[0]
  
  loadOverview()
})
</script>
