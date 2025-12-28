<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              Dashboard Summary
            </h1>
            <p class="text-base text-gray-600 leading-relaxed max-w-2xl">
              Overview of your writing activity and performance
            </p>
          </div>
          <button
            @click="loadSummary"
            :disabled="loading"
            class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-16">
        <div class="flex flex-col items-center justify-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading dashboard...</p>
        </div>
      </div>

      <!-- Summary Content -->
      <div v-else-if="summary" class="space-y-6">
        <!-- Revision Requests -->
        <div
          v-if="summary.revision_requests && summary.revision_requests.length > 0"
          class="bg-white rounded-xl shadow-md border-l-4 border-yellow-600"
        >
          <div class="p-6 sm:p-8">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span class="text-xl">⚠️</span>
                </div>
                <span>
                  Revision Requests
                  <span class="text-lg text-yellow-600">
                    ({{ summary.revision_requests.length }})
                  </span>
                </span>
              </h2>
              <router-link
                to="/writer/orders"
                class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <span>View All</span>
                <span>→</span>
              </router-link>
            </div>
            <div class="space-y-4">
              <div
                v-for="revision in summary.revision_requests.slice(0, 5)"
                :key="revision.id"
                class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 p-5 bg-yellow-50 rounded-xl border-2 border-yellow-200 hover:bg-yellow-100 transition-colors"
              >
                <div class="flex-1 min-w-0">
                  <router-link
                    :to="`/orders/${revision.id}`"
                    class="text-lg font-bold text-gray-900 hover:text-primary-600 transition-colors mb-2 block"
                  >
                    Order #{{ revision.id }}
                  </router-link>
                  <p class="text-sm font-semibold text-gray-700 mb-3 line-clamp-2">
                    {{ revision.topic || 'No topic' }}
                  </p>
                  <div class="flex flex-wrap items-center gap-4 text-xs font-medium text-gray-600">
                    <span>
                      Client: <span class="font-bold text-gray-900">{{ revision.client_name }}</span>
                    </span>
                    <span>
                      <span class="font-bold text-gray-900">{{ revision.pages }}</span> pages
                    </span>
                    <span v-if="revision.deadline">
                      Due: <span class="font-bold text-gray-900">{{ formatDateTime(revision.deadline) }}</span>
                    </span>
                  </div>
                </div>
                <router-link
                  :to="`/orders/${revision.id}`"
                  class="inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold text-primary-600 hover:bg-primary-50 rounded-lg transition-all shadow-sm hover:shadow-md whitespace-nowrap shrink-0"
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
              class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
            >
              <span>View All Tips</span>
              <span>→</span>
            </router-link>
          </div>

          <!-- Fines Summary -->
          <div class="bg-white rounded-xl shadow-md p-6 sm:p-8">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <span class="text-xl">⚠️</span>
              </div>
              <h3 class="text-xl font-bold text-gray-900">
                Fines Summary
              </h3>
            </div>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                <span class="text-sm font-semibold text-gray-600 uppercase tracking-wide">
                  Total Fines
                </span>
                <span class="text-xl font-bold text-red-600 truncate ml-4">
                  ${{ formatCurrency(summary.fines_summary?.total_fines || 0) }}
                </span>
              </div>
              <div class="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                <span class="text-sm font-semibold text-gray-600 uppercase tracking-wide">
                  This Month
                </span>
                <span class="text-xl font-bold text-red-600 truncate ml-4">
                  ${{ formatCurrency(summary.fines_summary?.this_month_fines || 0) }}
                </span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                <span class="text-sm font-semibold text-gray-600 uppercase tracking-wide">
                  Active Fines
                </span>
                <span class="text-base font-bold text-gray-700">
                  {{ summary.fines_summary?.active_fines_count || 0 }} fine{{ (summary.fines_summary?.active_fines_count || 0) !== 1 ? 's' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Reviews Summary -->
        <div
          v-if="summary.reviews_summary"
          class="bg-white rounded-xl shadow-md p-6 sm:p-8"
        >
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span class="text-xl">⭐</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900">
              Reviews Summary
            </h3>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="text-center p-5 bg-gray-50 rounded-xl border border-gray-200">
              <p class="text-3xl font-bold text-gray-900 mb-2">
                {{ summary.reviews_summary.average_rating || 0 }}
              </p>
              <p class="text-xs font-bold text-gray-600 uppercase tracking-wide">
                Average Rating
              </p>
            </div>
            <div class="text-center p-5 bg-gray-50 rounded-xl border border-gray-200">
              <p class="text-3xl font-bold text-gray-900 mb-2">
                {{ summary.reviews_summary.total_reviews || 0 }}
              </p>
              <p class="text-xs font-bold text-gray-600 uppercase tracking-wide">
                Total Reviews
              </p>
            </div>
            <div class="text-center p-5 bg-green-50 rounded-xl border border-green-200">
              <p class="text-3xl font-bold text-green-600 mb-2">
                {{ summary.reviews_summary.positive_reviews || 0 }}
              </p>
              <p class="text-xs font-bold text-gray-600 uppercase tracking-wide">
                Positive Reviews
              </p>
            </div>
            <div class="text-center p-5 bg-gray-50 rounded-xl border border-gray-200">
              <p class="text-3xl font-bold text-gray-900 mb-2">
                {{ summary.reviews_summary.recent_reviews || 0 }}
              </p>
              <p class="text-xs font-bold text-gray-600 uppercase tracking-wide">
                Recent (30 days)
              </p>
            </div>
          </div>
          <router-link
            to="/writer/reviews"
            class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
          >
            <span>View All Reviews</span>
            <span>→</span>
          </router-link>
        </div>

        <!-- Level Progress -->
        <div
          v-if="summary.level_progress"
          class="bg-white rounded-xl shadow-md p-6 sm:p-8"
        >
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <span class="text-xl">📊</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900">
              Level Progress
            </h3>
          </div>
          <div class="space-y-6">
            <div>
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                <span class="text-sm font-bold text-gray-700 uppercase tracking-wide">
                  Current Level: 
                  <span class="text-base text-gray-900">{{ summary.level_progress.current_level || 'N/A' }}</span>
                </span>
                <span class="text-sm font-semibold text-primary-600">
                  {{ summary.level_progress.progress_percentage || 0 }}% to next level
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  class="bg-gradient-to-r from-primary-500 to-primary-600 h-4 rounded-full transition-all duration-500 ease-out flex items-center justify-end pr-2"
                  :style="{ width: `${summary.level_progress.progress_percentage || 0}%` }"
                >
                  <span
                    v-if="summary.level_progress.progress_percentage > 10"
                    class="text-xs font-bold text-white"
                  >
                    {{ Math.round(summary.level_progress.progress_percentage || 0) }}%
                  </span>
                </div>
              </div>
            </div>
            <div
              v-if="summary.level_progress.next_level"
              class="bg-gray-50 rounded-lg p-4 border border-gray-200"
            >
              <p class="text-sm font-semibold text-gray-700 mb-2">
                Next Level: 
                <span class="font-bold text-gray-900">{{ summary.level_progress.next_level }}</span>
              </p>
              <p
                v-if="summary.level_progress.requirements_remaining"
                class="text-sm text-gray-600 leading-relaxed"
              >
                Requirements remaining: 
                <span class="font-bold text-gray-900">
                  {{ summary.level_progress.requirements_remaining }}
                </span>
              </p>
            </div>
          </div>
          <router-link
            to="/writer/performance"
            class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
          >
            <span>View Full Performance</span>
            <span>→</span>
          </router-link>
        </div>

        <!-- Quick Stats Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md p-6 border-l-4 border-blue-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-2">
                  Active Orders
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-blue-900">
                  {{ summary.active_orders || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">📝</span>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-md p-6 border-l-4 border-green-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-green-700 uppercase tracking-wide mb-2">
                  Completed This Month
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-green-900">
                  {{ summary.completed_this_month || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">✅</span>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-md p-6 border-l-4 border-purple-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide mb-2">
                  Total Earnings
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-purple-900 truncate">
                  ${{ formatCurrency(summary.total_earnings || 0) }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">💰</span>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-md p-6 border-l-4 border-orange-600 hover:shadow-lg transition-shadow">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-orange-700 uppercase tracking-wide mb-2">
                  Pending Payments
                </p>
                <p class="text-3xl sm:text-4xl font-bold text-orange-900 truncate">
                  ${{ formatCurrency(summary.pending_payments || 0) }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">⏳</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="bg-red-50 border-2 border-red-300 rounded-xl p-6 sm:p-8"
      >
        <div class="flex items-start gap-4">
          <div class="shrink-0">
            <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <span class="text-xl">❌</span>
            </div>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold text-red-900 mb-2">Error</h3>
            <p class="text-sm font-medium text-red-800">{{ error }}</p>
          </div>
        </div>
      </div>
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

