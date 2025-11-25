<template>
  <div class="space-y-6">
    <PageHeader
      title="Payment Logs"
      subtitle="All payments made including wallet transactions"
      @refresh="loadTransactions"
    />

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'daily'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'daily'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Daily (Today)
        </button>
        <button
          @click="activeTab = 'weekly'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'weekly'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          This Week
        </button>
        <button
          @click="activeTab = 'monthly'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'monthly'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Monthly
        </button>
        <button
          @click="activeTab = 'all'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'all'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          All Payments
        </button>
      </nav>
    </div>

    <!-- Summary Cards for Monthly Tab -->
    <div v-if="activeTab === 'monthly'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card">
        <div class="text-sm text-gray-500">Total Amount</div>
        <div class="text-2xl font-bold text-primary-600">
          ${{ monthlySummary.totalAmount.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">{{ monthlySummary.totalTransactions }} transactions</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Months</div>
        <div class="text-2xl font-bold text-blue-600">
          {{ monthlySummary.monthCount }}
        </div>
        <div class="text-xs text-gray-400">active months</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Average per Month</div>
        <div class="text-2xl font-bold text-green-600">
          ${{ monthlySummary.averageAmount.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">per month</div>
      </div>
    </div>

    <!-- Summary Cards for Daily/Weekly Tabs -->
    <div v-if="activeTab === 'daily' || activeTab === 'weekly'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card">
        <div class="text-sm text-gray-500">Total Amount</div>
        <div class="text-2xl font-bold text-primary-600">
          ${{ periodSummary.totalAmount.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">{{ periodSummary.totalTransactions }} transactions</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Order Payments</div>
        <div class="text-2xl font-bold text-blue-600">
          ${{ periodSummary.orderPayments.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">{{ periodSummary.orderPaymentCount }} payments</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Wallet Transactions</div>
        <div class="text-2xl font-bold text-green-600">
          ${{ periodSummary.walletTransactions.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">{{ periodSummary.walletTransactionCount }} transactions</div>
      </div>
    </div>

    <FilterBar
      :filters="filterConfig"
      :loading="loading"
      @update:filter="updateFilter"
      @clear="clearFilters"
    >
      <template #filters>
        <select
          v-model="filters.website_id"
          class="border rounded px-3 py-2 text-sm"
          @change="() => loadTransactions(activeTab === 'monthly' || activeTab === 'all')"
        >
          <option value="">All Websites</option>
          <option v-for="website in websites" :key="website.id" :value="website.id">
            {{ website.name }}
          </option>
        </select>
        <select
          v-model="filters.payment_type"
          class="border rounded px-3 py-2 text-sm"
          @change="() => loadTransactions(activeTab === 'monthly' || activeTab === 'all')"
        >
          <option value="">All Types</option>
          <option value="order_payment">Order Payment</option>
          <option value="client_wallet">Client Wallet</option>
          <option value="writer_wallet">Writer Wallet</option>
        </select>
        <select
          v-model="filters.status"
          class="border rounded px-3 py-2 text-sm"
          @change="() => loadTransactions(activeTab === 'monthly' || activeTab === 'all')"
        >
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </template>
    </FilterBar>

    <!-- Monthly View -->
    <div v-if="activeTab === 'monthly'" class="space-y-6">
      <div
        v-for="month in monthlyGrouped"
        :key="month.monthKey"
        class="card"
      >
        <div class="flex items-center justify-between mb-4 pb-4 border-b">
          <div>
            <h3 class="font-semibold text-lg">{{ month.monthName }}</h3>
            <p class="text-sm text-gray-500">
              {{ month.transactions.length }} transactions
            </p>
          </div>
          <div class="text-right">
            <div class="text-2xl font-bold text-primary-600">
              ${{ month.totalAmount.toFixed(2) }}
            </div>
            <div class="text-xs text-gray-400">Total for month</div>
          </div>
        </div>
        <DataTable
          :columns="columns"
          :items="month.transactions"
          :loading="false"
          :pagination="null"
          @export="() => exportMonthToCSV(month)"
        />
      </div>
      <div v-if="!loading && monthlyGrouped.length === 0" class="text-center py-8 text-gray-500">
        No payments found for the selected period
      </div>
    </div>

    <!-- Daily, Weekly, and All View -->
    <div v-else class="card">
      <DataTable
        :columns="columns"
        :items="formattedTransactions"
        :loading="loading"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        @export="exportToCSV"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { debounce } from '@/utils/debounce'
import { exportToCSV } from '@/utils/export'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import DataTable from '@/components/common/DataTable.vue'
import paymentsAPI from '@/api/payments'
import apiClient from '@/api/client'

const loading = ref(false)
const transactions = ref([])
const allTransactions = ref([]) // Store all transactions for filtering
const websites = ref([])
const activeTab = ref('daily')
const filters = ref({
  search: '',
  website_id: '',
  payment_type: '',
  status: '',
  date_from: '',
  date_to: '',
  page: 1,
  page_size: 50,
})

const filterConfig = computed(() => [
  {
    key: 'search',
    label: 'Search',
    type: 'text',
    placeholder: 'Search transactions...',
  },
  {
    key: 'website_id',
    label: 'Website',
    type: 'select',
    options: [
      { value: '', label: 'All Websites' },
      ...websites.value.map(w => ({ value: w.id, label: w.name })),
    ],
  },
  {
    key: 'payment_type',
    label: 'Type',
    type: 'select',
    options: [
      { value: '', label: 'All Types' },
      { value: 'order_payment', label: 'Order Payment' },
      { value: 'client_wallet', label: 'Client Wallet' },
      { value: 'writer_wallet', label: 'Writer Wallet' },
    ],
  },
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { value: '', label: 'All Statuses' },
      { value: 'completed', label: 'Completed' },
      { value: 'pending', label: 'Pending' },
      { value: 'failed', label: 'Failed' },
    ],
  },
])
const pagination = ref({
  count: 0,
  next: null,
  previous: null,
})

const columns = computed(() => [
  { key: 'created_at', label: 'Date', sortable: true },
  { key: 'type', label: 'Type' },
  { key: 'client', label: 'Client/Writer' },
  { key: 'amount', label: 'Amount', sortable: true },
  { key: 'status', label: 'Status' },
  { key: 'payment_method', label: 'Method' },
  { key: 'reference_id', label: 'Reference' },
  { key: 'website', label: 'Website' },
])

// Calculate date ranges
const getDateRange = (tab) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  switch (tab) {
    case 'daily':
      return {
        date_from: today.toISOString().split('T')[0],
        date_to: new Date(today.getTime() + 24 * 60 * 60 * 1000 - 1).toISOString().split('T')[0],
      }
    case 'weekly':
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - today.getDay()) // Start of week (Sunday)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6) // End of week (Saturday)
      return {
        date_from: weekStart.toISOString().split('T')[0],
        date_to: weekEnd.toISOString().split('T')[0],
      }
    case 'monthly':
      // Get last 12 months
      const monthsAgo = new Date(today)
      monthsAgo.setMonth(today.getMonth() - 12)
      return {
        date_from: monthsAgo.toISOString().split('T')[0],
        date_to: today.toISOString().split('T')[0],
      }
    default:
      return { date_from: '', date_to: '' }
  }
}

const loadTransactions = async (loadAll = false) => {
  loading.value = true
  try {
    const dateRange = getDateRange(activeTab.value)
    const params = {}
    
    // For monthly and all, we might want to load more data
    if (loadAll || activeTab.value === 'monthly' || activeTab.value === 'all') {
      // Load all transactions without pagination for monthly view
      params.page_size = 1000
    } else {
      params.page = filters.value.page
      params.page_size = filters.value.page_size
    }
    
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website_id) params.website_id = filters.value.website_id
    if (filters.value.payment_type) params.payment_type = filters.value.payment_type
    if (filters.value.status) params.status = filters.value.status
    
    // Apply date range based on active tab
    if (activeTab.value !== 'all') {
      if (dateRange.date_from) params.date_from = dateRange.date_from
      if (dateRange.date_to) params.date_to = dateRange.date_to
    }

    const res = await paymentsAPI.getAllTransactions(params)
    const results = res.data.results || []
    
    // Store all transactions for filtering
    allTransactions.value = results
    
    // Apply client-side filtering
    let filtered = [...results]
    
    // Apply additional filters
    if (filters.value.website_id) {
      filtered = filtered.filter(t => t.website?.id === parseInt(filters.value.website_id))
    }
    if (filters.value.payment_type) {
      filtered = filtered.filter(t => t.type === filters.value.payment_type)
    }
    if (filters.value.status) {
      filtered = filtered.filter(t => t.status === filters.value.status)
    }
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      filtered = filtered.filter(t => 
        t.client?.email?.toLowerCase().includes(searchLower) ||
        t.client?.username?.toLowerCase().includes(searchLower) ||
        t.writer?.email?.toLowerCase().includes(searchLower) ||
        t.writer?.username?.toLowerCase().includes(searchLower) ||
        t.reference_id?.toLowerCase().includes(searchLower) ||
        t.transaction_id?.toLowerCase().includes(searchLower)
      )
    }
    
    transactions.value = filtered
    
    if (activeTab.value === 'all' && !loadAll) {
      pagination.value = {
        count: res.data.count || 0,
        next: res.data.next,
        previous: res.data.previous,
      }
    } else {
      pagination.value = {
        count: filtered.length,
        next: null,
        previous: null,
      }
    }
  } catch (e) {
    console.error('Failed to load transactions:', e)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const updateFilter = (key, value) => {
  filters.value[key] = value
  filters.value.page = 1
  loadTransactions(activeTab.value === 'monthly' || activeTab.value === 'all')
}

const clearFilters = () => {
  filters.value = {
    search: '',
    website_id: '',
    payment_type: '',
    status: '',
    date_from: '',
    date_to: '',
    page: 1,
    page_size: 50,
  }
  loadTransactions(activeTab.value === 'monthly' || activeTab.value === 'all')
}

const handlePageChange = (url) => {
  if (!url) return
  const urlObj = new URL(url)
  filters.value.page = parseInt(urlObj.searchParams.get('page')) || 1
  loadTransactions(activeTab.value === 'monthly' || activeTab.value === 'all')
}

const handlePageSizeChange = () => {
  filters.value.page = 1
  loadTransactions(activeTab.value === 'monthly' || activeTab.value === 'all')
}

// Format transaction data for display
const formatTransaction = (transaction) => {
  const date = new Date(transaction.created_at)
  return {
    ...transaction,
    client: transaction.client
      ? `${transaction.client.email} (${transaction.client.username})`
      : transaction.writer
      ? `${transaction.writer.email} (${transaction.writer.username})`
      : 'N/A',
    website: transaction.website ? `${transaction.website.name}` : 'N/A',
    created_at: date.toLocaleString(),
    created_at_date: date, // Keep original date for grouping
    amount: `$${transaction.amount.toFixed(2)}`,
    amountValue: transaction.amount, // Keep numeric value for calculations
  }
}

const formattedTransactions = computed(() => {
  return transactions.value.map(formatTransaction)
})

// Monthly grouping
const monthlyGrouped = computed(() => {
  const grouped = {}
  
  formattedTransactions.value.forEach(transaction => {
    const date = transaction.created_at_date || new Date(transaction.created_at)
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const monthName = date.toLocaleString('default', { month: 'long', year: 'numeric' })
    
    if (!grouped[monthKey]) {
      grouped[monthKey] = {
        monthKey,
        monthName,
        transactions: [],
        totalAmount: 0,
      }
    }
    
    grouped[monthKey].transactions.push(transaction)
    grouped[monthKey].totalAmount += transaction.amountValue || 0
  })
  
  // Sort transactions within each month by date descending
  Object.values(grouped).forEach(month => {
    month.transactions.sort((a, b) => {
      const dateA = a.created_at_date || new Date(a.created_at)
      const dateB = b.created_at_date || new Date(b.created_at)
      return dateB - dateA
    })
  })
  
  // Sort by month key descending (most recent first)
  return Object.values(grouped).sort((a, b) => b.monthKey.localeCompare(a.monthKey))
})

// Monthly summary
const monthlySummary = computed(() => {
  const totalAmount = monthlyGrouped.value.reduce((sum, month) => sum + month.totalAmount, 0)
  const totalTransactions = monthlyGrouped.value.reduce((sum, month) => sum + month.transactions.length, 0)
  const monthCount = monthlyGrouped.value.length
  const averageAmount = monthCount > 0 ? totalAmount / monthCount : 0
  
  return {
    totalAmount,
    totalTransactions,
    monthCount,
    averageAmount,
  }
})

// Period summary (daily/weekly)
const periodSummary = computed(() => {
  const orderPayments = formattedTransactions.value
    .filter(t => t.type === 'order_payment')
    .reduce((sum, t) => sum + (t.amountValue || 0), 0)
  
  const walletTransactions = formattedTransactions.value
    .filter(t => t.type === 'client_wallet' || t.type === 'writer_wallet')
    .reduce((sum, t) => sum + (t.amountValue || 0), 0)
  
  const totalAmount = orderPayments + walletTransactions
  const orderPaymentCount = formattedTransactions.value.filter(t => t.type === 'order_payment').length
  const walletTransactionCount = formattedTransactions.value.filter(t => t.type === 'client_wallet' || t.type === 'writer_wallet').length
  
  return {
    totalAmount,
    totalTransactions: formattedTransactions.value.length,
    orderPayments,
    orderPaymentCount,
    walletTransactions,
    walletTransactionCount,
  }
})

// Export functions
const exportMonthToCSV = (month) => {
  exportToCSV(month.transactions, `payments-${month.monthKey}.csv`)
}

// Watch for tab changes
watch(activeTab, () => {
  filters.value.page = 1
  loadTransactions(activeTab.value === 'monthly' || activeTab.value === 'all')
})

onMounted(async () => {
  await Promise.all([loadTransactions(true), loadWebsites()])
})
</script>

<style scoped>
@reference "tailwindcss";
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>

