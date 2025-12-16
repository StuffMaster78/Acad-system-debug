<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Referral Code Tracing</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track and analyze all referral codes with comprehensive usage statistics</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="loadCodes"
          :disabled="loading"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        <button
          @click="showGenerateModal = true"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Generate Code
        </button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Codes</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_codes || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active Codes</p>
        <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.active_codes || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Codes with Referrals</p>
        <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.codes_with_referrals || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Top Conversion Rate</p>
        <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">
          {{ topConversionRate }}%
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Code, username, email..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Website</label>
          <select
            v-model="filters.website"
            @change="loadCodes"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
          <select
            v-model="filters.is_active"
            @change="loadCodes"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
          >
            <option value="">All</option>
            <option value="true">Active Users</option>
            <option value="false">Inactive Users</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="resetFilters"
            class="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>
    </div>

    <!-- Codes Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="codes.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p>No referral codes found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Code</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">User</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Website</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total Referrals</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Successful</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Conversion</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Orders</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="code in codes"
              :key="code.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <td class="px-4 py-3">
                <code class="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded font-mono">{{ code.code }}</code>
              </td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900 dark:text-white">{{ code.user?.username || 'N/A' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ code.user?.email || '' }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                {{ code.website?.name || 'N/A' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                {{ code.usage_stats?.total_referrals || 0 }}
              </td>
              <td class="px-4 py-3">
                <span class="text-sm font-medium text-green-600 dark:text-green-400">
                  {{ code.usage_stats?.successful_referrals || 0 }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      class="bg-primary-600 h-2 rounded-full"
                      :style="{ width: `${code.usage_stats?.conversion_rate || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-900 dark:text-white">
                    {{ code.usage_stats?.conversion_rate || 0 }}%
                  </span>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                {{ code.usage_stats?.orders_placed || 0 }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(code.created_at) }}
              </td>
              <td class="px-4 py-3">
                <button
                  @click="traceCode(code.id)"
                  class="px-3 py-1.5 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Trace
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div class="text-sm text-gray-700 dark:text-gray-300">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Previous
          </button>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Trace Modal -->
    <NaiveModal
      v-model:visible="showTraceModal"
      title="Referral Code Trace"
      size="xl"
    >
      <div v-if="traceLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="traceData" class="space-y-6">
        <!-- Code Info -->
        <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Code Information</h3>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600 dark:text-gray-400">Code:</span>
              <code class="ml-2 font-mono text-gray-900 dark:text-white">{{ traceData.referral_code.code }}</code>
            </div>
            <div>
              <span class="text-gray-600 dark:text-gray-400">User:</span>
              <span class="ml-2 text-gray-900 dark:text-white">{{ traceData.referral_code.user.username }}</span>
            </div>
            <div>
              <span class="text-gray-600 dark:text-gray-400">Website:</span>
              <span class="ml-2 text-gray-900 dark:text-white">{{ traceData.referral_code.website.name }}</span>
            </div>
            <div>
              <span class="text-gray-600 dark:text-gray-400">Created:</span>
              <span class="ml-2 text-gray-900 dark:text-white">{{ formatDate(traceData.referral_code.created_at) }}</span>
            </div>
          </div>
          <div class="mt-3">
            <span class="text-gray-600 dark:text-gray-400">Referral Link:</span>
            <div class="mt-1 flex items-center gap-2">
              <input
                :value="traceData.referral_code.referral_link"
                readonly
                class="flex-1 border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-800 text-sm font-mono"
              />
              <button
                @click="copyToClipboard(traceData.referral_code.referral_link)"
                class="px-3 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm"
              >
                Copy
              </button>
            </div>
          </div>
        </div>

        <!-- Statistics -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-3">
            <p class="text-xs text-blue-700 dark:text-blue-300 mb-1">Total</p>
            <p class="text-xl font-bold text-blue-900 dark:text-blue-100">{{ traceData.statistics.total_referrals }}</p>
          </div>
          <div class="bg-green-50 dark:bg-green-900/30 rounded-lg p-3">
            <p class="text-xs text-green-700 dark:text-green-300 mb-1">Successful</p>
            <p class="text-xl font-bold text-green-900 dark:text-green-100">{{ traceData.statistics.successful_referrals }}</p>
          </div>
          <div class="bg-red-50 dark:bg-red-900/30 rounded-lg p-3">
            <p class="text-xs text-red-700 dark:text-red-300 mb-1">Flagged</p>
            <p class="text-xl font-bold text-red-900 dark:text-red-100">{{ traceData.statistics.flagged_referrals }}</p>
          </div>
          <div class="bg-orange-50 dark:bg-orange-900/30 rounded-lg p-3">
            <p class="text-xs text-orange-700 dark:text-orange-300 mb-1">Voided</p>
            <p class="text-xl font-bold text-orange-900 dark:text-orange-100">{{ traceData.statistics.voided_referrals }}</p>
          </div>
          <div class="bg-purple-50 dark:bg-purple-900/30 rounded-lg p-3">
            <p class="text-xs text-purple-700 dark:text-purple-300 mb-1">Conversion</p>
            <p class="text-xl font-bold text-purple-900 dark:text-purple-100">{{ traceData.statistics.conversion_rate }}%</p>
          </div>
        </div>

        <!-- Referrals List -->
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Referrals Made ({{ traceData.referrals.length }})</h3>
          <div class="space-y-3 max-h-96 overflow-y-auto">
            <div
              v-for="ref in traceData.referrals"
              :key="ref.referral_id"
              class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4"
            >
              <div class="flex items-start justify-between mb-2">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ ref.referee.username }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ ref.referee.email }}</p>
                </div>
                <div class="flex gap-2">
                  <span
                    v-if="ref.bonus_awarded"
                    class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded"
                  >
                    Successful
                  </span>
                  <span
                    v-if="ref.is_flagged"
                    class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 rounded"
                  >
                    Flagged
                  </span>
                  <span
                    v-if="ref.is_voided"
                    class="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300 rounded"
                  >
                    Voided
                  </span>
                </div>
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p>Joined: {{ formatDate(ref.referee.date_joined) }}</p>
                <p>Referred: {{ formatDate(ref.created_at) }}</p>
                <p>Orders placed: {{ ref.orders_count }}</p>
                <div v-if="ref.orders.length > 0" class="mt-2">
                  <p class="font-medium mb-1">Recent Orders:</p>
                  <ul class="list-disc list-inside space-y-1">
                    <li v-for="order in ref.orders" :key="order.id">
                      Order #{{ order.id }}: {{ order.topic }} ({{ order.status }}) - ${{ order.total_price }}
                    </li>
                  </ul>
                </div>
                <div v-if="ref.abuse_flags.length > 0" class="mt-2">
                  <p class="font-medium text-red-600 dark:text-red-400 mb-1">Abuse Flags:</p>
                  <ul class="list-disc list-inside space-y-1">
                    <li v-for="flag in ref.abuse_flags" :key="flag.detected_at">
                      {{ flag.type }}: {{ flag.reason }} ({{ flag.status }})
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </NaiveModal>

    <!-- Generate Code Modal -->
    <NaiveModal
      v-model:visible="showGenerateModal"
      title="Generate Referral Code"
      size="md"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">User ID</label>
          <input
            v-model="generateForm.user_id"
            type="number"
            placeholder="Enter client user ID"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div class="flex justify-end gap-3">
          <button
            @click="showGenerateModal = false"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="generateCode"
            :disabled="!generateForm.user_id || generating"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            {{ generating ? 'Generating...' : 'Generate' }}
          </button>
        </div>
      </div>
    </NaiveModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import adminManagementAPI from '@/api/admin-management'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import NaiveModal from '@/components/naive/NaiveModal.vue'

