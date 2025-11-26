<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Dashboard Summary</h1>
        <p class="mt-2 text-gray-600">Overview of your writing activity and performance</p>
      </div>
      <button
        @click="loadSummary"
        :disabled="loading"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <!-- Summary Content -->
    <div v-else-if="summary" class="space-y-6">
      <!-- Revision Requests -->
      <div v-if="summary.revision_requests && summary.revision_requests.length > 0" class="bg-white rounded-lg shadow-sm border border-yellow-200">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <span class="text-yellow-600">⚠️</span>
              Revision Requests ({{ summary.revision_requests.length }})
            </h2>
            <router-link
              to="/writer/orders"
              class="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View All →
            </router-link>
          </div>
          <div class="space-y-3">
            <div
              v-for="revision in summary.revision_requests.slice(0, 5)"
              :key="revision.id"
              class="flex items-start justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200"
            >
              <div class="flex-1">
                <router-link
                  :to="`/orders/${revision.id}`"
                  class="font-medium text-gray-900 hover:text-primary-600"
                >
                  Order #{{ revision.id }}
                </router-link>
                <p class="text-sm text-gray-600 mt-1">{{ revision.topic || 'No topic' }}</p>
                <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>Client: {{ revision.client_name }}</span>
                  <span>{{ revision.pages }} pages</span>
                  <span v-if="revision.deadline">
                    Due: {{ formatDateTime(revision.deadline) }}
                  </span>
                </div>
              </div>
              <router-link
                :to="`/orders/${revision.id}`"
                class="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                Review
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Tips Summary -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <span>💰</span> Tips Summary
          </h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Total Tips</span>
              <span class="text-lg font-bold text-gray-900">
                ${{ formatCurrency(summary.tips_summary?.total_tips || 0) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">This Month</span>
              <span class="text-lg font-semibold text-green-600">
                ${{ formatCurrency(summary.tips_summary?.this_month_tips || 0) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Total Tips Received</span>
              <span class="text-sm font-medium text-gray-700">
                {{ summary.tips_summary?.tips_count || 0 }} tips
              </span>
            </div>
          </div>
          <router-link
            to="/writer/tips"
            class="mt-4 inline-block text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View All Tips →
          </router-link>
        </div>

        <!-- Fines Summary -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <span>⚠️</span> Fines Summary
          </h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Total Fines</span>
              <span class="text-lg font-bold text-red-600">
                ${{ formatCurrency(summary.fines_summary?.total_fines || 0) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">This Month</span>
              <span class="text-lg font-semibold text-red-600">
                ${{ formatCurrency(summary.fines_summary?.this_month_fines || 0) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Active Fines</span>
              <span class="text-sm font-medium text-gray-700">
                {{ summary.fines_summary?.active_fines_count || 0 }} fines
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews Summary -->
      <div v-if="summary.reviews_summary" class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>⭐</span> Reviews Summary
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ summary.reviews_summary.average_rating || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Average Rating</p>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ summary.reviews_summary.total_reviews || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Total Reviews</p>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-green-600">{{ summary.reviews_summary.positive_reviews || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Positive Reviews</p>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-gray-900">{{ summary.reviews_summary.recent_reviews || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Recent (30 days)</p>
          </div>
        </div>
        <router-link
          to="/writer/reviews"
          class="mt-4 inline-block text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View All Reviews →
        </router-link>
      </div>

      <!-- Level Progress -->
      <div v-if="summary.level_progress" class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>📊</span> Level Progress
        </h3>
        <div class="space-y-4">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">
                Current Level: {{ summary.level_progress.current_level || 'N/A' }}
              </span>
              <span class="text-sm text-gray-600">
                {{ summary.level_progress.progress_percentage || 0 }}% to next level
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div
                class="bg-primary-600 h-3 rounded-full transition-all duration-300"
                :style="{ width: `${summary.level_progress.progress_percentage || 0}%` }"
              ></div>
            </div>
          </div>
          <div v-if="summary.level_progress.next_level" class="text-sm text-gray-600">
            <p>Next Level: <span class="font-medium text-gray-900">{{ summary.level_progress.next_level }}</span></p>
            <p v-if="summary.level_progress.requirements_remaining" class="mt-1">
              Requirements remaining: {{ summary.level_progress.requirements_remaining }}
            </p>
          </div>
        </div>
        <router-link
          to="/writer/performance"
          class="mt-4 inline-block text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View Full Performance →
        </router-link>
      </div>

      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
          <p class="text-sm font-medium text-blue-700 mb-1">Active Orders</p>
          <p class="text-3xl font-bold text-blue-900">{{ summary.active_orders || 0 }}</p>
        </div>
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
          <p class="text-sm font-medium text-green-700 mb-1">Completed This Month</p>
          <p class="text-3xl font-bold text-green-900">{{ summary.completed_this_month || 0 }}</p>
        </div>
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
          <p class="text-sm font-medium text-purple-700 mb-1">Total Earnings</p>
          <p class="text-3xl font-bold text-purple-900">${{ formatCurrency(summary.total_earnings || 0) }}</p>
        </div>
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
          <p class="text-sm font-medium text-orange-700 mb-1">Pending Payments</p>
          <p class="text-3xl font-bold text-orange-900">${{ formatCurrency(summary.pending_payments || 0) }}</p>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <p class="text-red-800">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError } = useToast()

const loading = ref(false)
const summary = ref(null)
const error = ref('')

const loadSummary = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await writerDashboardAPI.getDashboardSummary()
    summary.value = response.data
  } catch (err) {
    console.error('Failed to load dashboard summary:', err)
    error.value = getErrorMessage(err, 'Failed to load dashboard summary')
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadSummary()
})
</script>

