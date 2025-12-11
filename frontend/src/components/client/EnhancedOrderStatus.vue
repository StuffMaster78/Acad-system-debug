<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">Enhanced Order Status</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">Detailed tracking and analytics for Order #{{ orderId }}</p>
      </div>
      <button
        @click="refreshStatus"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
      >
        <svg v-if="loading" class="animate-spin h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
      <p class="text-sm text-gray-600 dark:text-gray-400">Loading enhanced status...</p>
    </div>

    <!-- Error State - Only show for actual errors, not 404/403 -->
    <div v-else-if="error && endpointAvailable" class="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-semibold text-red-800 dark:text-red-300 mb-1">Error Loading Status</h4>
          <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Endpoint Not Available - Show graceful message -->
    <div v-else-if="!loading && !error && !statusData && !endpointAvailable" class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-8 text-center shadow-sm">
      <div class="flex flex-col items-center gap-4">
        <div class="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <p class="text-base text-gray-700 dark:text-gray-300 font-semibold mb-1">Enhanced status tracking is not available</p>
          <p class="text-sm text-gray-500 dark:text-gray-400">This feature may not be enabled for this order or your account</p>
        </div>
      </div>
    </div>

    <!-- Status Content -->
    <div v-else-if="statusData" class="space-y-6">
      <!-- Current Status Card -->
      <div class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Current Status</h3>
          <div class="px-4 py-2 bg-gradient-to-r from-primary-100 to-primary-50 dark:from-primary-900/30 dark:to-primary-800/30 text-primary-700 dark:text-primary-300 rounded-lg font-semibold text-sm border border-primary-200 dark:border-primary-700">
            {{ formatStatus(statusData.current_status) }}
          </div>
        </div>
        <div v-if="statusData.progress" class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Overall Progress</span>
            <span class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.progress.percentage }}%</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              class="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500 shadow-sm"
              :style="{ width: `${statusData.progress.percentage}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Estimated Completion -->
      <div v-if="statusData.estimated_completion" class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Estimated Completion
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-5 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border border-blue-200 dark:border-blue-800">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div class="text-xs font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wide">Deadline</div>
            </div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
              {{ formatDateTime(statusData.estimated_completion.deadline) }}
            </div>
          </div>
          <div class="p-5 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl border border-orange-200 dark:border-orange-800">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-xs font-medium text-orange-700 dark:text-orange-300 uppercase tracking-wide">Time Remaining</div>
            </div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
              {{ statusData.estimated_completion.days_remaining }} days
              <span class="text-sm font-normal text-gray-600 dark:text-gray-400">({{ statusData.estimated_completion.hours_remaining }}h)</span>
            </div>
          </div>
          <div class="p-5 rounded-xl border" :class="statusData.estimated_completion.is_overdue ? 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-800' : 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800'">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4" :class="statusData.estimated_completion.is_overdue ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-xs font-medium uppercase tracking-wide" :class="statusData.estimated_completion.is_overdue ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'">Status</div>
            </div>
            <div class="text-lg font-bold" :class="statusData.estimated_completion.is_overdue ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'">
              {{ statusData.estimated_completion.is_overdue ? '⚠️ Overdue' : '✅ On Track' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Writer Activity -->
      <div v-if="statusData.writer_activity" class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Writer Activity
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Writer</div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.writer_activity.writer_username || 'Unassigned' }}</div>
          </div>
          <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Activity Status</div>
            <div class="flex items-center gap-2">
              <span
                class="px-3 py-1.5 rounded-full text-sm font-semibold flex items-center gap-1.5"
                :class="statusData.writer_activity.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600'"
              >
                <span class="w-2 h-2 rounded-full" :class="statusData.writer_activity.is_active ? 'bg-green-500' : 'bg-gray-400'"></span>
                {{ statusData.writer_activity.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          <div v-if="statusData.writer_activity.last_activity" class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Last Activity</div>
            <div class="text-base font-semibold text-gray-900 dark:text-gray-100">
              {{ formatDateTime(statusData.writer_activity.last_activity) }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">
              {{ statusData.writer_activity.hours_since_activity }} hours ago
            </div>
          </div>
        </div>
      </div>

      <!-- Quality Metrics -->
      <div v-if="statusData.quality_metrics" class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Quality Metrics
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center p-5 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border border-blue-200 dark:border-blue-800">
            <div class="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">{{ statusData.quality_metrics.revision_count || 0 }}</div>
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Revisions</div>
          </div>
          <div class="text-center p-5 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl border border-orange-200 dark:border-orange-800">
            <div class="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">{{ statusData.quality_metrics.dispute_count || 0 }}</div>
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Disputes</div>
          </div>
          <div class="text-center p-5 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl border border-green-200 dark:border-green-800">
            <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
              {{ statusData.quality_metrics.average_rating || 'N/A' }}
            </div>
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Avg Rating</div>
          </div>
          <div class="text-center p-5 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl border border-purple-200 dark:border-purple-800">
            <div class="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
              {{ statusData.quality_metrics.has_reviews ? '✅' : '❌' }}
            </div>
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Has Reviews</div>
          </div>
        </div>
      </div>

      <!-- Recent Progress Updates -->
      <div v-if="statusData.progress?.recent_updates?.length" class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Recent Progress Updates
        </h3>
        <div class="space-y-4">
          <div
            v-for="(update, index) in statusData.progress.recent_updates"
            :key="index"
            class="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
          >
            <div class="w-14 h-14 bg-gradient-to-br from-primary-100 to-primary-50 dark:from-primary-900/30 dark:to-primary-800/30 rounded-xl flex items-center justify-center border border-primary-200 dark:border-primary-800 flex-shrink-0">
              <span class="text-primary-700 dark:text-primary-300 font-bold text-lg">{{ update.progress_percentage }}%</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">{{ formatDateTime(update.timestamp) }}</div>
              <div v-if="update.notes" class="text-sm text-gray-600 dark:text-gray-400 mt-2 leading-relaxed">{{ update.notes }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Timeline -->
      <div v-if="statusData.status_timeline?.length" class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Status Timeline
        </h3>
        <div class="relative border-l-2 border-gray-300 dark:border-gray-600 pl-6 space-y-6">
          <div
            v-for="(transition, index) in statusData.status_timeline"
            :key="index"
            class="relative"
          >
            <div class="absolute -left-[22px] top-0 w-4 h-4 rounded-full bg-primary-500 dark:bg-primary-600 border-2 border-white dark:border-gray-800 shadow-md"></div>
            <div class="pb-6">
              <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                <div class="flex-1">
                  <div class="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                    {{ formatStatus(transition.from_status) }} → {{ formatStatus(transition.to_status) }}
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ transition.action }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-500 mt-1.5 flex items-center gap-2">
                    <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                      {{ transition.is_automatic ? 'Auto' : 'Manual' }}
                    </span>
                    <span>by {{ transition.actor }}</span>
                  </div>
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">{{ formatDateTime(transition.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Writer Reassignments -->
      <div v-if="statusData.writer_reassignments?.length" class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          Writer Reassignments
        </h3>
        <div class="space-y-4">
          <div
            v-for="(reassignment, index) in statusData.writer_reassignments"
            :key="index"
            class="p-5 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-xl border border-yellow-200 dark:border-yellow-800"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="font-semibold text-gray-900 dark:text-gray-100">
                {{ reassignment.previous_writer || 'Unassigned' }} → {{ reassignment.new_writer || 'Unassigned' }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">{{ formatDateTime(reassignment.timestamp) }}</div>
            </div>
            <div class="text-sm text-gray-700 dark:text-gray-300 mb-2">{{ reassignment.reason }}</div>
            <div class="text-xs text-gray-500 dark:text-gray-400">Reassigned by: {{ reassignment.reassigned_by }}</div>
          </div>
        </div>
      </div>

      <!-- Order Details -->
      <div class="card bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Order Details
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Topic</div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_topic }}</div>
          </div>
          <div v-if="statusData.order_details.type_of_work" class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Type of Work</div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_details.type_of_work }}</div>
          </div>
          <div v-if="statusData.order_details.paper_type" class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Paper Type</div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_details.paper_type }}</div>
          </div>
          <div v-if="statusData.order_details.number_of_pages" class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Pages</div>
            <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_details.number_of_pages }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import clientDashboardAPI from '@/api/client-dashboard'

