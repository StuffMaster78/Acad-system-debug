<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-gray-900">Referrals</h1>

    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="p-3 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Not a client message -->
    <div v-if="notClientMessage" class="p-4 rounded-lg bg-yellow-50 border border-yellow-200">
      <div class="flex items-start">
        <span class="text-2xl mr-3">⚠️</span>
        <div>
          <h3 class="font-semibold text-yellow-900 mb-1">Access Restricted</h3>
          <p class="text-sm text-yellow-800">{{ notClientMessage }}</p>
        </div>
      </div>
    </div>

    <!-- Only show referral content for clients -->
    <template v-if="isClient">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Referred</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">{{ stats.total_referred || 0 }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-lg">
            <span class="text-2xl">👥</span>
          </div>
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Completed Orders</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">{{ stats.completed_orders || 0 }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-lg">
            <span class="text-2xl">✅</span>
          </div>
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Referral Code</p>
            <p class="mt-2 text-lg font-bold text-gray-900">{{ stats.referral_code || 'Not generated' }}</p>
          </div>
          <div class="p-3 bg-purple-100 rounded-lg">
            <span class="text-2xl">🎁</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Referral Link Sharing Component -->
    <ReferralLinkSharing
      :referral-code="stats.referral_code"
      :referral-link="stats.referral_link"
    />

    <!-- Referral Code & Link Section (Legacy - can be removed if ReferralLinkSharing covers everything) -->
    <div class="card p-6" style="display: none;">
      <h2 class="text-xl font-semibold mb-4">Your Referral Code</h2>
      <div v-if="stats.referral_code" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Referral Code</label>
          <div class="flex items-center gap-3">
            <input
              :value="stats.referral_code"
              readonly
              class="flex-1 border rounded-lg px-4 py-3 bg-gray-50 font-mono text-lg"
            />
            <button
              @click="copyToClipboard(stats.referral_code)"
              class="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy Code
            </button>
          </div>
        </div>
        <div v-if="stats.referral_link">
          <label class="block text-sm font-medium text-gray-700 mb-2">Referral Link</label>
          <div class="flex items-center gap-3">
            <input
              :value="stats.referral_link"
              readonly
              class="flex-1 border rounded-lg px-4 py-3 bg-gray-50 font-mono text-sm"
            />
            <button
              @click="copyToClipboard(stats.referral_link)"
              class="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy Link
            </button>
          </div>
        </div>
        <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-blue-800">
            <strong>Share your referral link:</strong> When someone signs up using your link, you both get rewards!
          </p>
        </div>
      </div>
      <div v-else class="text-center py-8">
        <p v-if="!isClient" class="text-gray-600 mb-4 text-yellow-600">
          Only clients can generate referral codes. Your current role does not have permission.
        </p>
        <p v-else class="text-gray-600 mb-4">You don't have a referral code yet.</p>
        <button
          v-if="isClient"
          @click="generateCode"
          :disabled="generating || loading"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ generating ? 'Generating...' : (loading ? 'Checking...' : 'Generate Referral Code') }}
        </button>
        <p v-if="generating && isClient" class="text-sm text-gray-500 mt-2">Checking database and generating code...</p>
      </div>
    </div>

    <!-- Manual Referral Entry -->
    <div v-if="isClient" class="card p-6">
      <h2 class="text-xl font-semibold mb-4">Refer Someone by Email</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Enter the email address of the person you want to refer
          </label>
          <div class="flex gap-3">
            <input
              v-model="referralEmail"
              type="email"
              placeholder="friend@example.com"
              class="flex-1 border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              :disabled="referring"
              @keyup.enter="submitReferral"
            />
            <button
              @click="submitReferral"
              :disabled="referring || !referralEmail"
              class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ referring ? 'Referring...' : 'Refer' }}
            </button>
          </div>
          <p class="mt-2 text-sm text-gray-500">
            Enter the email of someone who doesn't have an account yet. They'll receive an invitation email with your referral link.
          </p>
        </div>
      </div>
    </div>

    <!-- Referrals List -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Your Referrals</h2>
        <button @click="loadReferrals" class="text-sm text-primary-600 hover:underline">Refresh</button>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!referrals.length" class="text-center py-12">
        <p class="text-gray-500">No referrals yet. Share your referral link to get started!</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Referee</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code Used</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bonus</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="ref in referrals" :key="ref.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ ref.referee?.email || ref.referee?.username || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-500 font-mono">{{ ref.referral_code || '—' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ formatDate(ref.created_at) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(ref)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ getStatusText(ref) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="ref.bonus_awarded" class="text-sm text-green-600 font-medium">✓ Awarded</span>
                <span v-else class="text-sm text-gray-400">Pending</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- How It Works -->
    <div class="card p-6 bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200">
      <h2 class="text-xl font-semibold mb-4">How Referrals Work</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">1</div>
          <div>
            <h3 class="font-semibold mb-1">Share Your Link</h3>
            <p class="text-sm text-gray-600">Copy and share your unique referral link with friends and family.</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">2</div>
          <div>
            <h3 class="font-semibold mb-1">They Sign Up</h3>
            <p class="text-sm text-gray-600">When someone signs up using your link, they become your referral.</p>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">3</div>
          <div>
            <h3 class="font-semibold mb-1">Earn Rewards</h3>
            <p class="text-sm text-gray-600">You earn bonuses when your referrals complete their first order!</p>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import referralsAPI from '@/api/referrals'
import ReferralLinkSharing from '@/components/referrals/ReferralLinkSharing.vue'

const authStore = useAuthStore()

// Check if user is a client - only clients can use referrals
const isClient = computed(() => {
  const role = authStore.user?.role || authStore.userRole
  return role === 'client'
})

// Show message if not a client
const notClientMessage = computed(() => {
  if (!isClient.value) {
    const role = authStore.user?.role || authStore.userRole || 'unknown'
    return `Referrals and loyalty points are only available for clients. Your role (${role}) does not have access to this feature.`
  }
  return null
})

const loading = ref(true)
const statsLoading = ref(false)
const generating = ref(false)
const referring = ref(false)
const referralEmail = ref('')
const referrals = ref([])
const stats = ref({
  total_referred: 0,
  completed_orders: 0,
  referral_code: null,
  referral_link: null,
})
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const getWebsiteId = () => {
  // Try different possible field names for website ID
  const user = authStore.user
  if (!user) {
    console.warn('No user found in authStore')
    return null
  }
  
  // Debug: log user object to see what fields are available
  console.log('User object for website ID:', {
    website_id: user.website_id,
    website: user.website,
    has_website_object: !!user.website,
    website_type: typeof user.website
  })
  
  // Check various possible field names
  if (user.website_id) {
    console.log('Using user.website_id:', user.website_id)
    return user.website_id
  }
  if (user.website?.id) {
    console.log('Using user.website.id:', user.website.id)
    return user.website.id
  }
  if (typeof user.website === 'number') {
    console.log('Using user.website (number):', user.website)
    return user.website
  }
  if (typeof user.website === 'string') {
    const parsed = parseInt(user.website)
    if (!isNaN(parsed)) {
      console.log('Using user.website (parsed string):', parsed)
      return parsed
    }
  }
  
  // Try to get from localStorage as fallback
  const storedWebsite = localStorage.getItem('current_website')
  if (storedWebsite) {
    const parsed = parseInt(storedWebsite)
    if (!isNaN(parsed)) {
      console.log('Using localStorage current_website:', parsed)
      return parsed
    }
  }
  
  // No website found
  console.warn('No website ID found for user:', user)
  return null
}

const loadStats = async () => {
  statsLoading.value = true
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      error.value = 'Website ID is required. Please contact support or refresh the page.'
      statsLoading.value = false
      return
    }
    const res = await referralsAPI.getStats(websiteId)
    stats.value = res.data || stats.value
    error.value = ''
  } catch (e) {
    console.error('Failed to load stats:', e)
    const errorMsg = e?.response?.data?.error || e?.response?.data?.message || e.message
    const status = e?.response?.status
    
    // Handle specific error cases
    if (status === 404 && errorMsg?.includes('Website not found')) {
      error.value = `Website ID ${getWebsiteId()} not found. Please contact support.`
    } else if (errorMsg && errorMsg.includes('Website is required')) {
      error.value = 'Website ID is required. Please contact support.'
    } else {
      error.value = errorMsg || 'Failed to load referral statistics'
    }
  } finally {
    statsLoading.value = false
  }
}

