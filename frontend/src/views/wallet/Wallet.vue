<template>
  <div class="space-y-6">
    <!-- Header -->
    <PageHeader
      title="My Wallet"
      subtitle="Manage your wallet balance, view transactions, and make payments"
      @refresh="loadWallet"
    />

    <!-- Messages -->
    <div v-if="message" class="p-4 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="p-4 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Wallet Balance Card -->
    <div class="bg-linear-to-r from-primary-500 to-blue-600 p-6 rounded-lg shadow-lg text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium opacity-90 mb-2">Available Balance</p>
          <p class="text-5xl font-bold">${{ (wallet?.balance || 0).toFixed(2) }}</p>
          <p class="text-sm opacity-75 mt-2">{{ wallet?.currency || 'USD' }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm font-medium opacity-90 mb-2">Loyalty Points</p>
          <p class="text-3xl font-bold">{{ wallet?.loyalty_points || 0 }}</p>
          <button 
            v-if="wallet?.loyalty_points > 0"
            @click="showConvertLoyaltyModal = true"
            class="mt-2 text-xs underline opacity-90 hover:opacity-100"
          >
            Convert to Balance
          </button>
        </div>
      </div>
    </div>

    <!-- Fund Sources Summary -->
    <div v-if="wallet" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
        <div class="text-sm font-medium text-gray-600 mb-1">From Your Payments</div>
        <div class="text-2xl font-bold text-green-600">
          ${{ clientPaymentsTotal.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Total you've added</div>
      </div>
      <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
        <div class="text-sm font-medium text-gray-600 mb-1">Company Credits</div>
        <div class="text-2xl font-bold text-blue-600">
          ${{ companyCreditsTotal.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Bonuses, refunds, adjustments</div>
      </div>
      <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
        <div class="text-sm font-medium text-gray-600 mb-1">Used for Payments</div>
        <div class="text-2xl font-bold text-orange-600">
          ${{ walletUsageTotal.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Total spent from wallet</div>
      </div>
    </div>

    <!-- Top Up Section -->
    <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
      <div class="mb-4">
        <h2 class="text-xl font-semibold text-gray-900">Top Up Wallet</h2>
        <p class="text-sm text-gray-600 mt-1">Add funds to your wallet for faster checkout</p>
      </div>

      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
            <label class="block text-sm font-medium mb-1">Amount ($) *</label>
            <input 
              v-model.number="topUpAmount" 
              type="number" 
              min="1" 
              step="0.01" 
              required 
              class="w-full border rounded px-3 py-2"
              placeholder="Enter amount (e.g., 50.00)"
            />
            <p class="text-xs text-gray-500 mt-1">Minimum: $1.00</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Description (optional)</label>
            <input 
              v-model="topUpDescription" 
              type="text" 
              class="w-full border rounded px-3 py-2"
              placeholder="e.g., Payment for future orders"
            />
          </div>
        </div>
        <div class="flex gap-2">
          <button 
            @click="topUpWallet"
            :disabled="!topUpAmount || topUpAmount <= 0 || toppingUp"
            class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ toppingUp ? 'Processing...' : `Top Up $${(topUpAmount || 0).toFixed(2)}` }}
          </button>
          <button 
            @click="resetTopUpForm"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Clear
        </button>
        </div>
        <div class="p-3 bg-blue-50 rounded border border-blue-200">
          <p class="text-sm text-blue-800">
            <strong>Note:</strong> After clicking "Top Up", you'll be redirected to complete the payment. 
            Funds will be added to your wallet once payment is confirmed.
          </p>
        </div>
      </div>
    </div>

    <!-- Payment Information -->
    <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Paying from Wallet</h2>
      <div class="space-y-4">
        <div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 class="font-semibold text-blue-900 mb-2">How to Pay with Wallet</h3>
          <ol class="list-decimal list-inside space-y-2 text-sm text-blue-800">
            <li>Create a new order or go to checkout</li>
            <li>Select "Pay with Wallet" as your payment method</li>
            <li>If your wallet balance covers the full amount, payment will be processed automatically</li>
            <li>If your balance is insufficient, you can pay partially from wallet and use another payment method for the remainder</li>
            <li>Wallet balance will be deducted immediately upon order confirmation</li>
          </ol>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 class="font-semibold text-green-900 mb-2">✅ Full Payment</h4>
            <p class="text-sm text-green-800">
              If your wallet balance is sufficient, you can pay the entire order amount from your wallet.
            </p>
          </div>
          <div class="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <h4 class="font-semibold text-yellow-900 mb-2">💰 Partial Payment</h4>
            <p class="text-sm text-yellow-800">
              If your balance is less than the order total, you can use your wallet balance first, then pay the remainder with another method.
            </p>
          </div>
        </div>
        <div class="flex gap-2">
          <router-link 
            to="/orders/new"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Create New Order
          </router-link>
          <router-link 
            to="/orders"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            View My Orders
          </router-link>
        </div>
      </div>
      </div>

    <!-- Wallet Usage Guidelines -->
    <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Wallet Usage Guidelines</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="text-lg font-medium text-green-700 mb-3 flex items-center">
            <span class="mr-2">✅</span> What You CAN Do
          </h3>
          <ul class="space-y-2 text-sm text-gray-700">
            <li class="flex items-start">
              <span class="mr-2 text-green-600">•</span>
              <span>Top up your wallet with any amount ($1 minimum)</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-green-600">•</span>
              <span>Use wallet balance to pay for orders (full or partial payment)</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-green-600">•</span>
              <span>View complete transaction history with source tracking</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-green-600">•</span>
              <span>Convert loyalty points to wallet balance (when available)</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-green-600">•</span>
              <span>Receive refunds directly to your wallet</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-green-600">•</span>
              <span>Track funds from your payments vs company credits</span>
            </li>
          </ul>
        </div>
        <div>
          <h3 class="text-lg font-medium text-red-700 mb-3 flex items-center">
            <span class="mr-2">❌</span> What You CANNOT Do
          </h3>
          <ul class="space-y-2 text-sm text-gray-700">
            <li class="flex items-start">
              <span class="mr-2 text-red-600">•</span>
              <span>Withdraw funds from wallet (non-refundable)</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-red-600">•</span>
              <span>Transfer wallet balance to another account</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-red-600">•</span>
              <span>Use wallet for non-order related payments</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-red-600">•</span>
              <span>Manually adjust your own wallet balance</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-red-600">•</span>
              <span>Use wallet balance for subscription payments (if applicable)</span>
            </li>
            <li class="flex items-start">
              <span class="mr-2 text-red-600">•</span>
              <span>Request refunds of wallet top-ups (company credits may have restrictions)</span>
            </li>
          </ul>
        </div>
      </div>
      <div class="mt-4 p-3 bg-yellow-50 rounded border border-yellow-200">
        <p class="text-sm text-yellow-800">
          <strong>Important:</strong> Wallet funds do not expire. Company credits (bonuses, adjustments) 
          may have specific terms. Contact support if you have questions about your wallet balance.
        </p>
      </div>
    </div>

    <!-- Transaction History -->
    <FilterBar
      :filters="transactionFilters"
      v-model="transactionFiltersModel"
      @change="applyTransactionFilters"
      :debounce-ms="0"
    />

    <DataTable
      title="Transaction History"
      subtitle="All wallet transactions with source tracking"
      :columns="transactionColumns"
      :data="filteredTransactions"
      :loading="transactionsLoading"
      empty-message="No transactions found."
      :show-export="true"
      :pagination="transactionPagination"
      @export="exportTransactions"
      @page-change="(url) => url && loadMoreTransactions(url)"
    >
      <template #cell-transaction_type="{ row }">
        <span :class="getTransactionTypeClass(row.transaction_type)" class="px-2 py-1 rounded text-xs font-medium">
          {{ formatTransactionType(row.transaction_type) }}
        </span>
      </template>
      <template #cell-source="{ row }">
        <span :class="getSourceClass(row.source)" class="px-2 py-1 rounded text-xs font-medium">
          {{ formatSource(row.source) }}
                </span>
      </template>
      <template #cell-amount="{ row }">
        <span :class="row.is_credit ? 'text-green-600 font-bold' : 'text-red-600 font-bold'" class="text-sm">
          {{ row.is_credit ? '+' : '-' }}${{ Math.abs(parseFloat(row.amount || 0)).toFixed(2) }}
                </span>
      </template>
    </DataTable>

    <!-- Convert Loyalty Points Modal -->
    <div v-if="showConvertLoyaltyModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold">Convert Loyalty Points</h2>
          <button @click="showConvertLoyaltyModal = false" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div class="space-y-4">
          <div class="p-4 bg-blue-50 rounded border border-blue-200">
            <p class="text-sm text-blue-800">
              You have <strong>{{ wallet?.loyalty_points || 0 }}</strong> loyalty points available for conversion.
            </p>
          </div>
          <div class="flex gap-2">
            <button 
              @click="convertLoyaltyPoints"
              :disabled="convertingLoyalty"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
            >
              {{ convertingLoyalty ? 'Converting...' : 'Convert to Wallet Balance' }}
            </button>
            <button 
              @click="showConvertLoyaltyModal = false"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import walletAPI from '@/api/wallet'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import DataTable from '@/components/common/DataTable.vue'
import { exportToCSV } from '@/utils/export'

const wallet = ref(null)
const transactions = ref([])
const filteredTransactions = ref([])
const transactionsLoading = ref(true)
const loading = ref(true)

const topUpAmount = ref(0)
const topUpDescription = ref('')
const toppingUp = ref(false)
const showTopUpForm = ref(true)
const showConvertLoyaltyModal = ref(false)
const convertingLoyalty = ref(false)

const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const transactionFiltersModel = ref({
  source: '',
  type: ''
})
const transactionPagination = ref(null)

const transactionFilters = [
  {
    key: 'source',
    label: 'Source',
    type: 'select',
    options: [
      { value: '', label: 'All Sources' },
      { value: 'client_payment', label: 'My Payments' },
      { value: 'company_credit', label: 'Company Credits' },
      { value: 'wallet_usage', label: 'Wallet Usage' },
      { value: 'credit', label: 'Credits Only' },
      { value: 'debit', label: 'Debits Only' }
    ]
  },
  {
    key: 'type',
    label: 'Type',
    type: 'select',
    options: [
      { value: '', label: 'All Types' },
      { value: 'top-up', label: 'Top-Up' },
      { value: 'payment', label: 'Payment' },
      { value: 'refund', label: 'Refund' },
      { value: 'bonus', label: 'Bonus' },
      { value: 'adjustment', label: 'Adjustment' },
      { value: 'referral_bonus', label: 'Referral Bonus' },
      { value: 'loyalty_conversion', label: 'Loyalty Conversion' }
    ]
  }
]

const transactionColumns = [
  { key: 'created_at', label: 'Date', format: 'date' },
  { key: 'transaction_type', label: 'Type' },
  { key: 'source', label: 'Source' },
  { key: 'amount', label: 'Amount', align: 'right' },
  { key: 'description', label: 'Description' },
  { key: 'reference_id', label: 'Reference' }
]

// Computed totals
const clientPaymentsTotal = computed(() => {
  return transactions.value
    .filter(tx => tx.source === 'client_payment' && tx.is_credit)
    .reduce((sum, tx) => sum + Math.abs(parseFloat(tx.amount || 0)), 0)
})

const companyCreditsTotal = computed(() => {
  return transactions.value
    .filter(tx => tx.source === 'company_credit' && tx.is_credit)
    .reduce((sum, tx) => sum + Math.abs(parseFloat(tx.amount || 0)), 0)
})

const walletUsageTotal = computed(() => {
  return transactions.value
    .filter(tx => tx.source === 'wallet_usage' && !tx.is_credit)
    .reduce((sum, tx) => sum + Math.abs(parseFloat(tx.amount || 0)), 0)
})

const loadWallet = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await walletAPI.getWallet()
    wallet.value = res.data.wallet || res.data
    // Load transactions from wallet response or separate call
    if (res.data.transactions) {
      transactions.value = Array.isArray(res.data.transactions) ? res.data.transactions : []
      filteredTransactions.value = filterTransactions(transactions.value)
    } else {
      // Load transactions separately
      await loadTransactions()
    }
  } catch (e) {
    console.error('Failed to load wallet:', e)
    error.value = e?.response?.data?.detail || 'Failed to load wallet'
  } finally {
    loading.value = false
  }
}

const loadTransactions = async () => {
  transactionsLoading.value = true
  try {
    const res = await walletAPI.getTransactions({})
    if (res.data?.results) {
      transactions.value = Array.isArray(res.data.results) ? res.data.results : []
      transactionPagination.value = {
        count: res.data.count,
        next: res.data.next,
        previous: res.data.previous,
        current_page: extractPageNumber(res.data.next) || 1,
        page_size: 25,
        total_pages: Math.ceil((res.data.count || transactions.value.length) / 25)
      }
    } else if (res.data?.transactions) {
      transactions.value = Array.isArray(res.data.transactions) ? res.data.transactions : []
      transactionPagination.value = null
    } else {
      transactions.value = []
      transactionPagination.value = null
    }
    filteredTransactions.value = filterTransactions(transactions.value)
  } catch (e) {
    console.error('Failed to load transactions:', e)
    transactions.value = []
    transactionPagination.value = null
  } finally {
    transactionsLoading.value = false
  }
}

const applyTransactionFilters = () => {
  filteredTransactions.value = filterTransactions(transactions.value)
}

const filterTransactions = (txs) => {
  let filtered = [...txs]
  
  if (transactionFiltersModel.value.source) {
    if (transactionFiltersModel.value.source === 'credit') {
      filtered = filtered.filter(tx => tx.is_credit)
    } else if (transactionFiltersModel.value.source === 'debit') {
      filtered = filtered.filter(tx => !tx.is_credit)
    } else {
      filtered = filtered.filter(tx => tx.source === transactionFiltersModel.value.source)
    }
  }
  
  if (transactionFiltersModel.value.type) {
    filtered = filtered.filter(tx => tx.transaction_type === transactionFiltersModel.value.type)
  }
  
  return filtered
}

const loadMoreTransactions = async (url) => {
  if (!url) return
  
  try {
    const urlObj = new URL(url)
    const params = {}
    urlObj.searchParams.forEach((value, key) => {
      params[key] = value
    })
    
    const res = await walletAPI.getTransactions(params)
    if (res.data?.results) {
      transactions.value = [...transactions.value, ...res.data.results]
      transactionPagination.value = {
        count: res.data.count,
        next: res.data.next,
        previous: res.data.previous,
        current_page: extractPageNumber(res.data.next) || (res.data.previous ? extractPageNumber(res.data.previous) + 1 : 1),
        page_size: 25,
        total_pages: Math.ceil((res.data.count || transactions.value.length) / 25)
      }
      filteredTransactions.value = filterTransactions(transactions.value)
    }
  } catch (e) {
    console.error('Failed to load more transactions:', e)
  }
}

const extractPageNumber = (url) => {
  if (!url) return 1
  try {
    const urlObj = new URL(url)
    const page = urlObj.searchParams.get('page')
    return page ? parseInt(page) : 1
  } catch {
    return 1
  }
}

const topUpWallet = async () => {
  if (!topUpAmount.value || topUpAmount.value <= 0) return
  toppingUp.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await walletAPI.topUp(topUpAmount.value, topUpDescription.value)
    message.value = res.data.detail || `Wallet topped up successfully! $${topUpAmount.value.toFixed(2)} added.`
    messageSuccess.value = true
    resetTopUpForm()
    await loadWallet()
    await loadTransactions()
    setTimeout(() => {
      message.value = ''
    }, 5000)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to top up wallet'
  } finally {
    toppingUp.value = false
  }
}

const resetTopUpForm = () => {
  topUpAmount.value = 0
  topUpDescription.value = ''
}

const convertLoyaltyPoints = async () => {
  convertingLoyalty.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await walletAPI.convertLoyaltyPoints()
    message.value = res.data.detail || 'Loyalty points converted successfully!'
    messageSuccess.value = true
    showConvertLoyaltyModal.value = false
    await loadWallet()
    await loadTransactions()
    setTimeout(() => {
      message.value = ''
    }, 5000)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to convert loyalty points'
  } finally {
    convertingLoyalty.value = false
  }
}

const exportTransactions = () => {
  exportToCSV(filteredTransactions.value, 'wallet_transactions', [
    'created_at', 'transaction_type', 'source', 'amount', 'description', 'reference_id'
  ])
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatTransactionType = (type) => {
  const typeMap = {
    'top-up': 'Top-Up',
    'payment': 'Payment',
    'refund': 'Refund',
    'bonus': 'Bonus',
    'adjustment': 'Adjustment',
    'referral_bonus': 'Referral Bonus',
    'loyalty_conversion': 'Loyalty Conversion',
  }
  return typeMap[type] || type
}

const formatSource = (source) => {
  const sourceMap = {
    'client_payment': 'My Payment',
    'company_credit': 'Company Credit',
    'wallet_usage': 'Wallet Usage',
    'other': 'Other',
  }
  return sourceMap[source] || source
}

const getTransactionTypeClass = (type) => {
  const typeMap = {
    'top-up': 'bg-green-100 text-green-800',
    'payment': 'bg-red-100 text-red-800',
    'refund': 'bg-blue-100 text-blue-800',
    'bonus': 'bg-purple-100 text-purple-800',
    'adjustment': 'bg-yellow-100 text-yellow-800',
    'referral_bonus': 'bg-pink-100 text-pink-800',
    'loyalty_conversion': 'bg-indigo-100 text-indigo-800',
  }
  return typeMap[type] || 'bg-gray-100 text-gray-800'
}

const getSourceClass = (source) => {
  const sourceMap = {
    'client_payment': 'bg-green-100 text-green-800',
    'company_credit': 'bg-blue-100 text-blue-800',
    'wallet_usage': 'bg-orange-100 text-orange-800',
    'other': 'bg-gray-100 text-gray-800',
  }
  return sourceMap[source] || 'bg-gray-100 text-gray-800'
}

// Watch filters to update filtered transactions
watch(() => transactionFiltersModel.value, () => {
  applyTransactionFilters()
}, { deep: true })

onMounted(async () => {
  await Promise.all([loadWallet(), loadTransactions()])
})
</script>
