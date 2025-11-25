<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Loyalty Points Tracking</h1>
        <p class="mt-2 text-gray-600">Monitor how loyalty points are awarded, redeemed, and track client activity</p>
      </div>
    </div>

    <!-- Info Banner -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 class="font-semibold text-blue-900 mb-2">How Loyalty Points Work</h3>
      <p class="text-sm text-blue-800 mb-2">
        <strong>Important:</strong> Only clients can earn and redeem loyalty points. 
        Admins, superadmins, support, editors, and writers do not participate in the loyalty program.
      </p>
      <ul class="text-sm text-blue-800 list-disc list-inside space-y-1">
        <li><strong>Points Awarded:</strong> Clients earn points when they complete orders, receive successful referrals, or are manually awarded points by admins.</li>
        <li><strong>Points Redeemed:</strong> Clients can redeem points for discounts, rewards, or other benefits based on your configuration.</li>
        <li><strong>Points Deducted:</strong> Points may be deducted for refunds, cancellations, or administrative actions.</li>
      </ul>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-green-50 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Total Awarded</p>
        <p class="text-2xl font-bold text-green-900">{{ stats.total_points_awarded || 0 }}</p>
        <p class="text-xs text-green-600 mt-1">All time</p>
      </div>
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Total Redeemed</p>
        <p class="text-2xl font-bold text-red-900">{{ stats.total_points_redeemed || 0 }}</p>
        <p class="text-xs text-red-600 mt-1">All time</p>
      </div>
      <div class="card p-4 bg-blue-50 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Net Points</p>
        <p class="text-2xl font-bold text-blue-900">{{ stats.net_points || 0 }}</p>
        <p class="text-xs text-blue-600 mt-1">Awarded - Redeemed - Deducted</p>
      </div>
      <div class="card p-4 bg-purple-50 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Transactions</p>
        <p class="text-2xl font-bold text-purple-900">{{ stats.total_transactions || 0 }}</p>
        <p class="text-xs text-purple-600 mt-1">All transactions</p>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-yellow-50 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Last 24 Hours</p>
        <p class="text-xl font-bold text-yellow-900">{{ stats.points_awarded_24h || 0 }} points</p>
        <p class="text-xs text-yellow-600 mt-1">{{ stats.transactions_24h || 0 }} transactions</p>
      </div>
      <div class="card p-4 bg-orange-50 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Last 7 Days</p>
        <p class="text-xl font-bold text-orange-900">{{ stats.points_awarded_7d || 0 }} points</p>
        <p class="text-xs text-orange-600 mt-1">{{ stats.transactions_7d || 0 }} transactions</p>
      </div>
      <div class="card p-4 bg-indigo-50 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-1">Last 30 Days</p>
        <p class="text-xl font-bold text-indigo-900">{{ stats.points_awarded_30d || 0 }} points</p>
        <p class="text-xs text-indigo-600 mt-1">{{ stats.transactions_30d || 0 }} transactions</p>
      </div>
    </div>

    <!-- Award Sources Breakdown -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold mb-4">Points Award Sources</h3>
      <div v-if="awardSources" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="(points, source) in awardSources.award_sources" :key="source" class="border rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-gray-900">{{ awardSources.explanation[source] }}</span>
            <span class="text-2xl font-bold text-blue-600">{{ points }}</span>
          </div>
          <p class="text-xs text-gray-500">{{ source.replace('_', ' ').toUpperCase() }}</p>
        </div>
      </div>
      <button @click="loadAwardSources" class="mt-4 text-blue-600 hover:text-blue-800 text-sm">
        Refresh Sources
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Client username, email..."
            class="w-full border rounded px-3 py-2"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Type</label>
          <select v-model="filters.transaction_type" @change="loadTransactions" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="add">Awarded</option>
            <option value="redeem">Redeemed</option>
            <option value="deduct">Deducted</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadTransactions" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Transactions Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Explanation</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="transaction in transactions" :key="transaction.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ transaction.client_username || 'N/A' }}</div>
                  <div class="text-sm text-gray-500">{{ transaction.client_email || '' }}</div>
                </td>
                <td class="px-4 py-3">
                  <span :class="getTransactionTypeClass(transaction.transaction_type)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ transaction.transaction_type }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span :class="getPointsClass(transaction.transaction_type)" class="text-lg font-bold">
                    {{ transaction.transaction_type === 'add' ? '+' : '-' }}{{ transaction.points }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-700 max-w-md">
                    {{ transaction.explanation || transaction.reason || 'No explanation' }}
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  {{ formatDateTime(transaction.timestamp) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!transactions.length" class="text-center py-12 text-gray-500">
          No transactions found.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { loyaltyTrackingAPI } from '@/api'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'

const { showToast } = useToast()

const loading = ref(false)
const transactions = ref([])
const stats = ref({})
const awardSources = ref(null)
const websites = ref([])

const filters = ref({
  search: '',
  transaction_type: '',
  website: '',
})

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
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.transaction_type) params.transaction_type = filters.value.transaction_type
    if (filters.value.website) params.website = filters.value.website
    
    const res = await loyaltyTrackingAPI.listTransactions(params)
    transactions.value = res.data?.results || res.data || []
  } catch (e) {
    showToast('Failed to load transactions: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await loyaltyTrackingAPI.getStatistics()
    stats.value = res.data || {}
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const loadAwardSources = async () => {
  try {
    const res = await loyaltyTrackingAPI.getAwardSources()
    awardSources.value = res.data || {}
  } catch (e) {
    console.error('Failed to load award sources:', e)
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const resetFilters = () => {
  filters.value = { search: '', transaction_type: '', website: '' }
  loadTransactions()
}

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

const getTransactionTypeClass = (type) => {
  const classes = {
    add: 'bg-green-100 text-green-800',
    redeem: 'bg-blue-100 text-blue-800',
    deduct: 'bg-red-100 text-red-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getPointsClass = (type) => {
  const classes = {
    add: 'text-green-600',
    redeem: 'text-blue-600',
    deduct: 'text-red-600',
  }
  return classes[type] || 'text-gray-600'
}

onMounted(async () => {
  await Promise.all([loadTransactions(), loadStats(), loadAwardSources(), loadWebsites()])
})
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  padding: 1.5rem;
}
</style>

