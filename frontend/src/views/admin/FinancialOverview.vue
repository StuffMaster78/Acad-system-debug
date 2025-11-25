<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Financial Overview</h1>
        <p class="mt-2 text-gray-600">Comprehensive financial analytics and revenue breakdown</p>
      </div>
      <div class="flex gap-2">
        <ExportButton
          :export-function="exportFinancialReport"
          :export-params="exportParams"
          filename="financial_report"
          @exported="handleExportSuccess"
          @error="handleExportError"
        />
        <router-link
          to="/admin/payments/batched"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Batched Payments
        </router-link>
        <router-link
          to="/admin/payments/all"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          All Payments
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadOverview"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            @change="loadOverview"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="overview" class="space-y-6">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
          <p class="text-sm font-medium text-green-700 mb-1">Total Revenue</p>
          <p class="text-3xl font-bold text-green-900">${{ formatCurrency(overview.summary.total_revenue) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
          <p class="text-sm font-medium text-red-700 mb-1">Total Expenses</p>
          <p class="text-3xl font-bold text-red-900">${{ formatCurrency(overview.summary.total_expenses) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
          <p class="text-sm font-medium text-blue-700 mb-1">Net Revenue</p>
          <p class="text-3xl font-bold text-blue-900">${{ formatCurrency(overview.summary.net_revenue) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
          <p class="text-sm font-medium text-purple-700 mb-1">Profit Margin</p>
          <p class="text-3xl font-bold text-purple-900">{{ formatCurrency(overview.summary.profit_margin) }}%</p>
        </div>
      </div>

      <!-- Revenue Breakdown -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold mb-4">Revenue Breakdown</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div class="text-sm text-blue-700 mb-1">Standard Orders</div>
            <div class="text-2xl font-bold text-blue-900">${{ formatCurrency(overview.summary.revenue_breakdown.orders) }}</div>
            <div class="text-xs text-blue-600 mt-1">
              {{ ((overview.summary.revenue_breakdown.orders / overview.summary.total_revenue) * 100).toFixed(1) }}% of total
            </div>
          </div>
          <div class="bg-green-50 rounded-lg p-4 border border-green-200">
            <div class="text-sm text-green-700 mb-1">Special Orders</div>
            <div class="text-2xl font-bold text-green-900">${{ formatCurrency(overview.summary.revenue_breakdown.special_orders) }}</div>
            <div class="text-xs text-green-600 mt-1">
              {{ ((overview.summary.revenue_breakdown.special_orders / overview.summary.total_revenue) * 100).toFixed(1) }}% of total
            </div>
          </div>
          <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div class="text-sm text-purple-700 mb-1">Classes</div>
            <div class="text-2xl font-bold text-purple-900">${{ formatCurrency(overview.summary.revenue_breakdown.classes) }}</div>
            <div class="text-xs text-purple-600 mt-1">
              {{ ((overview.summary.revenue_breakdown.classes / overview.summary.total_revenue) * 100).toFixed(1) }}% of total
            </div>
          </div>
        </div>
      </div>

      <!-- Expenses Breakdown -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold mb-4">Expenses Breakdown</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-red-50 rounded-lg p-4 border border-red-200">
            <div class="text-sm text-red-700 mb-1">Writer Payments</div>
            <div class="text-2xl font-bold text-red-900">${{ formatCurrency(overview.summary.expenses_breakdown.writer_payments) }}</div>
            <div class="text-xs text-red-600 mt-1">
              {{ ((overview.summary.expenses_breakdown.writer_payments / overview.summary.total_expenses) * 100).toFixed(1) }}% of expenses
            </div>
          </div>
          <div class="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <div class="text-sm text-orange-700 mb-1">Tips Paid</div>
            <div class="text-2xl font-bold text-orange-900">${{ formatCurrency(overview.summary.expenses_breakdown.tips) }}</div>
            <div class="text-xs text-orange-600 mt-1">
              {{ ((overview.summary.expenses_breakdown.tips / overview.summary.total_expenses) * 100).toFixed(1) }}% of expenses
            </div>
          </div>
        </div>
      </div>

      <!-- Period Breakdown (Last 12 Months) -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold mb-4">Monthly Breakdown (Last 12 Months)</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders Revenue</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Special Orders</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Classes</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Revenue</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expenses</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net Revenue</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="period in overview.period_breakdown" :key="period.period" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm font-medium">{{ period.month }}</td>
                <td class="px-4 py-3 text-sm">${{ formatCurrency(period.revenue.orders) }}</td>
                <td class="px-4 py-3 text-sm">${{ formatCurrency(period.revenue.special_orders) }}</td>
                <td class="px-4 py-3 text-sm">${{ formatCurrency(period.revenue.classes) }}</td>
                <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(period.revenue.total) }}</td>
                <td class="px-4 py-3 text-sm text-red-600">${{ formatCurrency(period.expenses.total) }}</td>
                <td class="px-4 py-3 text-sm font-bold" :class="period.net_revenue >= 0 ? 'text-green-600' : 'text-red-600'">
                  ${{ formatCurrency(period.net_revenue) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import financialOverviewAPI from '@/api/financial-overview'
import exportsAPI from '@/api/exports'
import ExportButton from '@/components/common/ExportButton.vue'

const loading = ref(false)
const overview = ref(null)

const filters = ref({
  date_from: '',
  date_to: '',
})

const loadOverview = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.date_from) {
      params.date_from = filters.value.date_from
    }
    if (filters.value.date_to) {
      params.date_to = filters.value.date_to
    }

    const response = await financialOverviewAPI.getOverview(params)
    overview.value = response.data
  } catch (error) {
    console.error('Failed to load financial overview:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    date_from: '',
    date_to: '',
  }
  loadOverview()
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

// Export functionality
const exportParams = computed(() => {
  const params = {}
  if (filters.value.date_from) params.date_from = filters.value.date_from
  if (filters.value.date_to) params.date_to = filters.value.date_to
  return params
})

const exportFinancialReport = exportsAPI.exportFinancialReport

const handleExportSuccess = (data) => {
  // You can add a toast notification here if needed
  console.log('Export successful:', data)
}

const handleExportError = (error) => {
  console.error('Export error:', error)
  // You can add error notification here if needed
}

onMounted(() => {
  loadOverview()
})
</script>