const { showToast } = useToast()

const loading = ref(false)
const codes = ref([])
const stats = ref({})
const websites = ref([])
const traceData = ref(null)
const traceLoading = ref(false)
const showTraceModal = ref(false)
const showGenerateModal = ref(false)
const generating = ref(false)

const filters = ref({
  search: '',
  website: '',
  is_active: '',
})

const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const topConversionRate = computed(() => {
  if (!stats.value.top_conversion_codes || stats.value.top_conversion_codes.length === 0) return 0
  return stats.value.top_conversion_codes[0]?.conversion_rate || 0
})

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadCodes()
  }, 500)
}

const loadCodes = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    if (filters.value.is_active) params.user__is_active = filters.value.is_active === 'true'

    const [codesRes, statsRes, websitesRes] = await Promise.all([
      adminManagementAPI.listReferralCodes(params),
      adminManagementAPI.listReferralCodes({ ...params, statistics: true }),
      websitesAPI.listWebsites(),
    ])

    codes.value = codesRes.data.results || codesRes.data || []
    totalCount.value = codesRes.data.count || codes.value.length
    stats.value = statsRes.data || {}
    websites.value = websitesRes.data.results || websitesRes.data || []
  } catch (error) {
    console.error('Failed to load referral codes:', error)
    showToast('Failed to load referral codes', 'error')
  } finally {
    loading.value = false
  }
}

const traceCode = async (codeId) => {
  showTraceModal.value = true
  traceLoading.value = true
  try {
    const response = await adminManagementAPI.traceReferralCode(codeId)
    traceData.value = response.data
  } catch (error) {
    console.error('Failed to trace referral code:', error)
    showToast('Failed to trace referral code', 'error')
    showTraceModal.value = false
  } finally {
    traceLoading.value = false
  }
}

const generateCode = async () => {
  generating.value = true
  try {
    await adminManagementAPI.generateReferralCodeForClient({ user_id: parseInt(generateForm.value.user_id) })
    showToast('Referral code generated successfully', 'success')
    showGenerateModal.value = false
    generateForm.value.user_id = ''
    loadCodes()
  } catch (error) {
    console.error('Failed to generate referral code:', error)
    showToast(error.response?.data?.error || 'Failed to generate referral code', 'error')
  } finally {
    generating.value = false
  }
}

const generateForm = ref({
  user_id: '',
})

const resetFilters = () => {
  filters.value = {
    search: '',
    website: '',
    is_active: '',
  }
  currentPage.value = 1
  loadCodes()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  showToast('Copied to clipboard', 'success')
}

watch([currentPage], () => {
  loadCodes()
})

onMounted(() => {
  loadCodes()
})
</script>

