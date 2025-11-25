<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-gray-900">Loyalty Program</h1>

    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="p-3 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Loyalty Points</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">{{ summary.loyalty_points || 0 }}</p>
          </div>
          <div class="p-3 bg-purple-100 rounded-lg">
            <span class="text-2xl">⭐</span>
          </div>
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Wallet Balance</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">${{ (summary.wallet_balance || 0).toFixed(2) }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-lg">
            <span class="text-2xl">💰</span>
          </div>
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Current Tier</p>
            <p class="mt-2 text-lg font-bold text-gray-900">{{ summary.tier || 'None' }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-lg">
            <span class="text-2xl">🏆</span>
          </div>
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Conversion Rate</p>
            <p class="mt-2 text-lg font-bold text-gray-900">{{ summary.conversion_rate || '0.00' }} pts = $1</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-lg">
            <span class="text-2xl">🔄</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Convert Points Section -->
    <div class="card p-6">
      <h2 class="text-xl font-semibold mb-4">Convert Points to Wallet</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Points to Convert</label>
          <input
            v-model.number="convertPoints"
            type="number"
            min="1"
            :max="summary.loyalty_points || 0"
            class="w-full border rounded-lg px-4 py-3"
            placeholder="Enter points"
          />
          <p class="text-xs text-gray-500 mt-1">
            Available: {{ summary.loyalty_points || 0 }} points
          </p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Wallet Amount</label>
          <div class="w-full border rounded-lg px-4 py-3 bg-gray-50">
            ${{ convertAmount.toFixed(2) }}
          </div>
        </div>
        <div>
          <button
            @click="convertLoyaltyPoints"
            :disabled="converting || !convertPoints || convertPoints <= 0 || convertPoints > (summary.loyalty_points || 0)"
            class="w-full px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ converting ? 'Converting...' : 'Convert' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'transactions'"
          :class="[
            activeTab === 'transactions'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Transactions
        </button>
        <button
          @click="activeTab = 'redemption'"
          :class="[
            activeTab === 'redemption'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Redeem Points
        </button>
        <button
          @click="activeTab = 'requests'"
          :class="[
            activeTab === 'requests'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Redemption Requests
        </button>
      </nav>
    </div>

    <!-- Transactions Tab -->
    <div v-if="activeTab === 'transactions'" class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Transaction History</h2>
        <button @click="loadTransactions" class="text-sm text-primary-600 hover:underline">Refresh</button>
      </div>

      <div v-if="transactionsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!transactions.length" class="text-center py-12">
        <p class="text-gray-500">No transactions yet.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="tx in transactions" :key="tx.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(tx.timestamp || tx.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getTransactionTypeClass(tx.transaction_type)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ tx.transaction_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="tx.points > 0 ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ tx.points > 0 ? '+' : '' }}{{ tx.points }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ tx.reason || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Redemption Tab -->
    <div v-if="activeTab === 'redemption'" class="space-y-6">
      <LoyaltyRedemption
        :points-balance="summary.loyalty_points || 0"
        @redemption-success="handleRedemptionSuccess"
        @points-updated="handlePointsUpdated"
      />
    </div>

    <!-- Redemption Requests Tab -->
    <div v-if="activeTab === 'requests'" class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Redemption Requests</h2>
        <button @click="loadRedemptionRequests" class="text-sm text-primary-600 hover:underline">Refresh</button>
      </div>

      <div v-if="requestsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!redemptionRequests.length" class="text-center py-12">
        <p class="text-gray-500">No redemption requests yet.</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="req in redemptionRequests" :key="req.id" class="border rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <div>
              <h3 class="font-semibold">{{ req.item_name }}</h3>
              <p class="text-sm text-gray-500">{{ req.item_points }} points</p>
            </div>
            <span :class="getRequestStatusClass(req.status)" class="px-3 py-1 rounded-full text-xs font-medium">
              {{ req.status }}
            </span>
          </div>
          <div class="text-sm text-gray-600 mb-2">
            Requested: {{ formatDate(req.created_at) }}
          </div>
          <div v-if="req.status === 'pending'" class="flex gap-2">
            <button
              @click="cancelRequest(req.id)"
              class="text-sm text-red-600 hover:underline"
            >
              Cancel Request
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import loyaltyAPI from '@/api/loyalty'
import LoyaltyRedemption from '@/components/loyalty/LoyaltyRedemption.vue'

const activeTab = ref('transactions')

const summary = ref({
  loyalty_points: 0,
  wallet_balance: 0,
  tier: 'None',
  conversion_rate: '0.00',
})
const summaryLoading = ref(true)

const convertPoints = ref(0)
const converting = ref(false)

const transactions = ref([])
const transactionsLoading = ref(true)

const redemptionItems = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const redemptionLoading = ref(true)
const redeeming = ref(false)

const redemptionRequests = ref([])
const requestsLoading = ref(true)

const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const convertAmount = computed(() => {
  if (!convertPoints.value || !summary.value.conversion_rate) return 0
  const rate = parseFloat(summary.value.conversion_rate) || 0
  return rate > 0 ? convertPoints.value / rate : 0
})

const filteredItems = computed(() => {
  if (!selectedCategory.value) return redemptionItems.value
  return redemptionItems.value.filter(item => item.category === selectedCategory.value)
})

const loadSummary = async () => {
  summaryLoading.value = true
  try {
    const res = await loyaltyAPI.getSummary()
    summary.value = res.data || summary.value
  } catch (e) {
    console.error('Failed to load summary:', e)
    error.value = 'Failed to load loyalty summary'
  } finally {
    summaryLoading.value = false
  }
}

const loadTransactions = async () => {
  transactionsLoading.value = true
  try {
    const res = await loyaltyAPI.getTransactions({})
    transactions.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load transactions:', e)
    error.value = 'Failed to load transactions'
  } finally {
    transactionsLoading.value = false
  }
}

const loadRedemptionItems = async () => {
  redemptionLoading.value = true
  try {
    const [itemsRes, catsRes] = await Promise.all([
      loyaltyAPI.getRedemptionItems({}),
      loyaltyAPI.getRedemptionCategories({}),
    ])
    redemptionItems.value = Array.isArray(itemsRes.data?.results) ? itemsRes.data.results : (itemsRes.data || [])
    categories.value = Array.isArray(catsRes.data?.results) ? catsRes.data.results : (catsRes.data || [])
  } catch (e) {
    console.error('Failed to load redemption items:', e)
  } finally {
    redemptionLoading.value = false
  }
}

const loadRedemptionRequests = async () => {
  requestsLoading.value = true
  try {
    const res = await loyaltyAPI.getRedemptionRequests({})
    redemptionRequests.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load redemption requests:', e)
  } finally {
    requestsLoading.value = false
  }
}

const convertLoyaltyPoints = async () => {
  if (!convertPoints.value || convertPoints.value <= 0) return
  converting.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await loyaltyAPI.convertPoints(convertPoints.value)
    message.value = `Successfully converted ${res.data.converted} points to $${res.data.amount}`
    messageSuccess.value = true
    convertPoints.value = 0
    await loadSummary()
    await loadTransactions()
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to convert points'
  } finally {
    converting.value = false
  }
}

const handleRedemptionSuccess = (data) => {
  message.value = `Redemption request created successfully!`
  messageSuccess.value = true
  loadSummary()
  loadRedemptionRequests()
}

const handlePointsUpdated = (newBalance) => {
  summary.value.loyalty_points = newBalance
}

const cancelRequest = async (id) => {
  try {
    await loyaltyAPI.cancelRedemptionRequest(id)
    message.value = 'Redemption request cancelled'
    messageSuccess.value = true
    await loadRedemptionRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to cancel request'
  }
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

const getTransactionTypeClass = (type) => {
  if (type === 'add' || type === 'award') return 'bg-green-100 text-green-700'
  if (type === 'deduct' || type === 'redeem') return 'bg-red-100 text-red-700'
  return 'bg-gray-100 text-gray-700'
}

const getRequestStatusClass = (status) => {
  if (status === 'approved' || status === 'fulfilled') return 'bg-green-100 text-green-700'
  if (status === 'rejected' || status === 'cancelled') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

onMounted(async () => {
  await Promise.all([
    loadSummary(),
    loadTransactions(),
    loadRedemptionItems(),
    loadRedemptionRequests(),
  ])
})
</script>

