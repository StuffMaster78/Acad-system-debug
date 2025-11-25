<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Referral Tracking</h1>
        <p class="mt-2 text-gray-600">Monitor all referrals, detect abuse, and manage the referral system</p>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-blue-50 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Referrals</p>
        <p class="text-2xl font-bold text-blue-900">{{ stats.total_referrals || 0 }}</p>
      </div>
      <div class="card p-4 bg-green-50 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Successful</p>
        <p class="text-2xl font-bold text-green-900">{{ stats.successful_referrals || 0 }}</p>
      </div>
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Flagged</p>
        <p class="text-2xl font-bold text-red-900">{{ stats.flagged_referrals || 0 }}</p>
      </div>
      <div class="card p-4 bg-orange-50 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Voided</p>
        <p class="text-2xl font-bold text-orange-900">{{ stats.voided_referrals || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Referrer, referee, code..."
            class="w-full border rounded px-3 py-2"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadReferrals" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="flagged">Flagged</option>
            <option value="voided">Voided</option>
            <option value="successful">Successful</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadReferrals" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Referrals Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Referrer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Referee</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Addresses</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="referral in referrals" :key="referral.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ referral.referrer?.username || 'N/A' }}</div>
                  <div class="text-sm text-gray-500">{{ referral.referrer?.email || '' }}</div>
                </td>
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ referral.referee?.username || 'N/A' }}</div>
                  <div class="text-sm text-gray-500">{{ referral.referee?.email || '' }}</div>
                </td>
                <td class="px-4 py-3">
                  <code class="text-sm bg-gray-100 px-2 py-1 rounded">{{ referral.referral_code || 'N/A' }}</code>
                </td>
                <td class="px-4 py-3 text-sm">
                  <div v-if="referral.referrer_ip || referral.referee_ip">
                    <div v-if="referral.referrer_ip">Referrer: {{ referral.referrer_ip }}</div>
                    <div v-if="referral.referee_ip">Referee: {{ referral.referee_ip }}</div>
                    <div v-if="referral.referrer_ip === referral.referee_ip" class="text-red-600 text-xs mt-1">
                      ⚠️ Same IP
                    </div>
                  </div>
                  <span v-else class="text-gray-400">—</span>
                </td>
                <td class="px-4 py-3">
                  <div class="space-y-1">
                    <span v-if="referral.is_voided" class="px-2 py-1 rounded text-xs bg-red-100 text-red-800">
                      Voided
                    </span>
                    <span v-else-if="referral.is_flagged" class="px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800">
                      Flagged
                    </span>
                    <span v-else-if="referral.bonus_awarded" class="px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                      Successful
                    </span>
                    <span v-else class="px-2 py-1 rounded text-xs bg-gray-100 text-gray-800">
                      Pending
                    </span>
                    <div v-if="referral.flagged_reason" class="text-xs text-red-600 mt-1">
                      {{ referral.flagged_reason }}
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  {{ formatDate(referral.created_at) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <button
                      v-if="!referral.is_voided"
                      @click="voidReferral(referral)"
                      class="text-red-600 hover:text-red-800 text-sm"
                      title="Void Referral"
                    >
                      Void
                    </button>
                    <button
                      @click="viewAbuseFlags(referral)"
                      v-if="referral.is_flagged"
                      class="text-yellow-600 hover:text-yellow-800 text-sm"
                      title="View Abuse Flags"
                    >
                      Flags
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!referrals.length" class="text-center py-12 text-gray-500">
          No referrals found.
        </div>
      </div>
    </div>

    <!-- Abuse Flags Modal -->
    <div v-if="viewingAbuseFlags" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Abuse Flags for Referral #{{ viewingAbuseFlags.id }}</h2>
          <button @click="viewingAbuseFlags = null" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div v-if="abuseFlags.length" class="space-y-4">
          <div v-for="flag in abuseFlags" :key="flag.id" class="border rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span :class="getAbuseTypeClass(flag.abuse_type)" class="px-2 py-1 rounded text-xs font-medium">
                {{ flag.abuse_type_display }}
              </span>
              <span :class="getStatusClass(flag.status)" class="px-2 py-1 rounded text-xs font-medium">
                {{ flag.status_display }}
              </span>
            </div>
            <p class="text-sm text-gray-700 mb-2">{{ flag.reason }}</p>
            <div class="text-xs text-gray-500">
              Detected: {{ formatDateTime(flag.detected_at) }} by {{ flag.detected_by }}
            </div>
            <div v-if="flag.reviewed_by" class="text-xs text-gray-500 mt-1">
              Reviewed: {{ formatDateTime(flag.reviewed_at) }} by {{ flag.reviewed_by_username }}
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No abuse flags found for this referral.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { referralTrackingAPI } from '@/api'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'

const { showToast } = useToast()

const loading = ref(false)
const referrals = ref([])
const stats = ref({})
const websites = ref([])
const viewingAbuseFlags = ref(null)
const abuseFlags = ref([])

const filters = ref({
  search: '',
  status: '',
  website: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadReferrals()
  }, 500)
}

const loadReferrals = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    if (filters.value.status === 'flagged') params.is_flagged = true
    if (filters.value.status === 'voided') params.is_voided = true
    if (filters.value.status === 'successful') params.bonus_awarded = true
    
    const res = await referralTrackingAPI.listReferrals(params)
    referrals.value = res.data?.results || res.data || []
  } catch (e) {
    showToast('Failed to load referrals: ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await referralTrackingAPI.getReferralStatistics()
    stats.value = res.data || {}
  } catch (e) {
    console.error('Failed to load stats:', e)
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

const voidReferral = async (referral) => {
  if (!confirm(`Are you sure you want to void this referral?\n\nThis will prevent bonuses from being awarded.`)) return
  
  try {
    await referralTrackingAPI.voidReferral(referral.id, {
      reason: 'Voided by admin'
    })
    showToast('Referral voided successfully', 'success')
    await loadReferrals()
    await loadStats()
  } catch (e) {
    showToast('Failed to void referral: ' + (e.response?.data?.detail || e.message), 'error')
  }
}

const viewAbuseFlags = async (referral) => {
  viewingAbuseFlags.value = referral
  try {
    const res = await referralTrackingAPI.listAbuseFlags({ referral: referral.id })
    abuseFlags.value = res.data?.results || res.data || []
  } catch (e) {
    showToast('Failed to load abuse flags', 'error')
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: '', website: '' }
  loadReferrals()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

const getAbuseTypeClass = (type) => {
  const classes = {
    self_referral: 'bg-red-100 text-red-800',
    multiple_accounts: 'bg-orange-100 text-orange-800',
    suspicious_ip: 'bg-yellow-100 text-yellow-800',
    rapid_referrals: 'bg-purple-100 text-purple-800',
    fake_accounts: 'bg-pink-100 text-pink-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    reviewed: 'bg-blue-100 text-blue-800',
    resolved: 'bg-green-100 text-green-800',
    false_positive: 'bg-gray-100 text-gray-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

onMounted(async () => {
  await Promise.all([loadReferrals(), loadStats(), loadWebsites()])
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

