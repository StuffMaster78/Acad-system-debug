<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Payments</h1>
        <p class="text-gray-600 mt-1">View your payment history and upcoming payments</p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="periodView"
          @change="loadPayments"
          class="border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="monthly">Monthly View</option>
          <option value="fortnightly">Fortnightly View</option>
        </select>
      </div>
    </div>

    <!-- Controls -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="flex flex-wrap items-center gap-3">
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Date From
            </label>
            <input
              v-model="filters.dateFrom"
              type="date"
              class="border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Date To
            </label>
            <input
              v-model="filters.dateTo"
              type="date"
              class="border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Payment Status
            </label>
            <select
              v-model="filters.status"
              class="border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Search
            </label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="Order or description"
              class="border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <button
            @click="resetFilters"
            type="button"
            class="mt-6 md:mt-0 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Reset
          </button>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="downloadPaymentsCsv"
            type="button"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-semibold"
          >
            Download CSV
          </button>
          <select
            v-model="periodView"
            @change="loadPayments"
            class="border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="monthly">Monthly View</option>
            <option value="fortnightly">Fortnightly View</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Upcoming Payments Card -->
    <div class="bg-blue-50 rounded-lg shadow-sm border border-blue-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-semibold text-blue-900">Upcoming Payments</h2>
          <p class="text-sm text-blue-700 mt-1">Completed orders awaiting payment processing</p>
        </div>
        <div class="text-right">
          <div class="text-3xl font-bold text-blue-900">${{ formatCurrency(upcomingPayments.total_amount) }}</div>
          <div class="text-sm text-blue-700">{{ upcomingPayments.order_count }} order(s)</div>
        </div>
      </div>

      <div v-if="loading" class="text-sm text-blue-600">Loading...</div>
      <div v-else-if="upcomingPayments.orders.length === 0" class="text-sm text-blue-700">
        No upcoming payments at this time.
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="order in upcomingPayments.orders"
          :key="order.id"
          class="flex items-center justify-between p-3 bg-white rounded-lg border border-blue-100"
        >
          <div class="flex-1">
            <div class="font-medium text-gray-900">Order #{{ order.id }}</div>
            <div class="text-sm text-gray-600">{{ order.topic }}</div>
            <div class="text-xs text-gray-500 mt-1">
              Completed: {{ formatDate(order.completed_at || order.created_at) }}
            </div>
          </div>
          <div class="text-right">
            <div class="font-semibold text-blue-900">${{ formatCurrency(order.total_price) }}</div>
            <div class="text-xs text-blue-600 capitalize">{{ order.status }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment History -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Payment History</h2>

      <div v-if="loading" class="text-center py-8 text-gray-500">Loading payment history...</div>
      <div v-else-if="paymentPeriods.length === 0" class="text-center py-8 text-gray-500">
        No payment history available.
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="period in filteredPaymentPeriods"
          :key="period.period || period.period_start"
          class="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 class="font-semibold text-gray-900">
                {{ formatPeriod(period.period || period.period_start, period.period_end) }}
              </h3>
              <p class="text-sm text-gray-600">
                {{ period.payment_count }} payment(s)
              </p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-green-600">
                ${{ formatCurrency(period.total_amount) }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                <span v-if="period.total_bonuses > 0" class="text-green-600">+${{ formatCurrency(period.total_bonuses) }} bonuses</span>
                <span v-if="period.total_tips > 0" class="text-blue-600 ml-2">+${{ formatCurrency(period.total_tips) }} tips</span>
                <span v-if="period.total_fines > 0" class="text-red-600 ml-2">-${{ formatCurrency(period.total_fines) }} fines</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Payments -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Recent Payments</h2>

      <div v-if="loading" class="text-center py-8 text-gray-500">Loading...</div>
      <div v-else-if="recentPayments.length === 0" class="text-center py-8 text-gray-500">
        No recent payments.
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="payment in filteredRecentPayments"
          :key="payment.id"
          class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="flex-1">
            <div class="font-medium text-gray-900">
              Payment #{{ payment.id }}
            </div>
            <div class="text-sm text-gray-600 mt-1">
              {{ payment.description || 'Writer payment' }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatDate(payment.payment_date) }}
            </div>
          </div>
          <div class="text-right">
            <div class="font-semibold text-gray-900">
              ${{ formatCurrency(payment.amount) }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              <span v-if="payment.bonuses > 0" class="text-green-600">+${{ formatCurrency(payment.bonuses) }} bonus</span>
              <span v-if="payment.tips > 0" class="text-blue-600 ml-2">+${{ formatCurrency(payment.tips) }} tip</span>
              <span v-if="payment.fines > 0" class="text-red-600 ml-2">-${{ formatCurrency(payment.fines) }} fine</span>
            </div>
            <button
              @click="downloadReceipt(payment)"
              :disabled="downloadingReceipt === payment.id"
              class="mt-2 px-3 py-1 text-xs font-medium text-primary-600 bg-primary-50 rounded hover:bg-primary-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              title="Download PDF receipt"
            >
              <svg v-if="downloadingReceipt !== payment.id" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span v-if="downloadingReceipt === payment.id" class="animate-spin">⟳</span>
              <span>{{ downloadingReceipt === payment.id ? 'Downloading...' : 'Receipt' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import writerDashboardAPI from '@/api/writer-dashboard'
import writerManagementAPI from '@/api/writer-management'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const downloadingReceipt = ref(null)
const periodView = ref('monthly')
const filters = ref({
  dateFrom: '',
  dateTo: '',
  status: '',
  search: '',
})
const paymentsData = ref({
  historical_payments: {
    monthly: [],
    fortnightly: [],
  },
  upcoming_payments: {
    total_amount: 0,
    order_count: 0,
    orders: [],
  },
  recent_payments: [],
})

const upcomingPayments = computed(() => paymentsData.value.upcoming_payments)
const recentPayments = computed(() => paymentsData.value.recent_payments || [])
const paymentPeriods = computed(() => {
  if (periodView.value === 'monthly') {
    return paymentsData.value.historical_payments.monthly
  } else {
    return paymentsData.value.historical_payments.fortnightly
  }
})

const filteredPaymentPeriods = computed(() => {
  if (!filters.value.dateFrom && !filters.value.dateTo) {
    return paymentPeriods.value
  }
  const start = filters.value.dateFrom ? new Date(filters.value.dateFrom) : null
  const end = filters.value.dateTo ? new Date(filters.value.dateTo) : null
  return paymentPeriods.value.filter(period => {
    const periodStart = new Date(period.period_start || period.period || period.period_end)
    if (start && periodStart < start) return false
    if (end && periodStart > end) return false
    return true
  })
})

const filteredRecentPayments = computed(() => {
  return recentPayments.value.filter(payment => {
    const paymentDate = payment.payment_date ? new Date(payment.payment_date) : null
    if (filters.value.dateFrom && paymentDate && paymentDate < new Date(filters.value.dateFrom)) {
      return false
    }
    if (filters.value.dateTo && paymentDate && paymentDate > new Date(filters.value.dateTo)) {
      return false
    }
    if (filters.value.status) {
      const status = (payment.payment_status || payment.status || '').toLowerCase()
      if (status !== filters.value.status.toLowerCase()) {
        return false
      }
    }
    if (filters.value.search) {
      const query = filters.value.search.toLowerCase()
      const haystack = [
        payment.description,
        payment.order_id,
        payment.id,
      ].join(' ').toLowerCase()
      if (!haystack.includes(query)) {
        return false
      }
    }
    return true
  })
})

const loadPayments = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getPayments()
    paymentsData.value = response.data
  } catch (error) {
    console.error('Failed to load payments:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load payments. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatPeriod = (startDate, endDate) => {
  if (!startDate) return 'Unknown Period'
  
  const start = new Date(startDate)
  const end = endDate ? new Date(endDate) : null
  
  if (periodView.value === 'monthly') {
    return start.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  } else {
    // Fortnightly
    const startStr = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    if (end) {
      const endStr = end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      return `${startStr} - ${endStr}`
    }
    return startStr
  }
}

onMounted(() => {
  loadPayments()
})

const resetFilters = () => {
  filters.value = {
    dateFrom: '',
    dateTo: '',
    status: '',
    search: '',
  }
}

const downloadPaymentsCsv = () => {
  if (!filteredRecentPayments.value.length) {
    showError('No payments match the current filters.')
    return
  }
  const header = ['Payment ID', 'Order ID', 'Date', 'Amount', 'Status', 'Bonuses', 'Tips', 'Fines', 'Description']
  const rows = filteredRecentPayments.value.map(payment => [
    payment.id,
    payment.order_id || '',
    payment.payment_date || '',
    formatCurrency(payment.amount),
    payment.payment_status || payment.status || '',
    formatCurrency(payment.bonuses),
    formatCurrency(payment.tips),
    formatCurrency(payment.fines),
    (payment.description || '').replace(/"/g, '""'),
  ])

  const csv = [
    header.join(','),
    ...rows.map(row => row.map((value, idx) => idx === 8 ? `"${value}"` : value).join(',')),
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `writer_payments_${new Date().toISOString().split('T')[0]}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const downloadReceipt = async (payment) => {
  if (!payment || !payment.id) return
  
  downloadingReceipt.value = payment.id
  try {
    const response = await writerManagementAPI.downloadReceipt(payment.id)
    
    // Create blob from response
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `payment_receipt_${payment.id}_${new Date().toISOString().split('T')[0]}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    showSuccess('Receipt downloaded successfully!')
  } catch (error) {
    console.error('Receipt download error:', error)
    if (error.response?.status === 503) {
      showError('PDF generation is not available. Please contact support.')
    } else {
      const errorMsg = getErrorMessage(error, 'Failed to download receipt. Please try again.')
      showError(errorMsg)
    }
  } finally {
    downloadingReceipt.value = null
  }
}
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