const props = defineProps({
  orderId: {
    type: [String, Number],
    required: true
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const loading = ref(false)
const error = ref(null)
const statusData = ref(null)
const endpointAvailable = ref(true) // Track if endpoint is available

const fetchStatus = async () => {
  if (!props.orderId) return
  
  loading.value = true
  error.value = null
  try {
    const response = await clientDashboardAPI.getEnhancedOrderStatus(props.orderId)
    statusData.value = response?.data || null
    endpointAvailable.value = true
  } catch (err) {
    // Handle 404 and 403 gracefully - endpoint may not be available or user may not have access
    if (err.response?.status === 404 || err.response?.status === 403) {
      // Silently handle - endpoint doesn't exist, isn't accessible, or user doesn't have permission
      statusData.value = null
      error.value = null // Don't show error for 404/403
      endpointAvailable.value = false // Mark endpoint as unavailable
      loading.value = false
      return
    }
    // Only show errors for server errors (5xx) or other unexpected errors
    // Don't show errors for client errors (4xx) except 404/403 which are handled above
    if (err.response?.status >= 500 || !err.response) {
    console.error('Failed to fetch enhanced order status:', err)
    error.value = err.response?.data?.detail || 'Failed to load order status'
      endpointAvailable.value = true // Keep endpoint as available for retry
    } else {
      // For other 4xx errors, handle silently
    statusData.value = null
      error.value = null
      endpointAvailable.value = false
    }
  } finally {
    loading.value = false
  }
}

const refreshStatus = () => {
  fetchStatus()
}

const formatStatus = (status) => {
  if (!status) return 'Unknown'
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

watch(() => props.orderId, (newId) => {
  if (newId && props.autoLoad) {
    fetchStatus()
  }
})

onMounted(() => {
  if (props.autoLoad && props.orderId) {
    fetchStatus()
  }
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

@media (prefers-color-scheme: dark) {
  .card {
    background-color: #1f2937;
    border-color: #374151;
  }
}
</style>


