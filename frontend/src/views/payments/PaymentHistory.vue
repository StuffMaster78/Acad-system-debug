<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Payment History</h1>
        <p class="mt-2 text-gray-600">View all your payment transactions and receipts</p>
      </div>
      <div class="flex items-center gap-2">
        <ExportButton
          v-if="authStore.isAdmin || authStore.isSuperAdmin"
          :export-function="exportPayments"
          :export-params="exportParams"
          filename="payments"
          @exported="handleExportSuccess"
          @error="handleExportError"
        />
        <button
          @click="loadTransactions"
          :disabled="loading"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Total Paid</p>
        <p class="text-2xl font-bold text-green-900">${{ formatCurrency(stats.totalPaid) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">This Month</p>
        <p class="text-2xl font-bold text-blue-900">${{ formatCurrency(stats.thisMonth) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Transactions</p>
        <p class="text-2xl font-bold text-purple-900">{{ stats.totalTransactions }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Payment Type</label>
          <select v-model="filters.payment_type" @change="loadTransactions" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="standard">Standard Order</option>
            <option value="special_order">Special Order</option>
            <option value="class_payment">Class Payment</option>
            <option value="wallet_transaction">Wallet Transaction</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadTransactions" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadTransactions"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            @change="loadTransactions"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Order ID, Reference..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && transactions.length === 0" class="card p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="ml-3 text-gray-600">Loading transactions...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="transactions.length === 0" class="card p-12 text-center">
      <p class="text-gray-500 text-lg">No transactions found</p>
      <p class="text-gray-400 text-sm mt-2">Your payment history will appear here</p>
    </div>

    <!-- Transactions List -->
    <div v-else class="space-y-4">
      <div
        v-for="transaction in transactions"
        :key="transaction.id"
        class="card p-6 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <span
                class="px-3 py-1 rounded-full text-xs font-medium"
                :class="getTypeClass(transaction.type)"
              >
                {{ getTypeLabel(transaction.type) }}
              </span>
              <span
                class="px-3 py-1 rounded-full text-xs font-medium"
                :class="getStatusClass(transaction.status)"
              >
                {{ formatStatus(transaction.status) }}
              </span>
              <span
                v-if="transaction.payment_method"
                class="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
              >
                {{ formatPaymentMethod(transaction.payment_method) }}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <span class="text-sm font-medium text-gray-600">Amount:</span>
                <p class="text-lg font-bold text-gray-900">${{ formatCurrency(transaction.amount) }}</p>
              </div>
              <div v-if="transaction.order_id">
                <span class="text-sm font-medium text-gray-600">Order:</span>
                <router-link
                  :to="`/orders/${transaction.order_id}`"
                  class="text-primary-600 hover:text-primary-700 font-medium"
                >
                  #{{ transaction.order_id }}
                </router-link>
              </div>
              <div>
                <span class="text-sm font-medium text-gray-600">Date:</span>
                <p class="text-gray-900">{{ formatDateTime(transaction.created_at) }}</p>
              </div>
            </div>

            <div v-if="transaction.reference_id || transaction.transaction_id" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div v-if="transaction.reference_id">
                <span class="text-gray-600">Reference:</span>
                <span class="ml-2 font-mono text-gray-700">{{ transaction.reference_id }}</span>
              </div>
              <div v-if="transaction.transaction_id">
                <span class="text-gray-600">Transaction ID:</span>
                <span class="ml-2 font-mono text-gray-700">{{ transaction.transaction_id }}</span>
              </div>
            </div>

            <div v-if="transaction.confirmed_at" class="mt-2 text-sm text-gray-500">
              Confirmed: {{ formatDateTime(transaction.confirmed_at) }}
            </div>
          </div>

          <div class="ml-4 flex flex-col gap-2">
            <button
              @click="viewTransaction(transaction)"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            >
              View Details
            </button>
            <button
              v-if="transaction.status === 'completed'"
              @click="downloadReceipt(transaction)"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
            >
              Download Receipt
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <Pagination
      v-if="pagination && pagination.totalItems > 0"
      :current-page="pagination.currentPage || 1"
      :total-items="pagination.totalItems || transactions.length"
      :items-per-page="pagination.itemsPerPage || 50"
      @page-change="handlePageChange"
    />

    <!-- Transaction Detail Modal -->
    <Modal
      :visible="showDetailModal"
      title="Transaction Details"
      size="lg"
      @update:visible="showDetailModal = $event"
    >
      <div v-if="selectedTransaction" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-sm font-medium text-gray-600">Transaction Type:</span>
            <p class="text-gray-900">{{ getTypeLabel(selectedTransaction.type) }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Status:</span>
            <p class="text-gray-900">{{ formatStatus(selectedTransaction.status) }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Amount:</span>
            <p class="text-lg font-bold text-gray-900">${{ formatCurrency(selectedTransaction.amount) }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Payment Method:</span>
            <p class="text-gray-900">{{ formatPaymentMethod(selectedTransaction.payment_method) }}</p>
          </div>
          <div v-if="selectedTransaction.order_id">
            <span class="text-sm font-medium text-gray-600">Order ID:</span>
            <router-link
              :to="`/orders/${selectedTransaction.order_id}`"
              class="text-primary-600 hover:text-primary-700"
            >
              #{{ selectedTransaction.order_id }}
            </router-link>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Date:</span>
            <p class="text-gray-900">{{ formatDateTime(selectedTransaction.created_at) }}</p>
          </div>
          <div v-if="selectedTransaction.reference_id">
            <span class="text-sm font-medium text-gray-600">Reference ID:</span>
            <p class="font-mono text-gray-900">{{ selectedTransaction.reference_id }}</p>
          </div>
          <div v-if="selectedTransaction.transaction_id">
            <span class="text-sm font-medium text-gray-600">Transaction ID:</span>
            <p class="font-mono text-gray-900">{{ selectedTransaction.transaction_id }}</p>
          </div>
          <div v-if="selectedTransaction.confirmed_at">
            <span class="text-sm font-medium text-gray-600">Confirmed At:</span>
            <p class="text-gray-900">{{ formatDateTime(selectedTransaction.confirmed_at) }}</p>
          </div>
        </div>
      </div>

      <template #footer>
        <button
          @click="showDetailModal = false"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Close
        </button>
        <button
          v-if="selectedTransaction && selectedTransaction.status === 'completed'"
          @click="downloadReceipt(selectedTransaction)"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Download Receipt
        </button>
      </template>
    </Modal>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import paymentsAPI from '@/api/payments'
import exportsAPI from '@/api/exports'
import Pagination from '@/components/common/Pagination.vue'
import Modal from '@/components/common/Modal.vue'
import ExportButton from '@/components/common/ExportButton.vue'

const authStore = useAuthStore()
const loading = ref(false)
const transactions = ref([])
const pagination = ref(null)
const stats = ref({
  totalPaid: 0,
  thisMonth: 0,
  totalTransactions: 0
})

const filters = ref({
  payment_type: '',
  status: '',
  date_from: '',
  date_to: '',
  search: ''
})

const showDetailModal = ref(false)
const selectedTransaction = ref(null)
const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadTransactions()
  }, 500)
}

const loadTransactions = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.payment_type) params.payment_type = filters.value.payment_type
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    if (filters.value.search) params.search = filters.value.search

    const res = await paymentsAPI.getAllTransactions(params)
    
    if (res.data.results) {
      transactions.value = res.data.results
      pagination.value = {
        currentPage: res.data.current_page || res.data.page || 1,
        totalItems: res.data.count || res.data.total || transactions.value.length,
        itemsPerPage: res.data.page_size || res.data.pageSize || 50
      }
    } else {
      transactions.value = res.data || []
      pagination.value = {
        currentPage: 1,
        totalItems: transactions.value.length,
        itemsPerPage: 50
      }
    }

    calculateStats()
  } catch (error) {
    showMessage('Failed to load transactions: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)

  const completed = transactions.value.filter(t => t.status === 'completed')
  
  stats.value = {
    totalPaid: completed.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0),
    thisMonth: completed
      .filter(t => new Date(t.created_at) >= startOfMonth)
      .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0),
    totalTransactions: transactions.value.length
  }
}

const viewTransaction = (transaction) => {
  selectedTransaction.value = transaction
  showDetailModal.value = true
}

const downloadReceipt = async (transaction) => {
  try {
    loading.value = true
    const response = await paymentsAPI.downloadReceipt(transaction.id)
    
    // Create a blob from the response
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `receipt_${transaction.reference_id || transaction.transaction_id}_${new Date().toISOString().split('T')[0]}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    showMessage('Receipt downloaded successfully', true)
  } catch (error) {
    console.error('Receipt download error:', error)
    if (error.response?.status === 503) {
      showMessage('PDF generation is not available. Please contact support.', false)
    } else {
      showMessage('Failed to download receipt: ' + (error.response?.data?.error || error.response?.data?.detail || error.message), false)
    }
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  if (pagination.value) {
    pagination.value.currentPage = page
  }
  loadTransactions()
}

const getTypeLabel = (type) => {
  const labels = {
    order_payment: 'Order Payment',
    client_wallet: 'Wallet Transaction',
    writer_payment: 'Writer Payment'
  }
  return labels[type] || type
}

const getTypeClass = (type) => {
  const classes = {
    order_payment: 'bg-blue-100 text-blue-800',
    client_wallet: 'bg-green-100 text-green-800',
    writer_payment: 'bg-purple-100 text-purple-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusClass = (status) => {
  const classes = {
    completed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatStatus = (status) => {
  if (!status) return 'N/A'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatPaymentMethod = (method) => {
  if (!method) return 'N/A'
  const methods = {
    wallet: 'Wallet',
    stripe: 'Credit/Debit Card',
    paypal: 'PayPal',
    bank_transfer: 'Bank Transfer',
    manual: 'Manual Payment'
  }
  return methods[method] || method
}

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

// Export functionality
const exportParams = computed(() => {
  const params = {}
  if (filters.value.payment_type) params.payment_type = filters.value.payment_type
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.date_from) params.date_from = filters.value.date_from
  if (filters.value.date_to) params.date_to = filters.value.date_to
  return params
})

const exportPayments = exportsAPI.exportPayments

const handleExportSuccess = (data) => {
  showMessage(`Successfully exported ${data.filename}`, true)
}

const handleExportError = (error) => {
  showMessage('Failed to export: ' + (error.response?.data?.error || error.message), false)
}

onMounted(() => {
  loadTransactions()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1rem;
}
</style>

