<template>
  <div class="space-y-6">
    <!-- Page header with Place Order button -->
    <div class="flex items-center justify-between">
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
          <div v-if="!isOnline" class="flex items-center gap-2 px-3 py-1 bg-red-50 border border-red-200 rounded-lg">
            <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
            </svg>
            <span class="text-xs font-medium text-red-600">Offline</span>
          </div>
        </div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Welcome back, {{ authStore.user?.email }}</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          v-if="authStore.isAdmin || authStore.isSuperAdmin"
          @click="refreshDashboard"
          :disabled="refreshing"
          class="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <svg 
            class="w-5 h-5" 
            :class="{ 'animate-spin': refreshing }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ refreshing ? 'Refreshing...' : 'Refresh' }}
        </button>
        <router-link
          v-if="authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport"
          to="/admin/orders/create"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Place Order
        </router-link>
        <router-link
          v-if="authStore.isClient"
          to="/orders/wizard"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm hover:shadow-md font-semibold"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create Order
        </router-link>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <p class="text-sm text-red-800">
            <strong>Error loading dashboard:</strong> {{ error }}
          </p>
        </div>
        <button
          @click="refreshDashboard"
          class="text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Loading State for Admin/Superadmin -->
    <div v-if="(authStore.isAdmin || authStore.isSuperAdmin) && loading.summary && !error" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Loading dashboard data...</p>
      </div>
    </div>

    <!-- Impersonation banner -->
    <div v-if="authStore.isImpersonating" class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <p class="text-sm text-yellow-800">
            You are impersonating <strong>{{ authStore.user?.email }}</strong>
          </p>
        </div>
        <button
          @click="handleEndImpersonation"
          class="btn btn-secondary text-sm"
        >
          End Impersonation
        </button>
      </div>
    </div>

    <!-- Role-Specific Dashboards -->
    <div v-if="authStore.isClient">
      <!-- Loading State -->
      <div v-if="loading.summary" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
      
      <!-- Client Dashboard Content -->
    <ClientDashboard
        v-else
        :client-dashboard-data="clientDashboardData || {}"
        :client-loyalty-data="clientLoyaltyData || {}"
        :client-analytics-data="clientAnalyticsData || {}"
        :client-wallet-analytics="clientWalletAnalytics || {}"
        :wallet-balance="walletBalance || 0"
        :recent-orders="recentOrders || []"
      :recent-orders-loading="recentOrdersLoading"
        :recent-notifications="recentNotifications || []"
      :recent-notifications-loading="recentNotificationsLoading"
        :loading="false"
      />
    </div>

    <!-- Writer Summary Stats -->
    <div v-if="authStore.isWriter" class="space-y-6">
      <!-- Enhanced Summary Stats Grid -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="stat in enhancedWriterStats"
          :key="stat.name"
          class="card bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border border-gray-100 transform hover:scale-[1.02]"
          :class="stat.gradientBg"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex-1">
              <p class="text-sm font-semibold text-gray-600 mb-1 uppercase tracking-wide">{{ stat.name }}</p>
              <p class="text-3xl font-bold mb-1" :class="stat.valueColor">{{ stat.value }}</p>
              <p v-if="stat.subtitle" class="text-xs font-medium mt-1" :class="stat.subtitleColor">{{ stat.subtitle }}</p>
              <div v-if="stat.trend !== null && stat.trend !== undefined" class="mt-2 flex items-center gap-1">
                <span :class="[
                  'text-xs font-semibold flex items-center gap-1',
                  stat.trend > 0 ? 'text-green-600' : stat.trend < 0 ? 'text-red-600' : 'text-gray-500'
                ]">
                  <svg v-if="stat.trend > 0" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                  <svg v-else-if="stat.trend < 0" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span>{{ Math.abs(stat.trend) }}%</span>
                </span>
                <span class="text-xs text-gray-500">vs last month</span>
              </div>
            </div>
            <div class="p-4 rounded-xl shadow-md" :class="stat.iconBg">
              <span class="text-3xl">{{ stat.icon }}</span>
            </div>
          </div>
          <div v-if="stat.progress !== null && stat.progress !== undefined" class="mt-4">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-gray-600">Progress</span>
              <span class="text-xs font-semibold" :class="stat.valueColor">{{ stat.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                class="h-2 rounded-full transition-all duration-500"
                :class="stat.progressColor"
                :style="{ width: `${Math.min(stat.progress, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Writer Metrics -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div
          v-for="metric in writerQuickMetrics"
          :key="metric.name"
          class="card bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-sm p-5 border border-gray-100 hover:shadow-md transition-all"
        >
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs font-semibold text-gray-600 uppercase tracking-wide">{{ metric.name }}</p>
            <span class="text-xl">{{ metric.icon }}</span>
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ metric.value }}</p>
          <p v-if="metric.description" class="text-xs text-gray-500 mt-1">{{ metric.description }}</p>
        </div>
      </div>
    </div>

    <WriterDashboard
      @order-requested="handleOrderRequested"
      @refresh-requested="handleWriterRefreshRequest"
      v-if="authStore.isWriter"
      :writer-earnings-data="writerEarningsData"
      :writer-performance-data="writerPerformanceData"
      :writer-queue-data="writerQueueData"
      :writer-badges-data="writerBadgesData"
      :writer-level-data="writerLevelData"
      :writer-summary-data="writerSummaryData"
      :recent-orders="recentOrders"
      :recent-orders-loading="recentOrdersLoading"
      :loading="loading.summary"
    />

    <EditorDashboard
      v-if="authStore.isEditor"
      :editor-dashboard-data="editorDashboardData"
      :loading="loading.summary"
    />

    <SupportDashboard
      v-if="authStore.isSupport"
      :support-dashboard-data="supportDashboardData"
      :support-recent-tickets="supportRecentTickets"
      :support-recent-tickets-loading="supportRecentTicketsLoading"
      :loading="loading.summary"
    />

    <!-- Admin/Superadmin Quick Actions - Improved Layout -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Quick Actions</h2>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <router-link 
          to="/admin/orders" 
          class="group relative bg-white rounded-xl shadow-sm p-5 text-center transition-all duration-200 hover:shadow-lg hover:scale-[1.02] border-2 border-gray-200 hover:border-primary-400"
        >
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">📝</div>
          <div class="font-semibold text-gray-900 mb-1">Orders</div>
          <div class="text-xs text-gray-500">Manage all orders</div>
          <div class="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </router-link>
        <router-link 
          to="/admin/users" 
          class="group relative bg-white rounded-xl shadow-sm p-5 text-center transition-all duration-200 hover:shadow-lg hover:scale-[1.02] border-2 border-gray-200 hover:border-primary-400"
        >
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">👥</div>
          <div class="font-semibold text-gray-900 mb-1">Users</div>
          <div class="text-xs text-gray-500">Manage users</div>
          <div class="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </router-link>
        <router-link 
          to="/admin/payments/writer-payments" 
          class="group relative bg-white rounded-xl shadow-sm p-5 text-center transition-all duration-200 hover:shadow-lg hover:scale-[1.02] border-2 border-gray-200 hover:border-primary-400"
        >
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">💳</div>
          <div class="font-semibold text-gray-900 mb-1">Payments</div>
          <div class="text-xs text-gray-500">Writer payouts</div>
          <div class="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </router-link>
        <router-link 
          to="/admin/refunds" 
          class="group relative bg-white rounded-xl shadow-sm p-5 text-center transition-all duration-200 hover:shadow-lg hover:scale-[1.02] border-2 border-gray-200 hover:border-primary-400"
        >
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">↩️</div>
          <div class="font-semibold text-gray-900 mb-1">Refunds</div>
          <div class="text-xs text-gray-500">Process refunds</div>
          <div class="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </router-link>
        <router-link 
          to="/websites" 
          class="group relative bg-white rounded-xl shadow-sm p-5 text-center transition-all duration-200 hover:shadow-lg hover:scale-[1.02] border-2 border-gray-200 hover:border-primary-400"
        >
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">🌐</div>
          <div class="font-semibold text-gray-900 mb-1">Websites</div>
          <div class="text-xs text-gray-500">Multi-tenant</div>
          <div class="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </router-link>
      </div>
    </div>

    <!-- Content Metrics Quick Link (Admin/Superadmin) -->
    <router-link
      v-if="authStore.isAdmin || authStore.isSuperAdmin"
      to="/admin/content-metrics-report"
      class="block mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 hover:shadow-md transition-all cursor-pointer relative z-10 no-underline"
    >
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">Content Metrics & Reporting</h3>
          <p class="text-sm text-gray-600 mt-1">View content performance, publishing targets, and freshness metrics</p>
        </div>
        <svg class="w-6 h-6 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </router-link>

    <!-- Summary Stats Grid (Admin/Superadmin) - Primary Metrics -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="stat in summaryStats"
        :key="stat.name"
        :class="[
          'card bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-primary-200',
          stat.name === 'Total Revenue' 
            ? 'lg:col-span-2 p-8' 
            : 'p-6'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0 pr-4">
            <p 
              :class="[
                'font-medium text-gray-600 mb-2 uppercase tracking-wide',
                stat.name === 'Total Revenue' ? 'text-base' : 'text-sm'
              ]"
            >{{ stat.name }}</p>
            <p 
              :class="[
                'font-bold text-gray-900 mb-1 break-words',
                stat.name === 'Total Revenue' 
                  ? 'text-4xl sm:text-5xl lg:text-6xl' 
                  : stat.size === 'compact' 
                    ? 'text-2xl' 
                    : 'text-3xl'
              ]"
              style="word-break: break-word; overflow-wrap: break-word;"
            >{{ stat.value }}</p>
            <p 
              v-if="stat.subtitle" 
              :class="[
                'text-gray-500 mt-1 leading-relaxed',
                stat.name === 'Total Revenue' ? 'text-sm' : 'text-xs'
              ]"
            >{{ stat.subtitle }}</p>
            <p v-if="stat.change !== null && stat.change !== undefined" :class="[
              'text-sm mt-2 flex items-center',
              stat.change > 0 ? 'text-green-600' : stat.change < 0 ? 'text-red-600' : 'text-gray-500'
            ]">
              <span class="mr-1">{{ stat.change > 0 ? '↑' : stat.change < 0 ? '↓' : '→' }}</span>
              {{ Math.abs(stat.change) }}% from last month
            </p>
          </div>
          <div 
            :class="[
              'rounded-lg shrink-0',
              stat.name === 'Total Revenue' ? 'p-4 ml-4' : 'p-3 ml-4',
              stat.bgColor || 'bg-primary-100'
            ]"
          >
            <span :class="stat.name === 'Total Revenue' ? 'text-4xl' : 'text-2xl'">{{ stat.icon }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Grid (Admin/Superadmin) - Secondary Metrics -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mt-6">
      <div
        v-for="metric in keyMetrics"
        :key="metric.name"
        class="card bg-white rounded-lg shadow-sm p-5 hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-primary-200"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">{{ metric.name }}</p>
            <p 
              :class="[
                'font-bold text-gray-900 mb-1',
                metric.size === 'compact' ? 'text-xl' : 'text-2xl'
              ]"
            >{{ metric.value }}</p>
            <p v-if="metric.subtitle" class="text-xs text-gray-500 mt-1">{{ metric.subtitle }}</p>
          </div>
          <div class="p-2.5 rounded-lg ml-3 shrink-0" :class="metric.bgColor || 'bg-gray-100'">
            <span class="text-xl">{{ metric.icon }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- User Statistics (Admin/Superadmin) -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div
        v-for="stat in userStats"
        :key="stat.name"
        class="card bg-gradient-to-br from-white to-gray-50 rounded-lg shadow-sm p-5 border border-gray-100 hover:shadow-md transition-all duration-200 hover:scale-[1.02]"
      >
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ stat.name }}</p>
          <span class="text-xl">{{ stat.icon }}</span>
        </div>
        <p v-if="loading.summary" class="text-2xl font-bold text-gray-300 animate-pulse mb-1">—</p>
        <p v-else class="text-2xl font-bold text-gray-900 mb-1">{{ stat.value }}</p>
        <p v-if="stat.percentage !== undefined && !loading.summary" class="text-xs text-gray-500">{{ stat.percentage }}% of total</p>
      </div>
    </div>

    <!-- Order Status Metrics Quick Link (Admin/Superadmin) -->
    <router-link
      v-if="authStore.isAdmin || authStore.isSuperAdmin"
      to="/admin/order-status-metrics"
      class="block mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200 hover:shadow-md transition-all cursor-pointer relative z-10 no-underline"
    >
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">Order Status Metrics</h3>
          <p class="text-sm text-gray-600 mt-1">View order status distribution and workflow metrics</p>
        </div>
        <svg class="w-6 h-6 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </router-link>

    <!-- Tickets Overview (Admin/Superadmin) -->
    <div v-if="(authStore.isAdmin || authStore.isSuperAdmin) && summaryData?.total_tickets !== undefined" class="card bg-white rounded-lg shadow-sm p-6 border border-gray-100">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Support Tickets</h2>
        <router-link to="/tickets" class="text-primary-600 text-sm hover:underline">View all tickets</router-link>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="text-center p-4 bg-blue-50 rounded-lg">
          <p class="text-sm font-medium text-gray-600 mb-1">Total Tickets</p>
          <p class="text-2xl font-bold text-blue-600">{{ summaryData.total_tickets || 0 }}</p>
        </div>
        <div class="text-center p-4 bg-orange-50 rounded-lg">
          <p class="text-sm font-medium text-gray-600 mb-1">Open Tickets</p>
          <p class="text-2xl font-bold text-orange-600">{{ summaryData.open_tickets_count || 0 }}</p>
        </div>
        <div class="text-center p-4 bg-green-50 rounded-lg">
          <p class="text-sm font-medium text-gray-600 mb-1">Closed Tickets</p>
          <p class="text-2xl font-bold text-green-600">{{ summaryData.closed_tickets_count || 0 }}</p>
        </div>
      </div>
    </div>

    <!-- Payment Reminders Overview (Admin/Superadmin) -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="card bg-white rounded-lg shadow-sm p-6 border border-gray-100">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Payment Reminders</h2>
        <router-link to="/admin/configs?tab=payment-reminders" class="text-primary-600 text-sm hover:underline">Manage reminders</router-link>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-gray-600">Reminder Configs</p>
            <span class="text-xl">📧</span>
          </div>
          <p class="text-2xl font-bold text-blue-600">{{ paymentReminderStats?.total_reminder_configs ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ paymentReminderStats?.active_reminder_configs ?? 0 }} active</p>
        </div>
        <div class="p-4 bg-purple-50 rounded-lg border border-purple-100">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-gray-600">Deletion Messages</p>
            <span class="text-xl">🗑️</span>
          </div>
          <p class="text-2xl font-bold text-purple-600">{{ paymentReminderStats?.total_deletion_messages ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ paymentReminderStats?.active_deletion_messages ?? 0 }} active</p>
        </div>
        <div class="p-4 bg-green-50 rounded-lg border border-green-100">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-gray-600">Sent Reminders</p>
            <span class="text-xl">✅</span>
          </div>
          <p class="text-2xl font-bold text-green-600">{{ paymentReminderStats?.total_sent_reminders ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Total sent</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity (Admin/Superadmin) -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="card bg-white rounded-lg shadow-sm p-6 border border-gray-100">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Recent Activity</h2>
        <router-link to="/activity" class="text-primary-600 text-sm hover:underline">View all logs</router-link>
      </div>
      <div v-if="recentActivityLoading" class="text-center py-8 text-gray-500">Loading activity...</div>
      <div v-else-if="recentActivity.length" class="space-y-3">
        <div 
          v-for="(activity, index) in recentActivity.slice(0, 5)" 
          :key="index"
          class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-sm">📋</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900">{{ activity.action }}</p>
            <div class="flex items-center gap-2 mt-1">
              <p v-if="activity.timestamp" class="text-xs text-gray-500">{{ formatDate(activity.timestamp) }}</p>
              <p v-if="activity.admin" class="text-xs text-gray-400">by {{ activity.admin }}</p>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">No recent activity</div>
    </div>

    <!-- Charts Grid (Admin/Superadmin only) -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Yearly Orders Chart -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Orders by Month ({{ currentYear }})</h2>
        <div v-if="yearlyOrdersLoading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
        <div v-else>
          <div
            v-if="!chartsReady"
            class="flex items-center justify-center h-64 text-gray-400 bg-gray-50 border border-dashed border-gray-200 rounded-lg"
          >
            Preparing chart...
        </div>
        <apexchart
          v-else
          type="area"
          height="300"
          :options="yearlyOrdersChartOptions"
          :series="yearlyOrdersSeries"
        ></apexchart>
        </div>
      </div>

      <!-- Yearly Earnings Chart -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Earnings by Month ({{ currentYear }})</h2>
        <div v-if="yearlyEarningsLoading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
        <div v-else>
          <div
            v-if="!chartsReady"
            class="flex items-center justify-center h-64 text-gray-400 bg-gray-50 border border-dashed border-gray-200 rounded-lg"
          >
            Preparing chart...
        </div>
        <apexchart
          v-else
          type="bar"
          height="300"
          :options="yearlyEarningsChartOptions"
          :series="yearlyEarningsSeries"
        ></apexchart>
        </div>
      </div>

      <!-- Payment Status Chart -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Payment Status Breakdown</h2>
        <div v-if="paymentStatusLoading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
        <div v-else>
          <div
            v-if="!chartsReady"
            class="flex items-center justify-center h-64 text-gray-400 bg-gray-50 border border-dashed border-gray-200 rounded-lg"
          >
            Preparing chart...
        </div>
        <apexchart
          v-else
          type="donut"
          height="300"
          :options="paymentStatusChartOptions"
          :series="paymentStatusSeries"
        ></apexchart>
        </div>
      </div>

      <!-- Service Revenue Chart -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Service Revenue (Last 30 Days)</h2>
        <div v-if="serviceRevenueLoading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
        <div v-else>
          <div
            v-if="!chartsReady"
            class="flex items-center justify-center h-64 text-gray-400 bg-gray-50 border border-dashed border-gray-200 rounded-lg"
          >
            Preparing chart...
        </div>
        <apexchart
          v-else
          type="pie"
          height="300"
          :options="serviceRevenueChartOptions"
          :series="serviceRevenueSeries"
        ></apexchart>
        </div>
      </div>
    </div>

    <!-- Monthly Orders Chart (Admin/Superadmin only) -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Daily Orders ({{ currentMonthName }} {{ currentYear }})</h2>
        <select
          v-model="selectedMonth"
          @change="fetchMonthlyOrders"
          class="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
      </div>
      <div v-if="monthlyOrdersLoading" class="flex items-center justify-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
      <div v-else>
        <div
          v-if="!chartsReady"
          class="flex items-center justify-center h-72 text-gray-400 bg-gray-50 border border-dashed border-gray-200 rounded-lg"
        >
          Preparing chart...
      </div>
      <apexchart
        v-else
        type="line"
        height="350"
        :options="monthlyOrdersChartOptions"
        :series="monthlyOrdersSeries"
      ></apexchart>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import dashboardAPI from '@/api/dashboard'
import editorDashboardAPI from '@/api/editor-dashboard'
import editorTasksAPI from '@/api/editor-tasks'
import supportDashboardAPI from '@/api/support-dashboard'
import supportTicketsAPI from '@/api/support-tickets'
import writerDashboardAPI from '@/api/writer-dashboard'
import superadminDashboardAPI from '@/api/superadmin-dashboard'
import clientDashboardAPI from '@/api/client-dashboard'
import walletAPI from '@/api/wallet'
import notificationsAPI from '@/api/notifications'
import ClientDashboard from './components/ClientDashboard.vue'
import WriterDashboard from './components/WriterDashboard.vue'
import EditorDashboard from './components/EditorDashboard.vue'
// ContentRemindersWidget moved to ContentMetricsReport page
import SupportDashboard from './components/SupportDashboard.vue'
import { useReliableOrders } from '@/composables/useReliableOrders'
import { useConnectionStatus } from '@/composables/useConnectionStatus'
import { retryApiCall } from '@/utils/retry'
// ApexCharts is globally registered via VueApexCharts plugin

const authStore = useAuthStore()

// Connection status monitoring
const { isOnline } = useConnectionStatus()

// Listen for connection restoration to auto-refresh
let connectionRestoredHandler = null
onMounted(() => {
  connectionRestoredHandler = () => {
    // Auto-refresh dashboard when connection is restored
    if (authStore.isAuthenticated) {
      console.log('Connection restored, refreshing dashboard...')
      refreshDashboard()
    }
  }
  
  window.addEventListener('connection-restored', connectionRestoredHandler)
})

onUnmounted(() => {
  if (connectionRestoredHandler) {
    window.removeEventListener('connection-restored', connectionRestoredHandler)
  }
})

// State
const summaryData = ref(null)
const yearlyOrdersData = ref([])
const yearlyEarningsData = ref([])
const monthlyOrdersData = ref([])
const serviceRevenueData = ref(null)
const paymentStatusData = ref(null)
const recentActivity = ref([])
const paymentReminderStats = ref(null)
const chartsReady = ref(false)
const error = ref(null)

const loading = ref({
  summary: false,
  yearlyOrders: false,
  yearlyEarnings: false,
  monthlyOrders: false,
  serviceRevenue: false,
  paymentStatus: false,
})
const refreshing = ref(false)
const recentOrdersLoading = ref(false)
const recentOrders = ref([])
const walletBalance = ref(0)
const walletLoading = ref(false)
const recentNotifications = ref([])
const recentNotificationsLoading = ref(false)
const recentActivityLoading = ref(false)

// Role-specific dashboard data
const editorDashboardData = ref(null)
const writerDashboardData = ref(null)
const writerEarningsData = ref(null)
const writerPerformanceData = ref(null)
const writerQueueData = ref(null)
const writerBadgesData = ref(null)
const writerLevelData = ref(null)
const writerSummaryData = ref(null)
const supportDashboardData = ref(null)
const supportRecentTickets = ref([])
const supportRecentTicketsLoading = ref(false)
const superadminDashboardData = ref(null)
const clientDashboardData = ref({})
const clientLoyaltyData = ref({})
const clientAnalyticsData = ref({})
const clientWalletAnalytics = ref({})
const clientReferralsData = ref({})

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1
const selectedMonth = ref(currentMonth)

const months = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' },
]

const currentMonthName = computed(() => {
  return months.find(m => m.value === selectedMonth.value)?.label || 'Current Month'
})

// Editor Stats
const editorStats = computed(() => {
  if (!editorDashboardData.value) {
    return [
      { name: 'Active Tasks', value: '0', icon: '📋' },
      { name: 'Completed Reviews', value: '0', icon: '✅' },
      { name: 'Pending Tasks', value: '0', icon: '⏳' },
      { name: 'Average Score', value: '0.0', icon: '⭐' },
    ]
  }
  const data = editorDashboardData.value
  // Map backend data structure to frontend display
  const summary = data.summary || {}
  const performance = data.performance || {}
  const tasks = data.tasks || {}
  const taskBreakdown = tasks.breakdown_by_status || {}
  
  return [
    { 
      name: 'Active Tasks', 
      value: summary.active_tasks_count || (taskBreakdown.pending || 0) + (taskBreakdown.in_review || 0) || 0, 
      icon: '📋' 
    },
    { 
      name: 'Completed Reviews', 
      value: summary.recent_completions || taskBreakdown.completed || performance.total_orders_reviewed || 0, 
      icon: '✅' 
    },
    { 
      name: 'Pending Tasks', 
      value: summary.pending_tasks_count || taskBreakdown.pending || 0, 
      icon: '⏳' 
    },
    { 
      name: 'Average Score', 
      value: (performance.average_quality_score || 0).toFixed(1), 
      icon: '⭐' 
    },
  ]
})

// Enhanced Writer Stats with better formatting and metrics
const enhancedWriterStats = computed(() => {
  const earnings = writerEarningsData.value
  const performance = writerPerformanceData.value
  const summary = writerSummaryData.value
  const level = writerLevelData.value
  
  // Calculate trends (simplified - would need historical data for real trends)
  const completionRate = performance?.completion_rate || 0
  const onTimeRate = performance?.on_time_rate || 0
  const avgRating = performance?.avg_rating || 0
  
  return [
    { 
      name: 'Total Earnings', 
      value: earnings?.total_earnings ? `$${earnings.total_earnings.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '$0.00', 
      icon: '💰',
      subtitle: earnings?.this_month ? `$${earnings.this_month.toFixed(2)} earned this month` : 'Start earning today',
      trend: earnings?.earnings_trend?.length > 1 ? calculateTrend(earnings.earnings_trend) : null,
      gradientBg: 'bg-gradient-to-br from-green-50 to-emerald-50',
      valueColor: 'text-green-700',
      subtitleColor: 'text-green-600',
      iconBg: 'bg-green-100',
      progress: null,
      progressColor: ''
    },
    { 
      name: 'Completed Orders', 
      value: (performance?.completed_orders || 0).toLocaleString(), 
      icon: '✅',
      subtitle: performance?.completion_rate ? `${performance.completion_rate.toFixed(1)}% completion rate` : 'No orders yet',
      trend: null,
      gradientBg: 'bg-gradient-to-br from-blue-50 to-indigo-50',
      valueColor: 'text-blue-700',
      subtitleColor: 'text-blue-600',
      iconBg: 'bg-blue-100',
      progress: completionRate,
      progressColor: completionRate >= 90 ? 'bg-green-500' : completionRate >= 70 ? 'bg-yellow-500' : 'bg-red-500'
    },
    { 
      name: 'On-Time Rate', 
      value: performance?.on_time_rate ? `${performance.on_time_rate.toFixed(1)}%` : '0%', 
      icon: '⏰',
      subtitle: performance?.on_time_orders ? `${performance.on_time_orders} of ${performance.completed_orders || 0} orders on time` : 'Track your deadlines',
      trend: null,
      gradientBg: 'bg-gradient-to-br from-purple-50 to-pink-50',
      valueColor: 'text-purple-700',
      subtitleColor: 'text-purple-600',
      iconBg: 'bg-purple-100',
      progress: onTimeRate,
      progressColor: onTimeRate >= 95 ? 'bg-green-500' : onTimeRate >= 80 ? 'bg-yellow-500' : 'bg-red-500'
    },
    { 
      name: 'Average Rating', 
      value: performance?.avg_rating ? `${performance.avg_rating.toFixed(1)}` : 'N/A', 
      icon: '⭐',
      subtitle: performance?.total_reviews ? `From ${performance.total_reviews} reviews` : 'No reviews yet',
      trend: null,
      gradientBg: 'bg-gradient-to-br from-yellow-50 to-amber-50',
      valueColor: 'text-yellow-700',
      subtitleColor: 'text-yellow-600',
      iconBg: 'bg-yellow-100',
      progress: avgRating > 0 ? (avgRating / 5) * 100 : 0,
      progressColor: avgRating >= 4.5 ? 'bg-green-500' : avgRating >= 4.0 ? 'bg-yellow-500' : avgRating >= 3.0 ? 'bg-orange-500' : 'bg-red-500'
    },
  ]
})

// Writer Quick Metrics
const writerQuickMetrics = computed(() => {
  const earnings = writerEarningsData.value
  const performance = writerPerformanceData.value
  const summary = writerSummaryData.value
  const level = writerLevelData.value
  const queue = writerQueueData.value
  
  return [
    {
      name: 'Active Orders',
      value: performance?.active_orders || performance?.total_orders || 0,
      icon: '📝',
      description: 'Currently assigned'
    },
    {
      name: 'Pending Payments',
      value: earnings?.pending_payments ? `$${earnings.pending_payments.toFixed(2)}` : '$0.00',
      icon: '💳',
      description: 'Awaiting payment'
    },
    {
      name: 'Available Orders',
      value: queue?.available_orders?.length || 0,
      icon: '🎯',
      description: 'Ready to take'
    },
    {
      name: 'Revision Rate',
      value: performance?.revision_rate ? `${performance.revision_rate.toFixed(1)}%` : '0%',
      icon: '📝',
      description: `${performance?.revised_orders || 0} revised`
    },
    {
      name: 'Writer Level',
      value: level?.current_level?.name || 'Not Assigned',
      icon: '📊',
      description: level?.current_level?.description || 'Contact admin'
    }
  ]
})

// Helper function to calculate trend
const calculateTrend = (trendArray) => {
  if (!trendArray || trendArray.length < 2) return null
  const recent = trendArray.slice(-1)[0]?.total || 0
  const previous = trendArray.slice(-2)[0]?.total || 0
  if (previous === 0) return null
  return ((recent - previous) / previous) * 100
}

// Writer Stats (kept for backward compatibility)
const writerStats = computed(() => {
  const earnings = writerEarningsData.value
  const performance = writerPerformanceData.value
  
  return [
    { 
      name: 'Total Earnings', 
      value: earnings?.total_earnings ? `$${earnings.total_earnings.toFixed(2)}` : '$0.00', 
      icon: '💰',
      subtitle: earnings?.this_month ? `$${earnings.this_month.toFixed(2)} this month` : ''
    },
    { 
      name: 'Completed Orders', 
      value: performance?.completed_orders || 0, 
      icon: '✅',
      subtitle: performance?.completion_rate ? `${performance.completion_rate.toFixed(1)}% completion rate` : 'No data'
    },
    { 
      name: 'On-Time Rate', 
      value: performance?.on_time_rate ? `${performance.on_time_rate.toFixed(1)}%` : '0%', 
      icon: '⏰',
      subtitle: performance?.on_time_orders ? `${performance.on_time_orders}/${performance.completed_orders || 0} on time` : 'No data'
    },
    { 
      name: 'Pending Payments', 
      value: earnings?.pending_payments ? `$${earnings.pending_payments.toFixed(2)}` : '$0.00', 
      icon: '💳',
      subtitle: 'Awaiting payment'
    },
  ]
})

// Support Stats
const supportStats = computed(() => {
  if (!supportDashboardData.value) {
    return [
      { name: 'Open Tickets', value: '0', icon: '🎫' },
      { name: 'Resolved Today', value: '0', icon: '✅' },
      { name: 'Pending Orders', value: '0', icon: '⏳' },
      { name: 'Escalations', value: '0', icon: '🚨' },
    ]
  }
  const data = supportDashboardData.value
  return [
    { name: 'Open Tickets', value: data.open_tickets_count || 0, icon: '🎫' },
    { name: 'Resolved Today', value: data.resolved_today_count || 0, icon: '✅' },
    { name: 'Pending Orders', value: data.pending_orders_count || 0, icon: '⏳' },
    { name: 'Escalations', value: data.escalations_count || 0, icon: '🚨' },
  ]
})

// Summary Stats (Admin/Superadmin)
const summaryStats = computed(() => {
  // Show loading state with placeholders
  if (!summaryData.value || loading.value.summary) {
    return [
      { name: 'Total Orders', value: loading.value.summary ? '—' : '0', icon: '📝', change: null, subtitle: loading.value.summary ? 'Loading...' : 'No data', bgColor: 'bg-blue-100' },
      { name: 'Total Revenue', value: loading.value.summary ? '—' : '$0.00', icon: '💰', change: null, subtitle: loading.value.summary ? 'Loading...' : 'No data', bgColor: 'bg-green-100' },
      { name: 'Paid Orders', value: loading.value.summary ? '—' : '0', icon: '✅', change: null, subtitle: loading.value.summary ? 'Loading...' : 'No data', bgColor: 'bg-emerald-100' },
      { name: 'Unpaid Orders', value: loading.value.summary ? '—' : '0', icon: '⏳', change: null, subtitle: loading.value.summary ? 'Loading...' : 'No data', bgColor: 'bg-amber-100' },
    ]
  }

  const data = summaryData.value
  const totalOrders = Number(data.total_orders) || 0
  const paidOrders = Number(data.paid_orders_count) || 0
  const unpaidOrders = Number(data.unpaid_orders_count) || 0
  const recentOrders = Number(data.recent_orders_count) || 0 // Last 7 days
  const totalRevenue = parseFloat(data.total_revenue) || 0
  const ordersInProgress = Number(data.orders_in_progress) || 0
  const ordersOnRevision = Number(data.orders_on_revision) || 0
  const disputedOrders = Number(data.disputed_orders) || 0
  const amountPaidToday = parseFloat(data.amount_paid_today) || 0
  const income2Weeks = parseFloat(data.income_2weeks) || 0
  const incomeMonthly = parseFloat(data.income_monthly) || 0
  
  // Calculate percentages safely
  const paymentRate = totalOrders > 0 ? ((paidOrders / totalOrders) * 100).toFixed(1) : '0.0'
  const unpaidPercentage = totalOrders > 0 ? ((unpaidOrders / totalOrders) * 100).toFixed(1) : '0.0'
  
  // Format currency with proper formatting
  const formatCurrency = (amount) => {
    return amount.toLocaleString('en-US', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })
  }
  
  const formatCompactCurrency = (amount) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(2)}M`
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(2)}K`
    }
    return `$${formatCurrency(amount)}`
  }
  
  // Format currency for large display (handles overflow better)
  const formatLargeCurrency = (amount) => {
    // For very large amounts, use compact notation
    if (amount >= 1000000000) {
      return `$${(amount / 1000000000).toFixed(2)}B`
    } else if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(2)}M`
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(2)}K`
    }
    // For smaller amounts, use full formatting with commas
    return `$${formatCurrency(amount)}`
  }
  
  return [
    {
      name: 'Total Orders',
      value: totalOrders.toLocaleString(),
      icon: '📝',
      change: null,
      subtitle: recentOrders > 0 ? `${recentOrders} in last 7 days` : 'No orders in last 7 days',
      bgColor: 'bg-blue-100',
      size: 'normal',
    },
    {
      name: 'Total Revenue',
      value: formatLargeCurrency(totalRevenue),
      icon: '💰',
      change: null,
      subtitle: paidOrders > 0 ? `From ${paidOrders.toLocaleString()} paid order${paidOrders !== 1 ? 's' : ''}` : 'No paid orders yet',
      bgColor: 'bg-gradient-to-br from-green-100 to-emerald-100',
      size: 'large',
    },
    {
      name: 'Orders in Progress',
      value: ordersInProgress.toLocaleString(),
      icon: '⚙️',
      change: null,
      subtitle: 'Active work in progress',
      bgColor: 'bg-indigo-100',
      size: 'normal',
    },
    {
      name: 'Amount Paid Today',
      value: formatCompactCurrency(amountPaidToday),
      icon: '💵',
      change: null,
      subtitle: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      bgColor: 'bg-emerald-100',
      size: amountPaidToday >= 10000 ? 'compact' : 'normal',
    },
  ]
})

// Additional Key Metrics (Admin/Superadmin)
const keyMetrics = computed(() => {
  if (!summaryData.value || loading.value.summary) {
    return [
      { name: 'Orders on Revision', value: '—', icon: '🔄', bgColor: 'bg-orange-100' },
      { name: 'Disputed Orders', value: '—', icon: '⚠️', bgColor: 'bg-red-100' },
      { name: 'Payment (This Week)', value: '—', icon: '💳', bgColor: 'bg-purple-100' },
      { name: 'Payment (Monthly)', value: '—', icon: '📈', bgColor: 'bg-cyan-100' },
    ]
  }

  const data = summaryData.value
  const ordersOnRevision = Number(data.orders_on_revision) || 0
  const disputedOrders = Number(data.disputed_orders) || 0
  const incomeThisWeek = parseFloat(data.income_this_week) || 0
  const incomeMonthly = parseFloat(data.income_monthly) || 0
  
  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(2)}M`
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(2)}K`
    }
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }
  
  return [
    {
      name: 'Orders on Revision',
      value: ordersOnRevision.toLocaleString(),
      icon: '🔄',
      subtitle: 'Requiring revisions',
      bgColor: 'bg-orange-100',
    },
    {
      name: 'Disputed Orders',
      value: disputedOrders.toLocaleString(),
      icon: '⚠️',
      subtitle: 'Needs attention',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Payment (This Week)',
      value: formatCurrency(incomeThisWeek),
      icon: '💳',
      subtitle: 'Last 7 days',
      bgColor: 'bg-purple-100',
      size: incomeThisWeek >= 10000 ? 'compact' : 'normal',
    },
    {
      name: 'Payment (Monthly)',
      value: formatCurrency(incomeMonthly),
      icon: '📈',
      subtitle: 'Current month',
      bgColor: 'bg-cyan-100',
      size: incomeMonthly >= 10000 ? 'compact' : 'normal',
    },
  ]
})

// User Statistics (Admin/Superadmin)
const userStats = computed(() => {
  // Show loading state with placeholders
  if (!summaryData.value || loading.value.summary) {
    return [
      { name: 'WRITERS', value: loading.value.summary ? '—' : '0', icon: '✍️', percentage: '0.0' },
      { name: 'CLIENTS', value: loading.value.summary ? '—' : '0', icon: '👤', percentage: '0.0' },
      { name: 'EDITORS', value: loading.value.summary ? '—' : '0', icon: '📝', percentage: '0.0' },
      { name: 'SUPPORT', value: loading.value.summary ? '—' : '0', icon: '🎧', percentage: '0.0' },
      { name: 'SUSPENDED', value: loading.value.summary ? '—' : '0', icon: '🚫', percentage: '0.0' },
    ]
  }
  
  const data = summaryData.value
  const totalWriters = Number(data.total_writers) || 0
  const totalEditors = Number(data.total_editors) || 0
  const totalSupport = Number(data.total_support) || 0
  const totalClients = Number(data.total_clients) || 0
  const suspendedUsers = Number(data.suspended_users) || 0
  const totalUsers = totalWriters + totalEditors + totalSupport + totalClients
  
  // Calculate percentages safely
  const calculatePercentage = (count) => {
    if (totalUsers === 0) return '0.0'
    return ((count / totalUsers) * 100).toFixed(1)
  }
  
  return [
    {
      name: 'WRITERS',
      value: totalWriters.toLocaleString(),
      icon: '✍️',
      percentage: calculatePercentage(totalWriters),
    },
    {
      name: 'CLIENTS',
      value: totalClients.toLocaleString(),
      icon: '👤',
      percentage: calculatePercentage(totalClients),
    },
    {
      name: 'EDITORS',
      value: totalEditors.toLocaleString(),
      icon: '📝',
      percentage: calculatePercentage(totalEditors),
    },
    {
      name: 'SUPPORT',
      value: totalSupport.toLocaleString(),
      icon: '🎧',
      percentage: calculatePercentage(totalSupport),
    },
    {
      name: 'SUSPENDED',
      value: suspendedUsers.toLocaleString(),
      icon: '🚫',
      percentage: calculatePercentage(suspendedUsers),
    },
  ]
})

// Order Status Breakdown (Admin/Superadmin)
const orderStatusBreakdown = computed(() => {
  if (!summaryData.value || !summaryData.value.orders_by_status) {
    return []
  }
  
  const statusMap = {
    'pending': { name: 'Pending', icon: '⏳', borderColor: 'border-yellow-400', textColor: 'text-yellow-600' },
    'in_progress': { name: 'In Progress', icon: '🔄', borderColor: 'border-blue-400', textColor: 'text-blue-600' },
    'under_editing': { name: 'Editing', icon: '✏️', borderColor: 'border-purple-400', textColor: 'text-purple-600' },
    'completed': { name: 'Completed', icon: '✅', borderColor: 'border-green-400', textColor: 'text-green-600' },
    'on_revision': { name: 'Revision', icon: '📝', borderColor: 'border-orange-400', textColor: 'text-orange-600' },
    'disputed': { name: 'Disputed', icon: '⚠️', borderColor: 'border-red-400', textColor: 'text-red-600' },
    'canceled': { name: 'Canceled', icon: '❌', borderColor: 'border-gray-400', textColor: 'text-gray-600' },
    'closed': { name: 'Closed', icon: '🔒', borderColor: 'border-gray-500', textColor: 'text-gray-700' },
  }
  
  const ordersByStatus = summaryData.value.orders_by_status || {}
  const totalOrders = summaryData.value.total_orders || 0
  
  return Object.entries(ordersByStatus).map(([status, count]) => {
    const statusInfo = statusMap[status] || { name: status, icon: '📋', borderColor: 'border-gray-300', textColor: 'text-gray-600' }
    return {
      name: statusInfo.name,
      value: count.toLocaleString(),
      icon: statusInfo.icon,
      borderColor: statusInfo.borderColor,
      textColor: statusInfo.textColor,
      percentage: totalOrders > 0 ? ((count / totalOrders) * 100).toFixed(1) : '0',
    }
  }).sort((a, b) => parseInt(b.value) - parseInt(a.value))
})

// Chart Options and Series
const yearlyOrdersChartOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: false },
    zoom: { enabled: false },
  },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 2 },
  xaxis: {
    categories: yearlyOrdersData.value.map(item => item.month_name),
  },
  yaxis: {
    title: { text: 'Orders' },
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.3,
    },
  },
  colors: ['#3B82F6'],
}))

const yearlyOrdersSeries = computed(() => [{
  name: 'Orders',
  data: yearlyOrdersData.value.map(item => item.order_count),
}])

const yearlyEarningsChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: yearlyEarningsData.value.map(item => item.month_name),
  },
  yaxis: {
    title: { text: 'Revenue ($)' },
    labels: {
      formatter: (val) => `$${val.toLocaleString()}`,
    },
  },
  colors: ['#10B981'],
}))

const yearlyEarningsSeries = computed(() => [{
  name: 'Earnings',
  data: yearlyEarningsData.value.map(item => item.revenue),
}])

const monthlyOrdersChartOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: false },
    zoom: { enabled: false },
  },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 2 },
  xaxis: {
    categories: monthlyOrdersData.value.map(item => item.day),
    title: { text: 'Day of Month' },
  },
  yaxis: {
    title: { text: 'Orders' },
  },
  colors: ['#8B5CF6'],
}))

const monthlyOrdersSeries = computed(() => [{
  name: 'Orders',
  data: monthlyOrdersData.value.map(item => item.order_count),
}])

const paymentStatusChartOptions = computed(() => ({
  chart: {
    type: 'donut',
    toolbar: { show: false },
  },
  labels: ['Paid', 'Unpaid'],
  colors: ['#10B981', '#EF4444'],
  legend: {
    position: 'bottom',
  },
  dataLabels: {
    formatter: (val) => `${val.toFixed(1)}%`,
  },
}))

const paymentStatusSeries = computed(() => {
  if (!paymentStatusData.value) return [0, 0]
  const paid = paymentStatusData.value.paid?.count || 0
  const unpaid = paymentStatusData.value.unpaid?.count || 0
  return [paid, unpaid]
})

const serviceRevenueChartOptions = computed(() => {
  const labels = serviceRevenueData.value?.by_paper_type?.map(item => item.name) || []
  return {
    chart: {
      type: 'pie',
      toolbar: { show: false },
    },
    labels,
    legend: {
      position: 'bottom',
    },
    dataLabels: {
      formatter: (val) => `${val.toFixed(1)}%`,
    },
  }
})

const serviceRevenueSeries = computed(() => {
  return serviceRevenueData.value?.by_paper_type?.map(item => item.revenue) || []
})

// Computed loading states
const yearlyOrdersLoading = computed(() => loading.value.yearlyOrders)
const yearlyEarningsLoading = computed(() => loading.value.yearlyEarnings)
const monthlyOrdersLoading = computed(() => loading.value.monthlyOrders)
const serviceRevenueLoading = computed(() => loading.value.serviceRevenue)
const paymentStatusLoading = computed(() => loading.value.paymentStatus)

// Fetch functions
const fetchSummary = async (forceRefresh = false) => {
  loading.value.summary = true
  try {
    // Fetch full dashboard data which includes all stats
    // Add refresh parameter to clear cache if needed
    const params = forceRefresh ? { refresh: 'true' } : {}
    const response = await dashboardAPI.getDashboard(params)
    const dashboardData = response.data
    
    // Handle both nested (stats) and flat response structures
    const stats = dashboardData.stats || dashboardData
    const flatData = dashboardData
    
    // Debug: Log the actual data structure to understand what we're receiving
    if (import.meta.env.DEV) {
      console.debug('Dashboard API response structure:', {
        hasStats: !!dashboardData.stats,
        hasFlatData: !!dashboardData,
        statsKeys: dashboardData.stats ? Object.keys(dashboardData.stats) : [],
        flatDataKeys: Object.keys(dashboardData).slice(0, 20), // First 20 keys
        statsPaid: dashboardData.stats?.paid_orders_count,
        statsUnpaid: dashboardData.stats?.unpaid_orders_count,
        flatPaid: dashboardData.paid_orders_count,
        flatUnpaid: dashboardData.unpaid_orders_count,
      })
    }
    
    // Map the dashboard data to summaryData format with proper type conversion
    // Ensure all numeric values are properly converted
    summaryData.value = {
      total_orders: Number(stats.total_orders ?? flatData.total_orders ?? 0),
      orders_by_status: stats.orders_by_status ?? flatData.orders_by_status ?? {},
      total_revenue: parseFloat(stats.total_revenue ?? flatData.total_revenue ?? 0) || 0,
      paid_orders_count: Number(stats.paid_orders_count ?? flatData.paid_orders_count ?? 0),
      unpaid_orders_count: Number(stats.unpaid_orders_count ?? flatData.unpaid_orders_count ?? 0),
      recent_orders_count: Number(stats.recent_orders_count ?? flatData.recent_orders_count ?? 0), // Last 7 days
      total_tickets: Number(stats.open_tickets ?? flatData.total_tickets ?? 0),
      open_tickets_count: Number(stats.open_tickets ?? flatData.open_tickets_count ?? 0),
      closed_tickets_count: Number(stats.closed_tickets ?? flatData.closed_tickets_count ?? 0),
      // New comprehensive metrics
      orders_in_progress: Number(flatData.orders_in_progress ?? 0),
      orders_on_revision: Number(flatData.orders_on_revision ?? 0),
      disputed_orders: Number(flatData.disputed_orders ?? 0),
      amount_paid_today: parseFloat(flatData.amount_paid_today ?? 0) || 0,
      income_this_week: parseFloat(flatData.income_this_week ?? 0) || 0,
      income_2weeks: parseFloat(flatData.income_2weeks ?? 0) || 0,
      income_monthly: parseFloat(flatData.income_monthly ?? 0) || 0,
      // User statistics - check both nested and flat structure, ensure numbers
      total_writers: Number(flatData.total_writers ?? 0),
      total_editors: Number(flatData.total_editors ?? 0),
      total_support: Number(flatData.total_support ?? 0),
      total_clients: Number(flatData.total_clients ?? 0),
      suspended_users: Number(stats.suspended_users ?? flatData.suspended_users ?? 0),
    }
    
    // Validate data consistency (backend should ensure total_orders = paid + unpaid)
    const totalOrders = summaryData.value.total_orders
    const paidOrders = summaryData.value.paid_orders_count
    const unpaidOrders = summaryData.value.unpaid_orders_count
    const calculatedTotal = paidOrders + unpaidOrders
    
    // If there's a significant mismatch (> 5 orders difference), log it for debugging
    // This helps catch data issues but allows for minor rounding/calculation differences
    if (totalOrders > 0 && Math.abs(totalOrders - calculatedTotal) > 5) {
      console.warn('Data inconsistency detected (backend should ensure consistency):', {
        total_orders: totalOrders,
        paid: paidOrders,
        unpaid: unpaidOrders,
        calculated: calculatedTotal,
        difference: Math.abs(totalOrders - calculatedTotal)
      })
    }
    
    // Store recent logs for activity section
    const activities = dashboardData.recent_activities || dashboardData.recent_logs || []
    if (activities && activities.length > 0) {
      recentActivity.value = activities.map(log => ({
        action: typeof log === 'string' ? log : (log.action || log.message || JSON.stringify(log)),
        timestamp: log.timestamp || log.created_at || null,
      }))
    }
    
    // Extract payment reminder stats
    paymentReminderStats.value = dashboardData.payment_reminder_stats || {
      total_reminder_configs: 0,
      active_reminder_configs: 0,
      total_deletion_messages: 0,
      active_deletion_messages: 0,
      total_sent_reminders: 0,
      recent_sent_reminders: 0,
    }
    
    // Validate and log data for debugging (only in development)
    if (import.meta.env.DEV) {
      console.debug('Dashboard data received:', {
      hasStats: !!dashboardData.stats,
      hasFlatData: !!flatData.total_writers,
        summaryData: summaryData.value,
      userCounts: {
        writers: summaryData.value.total_writers,
        editors: summaryData.value.total_editors,
        support: summaryData.value.total_support,
        clients: summaryData.value.total_clients,
      }
    })
    }
  } catch (err) {
    console.error('Failed to fetch dashboard summary:', err)
    const errorMessage = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Failed to load dashboard data'
    
    // Fallback: try individual summary endpoint
    try {
      const summaryResponse = await dashboardAPI.getSummary()
      summaryData.value = summaryResponse.data
      error.value = null // Clear error on successful fallback
    } catch (e) {
      console.error('Failed to fetch summary fallback:', e)
      error.value = errorMessage
      // Set default values to prevent UI breakage
      summaryData.value = {
        total_orders: 0,
        orders_by_status: {},
        total_revenue: 0,
        paid_orders_count: 0,
        unpaid_orders_count: 0,
        recent_orders_count: 0,
        total_tickets: 0,
        open_tickets_count: 0,
        closed_tickets_count: 0,
        total_writers: 0,
        total_editors: 0,
        total_support: 0,
        total_clients: 0,
        suspended_users: 0,
      }
    }
  } finally {
    loading.value.summary = false
  }
}

const fetchYearlyOrders = async () => {
  loading.value.yearlyOrders = true
  try {
    const response = await dashboardAPI.getYearlyOrders(currentYear)
    yearlyOrdersData.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch yearly orders:', error)
  } finally {
    loading.value.yearlyOrders = false
  }
}

const fetchYearlyEarnings = async () => {
  loading.value.yearlyEarnings = true
  try {
    const response = await dashboardAPI.getYearlyEarnings(currentYear)
    yearlyEarningsData.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch yearly earnings:', error)
  } finally {
    loading.value.yearlyEarnings = false
  }
}

const fetchMonthlyOrders = async () => {
  loading.value.monthlyOrders = true
  try {
    const response = await dashboardAPI.getMonthlyOrders(currentYear, selectedMonth.value)
    monthlyOrdersData.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch monthly orders:', error)
  } finally {
    loading.value.monthlyOrders = false
  }
}

const fetchServiceRevenue = async () => {
  loading.value.serviceRevenue = true
  try {
    const response = await dashboardAPI.getServiceRevenue(30)
    serviceRevenueData.value = response.data
  } catch (error) {
    console.error('Failed to fetch service revenue:', error)
  } finally {
    loading.value.serviceRevenue = false
  }
}

const fetchPaymentStatus = async () => {
  loading.value.paymentStatus = true
  try {
    const response = await dashboardAPI.getPaymentStatus()
    paymentStatusData.value = response.data
  } catch (error) {
    console.error('Failed to fetch payment status:', error)
  } finally {
    loading.value.paymentStatus = false
  }
}

// Client recent orders with retry logic
const fetchRecentOrders = async () => {
  if (!authStore.isClient) return
  recentOrdersLoading.value = true
  try {
    const mod = await import('@/api/orders')
    const res = await retryApiCall(
      () => mod.default.list({}),
      {
        maxRetries: 3,
        initialDelay: 1000,
        shouldRetry: (error) => {
          // Retry on network errors and 5xx server errors
          if (!error.response) return true
          const status = error.response?.status
          return status >= 500 && status < 600
        },
      }
    )
    const items = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
    recentOrders.value = items.slice(0, 5)
  } catch (e) {
    // On final failure, set empty array instead of leaving undefined
    recentOrders.value = []
    console.warn('Failed to load recent orders after retries:', e.message)
  } finally {
    recentOrdersLoading.value = false
  }
}

const fetchWalletBalance = async () => {
  if (!authStore.isClient) return
  walletLoading.value = true
  try {
    const res = await walletAPI.getWallet()
    walletBalance.value = parseFloat(res.data?.balance || 0)
  } catch (e) {
    // silent
  } finally {
    walletLoading.value = false
  }
}

const fetchRecentNotifications = async () => {
  if (!authStore.isClient) return
  recentNotificationsLoading.value = true
  try {
    const res = await notificationsAPI.getNotifications({ is_read: false })
    const items = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
    recentNotifications.value = items.slice(0, 5)
  } catch (e) {
    // silent
  } finally {
    recentNotificationsLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getTicketStatusClass = (status) => {
  const classes = {
    open: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    closed: 'bg-green-100 text-green-800',
    awaiting_response: 'bg-orange-100 text-orange-800',
    escalated: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getTicketPriorityClass = (priority) => {
  const classes = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

// Event handlers
const handleEndImpersonation = async () => {
  try {
    await authStore.endImpersonation()
  } catch (error) {
    console.error('Failed to end impersonation:', error)
  }
}

// Refresh all dashboard data
const refreshDashboard = async () => {
  refreshing.value = true
  error.value = null // Clear any previous errors
  try {
    const refreshPromises = []
    
    if (authStore.isAdmin || authStore.isSuperAdmin) {
      // Force refresh to clear cache
      refreshPromises.push(
        fetchSummary(true), // Pass true to force refresh
        fetchYearlyOrders(),
        fetchYearlyEarnings(),
        fetchMonthlyOrders(),
        fetchServiceRevenue(),
        fetchPaymentStatus(),
        fetchRecentActivity()
      )
    } else if (authStore.isClient) {
      refreshPromises.push(
        fetchClientDashboard(),
        fetchClientLoyalty(),
        fetchClientAnalytics(),
        fetchClientWalletAnalytics(),
        fetchClientReferrals(),
        fetchRecentOrders(),
        fetchWalletBalance(),
        fetchRecentNotifications()
      )
    } else if (authStore.isWriter) {
      refreshPromises.push(
        fetchWriterDashboard(),
        fetchWriterEarnings(),
        fetchWriterPerformance(),
        fetchWriterQueue(),
        fetchWriterBadges(),
        fetchWriterLevel(),
        fetchWriterSummary()
      )
    } else if (authStore.isEditor) {
      refreshPromises.push(fetchEditorDashboard())
    } else if (authStore.isSupport) {
      refreshPromises.push(fetchSupportDashboard())
      refreshPromises.push(fetchSupportRecentTickets())
    }
    
    const results = await Promise.allSettled(refreshPromises)
    
    // Check if any critical requests failed
    const criticalFailures = results.filter((result, index) => {
      if (result.status === 'rejected') {
        // Summary fetch is critical for admin/superadmin
        if ((authStore.isAdmin || authStore.isSuperAdmin) && index === 0) {
          return true
        }
      }
      return false
    })
    
    if (criticalFailures.length > 0) {
      error.value = 'Some data failed to refresh. Please try again.'
    }
  } catch (err) {
    console.error('Failed to refresh dashboard:', err)
    error.value = err?.response?.data?.detail || err?.message || 'Failed to refresh dashboard'
  } finally {
    refreshing.value = false
  }
}

// Fetch recent activity
const fetchRecentActivity = async () => {
  if (!authStore.isAdmin && !authStore.isSuperAdmin) return
  
  recentActivityLoading.value = true
  try {
    // Fetch activity logs from dedicated endpoint (limit to 10 most recent)
    const response = await dashboardAPI.getActivityLogs({ page_size: 10 })
    
    // Handle both paginated and non-paginated responses
    let logs = []
    if (Array.isArray(response.data)) {
      logs = response.data.slice(0, 10) // Take first 10 if array
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      logs = response.data.results // Paginated response
    } else if (response.data?.data && Array.isArray(response.data.data)) {
      logs = response.data.data.slice(0, 10)
    }
    
    // Map logs to display format
    recentActivity.value = logs.map(log => {
      // Handle admin field - could be string (from StringRelatedField) or object
      let adminName = 'Unknown'
      if (log.admin_username) {
        adminName = log.admin_username
      } else if (typeof log.admin === 'string') {
        adminName = log.admin
      } else if (log.admin?.username) {
        adminName = log.admin.username
      }
      
      return {
        id: log.id,
        action: log.action || log.description || 'Unknown action',
        timestamp: log.timestamp || log.created_at || null,
        admin: adminName,
      }
    })
  } catch (error) {
    console.error('Failed to fetch recent activity:', error)
    // Fallback: try dashboard endpoint
    try {
      const dashboardResponse = await dashboardAPI.getDashboard()
      if (dashboardResponse.data?.recent_activities) {
        recentActivity.value = dashboardResponse.data.recent_activities.map(log => ({
          id: log.id,
          action: typeof log === 'string' ? log : (log.action || log.description || 'Unknown action'),
          timestamp: log.timestamp || null,
          admin: log.admin || 'Unknown',
        }))
      } else if (dashboardResponse.data?.recent_logs) {
        recentActivity.value = dashboardResponse.data.recent_logs.map(log => ({
          id: null,
          action: typeof log === 'string' ? log : (log.action || 'Unknown action'),
          timestamp: log.timestamp || null,
          admin: log.admin || 'Unknown',
        }))
      } else {
        recentActivity.value = []
      }
    } catch (fallbackError) {
      console.error('Failed to fetch activity from dashboard fallback:', fallbackError)
      recentActivity.value = []
    }
  } finally {
    recentActivityLoading.value = false
  }
}

// Role-specific fetch functions
const fetchEditorDashboard = async () => {
  if (!authStore.isEditor) return
  try {
    const response = await editorDashboardAPI.getDashboardStats(30)
    editorDashboardData.value = response.data
  } catch (error) {
    console.error('Failed to fetch editor dashboard:', error)
    editorDashboardData.value = null
  }
}

const fetchWriterDashboard = async () => {
  if (!authStore.isWriter) return
  try {
    // Try to get writer profile which might have dashboard data
    const response = await retryApiCall(
      () => writerDashboardAPI.getMyProfile(),
      { maxRetries: 2 }
    )
    writerDashboardData.value = response.data
  } catch (error) {
    console.error('Failed to fetch writer dashboard:', error)
  }
  
  // Also fetch recent orders for display with retry logic
  try {
    const ordersRes = await retryApiCall(
      () => writerDashboardAPI.getOrders({}),
      {
        maxRetries: 3,
        shouldRetry: (error) => {
          // Retry on network errors and 5xx server errors
          if (!error.response) return true
          const status = error.response?.status
          return status >= 500 && status < 600
        },
      }
    )
    const orders = Array.isArray(ordersRes.data?.results) ? ordersRes.data.results : (Array.isArray(ordersRes.data) ? ordersRes.data : [])
    recentOrders.value = orders.slice(0, 5)
  } catch (e) {
    // On final failure, set empty array
    recentOrders.value = []
    // Only log if it's not a 404 or expected error
    if (e.response?.status !== 404 && e.response?.status !== 500) {
      console.warn('Failed to fetch writer orders after retries:', e.response?.status || e.message)
    }
  } finally {
    recentOrdersLoading.value = false
  }
}

const fetchWriterEarnings = async () => {
  if (!authStore.isWriter) return
  try {
    const response = await writerDashboardAPI.getEarnings(30)
    if (response && response.data) {
    writerEarningsData.value = response.data
    } else {
      console.warn('Writer earnings response missing data:', response)
      writerEarningsData.value = null
    }
  } catch (error) {
    console.error('Failed to fetch writer earnings:', error)
    writerEarningsData.value = null
  }
}

const fetchWriterPerformance = async () => {
  if (!authStore.isWriter) return
  try {
    const response = await writerDashboardAPI.getPerformanceAnalytics(30)
    if (response && response.data) {
    writerPerformanceData.value = response.data
    } else {
      console.warn('Writer performance response missing data:', response)
      writerPerformanceData.value = null
    }
  } catch (error) {
    console.error('Failed to fetch writer performance:', error)
    writerPerformanceData.value = null
  }
}

const fetchWriterQueue = async () => {
  if (!authStore.isWriter) return
  try {
    const response = await writerDashboardAPI.getOrderQueue()
    if (response && response.data) {
    writerQueueData.value = response.data
    } else {
      console.warn('Writer queue response missing data:', response)
      writerQueueData.value = null
    }
  } catch (error) {
    console.error('Failed to fetch writer queue:', error)
    writerQueueData.value = null
  }
}

// Handle order request from WriterDashboard component
const handleOrderRequested = async () => {
  // Refresh the queue data after an order is requested
  await fetchWriterQueue()
}

const handleWriterRefreshRequest = async (payload) => {
  if (!payload || payload.scope === 'queue') {
    await fetchWriterQueue()
  }
}

const fetchWriterBadges = async () => {
  if (!authStore.isWriter) return
  try {
    const response = await writerDashboardAPI.getBadgesAndAchievements()
    writerBadgesData.value = response.data
  } catch (error) {
    console.error('Failed to fetch writer badges:', error)
  }
}

const fetchWriterLevel = async () => {
  if (!authStore.isWriter) return
  try {
    const response = await writerDashboardAPI.getLevelAndRanking()
    writerLevelData.value = response.data
    console.log('Writer level data loaded:', writerLevelData.value)
  } catch (error) {
    console.error('Failed to fetch writer level:', error)
    console.error('Error details:', error.response?.data || error.message)
    // Set to null so empty state shows
    writerLevelData.value = null
  }
}

const fetchWriterSummary = async () => {
  if (!authStore.isWriter) return
  try {
    const response = await writerDashboardAPI.getDashboardSummary()
    if (response && response.data) {
      writerSummaryData.value = response.data
    } else {
      console.warn('Writer summary response missing data:', response)
    }
  } catch (error) {
    console.error('Failed to fetch writer summary:', error)
    // Don't block dashboard if summary fails - it's supplementary data
    writerSummaryData.value = null
  }
}

const fetchSupportDashboard = async () => {
  if (!authStore.isSupport) return
  try {
    const response = await supportDashboardAPI.getDashboard()
    supportDashboardData.value = response.data
  } catch (error) {
    console.error('Failed to fetch support dashboard:', error)
    // Fallback: get tickets count
    try {
      const ticketsRes = await supportDashboardAPI.getTickets({})
      const tickets = Array.isArray(ticketsRes.data?.results) ? ticketsRes.data.results : (ticketsRes.data || [])
      supportDashboardData.value = {
        open_tickets_count: tickets.filter(t => t.status !== 'closed').length,
        resolved_today_count: 0,
        pending_orders_count: 0,
        escalations_count: 0,
      }
    } catch (e) {
      console.error('Failed to fetch support tickets:', e)
    }
  }
}

const fetchSupportRecentTickets = async () => {
  if (!authStore.isSupport) return
  supportRecentTicketsLoading.value = true
  try {
    const response = await supportTicketsAPI.list({ 
      page_size: 10,
      ordering: '-created_at'
    })
    supportRecentTickets.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to fetch support recent tickets:', error)
    supportRecentTickets.value = []
  } finally {
    supportRecentTicketsLoading.value = false
  }
}

const fetchSuperadminDashboard = async () => {
  if (!authStore.isSuperAdmin) return
  try {
    const response = await superadminDashboardAPI.getDashboard()
    superadminDashboardData.value = response.data
  } catch (error) {
    console.error('Failed to fetch superadmin dashboard:', error)
  }
}

// Client dashboard fetch functions
const fetchClientDashboard = async () => {
  if (!authStore.isClient) return
  loading.value.summary = true
  try {
    const response = await clientDashboardAPI.getStats(30)
    clientDashboardData.value = response.data || {}
  } catch (error) {
    console.error('Failed to fetch client dashboard stats:', error)
    clientDashboardData.value = {}
  } finally {
    loading.value.summary = false
  }
}

const fetchClientLoyalty = async () => {
  if (!authStore.isClient) return
  try {
    const response = await clientDashboardAPI.getLoyalty()
    clientLoyaltyData.value = response.data || {}
  } catch (error) {
    console.error('Failed to fetch client loyalty:', error)
    clientLoyaltyData.value = {}
  }
}

const fetchClientAnalytics = async () => {
  if (!authStore.isClient) return
  try {
    const response = await clientDashboardAPI.getAnalytics(30)
    clientAnalyticsData.value = response.data || {}
  } catch (error) {
    console.error('Failed to fetch client analytics:', error)
    clientAnalyticsData.value = {}
  }
}

const fetchClientWalletAnalytics = async () => {
  if (!authStore.isClient) return
  try {
    const response = await clientDashboardAPI.getWalletAnalytics(30)
    clientWalletAnalytics.value = response.data || {}
    // Update wallet balance from analytics
    if (response.data?.balance !== undefined) {
      walletBalance.value = response.data.balance
    }
  } catch (error) {
    console.error('Failed to fetch client wallet analytics:', error)
    clientWalletAnalytics.value = {}
  }
}

const fetchClientReferrals = async () => {
  if (!authStore.isClient) return
  try {
    const response = await clientDashboardAPI.getReferrals()
    clientReferralsData.value = response.data
  } catch (error) {
    console.error('Failed to fetch client referrals:', error)
    clientReferralsData.value = null
  }
}

// Lifecycle
onMounted(async () => {
  // Wait for next tick to ensure ApexCharts is fully loaded
  await new Promise(resolve => setTimeout(resolve, 100))
  chartsReady.value = true
  // Fetch role-specific dashboard data
  const roleFetches = []
  
  if (authStore.isClient) {
    roleFetches.push(
      fetchRecentOrders(), 
      fetchWalletBalance(), 
      fetchRecentNotifications(),
      fetchClientDashboard(),
      fetchClientLoyalty(),
      fetchClientAnalytics(),
      fetchClientWalletAnalytics(),
      fetchClientReferrals()
    )
  } else if (authStore.isWriter) {
    roleFetches.push(
      fetchWriterDashboard(),
      fetchWriterEarnings(),
      fetchWriterPerformance(),
      fetchWriterQueue(),
      fetchWriterBadges(),
      fetchWriterLevel(),
      fetchWriterSummary()
    )
  } else if (authStore.isAdmin || authStore.isSuperAdmin) {
    roleFetches.push(
      fetchSummary(false), // Initial load, no cache clear
      fetchYearlyOrders(),
      fetchYearlyEarnings(),
      fetchMonthlyOrders(),
      fetchServiceRevenue(),
      fetchPaymentStatus(),
      fetchRecentActivity()
    )
    if (authStore.isSuperAdmin) {
      roleFetches.push(fetchSuperadminDashboard())
    }
  } else if (authStore.isEditor) {
    roleFetches.push(fetchEditorDashboard())
  } else if (authStore.isSupport) {
    roleFetches.push(fetchSupportDashboard())
    roleFetches.push(fetchSupportRecentTickets())
  }
  
  await Promise.all(roleFetches)
})
</script>

<style scoped>
@reference "tailwindcss";
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>
