<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              Earnings Breakdown
            </h1>
            <p class="text-base text-gray-600 leading-relaxed max-w-2xl">
              Detailed breakdown of your earnings by source
            </p>
          </div>
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <select
              v-model="selectedDays"
              @change="loadBreakdown"
              class="px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
            >
              <option :value="30">Last 30 days</option>
              <option :value="90">Last 90 days</option>
              <option :value="180">Last 6 months</option>
              <option :value="365">Last year</option>
            </select>
            <button
              @click="exportEarnings"
              :disabled="exporting"
              class="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
            >
              <svg
                v-if="!exporting"
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <span v-else class="animate-spin w-5 h-5">⏳</span>
              <span>{{ exporting ? 'Exporting...' : 'Export CSV' }}</span>
            </button>
            <button
              @click="loadBreakdown"
              :disabled="loading"
              class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
            >
              {{ loading ? 'Loading...' : 'Refresh' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-16">
        <div class="flex flex-col items-center justify-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading earnings data...</p>
        </div>
      </div>

      <!-- Summary Cards -->
      <div v-else-if="breakdown" class="mb-8">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <!-- Total Earnings -->
          <div class="bg-linear-to-br from-blue-50 to-blue-100 rounded-xl shadow-md p-6 border-l-4 border-blue-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-2">
                  Total Earnings
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-blue-900 truncate">
                  ${{ formatCurrency(breakdown.summary.total_earnings) }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">💰</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Regular Orders -->
          <div class="bg-linear-to-br from-green-50 to-green-100 rounded-xl shadow-md p-6 border-l-4 border-green-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-green-700 uppercase tracking-wide mb-2">
                  Regular Orders
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-green-900 truncate">
                  ${{ formatCurrency(breakdown.summary.regular_orders) }}
                </p>
                <p class="text-xs font-medium text-green-600 mt-2">
                  {{ breakdown.breakdown.regular_orders.count }} order{{ breakdown.breakdown.regular_orders.count !== 1 ? 's' : '' }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">📄</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Special Orders -->
          <div class="bg-linear-to-br from-purple-50 to-purple-100 rounded-xl shadow-md p-6 border-l-4 border-purple-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide mb-2">
                  Special Orders
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-purple-900 truncate">
                  ${{ formatCurrency(breakdown.summary.special_orders) }}
                </p>
                <p class="text-xs font-medium text-purple-600 mt-2">
                  {{ breakdown.breakdown.special_orders.count }} order{{ breakdown.breakdown.special_orders.count !== 1 ? 's' : '' }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">⭐</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Class Bonuses -->
          <div class="bg-linear-to-br from-yellow-50 to-yellow-100 rounded-xl shadow-md p-6 border-l-4 border-yellow-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide mb-2">
                  Class Bonuses
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-yellow-900 truncate">
                  ${{ formatCurrency(breakdown.summary.class_bonuses) }}
                </p>
                <p class="text-xs font-medium text-yellow-600 mt-2">
                  {{ breakdown.breakdown.class_bonuses.count }} classe{{ breakdown.breakdown.class_bonuses.count !== 1 ? 's' : '' }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-yellow-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">🎓</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Tips -->
          <div class="bg-linear-to-br from-pink-50 to-pink-100 rounded-xl shadow-md p-6 border-l-4 border-pink-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-pink-700 uppercase tracking-wide mb-2">
                  Tips
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-pink-900 truncate">
                  ${{ formatCurrency(breakdown.summary.tips) }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-pink-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">💝</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Other Bonuses -->
          <div class="bg-linear-to-br from-indigo-50 to-indigo-100 rounded-xl shadow-md p-6 border-l-4 border-indigo-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-indigo-700 uppercase tracking-wide mb-2">
                  Other Bonuses
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-indigo-900 truncate">
                  ${{ formatCurrency(breakdown.summary.other_bonuses) }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">🎁</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Breakdown -->
      <div v-if="breakdown" class="space-y-6">
        <!-- Regular Orders -->
        <div class="bg-white rounded-xl shadow-md p-6 sm:p-8">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <span class="text-xl">📄</span>
              </div>
              <span>Regular Orders</span>
            </h2>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Total
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-green-600 truncate">
                ${{ formatCurrency(breakdown.breakdown.regular_orders.total) }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Count
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-gray-900">
                {{ breakdown.breakdown.regular_orders.count }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Average
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-gray-900 truncate">
                ${{ formatCurrency(breakdown.breakdown.regular_orders.average) }}
              </p>
            </div>
          </div>
          <div
            v-if="breakdown.breakdown.regular_orders.orders.length > 0"
            class="overflow-x-auto -mx-6 sm:mx-0"
          >
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Order ID
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Topic
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Pages
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Completed
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="order in breakdown.breakdown.regular_orders.orders"
                  :key="order.order_id"
                  class="hover:bg-gray-50 transition-colors"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                    #{{ order.order_id }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-700 max-w-xs">
                    <p class="truncate" :title="order.topic">
                      {{ order.topic }}
                    </p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600">
                    {{ order.pages }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">
                    ${{ formatCurrency(order.amount) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(order.completed_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            v-else
            class="text-center py-12"
          >
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <span class="text-2xl">📭</span>
            </div>
            <p class="text-sm font-medium text-gray-500">
              No regular orders in this period
            </p>
          </div>
        </div>

        <!-- Special Orders -->
        <div class="bg-white rounded-xl shadow-md p-6 sm:p-8">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <span class="text-xl">⭐</span>
              </div>
              <span>Special Orders</span>
            </h2>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Total
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-purple-600 truncate">
                ${{ formatCurrency(breakdown.breakdown.special_orders.total) }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Count
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-gray-900">
                {{ breakdown.breakdown.special_orders.count }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Average
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-gray-900 truncate">
                ${{ formatCurrency(breakdown.breakdown.special_orders.average) }}
              </p>
            </div>
          </div>
          <div
            v-if="breakdown.breakdown.special_orders.orders.length > 0"
            class="overflow-x-auto -mx-6 sm:mx-0"
          >
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Order ID
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Topic
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Total Cost
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Your Earnings
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Completed
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="order in breakdown.breakdown.special_orders.orders"
                  :key="order.order_id"
                  class="hover:bg-gray-50 transition-colors"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                    #{{ order.order_id }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-700 max-w-xs">
                    <p class="truncate" :title="order.topic">
                      {{ order.topic }}
                    </p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600">
                    ${{ formatCurrency(order.total_cost) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-purple-600">
                    ${{ formatCurrency(order.amount) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(order.completed_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            v-else
            class="text-center py-12"
          >
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <span class="text-2xl">📭</span>
            </div>
            <p class="text-sm font-medium text-gray-500">
              No special orders in this period
            </p>
          </div>
        </div>

        <!-- Class Bonuses -->
        <div class="bg-white rounded-xl shadow-md p-6 sm:p-8">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span class="text-xl">🎓</span>
              </div>
              <span>Class Bonuses</span>
            </h2>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Total
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-yellow-600 truncate">
                ${{ formatCurrency(breakdown.breakdown.class_bonuses.total) }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Count
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-gray-900">
                {{ breakdown.breakdown.class_bonuses.count }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Average
              </p>
              <p class="text-2xl sm:text-3xl font-bold text-gray-900 truncate">
                ${{ formatCurrency(breakdown.breakdown.class_bonuses.average) }}
              </p>
            </div>
          </div>
          <div
            v-if="breakdown.breakdown.class_bonuses.bonuses.length > 0"
            class="overflow-x-auto -mx-6 sm:mx-0"
          >
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Class ID
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Description
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Granted
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="bonus in breakdown.breakdown.class_bonuses.bonuses"
                  :key="bonus.id"
                  class="hover:bg-gray-50 transition-colors"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                    {{ bonus.class_id ? `#${bonus.class_id}` : 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-yellow-600">
                    ${{ formatCurrency(bonus.amount) }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-700 max-w-md">
                    <p class="truncate" :title="bonus.description">
                      {{ bonus.description }}
                    </p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(bonus.granted_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            v-else
            class="text-center py-12"
          >
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <span class="text-2xl">📭</span>
            </div>
            <p class="text-sm font-medium text-gray-500">
              No class bonuses in this period
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const exporting = ref(false)
const breakdown = ref(null)
const selectedDays = ref(30)

const loadBreakdown = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getEarningsBreakdown({
      days: selectedDays.value,
    })
    breakdown.value = response.data
  } catch (error) {
    console.error('Failed to load earnings breakdown:', error)
    const errorMsg = getErrorMessage(
      error,
      'Failed to load earnings breakdown. Please try again.'
    )
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const exportEarnings = async () => {
  exporting.value = true
  try {
    await writerDashboardAPI.exportEarnings({
      days: selectedDays.value,
      format: 'csv',
    })
    showSuccess('Earnings exported successfully!')
  } catch (error) {
    console.error('Failed to export earnings:', error)
    const errorMsg = getErrorMessage(
      error,
      'Failed to export earnings. Please try again.'
    )
    showError(errorMsg)
  } finally {
    exporting.value = false
  }
}

const formatCurrency = (value) => {
  return Number(value || 0).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadBreakdown()
})
</script>
