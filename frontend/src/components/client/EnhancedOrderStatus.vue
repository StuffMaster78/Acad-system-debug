<template>
  <div class="space-y-6">
    <!-- Enhanced Header with Gradient -->
    <div class="bg-gradient-to-r from-primary-50 via-blue-50 to-indigo-50 dark:from-primary-900/20 dark:via-blue-900/20 dark:to-indigo-900/20 rounded-2xl border border-primary-200/50 dark:border-primary-800/50 p-6 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 flex items-center justify-center shadow-lg">
            <ChartBarIcon class="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
              Order Status & Analytics
              <span class="text-sm font-normal text-primary-600 dark:text-primary-400 bg-primary-100 dark:bg-primary-900/30 px-2.5 py-0.5 rounded-full">
                #{{ orderId }}
              </span>
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">Comprehensive tracking, progress, and insights</p>
          </div>
        </div>
        <button
          @click="refreshStatus"
          :disabled="loading"
          class="px-5 py-2.5 bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-md hover:shadow-lg border border-primary-200 dark:border-primary-800 hover:scale-105 active:scale-95"
        >
          <ArrowPathIcon v-if="loading" class="animate-spin h-5 w-5" />
          <ArrowPathIcon v-else class="h-5 w-5" />
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Enhanced Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="relative">
        <div class="animate-spin rounded-full h-16 w-16 border-4 border-primary-100 dark:border-primary-900/30 border-t-primary-600 dark:border-t-primary-400 mb-6"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <ChartBarIcon class="w-6 h-6 text-primary-600 dark:text-primary-400 animate-pulse" />
        </div>
      </div>
      <p class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1">Loading Status Data</p>
      <p class="text-sm text-gray-600 dark:text-gray-400">Gathering comprehensive order analytics...</p>
      <p v-if="retryCount > 0" class="text-xs text-primary-600 dark:text-primary-400 mt-3 px-3 py-1.5 bg-primary-50 dark:bg-primary-900/20 rounded-full font-medium">
        Retrying... ({{ retryCount }}/{{ maxRetries }})
      </p>
    </div>

    <!-- Enhanced Error State -->
    <div v-else-if="error && endpointAvailable" class="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-2 border-red-200 dark:border-red-800 rounded-2xl p-8 shadow-lg">
      <div class="flex items-start gap-4">
        <div class="shrink-0 w-14 h-14 bg-red-500 dark:bg-red-600 rounded-xl flex items-center justify-center shadow-lg">
          <ExclamationTriangleIcon class="w-7 h-7 text-white" />
        </div>
        <div class="flex-1">
          <h4 class="text-lg font-bold text-red-800 dark:text-red-300 mb-2">Error Loading Status</h4>
          <p class="text-sm text-red-700 dark:text-red-400 mb-4">{{ error }}</p>
          <button
            @click="refreshStatus"
            class="px-4 py-2 bg-red-600 dark:bg-red-700 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-800 transition-colors text-sm font-semibold shadow-sm hover:shadow-md"
          >
            Try Again
          </button>
        </div>
      </div>
    </div>

    <!-- Enhanced Endpoint Not Available -->
    <div v-else-if="!loading && !error && !statusData && !endpointAvailable" class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border-2 border-gray-200 dark:border-gray-700 rounded-2xl p-12 text-center shadow-lg">
      <div class="flex flex-col items-center gap-6">
        <div class="w-20 h-20 bg-gradient-to-br from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-700 rounded-2xl flex items-center justify-center shadow-lg">
          <DocumentTextIcon class="w-10 h-10 text-gray-500 dark:text-gray-400" />
        </div>
        <div>
          <p class="text-lg text-gray-800 dark:text-gray-200 font-bold mb-2">Enhanced Status Tracking Unavailable</p>
          <p class="text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto">
            {{ isAdminUser ? 'Enhanced status data is not available for admin view. Please check the Overview tab for order details.' : 'This feature may not be enabled for this order or your account' }}
          </p>
          <button
            v-if="isAdminUser"
            @click="fetchStatus"
            class="mt-6 px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-all text-sm font-semibold shadow-md hover:shadow-lg"
          >
            Retry Loading
          </button>
        </div>
      </div>
    </div>

    <!-- Status Content -->
    <div v-else-if="statusData" class="space-y-6 animate-fade-in">
      <!-- Enhanced Current Status Card -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <CheckCircleIcon class="w-6 h-6 text-white" />
              </div>
              <h3 class="text-lg font-bold text-white">Current Status</h3>
            </div>
            <div class="px-5 py-2.5 bg-white/20 backdrop-blur-sm text-white rounded-xl font-bold text-sm border border-white/30 shadow-lg">
              {{ formatStatus(statusData.current_status) }}
            </div>
          </div>
        </div>
        <div class="p-6">
          <div v-if="statusData.progress" class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <ChartBarIcon class="w-4 h-4 text-primary-600 dark:text-primary-400" />
                Overall Progress
              </span>
              <span class="text-2xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-400 dark:to-primary-500 bg-clip-text text-transparent">
                {{ statusData.progress.percentage }}%
              </span>
            </div>
            <div class="relative w-full bg-gray-100 dark:bg-gray-700 rounded-full h-4 overflow-hidden shadow-inner">
              <div
                class="absolute inset-y-0 left-0 bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700 rounded-full transition-all duration-700 ease-out shadow-lg flex items-center justify-end pr-2"
                :style="{ width: `${statusData.progress.percentage}%` }"
              >
                <div v-if="statusData.progress.percentage > 10" class="w-2 h-2 bg-white rounded-full opacity-80"></div>
              </div>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-xs font-bold text-gray-600 dark:text-gray-300 z-10">{{ statusData.progress.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Estimated Completion -->
      <div v-if="statusData.estimated_completion" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 dark:from-indigo-600 dark:to-purple-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <ClockIcon class="w-6 h-6 text-white" />
            </div>
            Estimated Completion
          </h3>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div class="group p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border-2 border-blue-200 dark:border-blue-800 hover:border-blue-300 dark:hover:border-blue-700 transition-all hover:shadow-lg">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-blue-500 dark:bg-blue-600 flex items-center justify-center">
                  <ClockIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-blue-700 dark:text-blue-300 uppercase tracking-wider">Deadline</div>
              </div>
              <div class="text-xl font-bold text-gray-900 dark:text-gray-100">
                {{ formatDateTime(statusData.estimated_completion.deadline) }}
              </div>
            </div>
            <div class="group p-6 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl border-2 border-orange-200 dark:border-orange-800 hover:border-orange-300 dark:hover:border-orange-700 transition-all hover:shadow-lg">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-orange-500 dark:bg-orange-600 flex items-center justify-center">
                  <ClockIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-orange-700 dark:text-orange-300 uppercase tracking-wider">Time Remaining</div>
              </div>
              <div class="text-xl font-bold text-gray-900 dark:text-gray-100">
                {{ statusData.estimated_completion.days_remaining }} days
                <span class="text-sm font-normal text-gray-600 dark:text-gray-400 block mt-1">({{ statusData.estimated_completion.hours_remaining }} hours)</span>
              </div>
            </div>
            <div class="group p-6 rounded-xl border-2 transition-all hover:shadow-lg" :class="statusData.estimated_completion.is_overdue ? 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-800 hover:border-red-300 dark:hover:border-red-700' : 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800 hover:border-green-300 dark:hover:border-green-700'">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="statusData.estimated_completion.is_overdue ? 'bg-red-500 dark:bg-red-600' : 'bg-green-500 dark:bg-green-600'">
                  <ExclamationTriangleIcon v-if="statusData.estimated_completion.is_overdue" class="w-5 h-5 text-white" />
                  <CheckCircleIcon v-else class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold uppercase tracking-wider" :class="statusData.estimated_completion.is_overdue ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'">Status</div>
              </div>
              <div class="text-xl font-bold" :class="statusData.estimated_completion.is_overdue ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'">
                {{ statusData.estimated_completion.is_overdue ? 'Overdue' : 'On Track' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Writer Activity -->
      <div v-if="statusData.writer_activity" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 dark:from-emerald-600 dark:to-teal-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <UserIcon class="w-6 h-6 text-white" />
            </div>
            Writer Activity
          </h3>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-primary-500 dark:bg-primary-600 flex items-center justify-center">
                  <UserIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Writer</div>
              </div>
              <div class="text-xl font-bold text-gray-900 dark:text-gray-100">{{ statusData.writer_activity.writer_username || 'Unassigned' }}</div>
            </div>
            <div class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="statusData.writer_activity.is_active ? 'bg-green-500 dark:bg-green-600' : 'bg-gray-400 dark:bg-gray-600'">
                  <div class="w-3 h-3 rounded-full bg-white animate-pulse"></div>
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Activity Status</div>
              </div>
              <div class="flex items-center gap-2">
                <span
                  class="px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 shadow-sm"
                  :class="statusData.writer_activity.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-2 border-green-200 dark:border-green-800' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-gray-200 dark:border-gray-600'"
                >
                  <span class="w-2.5 h-2.5 rounded-full animate-pulse" :class="statusData.writer_activity.is_active ? 'bg-green-500' : 'bg-gray-400'"></span>
                  {{ statusData.writer_activity.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
            <div v-if="statusData.writer_activity.last_activity" class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-indigo-500 dark:bg-indigo-600 flex items-center justify-center">
                  <ClockIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Last Activity</div>
              </div>
              <div class="text-base font-bold text-gray-900 dark:text-gray-100 mb-1">
                {{ formatDateTime(statusData.writer_activity.last_activity) }}
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 font-medium">
                {{ statusData.writer_activity.hours_since_activity }} hours ago
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Quality Metrics -->
      <div v-if="statusData.quality_metrics" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-purple-500 to-pink-600 dark:from-purple-600 dark:to-pink-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <ChartPieIcon class="w-6 h-6 text-white" />
            </div>
            Quality Metrics
          </h3>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
            <div class="group text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border-2 border-blue-200 dark:border-blue-800 hover:border-blue-300 dark:hover:border-blue-700 transition-all hover:shadow-lg hover:scale-105">
              <div class="w-12 h-12 mx-auto mb-3 rounded-xl bg-blue-500 dark:bg-blue-600 flex items-center justify-center">
                <DocumentTextIcon class="w-6 h-6 text-white" />
              </div>
              <div class="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">{{ statusData.quality_metrics.revision_count || 0 }}</div>
              <div class="text-sm font-semibold text-gray-700 dark:text-gray-300">Revisions</div>
            </div>
            <div class="group text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl border-2 border-orange-200 dark:border-orange-800 hover:border-orange-300 dark:hover:border-orange-700 transition-all hover:shadow-lg hover:scale-105">
              <div class="w-12 h-12 mx-auto mb-3 rounded-xl bg-orange-500 dark:bg-orange-600 flex items-center justify-center">
                <ExclamationTriangleIcon class="w-6 h-6 text-white" />
              </div>
              <div class="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">{{ statusData.quality_metrics.dispute_count || 0 }}</div>
              <div class="text-sm font-semibold text-gray-700 dark:text-gray-300">Disputes</div>
            </div>
            <div class="group text-center p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl border-2 border-green-200 dark:border-green-800 hover:border-green-300 dark:hover:border-green-700 transition-all hover:shadow-lg hover:scale-105">
              <div class="w-12 h-12 mx-auto mb-3 rounded-xl bg-green-500 dark:bg-green-600 flex items-center justify-center">
                <ChartBarIcon class="w-6 h-6 text-white" />
              </div>
              <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
                {{ statusData.quality_metrics.average_rating || 'N/A' }}
              </div>
              <div class="text-sm font-semibold text-gray-700 dark:text-gray-300">Avg Rating</div>
            </div>
            <div class="group text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl border-2 border-purple-200 dark:border-purple-800 hover:border-purple-300 dark:hover:border-purple-700 transition-all hover:shadow-lg hover:scale-105">
              <div class="w-12 h-12 mx-auto mb-3 rounded-xl bg-purple-500 dark:bg-purple-600 flex items-center justify-center">
                <CheckCircleIcon v-if="statusData.quality_metrics.has_reviews" class="w-6 h-6 text-white" />
                <ExclamationTriangleIcon v-else class="w-6 h-6 text-white" />
              </div>
              <div class="text-3xl font-bold mb-2" :class="statusData.quality_metrics.has_reviews ? 'text-green-600 dark:text-green-400' : 'text-gray-400 dark:text-gray-500'">
                {{ statusData.quality_metrics.has_reviews ? 'Yes' : 'No' }}
              </div>
              <div class="text-sm font-semibold text-gray-700 dark:text-gray-300">Has Reviews</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Recent Progress Updates -->
      <div v-if="statusData.progress?.recent_updates?.length" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-cyan-500 to-blue-600 dark:from-cyan-600 dark:to-blue-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <ChartBarIcon class="w-6 h-6 text-white" />
            </div>
            Recent Progress Updates
          </h3>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div
              v-for="(update, index) in statusData.progress.recent_updates"
              :key="index"
              class="group flex items-start gap-4 p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-md transition-all"
            >
              <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 rounded-xl flex items-center justify-center border-2 border-primary-300 dark:border-primary-800 shrink-0 shadow-lg">
                <span class="text-white font-bold text-xl">{{ update.progress_percentage }}%</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-base font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
                  <ClockIcon class="w-4 h-4 text-primary-600 dark:text-primary-400" />
                  {{ formatDateTime(update.timestamp) }}
                </div>
                <div v-if="update.notes" class="text-sm text-gray-700 dark:text-gray-300 mt-2 leading-relaxed bg-white dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                  {{ update.notes }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Status Timeline -->
      <div v-if="statusData.status_timeline?.length" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-violet-500 to-purple-600 dark:from-violet-600 dark:to-purple-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <ClockIcon class="w-6 h-6 text-white" />
            </div>
            Status Timeline
          </h3>
        </div>
        <div class="p-6">
          <div class="relative border-l-4 border-primary-300 dark:border-primary-700 pl-8 space-y-8">
            <div
              v-for="(transition, index) in statusData.status_timeline"
              :key="index"
              class="relative group"
            >
              <div class="absolute -left-[36px] top-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 border-4 border-white dark:border-gray-800 shadow-lg flex items-center justify-center group-hover:scale-125 transition-transform">
                <div class="w-2 h-2 rounded-full bg-white"></div>
              </div>
              <div class="pb-8 last:pb-0">
                <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl p-5 border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-md transition-all">
                  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div class="flex-1">
                      <div class="font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2 text-lg">
                        <span class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-lg text-sm font-semibold">
                          {{ formatStatus(transition.from_status) }}
                        </span>
                        <ArrowRightIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        <span class="px-3 py-1 bg-primary-500 dark:bg-primary-600 text-white rounded-lg text-sm font-semibold">
                          {{ formatStatus(transition.to_status) }}
                        </span>
                      </div>
                      <div class="text-sm text-gray-700 dark:text-gray-300 mt-2 font-medium">{{ transition.action }}</div>
                      <div class="text-xs text-gray-600 dark:text-gray-400 mt-3 flex items-center gap-3">
                        <span class="px-3 py-1.5 rounded-lg font-semibold" :class="transition.is_automatic ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300' : 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'">
                          {{ transition.is_automatic ? '🤖 Auto' : '👤 Manual' }}
                        </span>
                        <span class="font-medium">by {{ transition.actor }}</span>
                      </div>
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap font-medium flex items-center gap-2">
                      <ClockIcon class="w-4 h-4" />
                      {{ formatDateTime(transition.timestamp) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Writer Reassignments -->
      <div v-if="statusData.writer_reassignments?.length" class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-amber-500 to-orange-600 dark:from-amber-600 dark:to-orange-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <ArrowRightIcon class="w-6 h-6 text-white" />
            </div>
            Writer Reassignments
          </h3>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div
              v-for="(reassignment, index) in statusData.writer_reassignments"
              :key="index"
              class="p-6 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-xl border-2 border-yellow-200 dark:border-yellow-800 hover:border-yellow-300 dark:hover:border-yellow-700 hover:shadow-lg transition-all"
            >
              <div class="flex items-center justify-between mb-4">
                <div class="font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3 text-lg">
                  <span class="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-semibold">
                    {{ reassignment.previous_writer || 'Unassigned' }}
                  </span>
                  <ArrowRightIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  <span class="px-3 py-1.5 bg-primary-500 dark:bg-primary-600 text-white rounded-lg text-sm font-semibold">
                    {{ reassignment.new_writer || 'Unassigned' }}
                  </span>
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap font-medium flex items-center gap-2">
                  <ClockIcon class="w-4 h-4" />
                  {{ formatDateTime(reassignment.timestamp) }}
                </div>
              </div>
              <div class="text-sm text-gray-700 dark:text-gray-300 mb-3 font-medium bg-white dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                {{ reassignment.reason }}
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 font-semibold">Reassigned by: <span class="text-primary-600 dark:text-primary-400">{{ reassignment.reassigned_by }}</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Order Details -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300">
        <div class="bg-gradient-to-r from-slate-500 to-gray-600 dark:from-slate-600 dark:to-gray-700 px-6 py-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <DocumentTextIcon class="w-6 h-6 text-white" />
            </div>
            Order Details
          </h3>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-primary-500 dark:bg-primary-600 flex items-center justify-center">
                  <DocumentTextIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Topic</div>
              </div>
              <div class="text-lg font-bold text-gray-900 dark:text-gray-100 line-clamp-2">{{ statusData.order_topic }}</div>
            </div>
            <div v-if="statusData.order_details.type_of_work" class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-indigo-500 dark:bg-indigo-600 flex items-center justify-center">
                  <DocumentTextIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type of Work</div>
              </div>
              <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_details.type_of_work }}</div>
            </div>
            <div v-if="statusData.order_details.paper_type" class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-blue-500 dark:bg-blue-600 flex items-center justify-center">
                  <DocumentTextIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Paper Type</div>
              </div>
              <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_details.paper_type }}</div>
            </div>
            <div v-if="statusData.order_details.number_of_pages" class="group p-5 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-md">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-lg bg-teal-500 dark:bg-teal-600 flex items-center justify-center">
                  <DocumentTextIcon class="w-5 h-5 text-white" />
                </div>
                <div class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Pages</div>
              </div>
              <div class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ statusData.order_details.number_of_pages }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import clientDashboardAPI from '@/api/client-dashboard'
import adminOrdersAPI from '@/api/admin-orders'
import ordersAPI from '@/api/orders'
import {
  ChartBarIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ClockIcon,
  UserIcon,
  ChartPieIcon,
  DocumentTextIcon,
  ArrowRightIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

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

const authStore = useAuthStore()
const loading = ref(false)
const error = ref(null)
const statusData = ref(null)
const endpointAvailable = ref(true) // Track if endpoint is available
const retryCount = ref(0)
const maxRetries = 2

// Determine which API to use based on user role
const isAdminUser = computed(() => {
  return authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport
})

const fetchStatus = async (isRetry = false) => {
  if (!props.orderId) return
  
  // Don't retry if we've exceeded max retries
  if (isRetry && retryCount.value >= maxRetries) {
    endpointAvailable.value = false
    loading.value = false
    return
  }
  
  if (isRetry) {
    retryCount.value++
  } else {
    retryCount.value = 0
  }
  
  loading.value = true
  error.value = null
  
  try {
    let response
    
    // For admin users, try admin endpoint first, then fall back to client endpoint
    if (isAdminUser.value) {
      try {
        // Try admin timeline endpoint as fallback for enhanced data
        const timelineResponse = await adminOrdersAPI.getOrderTimeline(props.orderId)
        if (timelineResponse?.data) {
          // Transform timeline data to match enhanced status format
          statusData.value = transformTimelineToEnhancedStatus(timelineResponse.data)
          endpointAvailable.value = true
          loading.value = false
          retryCount.value = 0
          return
        }
      } catch (adminErr) {
        // If admin endpoint fails (500, 404, etc.), silently continue to fallback
        // Only log in development mode
        if (import.meta.env.DEV) {
          console.log('Admin timeline endpoint not available:', adminErr.response?.status || 'network error')
        }
        // Don't return here - continue to try client endpoint or fallback to basic order data
      }
    }
    
    // Try client endpoint (works for clients, may work for admins if they have access)
    try {
      response = await clientDashboardAPI.getEnhancedOrderStatus(props.orderId)
      statusData.value = response?.data || null
      endpointAvailable.value = true
      retryCount.value = 0 // Reset retry count on success
      loading.value = false
      return
    } catch (clientErr) {
      // If client endpoint also fails, fall back to basic order data for admins
      if (isAdminUser.value && (clientErr.response?.status === 404 || clientErr.response?.status === 403)) {
        try {
          const orderResponse = await ordersAPI.get(props.orderId)
          if (orderResponse?.data) {
            // Create a basic enhanced status from order data
            statusData.value = createBasicEnhancedStatus(orderResponse.data)
            endpointAvailable.value = true
            loading.value = false
            retryCount.value = 0
            return
          }
        } catch (orderErr) {
          // Silently handle - order data fallback failed
          if (import.meta.env.DEV) {
            console.log('Could not fetch order data as fallback:', orderErr)
          }
        }
      }
      
      // Re-throw to be handled by outer catch
      throw clientErr
    }
    
  } catch (err) {
    // Handle 404 and 403 gracefully - endpoint may not be available or user may not have access
    if (err.response?.status === 404 || err.response?.status === 403) {
      // For admin users, try to get basic order data as fallback (if not already tried)
      if (isAdminUser.value) {
        try {
          const orderResponse = await ordersAPI.get(props.orderId)
          if (orderResponse?.data) {
            // Create a basic enhanced status from order data
            statusData.value = createBasicEnhancedStatus(orderResponse.data)
            endpointAvailable.value = true
            loading.value = false
            return
          }
        } catch (orderErr) {
          // Silently handle - order data fallback failed
          if (import.meta.env.DEV) {
            console.log('Could not fetch order data as fallback')
          }
        }
      }
      
      // Silently handle - endpoint doesn't exist, isn't accessible, or user doesn't have permission
      statusData.value = null
      error.value = null // Don't show error for 404/403
      endpointAvailable.value = false // Mark endpoint as unavailable
      loading.value = false
      return
    }
    
    // Handle 500 errors - try fallback to basic order data for admins
    if (err.response?.status >= 500) {
      // Only log in development mode
      if (import.meta.env.DEV) {
        console.error('Server error fetching enhanced order status:', err)
      }
      
      // For admin users, try to get basic order data as fallback
      if (isAdminUser.value) {
        try {
          const orderResponse = await ordersAPI.get(props.orderId)
          if (orderResponse?.data) {
            // Create a basic enhanced status from order data
            statusData.value = createBasicEnhancedStatus(orderResponse.data)
            endpointAvailable.value = true
            loading.value = false
            // Don't show error if we successfully got fallback data
            error.value = null
            return
          }
        } catch (orderErr) {
          // Silently handle - order data fallback failed
          if (import.meta.env.DEV) {
            console.log('Could not fetch order data as fallback after server error')
          }
        }
      }
      
      // If fallback failed or not admin, show error and retry
      error.value = err.response?.data?.detail || 'Failed to load order status'
      endpointAvailable.value = true // Keep endpoint as available for retry
      
      // Retry on server errors (only if we haven't already tried fallback)
      if (!isRetry && retryCount.value < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount.value + 1))) // Exponential backoff
        await fetchStatus(true)
        return
      }
    } else if (!err.response) {
      // Network error - try fallback for admins
      if (isAdminUser.value) {
        try {
          const orderResponse = await ordersAPI.get(props.orderId)
          if (orderResponse?.data) {
            statusData.value = createBasicEnhancedStatus(orderResponse.data)
            endpointAvailable.value = true
            loading.value = false
            error.value = null
            return
          }
        } catch (orderErr) {
          // Silently handle - order data fallback failed
          if (import.meta.env.DEV) {
            console.log('Could not fetch order data as fallback for network error')
          }
        }
      }
      
      error.value = 'Network error. Please check your connection and try again.'
      endpointAvailable.value = true
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

// Transform timeline data to enhanced status format
const transformTimelineToEnhancedStatus = (timelineData) => {
  return {
    current_status: timelineData.current_status || 'unknown',
    progress: {
      percentage: timelineData.progress_percentage || 0,
      recent_updates: timelineData.recent_progress || []
    },
    estimated_completion: timelineData.estimated_completion || null,
    writer_activity: timelineData.writer_activity || null,
    quality_metrics: timelineData.quality_metrics || null,
    status_timeline: timelineData.timeline || [],
    writer_reassignments: timelineData.reassignments || [],
    order_topic: timelineData.order_topic || '',
    order_details: timelineData.order_details || {}
  }
}

// Create basic enhanced status from order data
const createBasicEnhancedStatus = (orderData) => {
  return {
    current_status: orderData.status || 'unknown',
    progress: {
      percentage: 0,
      recent_updates: []
    },
    estimated_completion: orderData.writer_deadline ? {
      deadline: orderData.writer_deadline,
      days_remaining: calculateDaysRemaining(orderData.writer_deadline),
      hours_remaining: calculateHoursRemaining(orderData.writer_deadline),
      is_overdue: new Date(orderData.writer_deadline) < new Date()
    } : null,
    writer_activity: orderData.assigned_writer ? {
      writer_username: orderData.assigned_writer?.username || orderData.writer_username || 'Unknown',
      is_active: true,
      last_activity: orderData.updated_at,
      hours_since_activity: calculateHoursSince(orderData.updated_at)
    } : null,
    quality_metrics: {
      revision_count: 0,
      dispute_count: 0,
      average_rating: null,
      has_reviews: false
    },
    status_timeline: [],
    writer_reassignments: [],
    order_topic: orderData.topic || '',
    order_details: {
      type_of_work: orderData.type_of_work?.name || orderData.type_of_work_name,
      paper_type: orderData.paper_type?.name || orderData.paper_type_name,
      number_of_pages: orderData.number_of_pages
    }
  }
}

const calculateDaysRemaining = (deadline) => {
  if (!deadline) return 0
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate - now
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

const calculateHoursRemaining = (deadline) => {
  if (!deadline) return 0
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate - now
  return Math.ceil(diff / (1000 * 60 * 60))
}

const calculateHoursSince = (date) => {
  if (!date) return 0
  const now = new Date()
  const dateObj = new Date(date)
  const diff = now - dateObj
  return Math.floor(diff / (1000 * 60 * 60))
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
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>


