<template>
  <div class="space-y-6">
    <PageHeader
      title="Advance Payments"
      description="Request advance payments against your expected earnings"
    />

    <!-- Eligibility Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold mb-4 dark:text-white">Your Advance Eligibility</h2>
      <div v-if="loadingEligibility" class="text-center py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      </div>
      <div v-else-if="eligibility" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gray-50 dark:bg-gray-700 rounded p-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">Expected Earnings</div>
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatCurrency(eligibility.expected_earnings) }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 rounded p-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">Max Advance ({{ eligibility.max_percentage }}%)</div>
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatCurrency(eligibility.max_advance_amount) }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 rounded p-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">Outstanding Advances</div>
          <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {{ formatCurrency(eligibility.outstanding_advances) }}
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 rounded p-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">Available Advance</div>
          <div class="text-2xl font-bold text-green-600 dark:text-green-400">
            {{ formatCurrency(eligibility.available_advance) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Request Advance Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold mb-4 dark:text-white">Request Advance</h2>
      <form @submit.prevent="handleRequestAdvance" class="space-y-4">
        <div>
          <label for="advance-amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Amount ($)
          </label>
          <input
            id="advance-amount"
            name="advance-amount"
            v-model.number="requestForm.amount"
            type="number"
            step="0.01"
            min="0.01"
            :max="eligibility?.available_advance || 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary dark:bg-gray-700 dark:text-white"
            required
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Maximum: {{ formatCurrency(eligibility?.available_advance || 0) }}
          </p>
        </div>
        <div>
          <label for="advance-reason" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Reason (Optional)
          </label>
          <textarea
            id="advance-reason"
            name="advance-reason"
            v-model="requestForm.reason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary dark:bg-gray-700 dark:text-white"
            placeholder="Brief reason for advance request..."
          ></textarea>
        </div>
        <button
          type="submit"
          :disabled="loading || !eligibility || requestForm.amount > (eligibility.available_advance || 0) || !requestForm.amount || requestForm.amount <= 0"
          class="w-full flex items-center justify-center gap-2 bg-primary-600 text-white py-3 px-6 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold text-lg shadow-md hover:shadow-lg"
        >
          <span v-if="!loading">💳</span>
          <span v-if="loading" class="animate-spin">⏳</span>
          <span>{{ loading ? 'Processing...' : 'Request Advance' }}</span>
        </button>
      </form>
    </div>

    <!-- Request History -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold dark:text-white">Request History</h2>
      </div>
      <div v-if="loadingRequests" class="p-6 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      </div>
      <div v-else-if="requests.length === 0" class="p-6 text-center text-gray-500 dark:text-gray-400">
        No advance requests yet
      </div>
      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="request in requests"
          :key="request.id"
          class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <StatusBadge :status="request.status" />
                <span class="text-lg font-semibold dark:text-white">
                  {{ formatCurrency(request.requested_amount) }}
                </span>
                <span v-if="request.approved_amount && request.approved_amount < request.requested_amount" 
                      class="text-sm text-blue-600 dark:text-blue-400">
                  (Counteroffer: {{ formatCurrency(request.approved_amount) }})
                </span>
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <div>Requested: {{ formatDate(request.requested_at) }}</div>
                <div v-if="request.approved_amount">
                  Approved: {{ formatCurrency(request.approved_amount) }}
                </div>
                <div v-if="request.disbursed_amount">
                  Disbursed: {{ formatCurrency(request.disbursed_amount) }}
                </div>
                <div v-if="request.outstanding_amount > 0" class="text-orange-600 dark:text-orange-400">
                  Outstanding: {{ formatCurrency(request.outstanding_amount) }}
                </div>
                <div v-if="request.reason" class="mt-2 italic">
                  "{{ request.reason }}"
                </div>
                <div v-if="request.review_notes" class="mt-2 text-sm">
                  <strong>Admin Notes:</strong> {{ request.review_notes }}
                </div>
              </div>
            </div>
            <div class="text-right">
              <div v-if="request.status === 'repaid'" class="text-green-600 dark:text-green-400 font-semibold">
                Fully Repaid
              </div>
            </div>
          </div>
          <!-- Deductions Timeline -->
          <div v-if="request.deductions && request.deductions.length > 0" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div class="text-sm font-medium mb-2 dark:text-white">Repayment History:</div>
            <div class="space-y-2">
              <div
                v-for="deduction in request.deductions"
                :key="deduction.id"
                class="text-sm text-gray-600 dark:text-gray-400"
              >
                {{ formatCurrency(deduction.amount_deducted) }} deducted on {{ formatDate(deduction.deducted_at) }}
                <span v-if="deduction.order_number" class="text-gray-500 dark:text-gray-500">
                  (Order #{{ deduction.order_number }})
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import writerAdvanceAPI from '@/api/writer-advance'
import writerManagementAPI from '@/api/writer-management'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const { success, error } = useToast()
const authStore = useAuthStore()

// Get website ID from multiple sources
const getWebsiteId = () => {
  // First, try to get from user's profile in authStore
  const user = authStore.user
  if (user) {
    if (user.website_id) {
      return String(user.website_id)
    }
    if (user.website?.id) {
      return String(user.website.id)
    }
    if (typeof user.website === 'number') {
      return String(user.website)
    }
    if (typeof user.website === 'string') {
      const parsed = parseInt(user.website)
      if (!isNaN(parsed)) {
        return String(parsed)
      }
    }
    // Check writer profile if available
    if (user.writer_profile?.website_id) {
      return String(user.writer_profile.website_id)
    }
    if (user.writer_profile?.website?.id) {
      return String(user.writer_profile.website.id)
    }
  }
  
  // Fallback to localStorage
  const storedWebsite = localStorage.getItem('current_website')
  if (storedWebsite) {
    return storedWebsite
  }
  
  // Also check website_id in localStorage (set by auth store)
  const storedWebsiteId = localStorage.getItem('website_id')
  if (storedWebsiteId) {
    return storedWebsiteId
  }
  
  // No website found - return null (will be handled by error messages)
  return null
}

// Format currency amount
const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '0.00'
  return parseFloat(amount).toFixed(2)
}

// Format date string
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const loadingEligibility = ref(false)
const loadingRequests = ref(false)
const loading = ref(false)
const eligibility = ref(null)
const requests = ref([])

const requestForm = ref({
  amount: null,
  reason: ''
})

const loadEligibility = async () => {
  loadingEligibility.value = true
  try {
    let websiteId = getWebsiteId()
    
    // If no website ID found, try to get it from writer profile
    if (!websiteId) {
      try {
        const profileResponse = await writerManagementAPI.getMyProfile()
        const profile = profileResponse.data
        if (profile?.website_id) {
          websiteId = String(profile.website_id)
          // Store it for future use
          localStorage.setItem('current_website', websiteId)
        } else if (profile?.website?.id) {
          websiteId = String(profile.website.id)
          localStorage.setItem('current_website', websiteId)
        }
      } catch (e) {
        console.warn('Could not fetch writer profile for website ID:', e)
      }
    }
    
    if (!websiteId) {
      error('Website context is required. Please refresh the page or contact support.')
      return
    }
    
    const response = await writerAdvanceAPI.getEligibility({
      website: websiteId
    })
    eligibility.value = response.data
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || 'Failed to load eligibility'
    error(errorMsg)
    console.error('Eligibility error:', err)
  } finally {
    loadingEligibility.value = false
  }
}

const loadRequests = async () => {
  loadingRequests.value = true
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      // Don't show error for requests, just return empty array
      requests.value = []
      return
    }
    
    const response = await writerAdvanceAPI.listRequests({
      website: websiteId
    })
    requests.value = response.data.results || response.data || []
  } catch (err) {
    // Suppress 400 errors for missing website (non-critical)
    if (err.response?.status !== 400) {
      error(err.response?.data?.detail || 'Failed to load requests')
    }
    requests.value = []
  } finally {
    loadingRequests.value = false
  }
}

const handleRequestAdvance = async () => {
  if (!requestForm.value.amount || requestForm.value.amount <= 0) {
    error('Please enter a valid amount')
    return
  }

  if (eligibility.value && requestForm.value.amount > eligibility.value.available_advance) {
    error(`Amount exceeds available advance of $${formatCurrency(eligibility.value.available_advance)}`)
    return
  }

  const websiteId = getWebsiteId()
  if (!websiteId) {
    error('Website context is required. Please refresh the page.')
    return
  }

  loading.value = true
  try {
    await writerAdvanceAPI.requestAdvance({
      amount: requestForm.value.amount,
      reason: requestForm.value.reason,
      website: websiteId
    })
    success('Advance request submitted successfully')
    requestForm.value = { amount: null, reason: '' }
    await loadEligibility()
    await loadRequests()
  } catch (err) {
    error(err.response?.data?.detail || 'Failed to submit request')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEligibility()
  loadRequests()
})
</script>

