<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">All Writer Payments</h1>
        <p class="mt-2 text-gray-600">Complete payment history from system start</p>
      </div>
      <div class="flex gap-2 flex-wrap md:justify-end">
        <router-link
          to="/admin/payments/batched"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Batched Payments
        </router-link>
        <router-link
          to="/admin/financial-overview"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Financial Overview
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadPayments" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="Paid">Paid</option>
            <option value="Pending">Pending</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadPayments"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            @change="loadPayments"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search Writer</label>
          <input
            v-model="filters.search"
            type="text"
            @input="debouncedSearch"
            placeholder="Name or email..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="summary" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Payments</p>
        <p class="text-3xl font-bold text-blue-900">{{ summary.total || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Total Amount</p>
        <p class="text-3xl font-bold text-green-900">${{ formatCurrency(summary.total_amount || 0) }}</p>
      </div>
    </div>

    <!-- Payments Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 text-xs">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Payment ID</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Writer</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider hidden md:table-cell">Email</th>
              <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Orders</th>
            <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Client Total</th>
            <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Writer Amount</th>
            <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Platform Margin</th>
              <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Tips</th>
              <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Fines</th>
              <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Total</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Date</th>
              <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Type</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Reference</th>
              <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="payment in payments" :key="payment.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-3 py-2 text-xs font-mono font-normal text-gray-900">{{ payment.payment_id }}</td>
              <td class="px-3 py-2 text-xs">
                <div class="font-medium text-gray-900">{{ payment.writer.name }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ payment.writer.registration_id }}</div>
              </td>
              <td class="px-3 py-2 text-xs text-gray-600 hidden md:table-cell font-normal">{{ payment.writer.email }}</td>
              <td class="px-3 py-2 text-xs text-center font-medium text-gray-900">{{ payment.number_of_orders }}</td>
              <td class="px-3 py-2 text-xs text-right font-medium text-gray-900">
                ${{ formatCurrency(payment.client_total) }}
              </td>
              <td class="px-3 py-2 text-xs text-right font-medium text-gray-900">
                ${{ formatCurrency(payment.amount) }}
              </td>
              <td class="px-3 py-2 text-xs text-right font-medium" :class="payment.platform_margin >= 0 ? 'text-green-600' : 'text-red-600'">
                ${{ formatCurrency(payment.platform_margin) }}
              </td>
              <td class="px-3 py-2 text-xs text-right font-medium text-green-600">${{ formatCurrency(payment.tips) }}</td>
              <td class="px-3 py-2 text-xs text-right font-medium text-red-600">${{ formatCurrency(payment.fines) }}</td>
              <td class="px-3 py-2 text-xs text-right font-semibold text-gray-900">${{ formatCurrency(payment.total_earnings) }}</td>
              <td class="px-3 py-2 text-xs text-gray-600 font-normal">{{ formatDate(payment.date) }}</td>
              <td class="px-3 py-2 text-xs text-center">
                <span :class="getStatusClass(payment.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ payment.status }}
                </span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-600 font-normal">{{ payment.type }}</td>
              <td class="px-3 py-2 text-xs font-mono text-gray-500 font-normal">{{ payment.reference }}</td>
              <td class="px-3 py-2 text-xs text-center">
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="viewPaymentBreakdown(payment.id)"
                    class="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                  >
                    View
                  </button>
                  <button
                    v-if="authStore.isAdmin || authStore.isSuperAdmin"
                    @click="openAdjustModal(payment)"
                    class="text-purple-600 hover:text-purple-800 hover:underline font-medium"
                    title="Adjust Payment Amount"
                  >
                    Adjust
                  </button>
                  <button
                    v-if="payment.status === 'Pending' && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                    @click="markPaymentAsPaid(payment.id)"
                    :disabled="markingAsPaid"
                    class="text-green-600 hover:text-green-800 hover:underline font-medium"
                  >
                    {{ markingAsPaid ? 'Processing...' : 'Mark Paid' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!loading && payments.length === 0" class="text-center py-12 text-gray-500">
          No payments found.
        </div>
      </div>
    </div>

    <!-- Payment Breakdown Modal (reuse from BatchedWriterPayments) -->
    <div v-if="showBreakdownModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold">Payment Breakdown</h3>
            <button @click="showBreakdownModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div v-if="breakdownLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="paymentBreakdown" class="space-y-6">
            <!-- Payment Summary -->
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Payment ID:</span>
                  <div class="font-mono font-medium">{{ paymentBreakdown.reference_code }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Writer:</span>
                  <div class="font-medium">{{ paymentBreakdown.writer.full_name }}</div>
                  <div class="text-xs text-gray-500">{{ paymentBreakdown.writer.registration_id }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Status:</span>
                  <div>
                    <span :class="getStatusClass(paymentBreakdown.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ paymentBreakdown.status }}
                    </span>
                  </div>
                </div>
                <div>
                  <span class="text-gray-600">Date:</span>
                  <div class="font-medium">{{ formatDateTime(paymentBreakdown.payment_date) }}</div>
                </div>
              </div>
            </div>

            <!-- Summary Stats -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div class="text-sm text-blue-700 mb-1">Total Orders</div>
                <div class="text-2xl font-bold text-blue-900">{{ paymentBreakdown.summary.total_orders }}</div>
              </div>
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <div class="text-sm text-green-700 mb-1">Total Tips</div>
                <div class="text-2xl font-bold text-green-900">${{ formatCurrency(paymentBreakdown.summary.total_tips) }}</div>
              </div>
              <div class="bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="text-sm text-red-700 mb-1">Total Fines</div>
                <div class="text-2xl font-bold text-red-900">${{ formatCurrency(paymentBreakdown.summary.total_fines) }}</div>
              </div>
              <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div class="text-sm text-purple-700 mb-1">Net Earnings</div>
                <div class="text-2xl font-bold text-purple-900">${{ formatCurrency(paymentBreakdown.summary.net_earnings) }}</div>
              </div>
            </div>

            <!-- Orders -->
            <div>
              <h4 class="text-lg font-semibold mb-3">Orders ({{ paymentBreakdown.orders.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completed</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="order in paymentBreakdown.orders" :key="order.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-mono">#{{ order.id }}</td>
                      <td class="px-4 py-3 text-sm">{{ order.topic || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm">
                        <span :class="getStatusClass(order.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                          {{ order.status }}
                        </span>
                      </td>
                      <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(order.amount_paid) }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(order.completed_at) }}</td>
                      <td class="px-4 py-3 text-sm">
                        <router-link
                          :to="`/orders/${order.id}`"
                          class="text-blue-600 hover:underline"
                        >
                          View
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Tips -->
            <div v-if="paymentBreakdown.tips && paymentBreakdown.tips.length > 0">
              <h4 class="text-lg font-semibold mb-3">Tips ({{ paymentBreakdown.tips.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="tip in paymentBreakdown.tips" :key="tip.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-medium text-green-600">${{ formatCurrency(tip.amount) }}</td>
                      <td class="px-4 py-3 text-sm">
                        <router-link
                          v-if="tip.order_id"
                          :to="`/orders/${tip.order_id}`"
                          class="text-blue-600 hover:underline"
                        >
                          #{{ tip.order_id }}
                        </router-link>
                        <span v-else class="text-gray-400">Direct Tip</span>
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ tip.reason || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(tip.sent_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Fines -->
            <div v-if="paymentBreakdown.fines && paymentBreakdown.fines.length > 0">
              <h4 class="text-lg font-semibold mb-3">Fines ({{ paymentBreakdown.fines.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="fine in paymentBreakdown.fines" :key="fine.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-medium text-red-600">${{ formatCurrency(fine.amount) }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ fine.fine_type || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ fine.reason || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(fine.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Adjustment Modal -->
    <PaymentAdjustmentModal
      :is-open="showAdjustModal"
      :payment="selectedPayment"
      @close="closeAdjustModal"
      @success="handleAdjustmentSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import financialOverviewAPI from '@/api/financial-overview'
import writerPaymentsAPI from '@/api/writer-payments'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'
import PaymentAdjustmentModal from '@/components/admin/PaymentAdjustmentModal.vue'

const authStore = useAuthStore()

const loading = ref(false)
const payments = ref([])
const summary = ref(null)
const showBreakdownModal = ref(false)
const paymentBreakdown = ref(null)
const breakdownLoading = ref(false)
const markingAsPaid = ref(false)
const showAdjustModal = ref(false)
const selectedPayment = ref(null)

const filters = ref({
  status: '',
  date_from: '',
  date_to: '',
  search: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadPayments()
  }, 500)
}

const loadPayments = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) {
      params.status = filters.value.status
    }
    if (filters.value.date_from) {
      params.date_from = filters.value.date_from
    }
    if (filters.value.date_to) {
      params.date_to = filters.value.date_to
    }

    const response = await financialOverviewAPI.getAllPayments(params)
    let allPayments = response.data.payments || []
    
    // Client-side search filter
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      allPayments = allPayments.filter(p => 
        p.writer.name.toLowerCase().includes(searchLower) ||
        p.writer.email.toLowerCase().includes(searchLower) ||
        p.writer.registration_id.toLowerCase().includes(searchLower)
      )
    }
    
    payments.value = allPayments
    summary.value = {
      total: allPayments.length,
      total_amount: response.data.total_amount || 0,
    }
  } catch (error) {
    console.error('Failed to load payments:', error)
  } finally {
    loading.value = false
  }
}

const viewPaymentBreakdown = async (paymentId) => {
  breakdownLoading.value = true
  showBreakdownModal.value = true
  try {
    const response = await writerPaymentsAPI.getPaymentBreakdown(paymentId)
    paymentBreakdown.value = response.data
  } catch (error) {
    console.error('Failed to load payment breakdown:', error)
    alert('Failed to load payment breakdown: ' + (error.response?.data?.detail || error.message))
  } finally {
    breakdownLoading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    date_from: '',
    date_to: '',
    search: '',
  }
  loadPayments()
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getStatusClass = (status) => {
  const statusMap = {
    'Paid': 'bg-green-100 text-green-800',
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Blocked': 'bg-red-100 text-red-800',
    'Delayed': 'bg-orange-100 text-orange-800',
    'Voided': 'bg-gray-100 text-gray-800',
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

const markPaymentAsPaid = async (paymentId) => {
  if (!confirm('Are you sure you want to mark this payment as paid?')) {
    return
  }
  
  markingAsPaid.value = true
  try {
    await apiClient.post(`/writer-wallet/scheduled-payments/${paymentId}/mark-as-paid/`)
    alert('Payment marked as paid successfully!')
    await loadPayments()
  } catch (error) {
    console.error('Failed to mark payment as paid:', error)
    alert('Failed to mark payment as paid: ' + (error.response?.data?.error || error.message))
  } finally {
    markingAsPaid.value = false
  }
}

const openAdjustModal = (payment) => {
  // Map payment data to match modal expectations
  selectedPayment.value = {
    id: payment.payment_id || payment.id,
    amount: payment.amount || payment.total_earnings,
    writer_name: payment.writer?.name || 'Unknown',
    order_id: payment.order_id,
    payment_set_by: payment.payment_set_by
  }
  showAdjustModal.value = true
}

const closeAdjustModal = () => {
  showAdjustModal.value = false
  selectedPayment.value = null
}

const handleAdjustmentSuccess = async (data) => {
  alert('Payment adjusted successfully!')
  await loadPayments()
  closeAdjustModal()
}

onMounted(() => {
  loadPayments()
})
</script>

