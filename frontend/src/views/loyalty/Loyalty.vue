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

    <!-- Convert Points Section - Enhanced -->
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200 rounded-xl p-6 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 mb-1">Convert Points to Wallet</h2>
          <p class="text-sm text-gray-600">Instantly convert your loyalty points to wallet balance</p>
        </div>
        <div class="p-3 bg-primary-100 rounded-full">
          <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 border border-primary-100">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end mb-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">Points to Convert</label>
            <div class="relative">
              <input
                v-model.number="convertPoints"
                type="number"
                min="1"
                :max="summary.loyalty_points || 0"
                class="w-full border-2 border-gray-300 rounded-lg px-4 py-3 pr-20 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                placeholder="Enter points"
              />
              <button
                @click="convertPoints = summary.loyalty_points || 0"
                class="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 text-xs font-medium text-primary-600 hover:text-primary-700 bg-primary-50 rounded"
              >
                Max
              </button>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Available: <span class="font-semibold text-primary-600">{{ summary.loyalty_points || 0 }} points</span>
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Wallet Amount</label>
            <div class="w-full border-2 border-green-200 rounded-lg px-4 py-3 bg-green-50 font-bold text-lg text-green-700">
              ${{ convertAmount.toFixed(2) }}
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Rate: {{ summary.conversion_rate || '0.00' }} pts = $1
            </p>
          </div>
          <div>
            <button
              @click="convertLoyaltyPoints"
              :disabled="converting || !convertPoints || convertPoints <= 0 || convertPoints > (summary.loyalty_points || 0)"
              class="w-full px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md hover:shadow-lg transform hover:scale-[1.02]"
            >
              <span v-if="converting" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Converting...
              </span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Convert Now
              </span>
            </button>
          </div>
        </div>
        
        <!-- Quick Convert Options -->
        <div class="flex flex-wrap gap-2 pt-4 border-t border-gray-200">
          <button
            v-for="option in quickConvertOptions"
            :key="option.label"
            @click="convertPoints = option.points"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            {{ option.label }}
          </button>
        </div>
        
        <!-- Auto-Convert Toggle -->
        <div class="mt-4 pt-4 border-t border-gray-200">
          <label class="flex items-center justify-between cursor-pointer">
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">Automatic Conversion</p>
              <p class="text-xs text-gray-500">Automatically convert points to wallet when you reach the minimum threshold</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                v-model="autoConvertEnabled"
                @change="saveAutoConvertPreference"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </label>
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
const autoConvertEnabled = ref(false)

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

const quickConvertOptions = computed(() => {
  const points = summary.value.loyalty_points || 0
  const rate = parseFloat(summary.value.conversion_rate) || 1
  const minPoints = Math.ceil(10 * rate) // Minimum for $10
  
  const options = []
  if (points >= minPoints) {
    options.push({ label: `$10 (${minPoints} pts)`, points: minPoints })
  }
  if (points >= minPoints * 2) {
    options.push({ label: `$25 (${Math.ceil(25 * rate)} pts)`, points: Math.ceil(25 * rate) })
  }
  if (points >= minPoints * 5) {
    options.push({ label: `$50 (${Math.ceil(50 * rate)} pts)`, points: Math.ceil(50 * rate) })
  }
  if (points >= minPoints * 10) {
    options.push({ label: `$100 (${Math.ceil(100 * rate)} pts)`, points: Math.ceil(100 * rate) })
  }
  return options
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

    // Initialize auto-convert preference from localStorage (client-only)
    if (typeof window !== 'undefined') {
      const stored = window.localStorage.getItem('loyalty_auto_convert')
      if (stored === 'true') {
        autoConvertEnabled.value = true
      } else if (stored === 'false') {
        autoConvertEnabled.value = false
      }
    }
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

const saveAutoConvertPreference = async () => {
  try {
    // Save preference to localStorage (or API if you have a user preferences endpoint)
    localStorage.setItem('loyalty_auto_convert', autoConvertEnabled.value ? 'true' : 'false')
    message.value = autoConvertEnabled.value 
      ? 'Automatic conversion enabled. Points will be converted when you reach the minimum threshold.'
      : 'Automatic conversion disabled.'
    messageSuccess.value = true
    setTimeout(() => {
      message.value = ''
    }, 5000)
  } catch (e) {
    console.error('Failed to save auto-convert preference:', e)
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

