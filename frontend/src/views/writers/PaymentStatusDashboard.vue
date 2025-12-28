<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              Payment Status Dashboard
            </h1>
            <p class="text-base text-gray-600 leading-relaxed max-w-2xl">
              Track your payment processing status and timeline
            </p>
          </div>
          <button
            @click="loadPaymentStatus"
            :disabled="loading"
            class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-16">
        <div class="flex flex-col items-center justify-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading payment status...</p>
        </div>
      </div>

      <!-- Summary Cards -->
      <div v-else-if="paymentStatus" class="mb-8">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <!-- Pending -->
          <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl shadow-md p-6 border-l-4 border-yellow-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide mb-2">
                  Pending
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-yellow-900 truncate">
                  ${{ formatCurrency(paymentStatus.summary.pending_amount) }}
                </p>
                <p class="text-xs font-medium text-yellow-600 mt-2">
                  {{ getStatusCount('Pending') }} payment{{ getStatusCount('Pending') !== 1 ? 's' : '' }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-yellow-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">⏳</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Delayed -->
          <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl shadow-md p-6 border-l-4 border-red-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-red-700 uppercase tracking-wide mb-2">
                  Delayed
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-red-900 truncate">
                  ${{ formatCurrency(paymentStatus.summary.delayed_amount) }}
                </p>
                <p class="text-xs font-medium text-red-600 mt-2">
                  {{ getStatusCount('Delayed') }} payment{{ getStatusCount('Delayed') !== 1 ? 's' : '' }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">⚠️</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Paid (30 days) -->
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-md p-6 border-l-4 border-green-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-green-700 uppercase tracking-wide mb-2">
                  Paid (30 days)
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-green-900 truncate">
                  ${{ formatCurrency(paymentStatus.summary.recent_paid_30d) }}
                </p>
                <p class="text-xs font-medium text-green-600 mt-2">
                  Last 30 days
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">✅</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Total Earnings -->
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md p-6 border-l-4 border-blue-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-2">
                  Total Earnings
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-blue-900 truncate">
                  ${{ formatCurrency(paymentStatus.summary.total_earnings) }}
                </p>
                <p class="text-xs font-medium text-blue-600 mt-2">
                  All time
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">💰</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment Status Breakdown -->
      <div v-if="paymentStatus" class="bg-white rounded-xl shadow-md p-6 sm:p-8 mb-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <span class="text-xl">📊</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900">
            Payment Status Breakdown
          </h2>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="(data, status) in paymentStatus.status_breakdown"
            :key="status"
            class="p-5 rounded-xl border-2 transition-all hover:shadow-md"
            :class="getStatusCardClass(status)"
          >
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm font-bold uppercase tracking-wide">
                {{ formatStatus(status) }}
              </span>
              <span class="text-2xl">{{ getStatusIcon(status) }}</span>
            </div>
            <p class="text-2xl sm:text-3xl font-bold mb-1 truncate">
              ${{ formatCurrency(data.total_amount) }}
            </p>
            <p class="text-xs font-medium text-gray-600">
              {{ data.count }} payment{{ data.count !== 1 ? 's' : '' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Pending Payments -->
      <div
        v-if="paymentStatus && paymentStatus.pending_payments.length > 0"
        class="bg-white rounded-xl shadow-md p-6 sm:p-8 mb-8"
      >
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
            <span class="text-xl">⏳</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900">
            Pending Payments
          </h2>
        </div>
        <div class="space-y-4">
          <div
            v-for="payment in paymentStatus.pending_payments"
            :key="payment.id"
            class="border-2 border-yellow-200 rounded-xl p-5 bg-yellow-50 hover:bg-yellow-100 transition-colors"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-3 flex-wrap">
                  <span class="text-lg font-bold text-gray-900">
                    Payment #{{ payment.id }}
                  </span>
                  <span
                    class="px-3 py-1 rounded-full text-xs font-bold bg-yellow-200 text-yellow-800 uppercase tracking-wide"
                  >
                    {{ formatStatus(payment.status) }}
                  </span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Order
                    </span>
                    <span class="text-base font-semibold text-gray-900">
                      {{ payment.order_id ? `#${payment.order_id}` : 'N/A' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Amount
                    </span>
                    <span class="text-base font-bold text-green-600">
                      ${{ formatCurrency(payment.amount) }}
                    </span>
                  </div>
                  <div v-if="payment.bonuses > 0">
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Bonuses
                    </span>
                    <span class="text-base font-semibold text-blue-600">
                      ${{ formatCurrency(payment.bonuses) }}
                    </span>
                  </div>
                  <div v-if="payment.tips > 0">
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Tips
                    </span>
                    <span class="text-base font-semibold text-purple-600">
                      ${{ formatCurrency(payment.tips) }}
                    </span>
                  </div>
                </div>
                <div
                  v-if="payment.processed_at"
                  class="mt-4 pt-4 border-t border-yellow-200"
                >
                  <p class="text-xs font-medium text-gray-600">
                    Processed: <span class="text-gray-900">{{ formatDate(payment.processed_at) }}</span>
                  </p>
                </div>
              </div>
              <div class="shrink-0">
                <div class="flex flex-col items-center gap-2">
                  <div
                    class="w-4 h-4 rounded-full animate-pulse shadow-lg"
                    :class="getStatusDotClass(payment.status)"
                  ></div>
                  <span class="text-xs font-medium text-gray-500">Processing</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Delayed Payments -->
      <div
        v-if="paymentStatus && paymentStatus.delayed_payments.length > 0"
        class="bg-white rounded-xl shadow-md p-6 sm:p-8 mb-8 border-l-4 border-red-600"
      >
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
            <span class="text-xl">⚠️</span>
          </div>
          <h2 class="text-2xl font-bold text-red-900">
            Delayed Payments
          </h2>
        </div>
        <div class="space-y-4">
          <div
            v-for="payment in paymentStatus.delayed_payments"
            :key="payment.id"
            class="border-2 border-red-300 rounded-xl p-5 bg-red-50 hover:bg-red-100 transition-colors"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-3 flex-wrap">
                  <span class="text-lg font-bold text-gray-900">
                    Payment #{{ payment.id }}
                  </span>
                  <span
                    class="px-3 py-1 rounded-full text-xs font-bold bg-red-200 text-red-800 uppercase tracking-wide"
                  >
                    Delayed
                  </span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Order
                    </span>
                    <span class="text-base font-semibold text-gray-900">
                      {{ payment.order_id ? `#${payment.order_id}` : 'N/A' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Amount
                    </span>
                    <span class="text-base font-bold text-red-600">
                      ${{ formatCurrency(payment.amount) }}
                    </span>
                  </div>
                  <div>
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Last Updated
                    </span>
                    <span class="text-base font-medium text-gray-900">
                      {{ formatDate(payment.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Payments -->
      <div v-if="paymentStatus" class="bg-white rounded-xl shadow-md p-6 sm:p-8 mb-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <span class="text-xl">📋</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900">
            Recent Payment Activity
          </h2>
        </div>
        <div class="overflow-x-auto -mx-6 sm:mx-0">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Payment ID
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Order
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Amount
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Bonuses
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Tips
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Processed
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="payment in paymentStatus.recent_payments"
                :key="payment.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                  #{{ payment.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-700">
                  {{ payment.order_id ? `#${payment.order_id}` : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">
                  ${{ formatCurrency(payment.amount) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600">
                  ${{ formatCurrency(payment.bonuses) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600">
                  ${{ formatCurrency(payment.tips) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span
                    class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide"
                    :class="getStatusBadgeClass(payment.status)"
                  >
                    {{ formatStatus(payment.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(payment.processed_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Payout Requests -->
      <div
        v-if="paymentStatus && paymentStatus.payout_requests.length > 0"
        class="bg-white rounded-xl shadow-md p-6 sm:p-8"
      >
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
            <span class="text-xl">💳</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900">
            Payout Requests
          </h2>
        </div>
        <div class="space-y-4">
          <div
            v-for="request in paymentStatus.payout_requests"
            :key="request.id"
            class="border-2 border-gray-200 rounded-xl p-5 bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div class="flex-1 min-w-0">
                <p class="text-xl font-bold text-gray-900 mb-1 truncate">
                  ${{ formatCurrency(request.amount_requested) }}
                </p>
                <p class="text-sm font-medium text-gray-600">
                  Requested: <span class="text-gray-900">{{ formatDate(request.requested_at) }}</span>
                </p>
              </div>
              <div class="shrink-0">
                <span
                  class="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wide"
                  :class="getStatusBadgeClass(request.status)"
                >
                  {{ formatStatus(request.status) }}
                </span>
              </div>
            </div>
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

const { error: showError } = useToast()

const loading = ref(false)
const paymentStatus = ref(null)

const loadPaymentStatus = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getPaymentStatus()
    paymentStatus.value = response.data
  } catch (error) {
    console.error('Failed to load payment status:', error)
    const errorMsg = getErrorMessage(
      error,
      'Failed to load payment status. Please try again.'
    )
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const getStatusCount = (status) => {
  if (!paymentStatus.value) return 0
  return paymentStatus.value.status_breakdown[status]?.count || 0
}

const formatStatus = (status) => {
  const statusMap = {
    'Pending': 'Pending',
    'Processing': 'Processing',
    'Paid': 'Paid',
    'Delayed': 'Delayed',
    'Failed': 'Failed',
    'Cancelled': 'Cancelled',
  }
  return statusMap[status] || status
}

const getStatusIcon = (status) => {
  const icons = {
    'Pending': '⏳',
    'Processing': '🔄',
    'Paid': '✅',
    'Delayed': '⚠️',
    'Failed': '❌',
    'Cancelled': '🚫',
  }
  return icons[status] || '❓'
}

const getStatusCardClass = (status) => {
  const classes = {
    'Pending': 'border-yellow-300 bg-yellow-50',
    'Processing': 'border-blue-300 bg-blue-50',
    'Paid': 'border-green-300 bg-green-50',
    'Delayed': 'border-red-300 bg-red-50',
    'Failed': 'border-red-300 bg-red-50',
    'Cancelled': 'border-gray-300 bg-gray-50',
  }
  return classes[status] || 'border-gray-300 bg-gray-50'
}

const getStatusBadgeClass = (status) => {
  const classes = {
    'Pending': 'bg-yellow-100 text-yellow-700',
    'Processing': 'bg-blue-100 text-blue-700',
    'Paid': 'bg-green-100 text-green-700',
    'Delayed': 'bg-red-100 text-red-700',
    'Failed': 'bg-red-100 text-red-700',
    'Cancelled': 'bg-gray-100 text-gray-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const getStatusDotClass = (status) => {
  const classes = {
    'Pending': 'bg-yellow-500',
    'Processing': 'bg-blue-500',
    'Paid': 'bg-green-500',
    'Delayed': 'bg-red-500',
  }
  return classes[status] || 'bg-gray-500'
}

const formatCurrency = (value) => {
  return Number(value || 0).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadPaymentStatus()
})
</script>