const loadReferrals = async () => {
  loading.value = true
  try {
    const res = await referralsAPI.list({})
    referrals.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load referrals:', e)
    error.value = 'Failed to load referrals'
  } finally {
    loading.value = false
  }
}

const submitReferral = async () => {
  if (!referralEmail.value || !referralEmail.value.trim()) {
    error.value = 'Please enter an email address'
    return
  }

  referring.value = true
  error.value = ''
  message.value = ''
  
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      error.value = 'Website ID is required. Please contact support or refresh the page.'
      referring.value = false
      return
    }

    const res = await referralsAPI.referByEmail(referralEmail.value.trim(), websiteId)
    
    message.value = res.data?.message || `Successfully referred ${referralEmail.value}!`
    messageSuccess.value = true
    referralEmail.value = '' // Clear the input
    
    // Reload referrals list and stats
    await Promise.all([loadReferrals(), loadStats()])
  } catch (e) {
    console.error('Refer by email error:', e)
    const errorMsg = e?.response?.data?.error || e?.response?.data?.message || e.message
    error.value = errorMsg || 'Failed to create referral'
    messageSuccess.value = false
  } finally {
    referring.value = false
  }
}

const generateCode = async () => {
  generating.value = true
  error.value = ''
  message.value = ''
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      error.value = 'Website ID is required. Please contact support or refresh the page.'
      generating.value = false
      return
    }
    
    // Generate new code (backend will check if it already exists)
    const res = await referralsAPI.generateCode(websiteId)
    
    if (res.data?.already_exists) {
      message.value = res.data?.message || `Referral code already exists: ${res.data?.code}`
      messageSuccess.value = true
    } else {
      message.value = res.data?.message || 'Referral code generated successfully!'
      messageSuccess.value = true
    }
    
    // Reload stats to get the code and link
    await loadStats()
    
    // Verify code was created or already exists
    if (!stats.value.referral_code && !res.data?.already_exists) {
      throw new Error('Code generation succeeded but code not found in database')
    }
  } catch (e) {
    console.error('Generate code error:', e)
    const errorMsg = e?.response?.data?.error || e?.response?.data?.message || e.message
    const status = e?.response?.status
    
    // Handle specific error cases
    if (status === 404 && errorMsg?.includes('Website not found')) {
      error.value = `Website ID ${getWebsiteId()} not found. Please contact support.`
    } else {
      error.value = errorMsg || 'Failed to generate referral code'
    }
    messageSuccess.value = false
  } finally {
    generating.value = false
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    message.value = 'Copied to clipboard!'
    messageSuccess.value = true
    setTimeout(() => { message.value = '' }, 2000)
  } catch (e) {
    error.value = 'Failed to copy to clipboard'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getStatusText = (ref) => {
  if (ref.bonus_awarded) return 'Bonus Awarded'
  if (ref.first_order_bonus_credited) return 'Order Completed'
  if (ref.registration_bonus_credited) return 'Registered'
  return 'Pending'
}

const getStatusBadgeClass = (ref) => {
  if (ref.bonus_awarded) return 'bg-green-100 text-green-700'
  if (ref.first_order_bonus_credited) return 'bg-blue-100 text-blue-700'
  if (ref.registration_bonus_credited) return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([loadStats(), loadReferrals()])
  } catch (e) {
    console.error('Failed to load referrals page data:', e)
  } finally {
    loading.value = false
  }
})
</script>

