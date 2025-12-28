<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Payments</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">View your payment history and manage payments</p>
    </div>

    <!-- Wallet Balance -->
    <div class="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white shadow-lg">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-primary-100 mb-1">Wallet Balance</p>
          <p class="text-3xl font-bold">${{ walletBalance.toFixed(2) }}</p>
        </div>
        <button
          @click="showAddFunds = true"
          class="px-6 py-3 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors font-medium"
        >
          Add Funds
        </button>
      </div>
    </div>

    <!-- Payments List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Payment History</h2>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="payments.length === 0" class="text-center py-12 text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p>No payments yet</p>
      </div>

      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="payment in payments"
          :key="payment.id"
          class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h3 class="font-semibold text-gray-900 dark:text-white">
                  {{ payment.order?.topic || `Order #${payment.order_id || 'N/A'}` }}
                </h3>
                <span
                  class="px-3 py-1 text-xs font-semibold rounded-full"
                  :class="payment.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'"
                >
                  {{ payment.status === 'completed' ? 'Paid' : 'Pending' }}
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ formatDate(payment.created_at) }} • {{ payment.payment_method || 'N/A' }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                ${{ (payment.amount || 0).toFixed(2) }}
              </p>
              <button
                v-if="payment.status !== 'completed'"
                @click="handlePayment(payment)"
                class="mt-2 px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Pay Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import paymentsAPI from '@/api/payments'
import walletAPI from '@/api/wallet'

const route = useRoute()

const loading = ref(true)
const payments = ref([])
const walletBalance = ref(0)
const showAddFunds = ref(false)

const fetchPayments = async () => {
  loading.value = true
  try {
    const params = { ordering: '-created_at' }
    if (route.query.order) {
      params.order_id = route.query.order
    }
    const response = await paymentsAPI.list(params)
    payments.value = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    console.error('Failed to fetch payments:', err)
    payments.value = []
  } finally {
    loading.value = false
  }
}

const fetchWalletBalance = async () => {
  try {
    const response = await walletAPI.getBalance()
    walletBalance.value = response.data.balance || response.data.wallet?.balance || 0
  } catch (err) {
    console.error('Failed to fetch wallet balance:', err)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const handlePayment = async (payment) => {
  try {
    // Redirect to payment page or initiate payment
    window.location.href = `/client/payments/${payment.id}/pay`
  } catch (err) {
    console.error('Failed to process payment:', err)
    alert(err.response?.data?.detail || 'Failed to process payment')
  }
}

onMounted(async () => {
  await Promise.all([fetchPayments(), fetchWalletBalance()])
})
</script>

