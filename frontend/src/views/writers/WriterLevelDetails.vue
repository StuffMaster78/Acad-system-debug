<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Level Details</h1>
          <p class="mt-1 text-lg text-gray-600">{{ levelDetails?.name || 'Not Assigned' }}</p>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-3xl">📊</div>
          <button
            @click="loadProfile"
            :disabled="loading"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm font-medium"
          >
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-16 text-center">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading level details...</p>
        </div>
      </div>

      <div v-else-if="!levelDetails" class="bg-white rounded-xl shadow-sm p-16 text-center">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-6">
          <span class="text-4xl">📊</span>
        </div>
        <p class="text-lg font-semibold text-gray-900 mb-2">Level information is not available yet</p>
        <p class="text-sm text-gray-500 max-w-md mx-auto">
          Once your performance metrics are recorded, your level information will appear here.
        </p>
      </div>

      <div v-else class="space-y-6">
        <!-- First Row: Earnings Structure, Urgency Adjustments, Technical Orders -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Earnings Structure -->
          <div class="bg-white rounded-xl shadow-md p-5 border border-gray-200">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-12 h-12 bg-linear-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center text-white text-xl">
                💰
              </div>
              <h3 class="text-base font-semibold text-gray-900">Earnings Structure</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div v-if="levelDetails.earning_mode === 'fixed_per_page'" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Per Page:</span>
                  <span class="font-bold text-green-600">${{ formatCurrency(levelDetails.base_pay_per_page) }}</span>
                </div>
                <div v-if="levelDetails.base_pay_per_slide > 0" class="flex items-center justify-between">
                  <span class="text-gray-600">Per Slide:</span>
                  <span class="font-bold text-green-600">${{ formatCurrency(levelDetails.base_pay_per_slide) }}</span>
                </div>
              </div>
              <div v-else-if="levelDetails.earning_mode === 'percentage_of_order_cost'" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Percentage:</span>
                  <span class="font-bold text-green-600">{{ parseFloat(levelDetails.earnings_percentage_of_cost || 0).toFixed(1) }}%</span>
                </div>
                <p class="text-xs text-gray-500">of order cost</p>
              </div>
              <div v-else-if="levelDetails.earning_mode === 'percentage_of_order_total'" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Percentage:</span>
                  <span class="font-bold text-green-600">{{ parseFloat(levelDetails.earnings_percentage_of_total || 0).toFixed(1) }}%</span>
                </div>
                <p class="text-xs text-gray-500">of order total</p>
              </div>
              <div v-else class="text-gray-500 text-xs">No earnings structure configured</div>
              <div v-if="levelDetails.tips_percentage > 0" class="pt-2 border-t border-gray-100">
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Tips Share:</span>
                  <span class="font-semibold text-gray-900">{{ parseFloat(levelDetails.tips_percentage || 0).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Urgency Adjustments -->
          <div class="bg-white rounded-xl shadow-md p-5 border border-gray-200">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-12 h-12 bg-linear-to-br from-yellow-400 to-yellow-500 rounded-lg flex items-center justify-center text-white text-xl">
                ⚡
              </div>
              <h3 class="text-base font-semibold text-gray-900">Urgency Adjustments</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Urgency Hours:</span>
                <span class="font-bold text-orange-600">{{ levelDetails.urgent_order_deadline_hours || 0 }}h</span>
              </div>
              <div v-if="levelDetails.urgency_percentage_increase > 0" class="flex items-center justify-between">
                <span class="text-gray-600">% Increase:</span>
                <span class="font-semibold text-orange-600">+{{ parseFloat(levelDetails.urgency_percentage_increase || 0).toFixed(1) }}%</span>
              </div>
              <div v-if="levelDetails.urgency_additional_per_page > 0" class="flex items-center justify-between">
                <span class="text-gray-600">Extra Per Page:</span>
                <span class="font-semibold text-orange-600">+${{ formatCurrency(levelDetails.urgency_additional_per_page) }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100">
                Orders within {{ levelDetails.urgent_order_deadline_hours || 0 }} hours get urgency bonuses
              </p>
            </div>
          </div>

          <!-- Technical Orders -->
          <div class="bg-white rounded-xl shadow-md p-5 border border-gray-200">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-12 h-12 bg-linear-to-br from-gray-400 to-gray-600 rounded-lg flex items-center justify-center text-white text-xl">
                🔧
              </div>
              <h3 class="text-base font-semibold text-gray-900">Technical Orders</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div v-if="levelDetails.technical_order_adjustment_per_page > 0" class="flex items-center justify-between">
                <span class="text-gray-600">Extra Per Page:</span>
                <span class="font-semibold text-purple-600">+${{ formatCurrency(levelDetails.technical_order_adjustment_per_page) }}</span>
              </div>
              <div v-if="levelDetails.technical_order_adjustment_per_slide > 0" class="flex items-center justify-between">
                <span class="text-gray-600">Extra Per Slide:</span>
                <span class="font-semibold text-purple-600">+${{ formatCurrency(levelDetails.technical_order_adjustment_per_slide) }}</span>
              </div>
              <p v-if="!levelDetails.technical_order_adjustment_per_page && !levelDetails.technical_order_adjustment_per_slide" class="text-xs text-gray-500">
                No technical adjustments
              </p>
            </div>
          </div>
        </div>

        <!-- Second Row: Capacity & Limits, Your Performance -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Capacity & Limits -->
          <div class="bg-white rounded-xl shadow-md p-5 border border-gray-200">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-12 h-12 bg-linear-to-br from-amber-600 to-amber-800 rounded-lg flex items-center justify-center text-white text-xl">
                📋
              </div>
              <h3 class="text-base font-semibold text-gray-900">Capacity & Limits</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Max Orders:</span>
                <span class="font-bold text-blue-600">{{ levelDetails.max_orders || 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Current Takes:</span>
                <span class="font-bold text-blue-600">{{ currentStats?.total_takes || 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Deadline %:</span>
                <span class="font-bold text-blue-600">{{ parseFloat(levelDetails.deadline_percentage || 80).toFixed(0) }}%</span>
              </div>
              <p class="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100">
                You receive {{ parseFloat(levelDetails.deadline_percentage || 80).toFixed(0) }}% of client deadline time
              </p>
            </div>
          </div>

          <!-- Your Performance -->
          <div class="bg-white rounded-xl shadow-md p-5 border border-gray-200">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-12 h-12 bg-linear-to-br from-yellow-400 to-yellow-500 rounded-lg flex items-center justify-center text-white text-xl">
                ⭐
              </div>
              <h3 class="text-base font-semibold text-gray-900">Your Performance</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Average Rating:</span>
                <span class="font-bold text-green-600 flex items-center gap-1">
                  {{ currentStats?.avg_rating ? parseFloat(currentStats.avg_rating).toFixed(1) : 'N/A' }}
                  <span v-if="currentStats?.avg_rating" class="text-yellow-500">★</span>
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Completed Orders:</span>
                <span class="font-bold text-green-600">{{ currentStats?.total_completed_orders || 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Completion Rate:</span>
                <span class="font-bold text-green-600">
                  {{ currentStats?.completion_rate ? `${parseFloat(currentStats.completion_rate).toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-600">Revision Rate:</span>
                <span class="font-bold" :class="currentStats?.revision_rate > 20 ? 'text-red-600' : 'text-green-600'">
                  {{ currentStats?.revision_rate ? `${parseFloat(currentStats.revision_rate).toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Third Row: Quick Reference -->
        <div class="bg-white rounded-xl shadow-md p-5 border border-gray-200">
          <h3 class="text-base font-semibold text-gray-900 mb-4">Quick Reference</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="text-gray-600">Urgency Threshold:</span>
              <span class="font-bold text-gray-900 ml-2">{{ levelDetails.urgent_order_deadline_hours || 0 }} hours</span>
            </div>
            <div>
              <span class="text-gray-600">Urgency Bonus:</span>
              <span class="font-semibold text-gray-900 ml-2">
                <span v-if="levelDetails.urgency_percentage_increase > 0">+{{ parseFloat(levelDetails.urgency_percentage_increase).toFixed(1) }}%</span>
                <span v-else-if="levelDetails.urgency_additional_per_page > 0">+${{ formatCurrency(levelDetails.urgency_additional_per_page) }}/page</span>
                <span v-else>None</span>
              </span>
            </div>
            <div>
              <span class="text-gray-600">Technical Bonus:</span>
              <span class="font-semibold text-gray-900 ml-2">
                <span v-if="levelDetails.technical_order_adjustment_per_page > 0">+${{ formatCurrency(levelDetails.technical_order_adjustment_per_page) }}/page</span>
                <span v-else>None</span>
              </span>
            </div>
            <div>
              <span class="text-gray-600">Deadline Allocation:</span>
              <span class="font-bold text-gray-900 ml-2">{{ parseFloat(levelDetails.deadline_percentage || 80).toFixed(0) }}% of client deadline</span>
            </div>
          </div>
        </div>

        <!-- Requirements & Next Level Section -->
        <div v-if="nextLevelInfo" class="bg-linear-to-br from-indigo-50 to-white border border-indigo-200 rounded-xl shadow-md p-6">
          <h3 class="text-lg font-semibold text-indigo-900 mb-4 flex items-center gap-2">
            <span>🚀</span> Path to {{ nextLevelInfo.next_level.name }}
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            Complete the remaining requirements below to unlock the next level and higher earning limits.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="p-4 bg-white rounded-lg border border-indigo-100">
              <p class="text-xs text-gray-500 uppercase mb-1">Minimum Orders</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ nextLevelInfo.requirements.min_orders }}
              </p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-indigo-100">
              <p class="text-xs text-gray-500 uppercase mb-1">Average Rating</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ nextLevelInfo.requirements.min_rating }}
              </p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-indigo-100">
              <p class="text-xs text-gray-500 uppercase mb-1">Completion Rate</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ nextLevelInfo.requirements.min_completion_rate }}%
              </p>
            </div>
            <div class="p-4 bg-white rounded-lg border border-indigo-100">
              <p class="text-xs text-gray-500 uppercase mb-1">Order Takes</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ nextLevelInfo.requirements.min_takes }}
              </p>
            </div>
          </div>
        </div>

        <div v-else class="bg-white rounded-xl shadow-md p-6 text-center border border-green-200">
          <p class="text-lg font-semibold text-green-800">You're at the highest available level 🎉</p>
          <p class="text-sm text-gray-600 mt-2">
            Keep up the great work and maintain your performance to retain this status.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import writerManagementAPI from '@/api/writer-management'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError } = useToast()

const loading = ref(false)
const levelDetails = ref(null)
const nextLevelInfo = ref(null)
const currentStats = ref(null)

const loadProfile = async () => {
  loading.value = true
  try {
    // Load level details
    const profileResponse = await writerManagementAPI.getMyProfile()
    const profileData = profileResponse.data
    levelDetails.value = profileData.writer_level_details || null
    nextLevelInfo.value = profileData.next_level_info || null

    // Load performance stats
    try {
      const levelResponse = await writerDashboardAPI.getLevelAndRanking()
      currentStats.value = levelResponse.data?.current_stats || null
    } catch (statsError) {
      console.warn('Failed to load performance stats:', statsError)
      // Fallback to profile data if available
      currentStats.value = {
        total_takes: profileData.number_of_takes || 0,
        total_completed_orders: profileData.completed_orders || 0,
      }
    }
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

