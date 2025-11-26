<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Level Details</h1>
        <p class="mt-2 text-gray-600">
          Understand your current level, allowances, and what it takes to advance.
        </p>
      </div>
      <button
        @click="loadProfile"
        :disabled="loading"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
    </div>

    <div v-else-if="!levelDetails" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">Level information is not available yet.</p>
      <p class="text-gray-400 text-sm mt-2">
        Once your performance metrics are recorded, your level information will appear here.
      </p>
    </div>

    <div v-else class="space-y-6">
      <!-- Current Level -->
      <div class="bg-white rounded-lg shadow-sm border border-primary-100 p-6">
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p class="text-sm font-medium text-primary-600 uppercase tracking-wide">Current Level</p>
            <h2 class="text-2xl font-bold text-gray-900 mt-1">{{ levelDetails.name }}</h2>
            <p class="text-gray-600 mt-2" v-if="levelDetails.description">
              {{ levelDetails.description }}
            </p>
          </div>
          <div class="text-sm text-gray-500">
            <p>Max concurrent orders: <span class="font-semibold text-gray-900">{{ levelDetails.max_orders }}</span></p>
            <p>Max pending requests: <span class="font-semibold text-gray-900">{{ levelDetails.max_requests_per_writer }}</span></p>
            <p>Deadline allocation: <span class="font-semibold text-gray-900">{{ levelDetails.deadline_percentage }}%</span></p>
          </div>
        </div>
      </div>

      <!-- Earnings Structure -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Earnings Model</h3>
          <ul class="space-y-2 text-sm text-gray-600">
            <li>
              <span class="font-medium text-gray-900">Mode:</span>
              {{ formatEarningMode(levelDetails.earning_mode) }}
            </li>
            <li v-if="levelDetails.earning_mode === 'fixed_per_page'">
              <span class="font-medium text-gray-900">Base pay per page:</span>
              ${{ formatCurrency(levelDetails.base_pay_per_page) }}
            </li>
            <li v-if="levelDetails.earning_mode === 'fixed_per_page'">
              <span class="font-medium text-gray-900">Base pay per slide:</span>
              ${{ formatCurrency(levelDetails.base_pay_per_slide) }}
            </li>
            <li v-if="levelDetails.earnings_percentage_of_cost">
              <span class="font-medium text-gray-900">% of order cost:</span>
              {{ levelDetails.earnings_percentage_of_cost }}%
            </li>
            <li v-if="levelDetails.earnings_percentage_of_total">
              <span class="font-medium text-gray-900">% of order total:</span>
              {{ levelDetails.earnings_percentage_of_total }}%
            </li>
            <li>
              <span class="font-medium text-gray-900">Tips share:</span>
              {{ levelDetails.tips_percentage }}%
            </li>
            <li>
              <span class="font-medium text-gray-900">Urgent bonus:</span>
              +{{ levelDetails.urgency_percentage_increase }}% or ${{ formatCurrency(levelDetails.urgency_additional_per_page) }}/page
            </li>
            <li>
              <span class="font-medium text-gray-900">Technical order bonus:</span>
              ${{ formatCurrency(levelDetails.technical_order_adjustment_per_page) }}/page
            </li>
          </ul>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Bonuses & Incentives</h3>
          <ul class="space-y-2 text-sm text-gray-600">
            <li>
              <span class="font-medium text-gray-900">Bonus per completed order:</span>
              ${{ formatCurrency(levelDetails.bonus_per_order_completed) }}
            </li>
            <li>
              <span class="font-medium text-gray-900">Bonus for high-rated work:</span>
              ${{ formatCurrency(levelDetails.bonus_per_rating_above_threshold) }} (ratings ≥ {{ levelDetails.rating_threshold_for_bonus }})
            </li>
            <li>
              <span class="font-medium text-gray-900">Urgent order window:</span>
              {{ levelDetails.urgent_order_deadline_hours }} hours
            </li>
            <li>
              <span class="font-medium text-gray-900">Deadline allocation:</span>
              {{ levelDetails.deadline_percentage }}% of client time
            </li>
          </ul>
        </div>
      </div>

      <!-- Requirements -->
      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Requirements to Maintain This Level</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ levelDetails.min_orders_to_attain }}</p>
            <p class="text-sm text-gray-600 mt-1">Completed Orders</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ levelDetails.min_rating_to_attain }}</p>
            <p class="text-sm text-gray-600 mt-1">Average Rating</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ levelDetails.min_completion_rate }}%</p>
            <p class="text-sm text-gray-600 mt-1">Completion Rate</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ levelDetails.min_takes_to_attain }}</p>
            <p class="text-sm text-gray-600 mt-1">Successful Takes</p>
          </div>
        </div>
        <div class="mt-4 text-sm text-gray-500">
          <p v-if="levelDetails.max_revision_rate">Keep revision rate below {{ levelDetails.max_revision_rate }}%.</p>
          <p v-if="levelDetails.max_lateness_rate">Keep lateness rate below {{ levelDetails.max_lateness_rate }}%.</p>
        </div>
      </div>

      <!-- Next Level -->
      <div v-if="nextLevelInfo" class="bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-lg p-6 shadow-sm">
        <h3 class="text-lg font-semibold text-indigo-900 mb-4 flex items-center gap-2">
          <span>🚀</span> Path to {{ nextLevelInfo.next_level.name }}
        </h3>
        <p class="text-sm text-gray-600 mb-4">
          Complete the remaining requirements below to unlock the next level and higher earning limits.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-4 bg-white rounded-lg border border-indigo-100">
            <p class="text-xs text-gray-500 uppercase">Minimum Orders</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ nextLevelInfo.requirements.min_orders }}
            </p>
          </div>
          <div class="p-4 bg-white rounded-lg border border-indigo-100">
            <p class="text-xs text-gray-500 uppercase">Average Rating</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ nextLevelInfo.requirements.min_rating }}
            </p>
          </div>
          <div class="p-4 bg-white rounded-lg border border-indigo-100">
            <p class="text-xs text-gray-500 uppercase">Completion Rate</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ nextLevelInfo.requirements.min_completion_rate }}%
            </p>
          </div>
          <div class="p-4 bg-white rounded-lg border border-indigo-100">
            <p class="text-xs text-gray-500 uppercase">Order Takes</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ nextLevelInfo.requirements.min_takes }}
            </p>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-lg shadow-sm p-6 text-center border border-green-100">
        <p class="text-lg font-semibold text-green-800">You’re at the highest available level 🎉</p>
        <p class="text-sm text-gray-600 mt-2">
          Keep up the great work and maintain your performance to retain this status.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import writerManagementAPI from '@/api/writer-management'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError } = useToast()

const loading = ref(false)
const levelDetails = ref(null)
const nextLevelInfo = ref(null)

const loadProfile = async () => {
  loading.value = true
  try {
    const response = await writerManagementAPI.getMyProfile()
    const data = response.data
    levelDetails.value = data.writer_level_details || null
    nextLevelInfo.value = data.next_level_info || null
  } catch (error) {
    console.error('Failed to load writer level details:', error)
    showError(getErrorMessage(error, 'Unable to load level information'))
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  return Number(value || 0).toFixed(2)
}

const formatEarningMode = (mode) => {
  const map = {
    fixed_per_page: 'Fixed per page / slide',
    percentage_of_order_cost: 'Percentage of order cost',
    percentage_of_order_total: 'Percentage of order total',
  }
  return map[mode] || mode
}

onMounted(() => {
  loadProfile()
})
</script>

