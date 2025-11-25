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
          v-for="period in paymentPeriods"
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
          v-for="payment in recentPayments"
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError } = useToast()

const loading = ref(false)
const periodView = ref('monthly')
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
const recentPayments = computed(() => paymentsData.value.recent_payments)
const paymentPeriods = computed(() => {
  if (periodView.value === 'monthly') {
    return paymentsData.value.historical_payments.monthly
  } else {
    return paymentsData.value.historical_payments.fortnightly
  }
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
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

