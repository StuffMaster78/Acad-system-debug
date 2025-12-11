<template>
  <div class="space-y-6 p-6">
    <!-- Header with Back Button -->
    <div class="flex items-center gap-4 mb-2">
      <router-link
        :to="authStore.isWriter ? '/writer/orders' : '/orders'"
        class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="text-sm font-medium">Back to Orders</span>
      </router-link>
    </div>
    
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Order Details</h1>
        <p v-if="order" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Order #{{ order.id }} • {{ order.topic || 'N/A' }}
        </p>
      </div>
      <div v-if="order" class="flex gap-2">
        <router-link
          :to="`/orders/${order.id}/messages`"
          class="relative px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2 shadow-sm"
        >
          <span>💬</span>
          <span>Messages</span>
          <span
            v-if="unreadMessageCount > 0"
            class="absolute -top-2 -right-2 flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-red-600 rounded-full ring-2 ring-white animate-pulse"
          >
            {{ unreadMessageCount > 99 ? '99+' : unreadMessageCount }}
          </span>
        </router-link>
      </div>
    </div>

    <!-- Tabs Navigation -->
    <div v-if="order" class="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-t-lg">
      <nav class="flex space-x-1 overflow-x-auto" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-3 px-4 border-b-2 font-medium text-sm transition-all relative whitespace-nowrap',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          <span class="flex items-center gap-2">
            <span>{{ tab.icon }}</span>
            <span>{{ tab.label }}</span>
            <span
              v-if="tab.id === 'messages' && unreadMessageCount > 0"
              class="ml-2 px-2 py-0.5 text-xs font-bold text-white bg-red-600 rounded-full"
            >
              {{ unreadMessageCount > 99 ? '99+' : unreadMessageCount }}
            </span>
          </span>
        </button>
      </nav>
    </div>

    <template v-if="loading">
      <div class="card p-12">
        <div class="flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    </template>

    <template v-else-if="order">
      <div class="space-y-6">
        <!-- Action Center & Last Activity Banner (for completed/submitted/closed orders) -->
        <div v-if="order.status === 'completed' || order.status === 'submitted' || order.status === 'approved' || order.status === 'closed'" class="bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border-2 border-primary-200 p-6 shadow-sm">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="text-xl font-bold text-gray-900 mb-1">Order {{ order.status === 'completed' ? 'Completed' : order.status === 'submitted' ? 'Submitted' : order.status === 'closed' ? 'Closed' : 'Approved' }}!</h2>
              <p class="text-sm text-gray-600">What would you like to do next?</p>
            </div>
            <span class="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-semibold uppercase">
              {{ order.status }}
            </span>
          </div>
          
          <!-- Last Activity Indicator -->
          <div v-if="lastActivity" class="mb-4 p-3 bg-white rounded-lg border border-gray-200">
            <div class="flex items-center gap-3">
              <div class="flex-shrink-0">
                <span class="text-2xl">{{ lastActivity.type === 'message' ? '💬' : lastActivity.type === 'file' ? '📁' : '📋' }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900">
                  {{ lastActivity.type === 'message' ? 'Latest Message' : lastActivity.type === 'file' ? 'Latest File Upload' : 'Latest Activity' }}
                </div>
                <div class="text-xs text-gray-500 mt-0.5">
                  {{ lastActivity.description }} • {{ formatRelativeTime(lastActivity.timestamp) }}
                </div>
              </div>
              <button
                v-if="lastActivity.type === 'message'"
                @click="jumpToActivity(lastActivity)"
                class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-xs font-medium transition-colors"
              >
                View
              </button>
              <button
                v-else-if="lastActivity.type === 'file'"
                @click="jumpToActivity(lastActivity)"
                class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-xs font-medium transition-colors"
              >
                View
              </button>
            </div>
          </div>
          
          <!-- Revision Eligibility Banner (client view) -->
          <div
            v-if="authStore.isClient && revisionEligibility"
            class="mb-4"
          >
            <div
              v-if="revisionEligibility.is_within_free_window"
              class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-start gap-3"
            >
              <span class="text-xl">✅</span>
              <div class="text-sm text-emerald-900">
                <p class="font-semibold">
                  Unlimited revisions available
                </p>
                <p v-if="revisionEligibility.free_revision_until" class="mt-0.5">
                  Free revisions until
                  <span class="font-medium">
                    {{ formatDateTime(revisionEligibility.free_revision_until) }}
                  </span>
                  <span v-if="revisionEligibility.days_left && revisionEligibility.days_left > 0">
                    (about {{ revisionEligibility.days_left }} day<span v-if="revisionEligibility.days_left > 1">s</span> left)
                  </span>
                </p>
                <p class="mt-0.5 text-xs text-emerald-800">
                  If something doesn’t feel right, you can still request changes at no extra cost.
                </p>
              </div>
            </div>
            <div
              v-else
              class="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3"
            >
              <span class="text-xl">ℹ️</span>
              <div class="text-sm text-amber-900">
                <p class="font-semibold">
                  Free revision window has ended
                </p>
                <p class="mt-0.5">
                  Revisions may be billed, but you can still
                  <button
                    type="button"
                    class="underline font-medium"
                    @click="activeTab = 'messages'"
                  >
                    ask a question about your order
                  </button>.
                </p>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <!-- Request Revision -->
            <button
              v-if="canRequestRevision && order.status !== 'revision_requested'"
              @click="showRevisionModal = true"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-orange-300 text-orange-700 rounded-lg hover:bg-orange-50 hover:border-orange-400 transition-all font-medium shadow-sm"
            >
              <span>🔄</span>
              <span>Request Revision</span>
            </button>
            
            <!-- Rate & Review -->
            <button
              v-if="canSubmitReview && !hasReview"
              @click="scrollToReview"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-yellow-300 text-yellow-700 rounded-lg hover:bg-yellow-50 hover:border-yellow-400 transition-all font-medium shadow-sm"
            >
              <span>⭐</span>
              <span>Rate & Review</span>
            </button>
            
            <!-- Download Files -->
            <button
              v-if="hasDownloadableFiles"
              @click="activeTab = 'files'"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-green-300 text-green-700 rounded-lg hover:bg-green-50 hover:border-green-400 transition-all font-medium shadow-sm"
            >
              <span>📥</span>
              <span>Download Files</span>
            </button>
            
            <!-- View Messages -->
            <button
              v-if="unreadMessageCount > 0"
              @click="activeTab = 'messages'"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 hover:border-blue-400 transition-all font-medium shadow-sm relative"
            >
              <span>💬</span>
              <span>View Messages</span>
              <span class="absolute -top-2 -right-2 flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-red-600 rounded-full ring-2 ring-white">
                {{ unreadMessageCount > 99 ? '99+' : unreadMessageCount }}
              </span>
            </button>
            
            <!-- Tip Writer -->
            <button
              v-if="canTipWriter"
              @click="showTipModal = true"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-purple-300 text-purple-700 rounded-lg hover:bg-purple-50 hover:border-purple-400 transition-all font-medium shadow-sm"
            >
              <span>💰</span>
              <span>Tip Writer</span>
            </button>
          </div>
          
          <!-- Revision Requested Notice -->
          <div v-if="order.status === 'revision_requested'" class="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div class="flex items-center gap-2 text-sm text-orange-800">
              <span>⏳</span>
              <span>Revision request submitted. The writer is working on your changes.</span>
            </div>
          </div>
        </div>
        
        <div class="card p-6">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Order Details Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Left Column: Basic Information -->
          <div class="space-y-6">
            <!-- Order Identification -->
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Order Identification</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Order ID:</span>
                  <span class="font-mono text-gray-900">#{{ order.id }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Status:</span>
                  <span class="px-2 py-1 rounded-full text-xs font-medium" :class="getStatusClass(order.status)">
                {{ order.status }}
              </span>
            </div>
                <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Date Posted:</span>
                  <span class="text-gray-900">{{ formatDateTime(order.created_at) }}</span>
                </div>
              </div>
            </div>

            <!-- Client Information -->
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Client Information</h3>
                <router-link
                  v-if="authStore.isWriter && order.client_id && !order.is_unattributed"
                  :to="`/writers/client-orders/${order.client_id}`"
                  class="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                >
                  <span>📋</span>
                  <span>View All Orders</span>
                </router-link>
              </div>
              <div class="space-y-3 text-sm">
                <div v-if="order.is_unattributed && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)">
                  <div class="bg-orange-50 border border-orange-200 rounded-lg p-3 space-y-2">
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-orange-700">Order Type:</span>
                      <span class="text-orange-600 font-semibold">Unattributed</span>
                    </div>
                    <div v-if="order.fake_client_id" class="flex justify-between items-center">
                      <span class="font-medium text-gray-700">Client ID (shown to writer):</span>
                      <span class="font-mono text-gray-600">{{ order.fake_client_id }}</span>
                    </div>
                    <div v-if="order.external_contact_name" class="flex justify-between items-center">
                      <span class="font-medium text-gray-700">Contact Name:</span>
                      <span class="text-gray-900">{{ order.external_contact_name }}</span>
                    </div>
                    <div v-if="order.external_contact_email && (authStore.isAdmin || authStore.isSuperAdmin)" class="flex justify-between items-center">
                      <span class="font-medium text-gray-700">Contact Email:</span>
                      <span class="text-gray-900">{{ order.external_contact_email }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="space-y-3">
                  <div class="flex items-center justify-between">
              <span class="font-medium text-gray-600">Client:</span> 
              <div class="flex items-center gap-2">
                  <UserDisplayName :user="(typeof order.client === 'object' && order.client !== null) ? order.client : { id: order.client_id || order.client, role: 'client', registration_id: order.client_registration_id }" />
                <OnlineStatusIndicator
                  v-if="order.client_id && (authStore.isWriter || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                  :user-id="order.client_id"
                  :show-time-indicator="authStore.isWriter || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport"
                />
              </div>
            </div>
                  <div v-if="authStore.isWriter && order.client_id" class="flex items-center justify-between">
                    <span class="font-medium text-gray-600">Client ID:</span>
                    <span class="font-mono text-gray-900">{{ order.client?.registration_id || order.client_registration_id || `#${order.client_id}` }}</span>
                  </div>
                  <div v-if="(authStore.isAdmin || authStore.isSuperAdmin) && order.client" class="flex items-center justify-between">
                    <span class="font-medium text-gray-600">Client Email:</span>
                    <span class="text-gray-900">{{ order.client.email || order.client_email || 'N/A' }}</span>
                  </div>
                  <div v-if="(authStore.isAdmin || authStore.isSuperAdmin) && order.client" class="flex items-center justify-between">
                    <span class="font-medium text-gray-600">Registration ID:</span>
                    <span class="font-mono text-gray-900">{{ order.client.registration_id || order.client_registration_id || 'N/A' }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Writer Information -->
            <div v-if="order.writer_username || order.writer || order.assigned_writer" class="bg-white rounded-lg border border-gray-200 p-4">
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Writer Information</h3>
              <div class="space-y-3 text-sm">
                <div class="flex items-center justify-between">
              <span class="font-medium text-gray-600">Writer:</span>
              <div class="flex items-center gap-2">
                    <UserDisplayName :user="(typeof (order.writer || order.assigned_writer) === 'object' && (order.writer || order.assigned_writer) !== null) ? (order.writer || order.assigned_writer) : { id: order.writer_id || order.writer || order.assigned_writer, role: 'writer', pen_name: order.writer_pen_name, registration_id: order.writer_registration_id }" />
                <OnlineStatusIndicator
                  v-if="order.writer_id && (authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin)"
                  :user-id="order.writer_id"
                  :show-time-indicator="authStore.isClient"
                />
              </div>
            </div>
              </div>
            </div>

            <!-- Status Timeline -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-6 w-full">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">Status Timeline</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Key checkpoints from creation to completion</p>
                </div>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded-full">
                  {{ statusTimeline.length }} {{ statusTimeline.length === 1 ? 'event' : 'events' }}
                </span>
              </div>
              <div v-if="statusTimeline.length === 0" class="text-sm text-gray-500 dark:text-gray-400 py-12 text-center">
                <div class="flex flex-col items-center gap-2">
                  <svg class="w-12 h-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>No status updates recorded yet.</p>
                </div>
              </div>
              <ol v-else class="relative border-l-2 border-gray-300 dark:border-gray-600 pl-16 space-y-12">
                <li
                  v-for="(entry, index) in statusTimeline"
                  :key="entry.key"
                  class="relative group pb-3"
                >
                  <!-- Icon Circle moved closer to the left edge -->
                  <span 
                    class="absolute -left-[30px] top-0.5 w-11 h-11 rounded-full bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/30 dark:to-primary-800/30 border-2 border-white dark:border-gray-800 shadow-lg flex items-center justify-center text-xl transition-all duration-200 group-hover:scale-110 group-hover:shadow-xl z-10"
                    :class="{
                      'ring-2 ring-primary-200 dark:ring-primary-800': index === statusTimeline.length - 1
                    }"
                  >
                    {{ entry.icon }}
                  </span>
                  
                  <!-- Content Container pushed to the right with more padding -->
                  <div class="w-full min-w-0 pr-6 ml-4">
                    <!-- Status Label with proper text wrapping and overflow handling -->
                    <div 
                      class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2.5 leading-snug whitespace-normal"
                      style="word-break: break-word; overflow-wrap: anywhere; hyphens: auto;"
                    >
                      {{ entry.label }}
                    </div>
                    
                    <!-- Timestamp with improved layout and spacing -->
                    <div class="text-xs text-gray-500 dark:text-gray-400 mb-3.5 flex flex-wrap items-center gap-2.5">
                      <div class="flex items-center gap-1.5 flex-shrink-0">
                        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span class="whitespace-nowrap">{{ formatDateTime(entry.timestamp) }}</span>
                      </div>
                      <span v-if="entry.relativeTime" class="flex items-center gap-1.5 text-gray-400 dark:text-gray-500 flex-shrink-0">
                        <span class="w-1 h-1 rounded-full bg-gray-400 dark:bg-gray-500 flex-shrink-0"></span>
                        <span class="italic">{{ entry.relativeTime }}</span>
                      </span>
                    </div>
                    
                    <!-- Description with enhanced styling and proper spacing -->
                    <div 
                      v-if="entry.description" 
                      class="text-sm text-gray-600 dark:text-gray-300 mt-3.5 pl-4 pr-3 py-2.5 border-l-2 border-primary-200 dark:border-primary-700 bg-gray-50 dark:bg-gray-900/50 rounded-r-md"
                    >
                      <div class="flex items-start gap-2.5">
                        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span 
                          class="leading-relaxed whitespace-normal"
                          style="word-break: break-word; overflow-wrap: anywhere; hyphens: auto;"
                        >
                          {{ entry.description }}
                        </span>
                      </div>
                    </div>
                  </div>
                </li>
              </ol>
            </div>
          </div>

          <!-- Right Column: Order Specifications -->
          <div class="space-y-6">
            <!-- Payment & Installments -->
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">Payments & Installments</h3>
                  <p class="text-sm text-gray-500">Balance overview and recent activity</p>
                </div>
                <span
                  v-if="paymentSummary"
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-semibold',
                    paymentSummary.is_fully_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  ]"
                >
                  {{ paymentSummary.is_fully_paid ? 'Paid in Full' : 'Balance Due' }}
                </span>
              </div>

              <div v-if="paymentSummaryError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
                {{ paymentSummaryError }}
              </div>

              <div v-else-if="loadingPaymentSummary" class="flex items-center gap-2 text-sm text-gray-500">
                <span class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></span>
                Loading payment summary...
              </div>

              <div v-else>
                <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div>
                    <dt class="text-gray-500">Order Total</dt>
                    <dd class="text-lg font-semibold text-gray-900">{{ formatCurrency(paymentSummary?.order_total) }}</dd>
                  </div>
                  <div>
                    <dt class="text-gray-500">Paid</dt>
                    <dd class="text-lg font-semibold text-green-700">{{ formatCurrency(paymentSummary?.amount_paid) }}</dd>
                  </div>
                  <div>
                    <dt class="text-gray-500">Outstanding</dt>
                    <dd :class="['text-lg font-semibold', hasOutstandingBalance ? 'text-red-600' : 'text-gray-900']">
                      {{ formatCurrency(paymentSummary?.balance_due) }}
                    </dd>
                  </div>
                  <div>
                    <dt class="text-gray-500">Pending / Processing</dt>
                    <dd class="text-lg font-semibold text-yellow-700">{{ formatCurrency(paymentSummary?.pending_amount) }}</dd>
                  </div>
                </dl>

                <div v-if="hasOutstandingBalance && canPayOrder" class="mt-4">
                  <button
                    @click="showPaymentModal = true"
                    class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium transition-colors"
                  >
                    Pay Remaining Balance
                  </button>
                </div>

                <div class="mt-4">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="text-sm font-semibold text-gray-900">Recent Transactions</h4>
                    <span v-if="paymentTransactions.length" class="text-xs text-gray-500">
                      Showing {{ Math.min(paymentTransactions.length, 5) }} of {{ paymentTransactions.length }}
                    </span>
                  </div>
                  <div v-if="!paymentTransactions.length" class="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
                    No payment activity yet.
                  </div>
                  <div v-else class="space-y-3">
                    <div
                      v-for="payment in paymentTransactions.slice(0, 5)"
                      :key="payment.id"
                      class="flex items-center justify-between border rounded-lg p-3 text-sm"
                    >
                      <div>
                        <p class="font-semibold text-gray-900">{{ formatCurrency(payment.amount) }}</p>
                        <p class="text-xs text-gray-500">
                          {{ formatDateTime(payment.confirmed_at || payment.created_at) }}
                        </p>
                      </div>
                      <div class="text-right">
                        <p :class="['text-xs font-semibold px-2 py-0.5 rounded-full inline-block', getPaymentStatusClass(payment.status)]">
                          {{ payment.status.replaceAll('_', ' ') }}
                        </p>
                        <p class="text-xs text-gray-500 mt-1 capitalize">{{ payment.payment_method || 'Manual' }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-4">
                  <h4 class="text-sm font-semibold text-gray-900 mb-2">Installment Schedule</h4>
                  <div v-if="paymentInstallments.length === 0" class="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
                    No installment plan configured for this order.
                  </div>
                  <div v-else class="space-y-2">
                    <div
                      v-for="installment in paymentInstallments"
                      :key="installment.id"
                      class="flex items-center justify-between text-sm border rounded-lg p-2"
                    >
                      <div>
                        <p class="font-medium text-gray-900">{{ formatCurrency(installment.amount_due) }}</p>
                        <p class="text-xs text-gray-500">Due {{ formatDateTime(installment.due_date) }}</p>
                      </div>
                      <span
                        :class="[
                          'px-2 py-0.5 rounded-full text-xs font-semibold',
                          installment.is_paid ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                        ]"
                      >
                        {{ installment.is_paid ? 'Paid' : 'Pending' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Order Specifications -->
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Order Specifications</h3>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span class="font-medium text-gray-600">Topic:</span>
                  <p class="text-gray-900 mt-1">{{ order.topic || 'N/A' }}</p>
                </div>
                <div>
                  <span class="font-medium text-gray-600">State/Status:</span>
                  <p class="mt-1">
                    <span class="px-2 py-1 rounded-full text-xs font-medium" :class="getStatusClass(order.status)">
                      {{ order.status }}
              </span>
                  </p>
            </div>
                <div v-if="order.subject">
                  <span class="font-medium text-gray-600">Subject:</span>
                  <p class="text-gray-900 mt-1">{{ order.subject?.name || order.subject_name || 'N/A' }}</p>
          </div>
                <div v-if="order.subject && (order.subject?.is_technical !== undefined || order.subject_is_technical !== undefined)">
                  <span class="font-medium text-gray-600">Specialty:</span>
                  <p class="mt-1">
                    <span :class="(order.subject?.is_technical || order.subject_is_technical) ? 'px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs' : 'px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs'">
                      {{ (order.subject?.is_technical || order.subject_is_technical) ? 'Technical' : 'Non-Technical' }}
                    </span>
                  </p>
                </div>
                <div v-if="order.paper_type">
                  <span class="font-medium text-gray-600">Paper Type:</span>
                  <p class="text-gray-900 mt-1">{{ order.paper_type?.name || order.paper_type_name || 'N/A' }}</p>
                </div>
                <div v-if="order.english_type">
                  <span class="font-medium text-gray-600">English Type:</span>
                  <p class="text-gray-900 mt-1">{{ order.english_type?.name || order.english_type_name || 'N/A' }}</p>
                </div>
                <div v-if="order.formatting_style">
                  <span class="font-medium text-gray-600">Formatting Style:</span>
                  <p class="text-gray-900 mt-1">{{ order.formatting_style?.name || order.formatting_style_name || 'N/A' }}</p>
                </div>
                <div v-if="order.academic_level">
                  <span class="font-medium text-gray-600">Academic Level:</span>
                  <p class="text-gray-900 mt-1">{{ order.academic_level?.name || order.academic_level_name || 'N/A' }}</p>
        </div>
        <div>
                  <span class="font-medium text-gray-600">Number of Pages:</span>
                  <p class="text-gray-900 mt-1">{{ order.number_of_pages || 0 }}</p>
                </div>
                <div>
                  <span class="font-medium text-gray-600">Number of Slides:</span>
                  <p class="text-gray-900 mt-1">{{ order.number_of_slides || 0 }}</p>
                </div>
                <div>
                  <span class="font-medium text-gray-600">Number of Sources:</span>
                  <p class="text-gray-900 mt-1">{{ order.number_of_refereces || order.number_of_sources || 0 }}</p>
                </div>
                <div v-if="order.type_of_work">
                  <span class="font-medium text-gray-600">Type of Work:</span>
                  <p class="text-gray-900 mt-1">{{ order.type_of_work?.name || order.type_of_work_name || 'N/A' }}</p>
                </div>
              </div>
            </div>

            <!-- Additional Services -->
            <div v-if="order.extra_services && order.extra_services.length > 0" class="bg-white rounded-lg border border-gray-200 p-4">
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Additional Services</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="service in order.extra_services"
                  :key="service.id || service"
                  class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
                >
                  {{ service.name || service }}
                </span>
              </div>
            </div>

            <!-- Deadlines -->
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Deadlines</h3>
              <div class="space-y-3 text-sm">
                <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Client Deadline (Real):</span>
                  <span class="text-gray-900 font-medium">{{ formatDateTime(order.client_deadline) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Writer Deadline:</span>
                  <span class="text-gray-900 font-medium">{{ formatDateTime(order.writer_deadline || order.deadline) }}</span>
                </div>
                <div v-if="order.writer_deadline_percentage && (authStore.isAdmin || authStore.isSuperAdmin)" class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Deadline Config:</span>
                  <span class="text-gray-900">{{ order.writer_deadline_percentage?.writer_deadline_percentage || order.writer_deadline_percentage }}%</span>
                </div>
              </div>
            </div>

            <!-- Financial Information (Admin/SuperAdmin) -->
            <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="bg-white rounded-lg border border-gray-200 p-4">
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Financial Information</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Total Cost:</span>
                  <span class="text-gray-900 font-semibold">${{ parseFloat(order.total_cost || 0).toFixed(2) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Writer Compensation:</span>
                  <span class="text-gray-900">${{ parseFloat(order.writer_compensation || 0).toFixed(2) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Paid:</span>
                  <span :class="order.is_paid ? 'text-green-600 font-semibold' : 'text-yellow-600 font-semibold'">
                    {{ order.is_paid ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Instructions - Full Width -->
        <div v-if="order.instructions || order.order_instructions" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Order Instructions</h3>
          <div class="prose prose-sm max-w-none dark:prose-invert">
            <SafeHtml 
              :content="order.instructions || order.order_instructions"
              container-class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed"
            />
          </div>
        </div>
        
        <!-- Notes (if available) -->
        <div v-if="order.completion_notes || (authStore.isAdmin || authStore.isSuperAdmin)" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h3 class="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">Notes</h3>
          <div v-if="order.completion_notes" class="text-gray-700 dark:text-gray-300 text-sm whitespace-pre-wrap">{{ order.completion_notes }}</div>
          <div v-else class="text-gray-400 dark:text-gray-500 text-sm italic">No notes available</div>
        </div>
        
        <!-- Progress Bar (for clients) -->
        <div v-if="authStore.isClient && order.assigned_writer" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Order Progress</h3>
          <ProgressBar
            :progress-percentage="latestProgressPercentage"
            :last-update="latestProgressUpdate"
          />
        </div>
      </div>

      <!-- Enhanced Status Tab -->
      <div v-if="activeTab === 'enhanced-status'" class="space-y-6">
        <EnhancedOrderStatus :order-id="order.id" />
      </div>

      <!-- Unattributed Order Info (Admin Only) -->
      <div v-if="order.is_unattributed && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)" class="border-t pt-4">
        <h3 class="text-lg font-semibold mb-3 text-orange-600">Unattributed Order Information</h3>
        <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 space-y-2">
          <div v-if="order.external_contact_name" class="text-sm">
            <span class="font-medium text-gray-700">Contact Name:</span> 
            <span class="ml-2">{{ order.external_contact_name }}</span>
          </div>
          <div v-if="order.external_contact_email" class="text-sm">
            <span class="font-medium text-gray-700">Contact Email:</span> 
            <span class="ml-2">{{ order.external_contact_email }}</span>
          </div>
          <div v-if="order.external_contact_phone" class="text-sm">
            <span class="font-medium text-gray-700">Contact Phone:</span> 
            <span class="ml-2">{{ order.external_contact_phone }}</span>
          </div>
          <div v-if="order.fake_client_id" class="text-sm">
            <span class="font-medium text-gray-700">Fake Client ID (shown to writer):</span> 
            <span class="ml-2 font-mono text-gray-600">{{ order.fake_client_id }}</span>
          </div>
          <div v-if="order.allow_unpaid_access" class="text-sm">
            <span class="font-medium text-gray-700">Unpaid Access:</span> 
            <span class="ml-2 text-green-600">✓ Allowed</span>
          </div>
          <p class="text-xs text-orange-700 mt-2">
            <strong>Note:</strong> This order will be assigned to you (admin/superadmin) as the client upon completion.
          </p>
        </div>
      </div>

      <!-- Review Section (for completed orders) -->
      <div v-if="order.status === 'completed' && canSubmitReview" class="border-t pt-4" data-review-section>
        <h3 class="text-lg font-semibold mb-4">Submit Review</h3>
        <div v-if="!hasReview" class="bg-gray-50 rounded-lg p-4">
          <ReviewSubmission
            v-if="order.writer_id || order.writer?.id"
            :order-id="order.id"
            :writer-id="order.writer_id || order.writer?.id"
            @success="handleReviewSubmitted"
          />
        </div>
        <div v-else class="bg-green-50 border border-green-200 rounded-lg p-4">
          <p class="text-green-800">✓ You have already submitted a review for this order.</p>
        </div>
      </div>

      <!-- Order Actions -->
      <div class="border-t pt-4">
        <h3 class="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">Order Actions</h3>
        <div class="flex flex-wrap gap-2">
          <!-- Writer Actions Section -->
          <div v-if="authStore.isWriter" class="flex flex-wrap gap-2 w-full">
            <!-- Take Order (for available orders - not yet assigned) -->
            <button
              v-if="canTakeOrder"
              @click="takeOrder"
              :disabled="takingOrder || requestingOrder || !canTakeOrders"
              class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              :title="!canTakeOrders ? 'You have reached your order limit' : (isOrderRequested ? 'You have already requested this order' : 'Take this order immediately')"
            >
              <span>✅</span>
              <span>{{ takingOrder ? 'Taking...' : 'Take Order' }}</span>
            </button>
            
            <!-- Request Order (for available orders - not yet assigned) -->
            <button
              v-if="canRequestOrder"
              @click="openRequestModal"
              :disabled="isOrderRequested || requestingOrder || takingOrder"
              class="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              :title="isOrderRequested ? 'You have already requested this order' : 'Request this order (requires admin approval)'"
            >
              <span>📋</span>
              <span>{{ isOrderRequested ? 'Requested' : (requestingOrder ? 'Requesting...' : 'Request Order') }}</span>
            </button>
            
            <!-- Assigned Writer Actions (only for assigned writers) -->
            <template v-if="order.writer_id === userId || order.assigned_writer_id === userId || order.assigned_writer?.id === userId">
              <!-- Start Order (for available/reassigned orders - already assigned) -->
              <button
                v-if="canStartOrder"
                @click="startOrder"
                :disabled="processingAction"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <span>🚀</span>
                <span>{{ processingAction ? 'Processing...' : 'Start Order' }}</span>
              </button>
            
            <!-- Submit Order (for in_progress/revision_in_progress orders) -->
            <button
              v-if="canSubmitOrder"
              @click="submitOrder"
              :disabled="processingAction"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span>📤</span>
              <span>{{ processingAction ? 'Processing...' : 'Submit Order' }}</span>
            </button>
            
            <!-- Start Revision (for revision_requested orders) -->
            <button
              v-if="canStartRevision"
              @click="startRevision"
              :disabled="processingAction"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span>✏️</span>
              <span>{{ processingAction ? 'Processing...' : 'Start Revision' }}</span>
            </button>
            
            <!-- Resume Order (for on_hold orders) -->
            <button
              v-if="canResumeOrder"
              @click="resumeOrder"
              :disabled="processingAction"
              class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span>▶️</span>
              <span>{{ processingAction ? 'Processing...' : 'Resume Order' }}</span>
            </button>
            
            <!-- Deadline Extension Request -->
            <button
              v-if="canRequestDeadlineExtension"
              @click="showDeadlineExtensionModal = true"
              class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
            >
              <span>⏰</span>
              <span>Request Deadline Extension</span>
            </button>
            
            <!-- Request Hold -->
            <button
              v-if="canRequestHold"
              @click="showHoldRequestModal = true"
              class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2"
            >
              <span>🛑</span>
              <span>Request Hold</span>
            </button>
            </template>
          </div>
          
          <!-- Admin/Superadmin/Support Actions - Use Modal -->
          <button
            v-if="(authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) && order"
            @click="openActionModal()"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Order Actions
          </button>
          
          <!-- Client Actions (keep direct buttons for clients) -->
          <button
            v-if="canCompleteOrder && !authStore.isAdmin && !authStore.isSuperAdmin && !authStore.isSupport"
            @click="completeOrder"
            :disabled="processingAction"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ processingAction ? 'Processing...' : 'Mark as Complete' }}
          </button>
          
          <button
            v-if="canCancelOrder && !authStore.isAdmin && !authStore.isSuperAdmin && !authStore.isSupport"
            @click="cancelOrder"
            :disabled="processingAction"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ processingAction ? 'Processing...' : 'Cancel Order' }}
          </button>
          
          <button
            v-if="canReopenOrder && !authStore.isAdmin && !authStore.isSuperAdmin && !authStore.isSupport"
            @click="reopenOrder"
            :disabled="processingAction"
            class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ processingAction ? 'Processing...' : 'Reopen Order' }}
          </button>
          
          <!-- Payment Action -->
          <button
            v-if="canPayOrder && !order.is_paid"
            @click="showPaymentModal = true"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            💳 Pay Now
          </button>
        </div>
        
        <!-- Payment Modal -->
        <Modal
          v-model:visible="showPaymentModal"
          title="Payment Checkout"
          size="lg"
        >
          <PaymentCheckout
            :order-id="order.id"
            :order-total="parseFloat(order.total_cost || 0)"
            :discount-amount="0"
            :wallet-balance="walletBalance"
            @success="handlePaymentSuccess"
            @error="handlePaymentError"
            @cancel="showPaymentModal = false"
          />
        </Modal>
        <div v-if="actionError" class="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
          {{ actionError }}
        </div>
        <div v-if="actionSuccess" class="mt-2 text-sm text-green-600 bg-green-50 p-2 rounded">
          {{ actionSuccess }}
        </div>
      </div>

      </div>
      <!-- End Overview Tab -->

      <!-- Progress Tab -->
      <div v-if="activeTab === 'progress'" class="space-y-6">
        <!-- Progress Bar (for clients) -->
        <div v-if="authStore.isClient" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Order Progress
            </h3>
            <button
              @click="loadLatestProgress"
              class="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-1.5"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
          <ProgressBar
            :progress-percentage="latestProgressPercentage"
            :last-update="latestProgressUpdate"
          />
        </div>

        <!-- Progress Report Form (for writers) -->
        <div v-if="canSubmitProgress" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Report Progress
          </h3>
          <ProgressReportForm
            :order-id="order.id"
            :initial-progress="latestProgressPercentage"
            @success="handleProgressSubmitted"
            @error="handleProgressError"
          />
        </div>

        <!-- Progress History -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Progress History
          </h3>
          <ProgressHistory
            :order-id="order.id"
            @updated="loadLatestProgress"
            ref="progressHistoryRef"
          />
        </div>
      </div>
      <!-- End Progress Tab -->

      <!-- Messages Tab -->
      <div v-if="activeTab === 'messages'" class="space-y-6">
        <OrderMessagesTabbed
          :order-id="order.id"
          :order-topic="order.topic"
        />
      </div>
      <!-- End Messages Tab -->

      <!-- Files Tab -->
      <div v-if="activeTab === 'files'" class="space-y-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
              <svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Files
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">Upload and manage order files</p>

            <div
              v-if="finalPaperFile"
              class="mt-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-300 dark:border-green-700 rounded-xl flex items-center justify-between shadow-sm"
            >
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-bold text-green-800 dark:text-green-300">
                    Final Paper is ready to download
                  </p>
                  <p class="text-xs text-green-700 dark:text-green-400 mt-0.5">
                    Version {{ finalPaperFile.version || '1' }} •
                    {{ formatDateTime(finalPaperFile.created_at) }}
                  </p>
                </div>
              </div>
              <button
                @click="downloadFile(finalPaperFile)"
                class="px-4 py-2.5 bg-green-600 dark:bg-green-700 text-white rounded-lg hover:bg-green-700 dark:hover:bg-green-600 text-sm font-medium flex items-center gap-2 shadow-md transition-all"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Final Paper
              </button>
            </div>
          </div>
          <button
            @click="loadFiles"
            class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium flex items-center gap-2"
            :disabled="loadingFiles"
          >
            <svg v-if="loadingFiles" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ loadingFiles ? 'Loading...' : 'Refresh' }}
          </button>
        </div>

        <!-- File Upload Form -->
        <div class="mb-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 shadow-sm">
          <h4 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload Files
          </h4>
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">
                  Category <span class="text-gray-400">(Optional)</span>
                </label>
                <select
                  v-model="uploadForm.category"
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option :value="null">Select Category (Optional)</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                    <span v-if="category.is_final_draft"> (Final Draft)</span>
                  </option>
                </select>
                <p v-if="uploadForm.category && getCategoryById(uploadForm.category)?.is_final_draft" class="text-xs text-orange-600 mt-1">
                  ⚠️ Final Draft files require payment completion for client download
                </p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">
                  File Type
                </label>
                <select
                  v-model="uploadForm.fileType"
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="regular">Regular File</option>
                  <option value="extra_service">Extra Service File</option>
                </select>
              </div>
            </div>
            
            <div>
              <FileUpload
                v-model="uploadedFiles"
                :multiple="true"
                :auto-upload="false"
                :max-size="100 * 1024 * 1024"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.zip,.rar"
                label="Drop files here or click to browse"
                @upload="handleFileUpload"
              />
            </div>
            
            <div v-if="uploadSuccess" class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-sm text-green-700 dark:text-green-300 flex items-center gap-2">
              <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ uploadSuccess }}
            </div>
            <div v-if="uploadError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300 flex items-center gap-2">
              <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {{ uploadError }}
            </div>
            
            <div v-if="uploadedFiles.length > 0" class="flex justify-end gap-2">
              <button
                @click="clearUploadForm"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
              >
                Clear
              </button>
              <button
                @click="uploadSelectedFiles"
                :disabled="uploadingFiles"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm"
              >
                {{ uploadingFiles ? 'Uploading...' : `Upload ${uploadedFiles.length} File(s)` }}
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="loadingFiles" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="files.length === 0" class="text-center py-16 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-200 dark:border-gray-700">
          <div class="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">No files uploaded yet</p>
          <p class="text-gray-500 dark:text-gray-500 text-xs">Upload files using the form above</p>
        </div>
        
        <div v-else class="space-y-6">
          <!-- Files Separated by Uploader Type -->
          
          <!-- Staff Files -->
          <div v-if="staffFiles.length > 0" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 px-6 py-4 border-b border-gray-200">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                  <span class="text-purple-600 text-lg">🛟</span>
                </div>
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Staff Files</h4>
                  <p class="text-sm text-gray-600">Files uploaded by support, admin, or staff members</p>
                </div>
                <span class="ml-auto px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                  {{ staffFiles.length }} file{{ staffFiles.length !== 1 ? 's' : '' }}
              </span>
                  </div>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">File</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Uploaded By</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Size</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr
                    v-for="file in staffFiles"
                :key="file.id"
                    class="hover:bg-gray-50 transition-colors"
                  >
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="text-xl">📄</span>
                        <div class="min-w-0">
                          <div class="text-sm font-medium text-gray-900 truncate max-w-xs" :title="file.file_name">
                        {{ file.file_name || 'Unnamed File' }}
                      </div>
                          <div v-if="getCategoryById(file.category)?.is_final_draft" class="text-xs text-blue-600 mt-1">
                            Final Draft
                      </div>
                    </div>
                  </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-600 max-w-xs truncate" :title="file.description || file.file_description">
                        {{ file.description || file.file_description || '—' }}
                </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDateTime(file.created_at) }}</div>
                      <div class="text-xs text-gray-500">{{ formatRelativeTime(file.created_at) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-medium">Staff</span>
                        <div>
                          <div class="text-sm text-gray-900">{{ file.uploaded_by_username || file.uploaded_by || 'N/A' }}</div>
                          <div v-if="file.uploaded_by_email && (authStore.isAdmin || authStore.isSuperAdmin)" class="text-xs text-gray-500">
                            {{ file.uploaded_by_email }}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="text-sm text-gray-900">{{ formatFileSize(file.file_size) }}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ file.is_downloadable ? '✓ Downloadable' : '🔒 Locked' }}
                  </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center gap-2">
                        <button
                          v-if="canDownloadFile(file)"
                          @click="downloadFile(file)"
                          class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-xs flex items-center gap-1"
                          title="Download file"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download
                        </button>
                        <button
                          v-else
                          disabled
                          class="px-3 py-1.5 bg-gray-200 text-gray-500 rounded-lg cursor-not-allowed text-xs"
                          title="File is locked or payment required"
                        >
                          🔒 Locked
                        </button>
                        
                        <button
                          v-if="isAdmin"
                          @click="toggleFileDownload(file)"
                          class="px-2 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-xs"
                          :title="file.is_downloadable ? 'Lock file' : 'Unlock file'"
                        >
                          {{ file.is_downloadable ? '🔒' : '🔓' }}
                        </button>
                        
                        <button
                          v-if="canDeleteFile(file)"
                          @click="requestFileDeletion(file)"
                          class="px-2 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-xs"
                          title="Request deletion"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Client Files -->
          <div v-if="clientFiles.length > 0" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-4 border-b border-gray-200">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                  <span class="text-green-600 text-lg">👤</span>
                </div>
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Client Files</h4>
                  <p class="text-sm text-gray-600">Files uploaded by the client</p>
                </div>
                <span class="ml-auto px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                  {{ clientFiles.length }} file{{ clientFiles.length !== 1 ? 's' : '' }}
                  </span>
                </div>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">File</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Uploaded By</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Size</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr
                    v-for="file in clientFiles"
                    :key="file.id"
                    class="hover:bg-gray-50 transition-colors"
                  >
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="text-xl">📄</span>
                        <div class="min-w-0">
                          <div class="text-sm font-medium text-gray-900 truncate max-w-xs" :title="file.file_name">
                            {{ file.file_name || 'Unnamed File' }}
                          </div>
                          <div v-if="getCategoryById(file.category)?.is_final_draft" class="text-xs text-blue-600 mt-1">
                            Final Draft
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-600 max-w-xs truncate" :title="file.description || file.file_description">
                        {{ file.description || file.file_description || '—' }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDateTime(file.created_at) }}</div>
                      <div class="text-xs text-gray-500">{{ formatRelativeTime(file.created_at) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs font-medium">Client</span>
                        <div>
                          <div class="text-sm text-gray-900">{{ file.uploaded_by_username || file.uploaded_by || 'N/A' }}</div>
                          <div v-if="file.uploaded_by_email && (authStore.isAdmin || authStore.isSuperAdmin)" class="text-xs text-gray-500">
                            {{ file.uploaded_by_email }}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="text-sm text-gray-900">{{ formatFileSize(file.file_size) }}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ file.is_downloadable ? '✓ Downloadable' : '🔒 Locked' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center gap-2">
                        <button
                          v-if="canDownloadFile(file)"
                          @click="downloadFile(file)"
                          class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-xs flex items-center gap-1"
                          title="Download file"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download
                        </button>
                        <button
                          v-else
                          disabled
                          class="px-3 py-1.5 bg-gray-200 text-gray-500 rounded-lg cursor-not-allowed text-xs"
                          title="File is locked or payment required"
                        >
                          🔒 Locked
                        </button>
                        
                        <button
                          v-if="isAdmin"
                          @click="toggleFileDownload(file)"
                          class="px-2 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-xs"
                          :title="file.is_downloadable ? 'Lock file' : 'Unlock file'"
                        >
                          {{ file.is_downloadable ? '🔒' : '🔓' }}
                        </button>
                        
                        <button
                          v-if="canDeleteFile(file)"
                          @click="requestFileDeletion(file)"
                          class="px-2 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-xs"
                          title="Request deletion"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
                </div>
                
          <!-- Writer Files -->
          <div v-if="writerFiles.length > 0" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <span class="text-blue-600 text-lg">✍️</span>
                </div>
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Writer Files</h4>
                  <p class="text-sm text-gray-600">Files uploaded by the assigned writer</p>
                </div>
                <span class="ml-auto px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {{ writerFiles.length }} file{{ writerFiles.length !== 1 ? 's' : '' }}
                </span>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">File</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Uploaded By</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Size</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr
                    v-for="file in writerFiles"
                    :key="file.id"
                    class="hover:bg-gray-50 transition-colors"
                  >
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="text-xl">📄</span>
                        <div class="min-w-0">
                          <div class="text-sm font-medium text-gray-900 truncate max-w-xs" :title="file.file_name">
                            {{ file.file_name || 'Unnamed File' }}
                          </div>
                          <div v-if="getCategoryById(file.category)?.is_final_draft" class="text-xs text-blue-600 mt-1">
                            Final Draft
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-600 max-w-xs truncate" :title="file.description || file.file_description">
                        {{ file.description || file.file_description || '—' }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDateTime(file.created_at) }}</div>
                      <div class="text-xs text-gray-500">{{ formatRelativeTime(file.created_at) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-medium">Writer</span>
                        <div>
                          <div class="text-sm text-gray-900">{{ file.uploaded_by_username || file.uploaded_by || 'N/A' }}</div>
                          <div v-if="file.uploaded_by_email && (authStore.isAdmin || authStore.isSuperAdmin)" class="text-xs text-gray-500">
                            {{ file.uploaded_by_email }}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="text-sm text-gray-900">{{ formatFileSize(file.file_size) }}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ file.is_downloadable ? '✓ Downloadable' : '🔒 Locked' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    v-if="canDownloadFile(file)"
                    @click="downloadFile(file)"
                          class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-xs flex items-center gap-1"
                          title="Download file"
                  >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download
                  </button>
                  <button
                    v-else
                    disabled
                          class="px-3 py-1.5 bg-gray-200 text-gray-500 rounded-lg cursor-not-allowed text-xs"
                    title="File is locked or payment required"
                  >
                    🔒 Locked
                  </button>
                  
                  <button
                    v-if="isAdmin"
                    @click="toggleFileDownload(file)"
                          class="px-2 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-xs"
                    :title="file.is_downloadable ? 'Lock file' : 'Unlock file'"
                  >
                    {{ file.is_downloadable ? '🔒' : '🔓' }}
                  </button>
                  
                  <button
                    v-if="canDeleteFile(file)"
                    @click="requestFileDeletion(file)"
                          class="px-2 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-xs"
                    title="Request deletion"
                  >
                    🗑️
                  </button>
                </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              </div>
            </div>

          <!-- Other Files (Unknown uploader or by category if needed) -->
          <div v-if="otherFiles.length > 0" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="bg-gradient-to-r from-gray-50 to-slate-50 px-6 py-4 border-b border-gray-200">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                  <span class="text-gray-600 text-lg">📁</span>
          </div>
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Other Files</h4>
                  <p class="text-sm text-gray-600">Additional files</p>
        </div>
                <span class="ml-auto px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">
                  {{ otherFiles.length }} file{{ otherFiles.length !== 1 ? 's' : '' }}
                </span>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">File</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Uploaded By</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Size</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr
                    v-for="file in otherFiles"
                    :key="file.id"
                    class="hover:bg-gray-50 transition-colors"
                  >
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-2">
                        <span class="text-xl">📄</span>
                        <div class="min-w-0">
                          <div class="text-sm font-medium text-gray-900 truncate max-w-xs" :title="file.file_name">
                            {{ file.file_name || 'Unnamed File' }}
                          </div>
                          <div v-if="getCategoryById(file.category)?.is_final_draft" class="text-xs text-blue-600 mt-1">
                            Final Draft
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-600 max-w-xs truncate" :title="file.description || file.file_description">
                        {{ file.description || file.file_description || '—' }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDateTime(file.created_at) }}</div>
                      <div class="text-xs text-gray-500">{{ formatRelativeTime(file.created_at) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ file.uploaded_by_username || file.uploaded_by || 'N/A' }}</div>
                      <div v-if="file.uploaded_by_email && (authStore.isAdmin || authStore.isSuperAdmin)" class="text-xs text-gray-500">
                        {{ file.uploaded_by_email }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="text-sm text-gray-900">{{ formatFileSize(file.file_size) }}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ file.is_downloadable ? '✓ Downloadable' : '🔒 Locked' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center gap-2">
                        <button
                          v-if="canDownloadFile(file)"
                          @click="downloadFile(file)"
                          class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-xs flex items-center gap-1"
                          title="Download file"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download
                        </button>
                        <button
                          v-else
                          disabled
                          class="px-3 py-1.5 bg-gray-200 text-gray-500 rounded-lg cursor-not-allowed text-xs"
                          title="File is locked or payment required"
                        >
                          🔒 Locked
                        </button>
                        
                        <button
                          v-if="isAdmin"
                          @click="toggleFileDownload(file)"
                          class="px-2 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-xs"
                          :title="file.is_downloadable ? 'Lock file' : 'Unlock file'"
                        >
                          {{ file.is_downloadable ? '🔒' : '🔓' }}
                        </button>
                        
                        <button
                          v-if="canDeleteFile(file)"
                          @click="requestFileDeletion(file)"
                          class="px-2 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-xs"
                          title="Request deletion"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Extra Service Files Section (inside Files tab) -->
      <div v-if="extraServiceFiles.length > 0 || isAdmin" class="border-t pt-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold">Extra Service Files</h3>
            <p class="text-sm text-gray-500 mt-1">Plagiarism reports, Smart Papers, and other extra services</p>
          </div>
          <button
            @click="loadExtraServiceFiles"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            :disabled="loadingExtraServiceFiles"
          >
            {{ loadingExtraServiceFiles ? 'Loading...' : '🔄 Refresh' }}
          </button>
        </div>
        
        <div v-if="loadingExtraServiceFiles" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="extraServiceFiles.length === 0" class="text-center py-8 text-gray-500 text-sm bg-gray-50 rounded-lg">
          No extra service files yet
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="file in extraServiceFiles"
            :key="file.id"
            class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center gap-2 mb-2">
              <div class="text-2xl">📊</div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 truncate">{{ file.file_name || 'Extra Service File' }}</div>
                <div class="text-xs text-gray-500">{{ formatFileSize(file.file_size) }}</div>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-3">
              <button
                @click="downloadExtraServiceFile(file)"
                class="flex-1 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
              >
                Download
              </button>
            </div>
          </div>
        </div>
      </div>
      <!-- End Files Tab -->

      <!-- Draft Requests Tab -->
      <div v-if="activeTab === 'draft-requests'" class="space-y-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
              <svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Draft Requests
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">Request drafts to see order progress (requires Progressive Delivery)</p>
          </div>
          <button
            v-if="authStore.isClient"
            @click="checkDraftEligibility"
            class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium flex items-center gap-2"
            :disabled="loadingDraftEligibility"
          >
            <svg v-if="loadingDraftEligibility" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {{ loadingDraftEligibility ? 'Checking...' : 'Check Eligibility' }}
          </button>
        </div>

        <!-- Eligibility Check (Client) -->
        <div v-if="authStore.isClient && draftEligibility" class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border-2 border-blue-200 dark:border-blue-800 p-6 shadow-sm">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
              <span class="text-2xl">{{ draftEligibility.can_request ? '✅' : '⚠️' }}</span>
            </div>
            <div class="flex-1">
              <h4 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
                {{ draftEligibility.can_request ? 'You can request drafts!' : 'Cannot request drafts' }}
              </h4>
              <p v-if="draftEligibility.reason" class="text-sm text-gray-700 dark:text-gray-300 mb-3">
                {{ draftEligibility.reason }}
              </p>
              <p v-if="draftEligibility.has_pending_request" class="text-sm text-orange-700 dark:text-orange-400 mb-4 p-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                You already have a pending draft request for this order.
              </p>
              <button
                v-if="draftEligibility.can_request && !draftEligibility.has_pending_request"
                @click="showDraftRequestModal = true"
                class="px-4 py-2.5 bg-primary-600 dark:bg-primary-700 text-white rounded-lg hover:bg-primary-700 dark:hover:bg-primary-600 transition-colors text-sm font-medium shadow-md flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Request Draft
              </button>
            </div>
          </div>
        </div>

        <!-- Draft Requests List -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Draft Request History
            </h4>
          </div>

          <div v-if="loadingDraftRequests" class="flex flex-col items-center justify-center py-16">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mb-3"></div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Loading draft requests...</p>
          </div>

          <div v-else-if="draftRequests.length === 0" class="p-16 text-center">
            <div class="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">No draft requests yet</p>
            <p class="text-gray-500 dark:text-gray-500 text-xs">Request a draft to see order progress</p>
          </div>

          <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="request in draftRequests"
              :key="request.id"
              class="p-6 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <span
                      :class="{
                        'bg-yellow-100 text-yellow-800': request.status === 'pending',
                        'bg-blue-100 text-blue-800': request.status === 'in_progress',
                        'bg-green-100 text-green-800': request.status === 'fulfilled',
                        'bg-gray-100 text-gray-800': request.status === 'cancelled'
                      }"
                      class="px-2 py-1 rounded-full text-xs font-medium"
                    >
                      {{ request.status }}
                    </span>
                    <span class="text-sm text-gray-500">
                      Requested {{ formatDateTime(request.requested_at) }}
                    </span>
                  </div>
                  <p v-if="request.message" class="text-sm text-gray-700 mb-3">
                    {{ request.message }}
                  </p>
                  
                  <!-- Draft Files -->
                  <div v-if="request.files && request.files.length > 0" class="mt-4">
                    <h5 class="text-sm font-medium text-gray-900 mb-2">Draft Files ({{ request.files_count }})</h5>
                    <div class="space-y-2">
                      <div
                        v-for="file in request.files"
                        :key="file.id"
                        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div class="flex items-center gap-3">
                          <span class="text-lg">📄</span>
                          <div>
                            <div class="text-sm font-medium text-gray-900">{{ file.file_name }}</div>
                            <div class="text-xs text-gray-500">
                              Uploaded {{ formatDateTime(file.uploaded_at) }}
                              <span v-if="file.file_size_mb"> • {{ file.file_size_mb }} MB</span>
                            </div>
                            <div v-if="file.description" class="text-xs text-gray-600 mt-1">
                              {{ file.description }}
                            </div>
                          </div>
                        </div>
                        <button
                          @click="downloadDraftFile(file.id)"
                          class="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-xs"
                        >
                          Download
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="ml-4 flex flex-col gap-2">
                  <button
                    v-if="request.status === 'pending' && authStore.isClient"
                    @click="cancelDraftRequest(request.id)"
                    class="px-3 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-xs"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Writer: Upload Draft Section -->
        <div v-if="authStore.isWriter && (order.writer_id === userId || order.assigned_writer_id === userId || order.assigned_writer?.id === userId)" class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h4 class="text-lg font-semibold mb-4">Upload Draft for Client Request</h4>
          
          <div v-if="pendingDraftRequests.length === 0" class="text-center py-8 text-gray-500">
            <p>No pending draft requests for this order</p>
          </div>
          
          <div v-else class="space-y-4">
            <div
              v-for="request in pendingDraftRequests"
              :key="request.id"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex items-center justify-between mb-3">
                <div>
                  <div class="font-medium text-gray-900">Request #{{ request.id }}</div>
                  <div class="text-sm text-gray-500">
                    Requested {{ formatDateTime(request.requested_at) }}
                  </div>
                  <p v-if="request.message" class="text-sm text-gray-700 mt-2">
                    {{ request.message }}
                  </p>
                </div>
                <span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                  {{ request.status }}
                </span>
              </div>
              
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Upload Draft File
                </label>
                <input
                  type="file"
                  :ref="el => { if (el) draftFileInputs[request.id] = el }"
                  @change="handleDraftFileSelect(request.id, $event)"
                  class="w-full border rounded-lg px-3 py-2 text-sm"
                  accept=".pdf,.doc,.docx,.txt"
                />
                <textarea
                  v-model="draftFileDescriptions[request.id]"
                  rows="2"
                  class="w-full mt-2 border rounded-lg px-3 py-2 text-sm"
                  placeholder="Optional description of what's in this draft..."
                ></textarea>
                <button
                  @click="uploadDraftFile(request.id)"
                  :disabled="!draftSelectedFiles[request.id] || uploadingDraft[request.id]"
                  class="mt-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm"
                >
                  {{ uploadingDraft[request.id] ? 'Uploading...' : 'Upload Draft' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- End Draft Requests Tab -->

      <!-- External Links Tab -->
      <div v-if="activeTab === 'links'" class="space-y-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
              <svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              External Links
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">Submit and manage external file links</p>
          </div>
          <button
            @click="loadLinks"
            class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium flex items-center gap-2"
            :disabled="loadingLinks"
          >
            <svg v-if="loadingLinks" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ loadingLinks ? 'Loading...' : 'Refresh' }}
          </button>
        </div>

        <!-- External Link Submission Form -->
        <div class="mb-6 p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl border border-purple-200 dark:border-purple-800 shadow-sm">
          <h4 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Submit External Link
          </h4>
          <form @submit.prevent="submitLink" class="space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Link URL *</label>
                <input
                  v-model="linkForm.link"
                  type="url"
                  placeholder="https://drive.google.com/..."
                  class="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Description</label>
                <input
                  v-model="linkForm.description"
                  type="text"
                  placeholder="Brief description (optional)"
                  class="w-full border rounded px-3 py-2 text-sm"
                  maxlength="255"
                />
              </div>
              <div class="flex items-end">
                <button
                  type="submit"
                  :disabled="submittingLink || !linkForm.link"
                  class="w-full btn btn-primary text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ submittingLink ? 'Submitting...' : 'Submit Link' }}
                </button>
              </div>
            </div>
            <div v-if="linkError" class="text-xs text-red-600 bg-red-50 p-2 rounded">
              {{ linkError }}
            </div>
            <div v-if="linkSuccess" class="text-xs text-green-600 bg-green-50 p-2 rounded">
              {{ linkSuccess }}
            </div>
          </form>
        </div>
        
        <div v-if="loadingLinks" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="links.length === 0" class="text-center py-8 text-gray-500 text-sm">
          No external links submitted yet.
        </div>
        
        <div v-else class="overflow-x-auto bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Link</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewed By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="link in links" :key="link.id" class="hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
                <td class="px-4 py-3">
                  <a
                    :href="link.link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-600 hover:text-blue-800 hover:underline text-sm break-all"
                  >
                    {{ link.link }}
                  </a>
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">
                  {{ link.description || 'No description' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ link.uploaded_by_username || link.uploaded_by || 'N/A' }}</div>
                  <div v-if="link.uploaded_by_email" class="text-xs text-gray-500">{{ link.uploaded_by_email }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span
                    :class="{
                      'bg-yellow-100 text-yellow-800': link.status === 'pending',
                      'bg-green-100 text-green-800': link.status === 'approved',
                      'bg-red-100 text-red-800': link.status === 'rejected'
                    }"
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ link.status_display || link.status }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ link.reviewed_by_username || 'Not reviewed' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">
                  <div v-if="isAdmin && link.status === 'pending'" class="flex gap-2">
                    <button
                      @click="approveLink(link)"
                      class="text-green-600 hover:text-green-800 hover:underline"
                      :disabled="processingLink === link.id"
                    >
                      {{ processingLink === link.id ? 'Processing...' : 'Approve' }}
                    </button>
                    <button
                      @click="rejectLink(link)"
                      class="text-red-600 hover:text-red-800 hover:underline"
                      :disabled="processingLink === link.id"
                    >
                      Reject
                    </button>
                  </div>
                  <span v-else-if="link.status === 'approved'" class="text-green-600 text-xs">✓ Approved</span>
                  <span v-else-if="link.status === 'rejected'" class="text-red-600 text-xs">✗ Rejected</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <!-- End External Links Tab -->
      </div>

      <!-- Start Chat Modal (WhatsApp-style) -->
      <div
        v-if="showSendMessageModal"
        class="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center"
        @click.self="showSendMessageModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full h-[90vh] max-h-[700px] overflow-hidden flex flex-col">
          <!-- Header -->
          <div class="bg-primary-600 text-white px-4 py-3 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold">Start New Chat</h2>
              <p class="text-xs text-primary-100">Select a recipient</p>
            </div>
            <button
              @click="showSendMessageModal = false"
              class="text-white hover:text-gray-200 text-xl"
            >
              ✕
            </button>
          </div>

          <!-- Search/Filter -->
          <div class="px-4 py-3 bg-white border-b">
            <input
              v-model="recipientSearch"
              type="text"
              placeholder="Search recipients..."
              class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <!-- Recipients List -->
          <div class="flex-1 overflow-y-auto">
            <div v-if="loadingRecipientsForModal" class="flex items-center justify-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>

            <div v-else-if="filteredRecipients.length === 0" class="text-center py-12 text-gray-500">
              <div class="text-4xl mb-4">👤</div>
              <p>{{ recipientSearch ? 'No recipients found' : 'No recipients available' }}</p>
            </div>

            <div v-else class="divide-y divide-gray-200">
              <div
                v-for="recipient in filteredRecipients"
                :key="recipient.id"
                @click="selectRecipient(recipient)"
                class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors active:bg-gray-100 flex items-center gap-3"
              >
                <!-- Avatar -->
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold text-lg">
                    {{ getRecipientInitials(recipient) }}
                  </div>
                </div>

                <!-- Recipient Info -->
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 truncate">
                    {{ recipient.username || recipient.email }}
                  </div>
                  <div class="text-sm text-gray-500 capitalize">
                    {{ recipient.role || 'User' }}
                  </div>
                </div>

                <!-- Arrow -->
                <div class="flex-shrink-0 text-gray-400">
                  →
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Initial Message Modal (after selecting recipient) -->
      <div
        v-if="showInitialMessageModal && selectedRecipient"
        class="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center"
        @click.self="showInitialMessageModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full h-[90vh] max-h-[700px] overflow-hidden flex flex-col">
          <!-- Header -->
          <div class="bg-primary-600 text-white px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <button @click="showInitialMessageModal = false" class="text-white hover:text-gray-200 mr-2">
                ←
              </button>
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold">
                  {{ getRecipientInitials(selectedRecipient) }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <h2 class="font-semibold truncate">{{ selectedRecipient.username || selectedRecipient.email }}</h2>
                <p class="text-xs text-primary-100 capitalize">{{ selectedRecipient.role || 'User' }}</p>
              </div>
            </div>
          </div>

          <!-- Message Input Area -->
          <div class="flex-1 overflow-y-auto bg-gray-50 px-4 py-6">
            <div class="text-center text-gray-500 mb-6">
              <div class="text-4xl mb-2">💬</div>
              <p class="text-sm">Start a conversation</p>
              <p class="text-xs mt-1">Type a message to begin</p>
            </div>
          </div>

          <!-- Input Form -->
          <div class="border-t bg-white px-4 py-3">
            <form @submit.prevent="startChatWithMessage" class="space-y-3">
              <div>
                <RichTextEditor
                  v-model="initialMessage"
                  placeholder="Type a message..."
                  toolbar="minimal"
                  height="100px"
                  :allow-images="true"
                  :strip-html="true"
                />
              </div>

              <div v-if="sendMessageError" class="text-xs text-red-600 bg-red-50 p-2 rounded">
                {{ sendMessageError }}
              </div>

              <div class="flex gap-2">
                <button
                  type="button"
                  @click="showInitialMessageModal = false"
                  class="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  :disabled="sendingMessage"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  :disabled="sendingNewMessage"
                >
                  {{ sendingNewMessage ? 'Starting...' : 'Start Chat' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="card p-12">
        <div class="text-center text-gray-500">
          <p>Order not found</p>
        </div>
      </div>
    </template>

    <!-- Order Action Modal for Admin/Superadmin/Support -->
    <OrderActionModal
      v-if="authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport"
      v-model:visible="showActionModal"
      :order="order"
      :selected-action="selectedAction"
      :available-actions="availableActions"
      :available-writers="availableWriters"
      @success="handleActionSuccess"
      @error="handleActionError"
    />
    
    <!-- Tip Writer Modal -->
    <Modal
      v-model:visible="showTipModal"
      title="Tip Writer"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-purple-50 border border-purple-200 rounded-lg p-3 text-sm text-purple-800">
          <p><strong>Show your appreciation!</strong> Tips are a great way to thank your writer for excellent work. You can tip even for closed orders.</p>
        </div>
        
        <div v-if="order && (order.writer || order.writer_id)" class="bg-gray-50 rounded-lg p-3">
          <div class="text-sm text-gray-600">Writer:</div>
          <div class="font-medium text-gray-900 mt-1">
            {{ order.writer?.user?.get_full_name || order.writer?.user?.username || order.writer_username || 'Writer' }}
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Tip Amount <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
            <input
              v-model.number="tipAmount"
              type="number"
              step="0.01"
              min="0.01"
              class="w-full border rounded-lg px-3 pl-8 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              placeholder="0.00"
              required
            />
          </div>
          <p class="text-xs text-gray-500 mt-1">Minimum tip: $0.01</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Payment Method
          </label>
          <select
            v-model="tipPaymentMethod"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          >
            <option value="wallet">Wallet Balance</option>
            <option value="stripe">Credit Card (Stripe)</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason (Optional)
          </label>
          <textarea
            v-model="tipReason"
            rows="3"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            placeholder="Thank you for the excellent work! (optional)"
          ></textarea>
        </div>
        
        <div v-if="tipPaymentMethod === 'wallet'" class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
          <div class="flex justify-between items-center">
            <span class="text-gray-700">Available Balance:</span>
            <span class="font-semibold text-gray-900">${{ walletBalance.toFixed(2) }}</span>
          </div>
          <div v-if="tipAmount && tipAmount > walletBalance" class="mt-2 text-red-600 text-xs">
            ⚠️ Insufficient balance. Please use credit card or add funds to your wallet.
          </div>
        </div>
        
        <div class="flex gap-2 justify-end">
          <button
            @click="showTipModal = false"
            class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            :disabled="tipping"
          >
            Cancel
          </button>
          <button
            @click="submitTip"
            :disabled="tipping || !tipAmount || tipAmount <= 0 || (tipPaymentMethod === 'wallet' && tipAmount > walletBalance)"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            {{ tipping ? 'Processing...' : `Tip $${tipAmount ? tipAmount.toFixed(2) : '0.00'}` }}
          </button>
        </div>
      </div>
    </Modal>
    
    <!-- Revision Request Modal -->
    <Modal
      v-model:visible="showRevisionModal"
      title="Request Revision"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <p><strong>Note:</strong> Please provide specific details about what needs to be revised. This helps the writer make the necessary changes quickly.</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Revision Reason <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="revisionReason"
            rows="6"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Describe what needs to be revised. Be as specific as possible..."
            required
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">Examples: "Add more citations", "Expand section 3", "Fix formatting issues"</p>
        </div>
        
        <div class="flex gap-2 justify-end">
          <button
            @click="showRevisionModal = false"
            class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            :disabled="requestingRevision"
          >
            Cancel
          </button>
          <button
            @click="requestRevision"
            :disabled="requestingRevision || !revisionReason.trim()"
            class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 transition-colors"
          >
            {{ requestingRevision ? 'Submitting...' : 'Submit Revision Request' }}
          </button>
        </div>
      </div>
    </Modal>
    
    <!-- Deadline Extension Request Modal -->
    <Modal
      v-model:visible="showDeadlineExtensionModal"
      title="Request Deadline Extension"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <p><strong>Note:</strong> Please provide a valid reason for the deadline extension. The client will review your request.</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Current Deadline
          </label>
          <input
            :value="formatDateTime(order.writer_deadline || order.deadline)"
            type="text"
            disabled
            class="w-full border rounded-lg px-3 py-2 bg-gray-50 text-gray-600"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            New Requested Deadline <span class="text-red-500">*</span>
          </label>
          <input
            v-model="deadlineExtensionForm.requested_deadline"
            type="datetime-local"
            :min="getMinDeadlineDate()"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            required
          />
          <p class="text-xs text-gray-500 mt-1">Select a date and time for the new deadline</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="deadlineExtensionForm.reason"
            rows="4"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            placeholder="Explain why you need a deadline extension..."
            required
          ></textarea>
        </div>
        
        <div class="flex gap-2 justify-end">
          <button
            @click="closeDeadlineExtensionModal"
            class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            :disabled="submittingDeadlineExtension"
          >
            Cancel
          </button>
          <button
            @click="submitDeadlineExtension"
            :disabled="submittingDeadlineExtension || !deadlineExtensionForm.reason.trim() || !deadlineExtensionForm.requested_deadline"
            class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 transition-colors"
          >
            {{ submittingDeadlineExtension ? 'Submitting...' : 'Submit Request' }}
          </button>
        </div>
      </div>
    </Modal>
    
    <!-- Order Request Modal -->
    <Modal
      v-model:visible="showOrderRequestModal"
      title="Request Order"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h3 class="font-semibold text-gray-900 mb-2">Order #{{ order?.id }}</h3>
          <p class="text-sm text-gray-600">{{ order?.topic }}</p>
          <div class="mt-2 text-sm text-gray-500">
            <span>{{ order?.service_type || order?.type_of_work?.name || 'N/A' }}</span>
            <span class="mx-2">•</span>
            <span>{{ (order?.pages || order?.number_of_pages || 0) }} pages</span>
            <span class="mx-2">•</span>
            <span class="font-semibold text-green-600">${{ parseFloat(order?.total_cost || order?.price || 0).toFixed(2) }}</span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason for Request <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="orderRequestReason"
            rows="4"
            placeholder="Please explain why you're interested in this order (e.g., your expertise in this topic, availability, previous experience with similar orders, etc.)"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            required
          ></textarea>
          <p class="mt-1 text-xs text-gray-500">
            This helps admins make informed assignment decisions.
          </p>
        </div>
      </div>
      
      <template #footer>
        <button
          @click="closeOrderRequestModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="submitOrderRequest"
          :disabled="!orderRequestReason || !orderRequestReason.trim() || requestingOrder"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ requestingOrder ? 'Submitting...' : 'Submit Request' }}
        </button>
      </template>
    </Modal>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirmShow"
      :title="confirmTitle"
      :message="confirmMessage"
      :details="confirmDetails"
      :variant="confirmVariant"
      :confirm-text="confirmConfirmText"
      :cancel-text="confirmCancelText"
      :icon="confirmIcon"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />

    <!-- Input Modal -->
    <InputModal
      v-model:show="inputModalShow"
      :title="inputModalTitle"
      :message="inputModalMessage"
      :label="inputModalLabel"
      :placeholder="inputModalPlaceholder"
      :hint="inputModalHint"
      :multiline="inputModalMultiline"
      :rows="inputModalRows"
      :required="inputModalRequired"
      :default-value="inputModalDefaultValue"
      :confirm-text="inputModalConfirmText"
      :cancel-text="inputModalCancelText"
      @submit="inputModal.onSubmit"
      @cancel="inputModal.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ordersAPI from '@/api/orders'
import orderFilesAPI from '@/api/order-files'
import communicationsAPI from '@/api/communications'
import walletAPI from '@/api/wallet'
import reviewsAPI from '@/api/reviews'
import Modal from '@/components/common/Modal.vue'
import PaymentCheckout from '@/components/payments/PaymentCheckout.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import ReviewSubmission from '@/components/reviews/ReviewSubmission.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'
import OnlineStatusIndicator from '@/components/common/OnlineStatusIndicator.vue'
import UserDisplayName from '@/components/common/UserDisplayName.vue'
import ProgressBar from '@/components/orders/ProgressBar.vue'
import ProgressReportForm from '@/components/orders/ProgressReportForm.vue'
import ProgressHistory from '@/components/orders/ProgressHistory.vue'
import OrderMessagesTabbed from '@/components/order/OrderMessagesTabbed.vue'
import { useOnlineStatus } from '@/composables/useOnlineStatus'
import progressAPI from '@/api/progress'
import OrderActionModal from '@/components/order/OrderActionModal.vue'
import usersAPI from '@/api/users'
import { getErrorMessage, getSuccessMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useInputModal } from '@/composables/useInputModal'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import EnhancedOrderStatus from '@/components/client/EnhancedOrderStatus.vue'
import InputModal from '@/components/common/InputModal.vue'
import draftRequestsAPI from '@/api/draft-requests'
import writerManagementAPI from '@/api/writer-management'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import writerDashboardAPI from '@/api/writer-dashboard'
import { loadUnreadMessageCount } from '@/utils/messageUtils'

const route = useRoute()
const authStore = useAuthStore()
const { success: showSuccessToast, error: showErrorToast } = useToast()
const confirm = useConfirmDialog()
const inputModal = useInputModal()

// Create local refs for v-model binding (Vue 3 v-model requires refs, not computed)
const confirmShow = ref(false)
const inputModalShow = ref(false)

// Sync local refs with composable refs
watch(() => confirm.show.value, (newVal) => {
  confirmShow.value = newVal
}, { immediate: true })
watch(confirmShow, (newVal) => {
  if (confirm.show.value !== newVal) {
    confirm.show.value = newVal
  }
})

watch(() => inputModal.show.value, (newVal) => {
  inputModalShow.value = newVal
}, { immediate: true })
watch(inputModalShow, (newVal) => {
  if (inputModal.show.value !== newVal) {
    inputModal.show.value = newVal
  }
})

const order = ref(null)
const loading = ref(true)
const activeTab = ref('overview')
const unreadMessageCount = ref(0)
let unreadMessageInterval = null

// Tabs configuration
const tabs = [
  { id: 'overview', label: 'Overview', icon: '📋' },
  { id: 'enhanced-status', label: 'Enhanced Status', icon: '📈' },
  { id: 'progress', label: 'Progress', icon: '📊' },
  { id: 'messages', label: 'Messages', icon: '💬' },
  { id: 'files', label: 'Files', icon: '📁' },
  { id: 'draft-requests', label: 'Draft Requests', icon: '📝' },
  { id: 'links', label: 'External Links', icon: '🔗' }
]
const loadingFiles = ref(false)
const loadingLinks = ref(false)
const showSendMessageModal = ref(false)
const showInitialMessageModal = ref(false)
const availableRecipients = ref([])
const loadingRecipientsForModal = ref(false)
const sendingNewMessage = ref(false)
const sendMessageError = ref('')
const recipientSearch = ref('')
const selectedRecipient = ref(null)
const initialMessage = ref('')
const createdThreadId = ref(null)

// Inline messaging state
const threads = ref([])
const loadingThreads = ref(false)
const expandedThreads = ref({})
const threadMessages = ref({})
const loadingMessages = ref({})
const threadPagination = ref({})
const threadRecipients = ref({})
const loadingRecipientsForThread = ref({})
const sendingMessageToThreads = ref({})
const threadMessageForms = ref({})
const threadSelectedFiles = ref({})
const threadFileInputs = ref({})
const threadErrors = ref({})
const messageContainers = ref({})
const pollingIntervals = ref({})
const lastMessageIds = ref({})
const deletingMessage = ref({})
const deletingThread = ref({})

// Order actions state
const processingAction = ref(false)
const actionError = ref('')
const actionSuccess = ref('')
const showPaymentModal = ref(false)
const walletBalance = ref(0)

// Order Action Modal state (for admin/superadmin/support)
const showActionModal = ref(false)
const selectedAction = ref(null)
const availableActions = ref([])
const availableWriters = ref([])

// Draft Request state
const draftRequests = ref([])
const loadingDraftRequests = ref(false)
const draftEligibility = ref(null)
const loadingDraftEligibility = ref(false)
const showDraftRequestModal = ref(false)
const draftRequestForm = ref({ message: '' })
const uploadingDraft = ref({})
const draftSelectedFiles = ref({})
const draftFileDescriptions = ref({})
const draftFileInputs = ref({})

const isAdmin = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'superadmin'
})

const userRole = computed(() => authStore.user?.role)
const userId = computed(() => authStore.user?.id)

// Unwrap composable refs for component props (computed ensures proper reactivity and type safety)
const confirmTitle = computed(() => confirm.title.value)
const confirmMessage = computed(() => confirm.message.value)
const confirmDetails = computed(() => confirm.details.value)
const confirmVariant = computed(() => confirm.variant.value)
const confirmConfirmText = computed(() => confirm.confirmText.value)
const confirmCancelText = computed(() => confirm.cancelText.value)
const confirmIcon = computed(() => confirm.icon.value)

const inputModalTitle = computed(() => inputModal.title.value)
const inputModalMessage = computed(() => inputModal.message.value)
const inputModalLabel = computed(() => inputModal.label.value)
const inputModalPlaceholder = computed(() => inputModal.placeholder.value)
const inputModalHint = computed(() => inputModal.hint.value)
const inputModalMultiline = computed(() => inputModal.multiline.value)
const inputModalRows = computed(() => inputModal.rows.value)
const inputModalRequired = computed(() => inputModal.required.value)
const inputModalDefaultValue = computed(() => inputModal.defaultValue.value)
const inputModalConfirmText = computed(() => inputModal.confirmText.value)
const inputModalCancelText = computed(() => inputModal.cancelText.value)

// Order action permissions
const canSubmitOrder = computed(() => {
  if (!order.value) return false
  const status = order.value.status?.toLowerCase()
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value
  // Writer can only submit when a Final Paper file has been uploaded
  return isWriter && isAssignedWriter && hasFinalPaperFile.value && ['in_progress', 'assigned', 'draft'].includes(status)
})

const canCompleteOrder = computed(() => {
  if (!order.value) return false
  const status = order.value.status?.toLowerCase()
  const isClient = userRole.value === 'client'
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  return (isClient && isOrderClient && status === 'submitted') || (isAdmin.value && ['submitted', 'in_progress'].includes(status))
})

const canCancelOrder = computed(() => {
  if (!order.value) return false
  const status = order.value.status?.toLowerCase()
  const isClient = userRole.value === 'client'
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  return (isClient && isOrderClient && !['completed', 'cancelled'].includes(status)) || 
         (isAdmin.value && !['completed', 'cancelled'].includes(status))
})

const canReopenOrder = computed(() => {
  if (!order.value) return false
  const status = order.value.status?.toLowerCase()
  return isAdmin.value && ['completed', 'cancelled'].includes(status)
})

const canPayOrder = computed(() => {
  if (!order.value) return false
  const isClient = userRole.value === 'client'
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  return isClient && isOrderClient && !order.value.is_paid
})

const canSubmitReview = computed(() => {
  if (!order.value) return false
  const isClient = userRole.value === 'client'
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  return isClient && isOrderClient && order.value.status === 'completed'
})

const canRequestRevision = computed(() => {
  if (!order.value) return false
  const isClient = userRole.value === 'client'
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can request revision if order is completed, submitted, or approved
  return isClient && isOrderClient && ['completed', 'submitted', 'approved'].includes(status)
})

const canTipWriter = computed(() => {
  if (!order.value) return false
  const isClient = userRole.value === 'client'
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  const hasWriter = order.value.writer_id || order.value.writer?.id
  const status = order.value.status?.toLowerCase()
  // Can tip for completed, submitted, approved, or closed orders
  return isClient && isOrderClient && hasWriter && ['completed', 'submitted', 'approved', 'closed'].includes(status)
})

const canRequestDeadlineExtension = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can request extension for in_progress, assigned, or draft orders
  return isWriter && isAssignedWriter && ['in_progress', 'assigned', 'draft'].includes(status)
})

const canRequestHold = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can request hold for in_progress, assigned, or draft orders
  return isWriter && isAssignedWriter && ['in_progress', 'assigned', 'draft'].includes(status)
})

const canStartOrder = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can start order when it's available or reassigned
  return isWriter && isAssignedWriter && ['available', 'reassigned'].includes(status)
})

const canStartRevision = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can start revision when revision is requested
  return isWriter && isAssignedWriter && status === 'revision_requested'
})

const revisionEligibility = computed(() => {
  const rev = order.value?.revision_eligibility
  if (!rev) return null
  return rev
})

const canResumeOrder = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can resume order when it's on hold
  return isWriter && isAssignedWriter && status === 'on_hold'
})

const canTakeOrder = computed(() => {
  if (!order.value || !authStore.isWriter) return false
  const status = order.value.status?.toLowerCase()
  const isAssigned = order.value.writer_id || order.value.assigned_writer_id || order.value.assigned_writer?.id
  // Can take order when it's available and not yet assigned
  return status === 'available' && !isAssigned && !isOrderRequested.value
})

const canRequestOrder = computed(() => {
  if (!order.value || !authStore.isWriter) return false
  const status = order.value.status?.toLowerCase()
  const isAssigned = order.value.writer_id || order.value.assigned_writer_id || order.value.assigned_writer?.id
  // Can request order when it's available and not yet assigned
  return status === 'available' && !isAssigned
})

const hasDownloadableFiles = computed(() => {
  if (!files.value || files.value.length === 0) return false
  return files.value.some(f => f.is_downloadable && canDownloadFile(f))
})

// Check if there is at least one file explicitly marked as Final Paper
const hasFinalPaperFile = computed(() => {
  if (!files.value || files.value.length === 0) return false
  return files.value.some(f => f.is_final_paper)
})

// Get the latest Final Paper file (used for prominent download button)
const finalPaperFile = computed(() => {
  if (!files.value || files.value.length === 0) return null
  const finals = files.value.filter(f => f.is_final_paper)
  if (!finals.length) return null
  // Prefer highest version, then most recent created_at
  return finals
    .slice()
    .sort((a, b) => {
      const av = a.version || 0
      const bv = b.version || 0
      if (av !== bv) return bv - av
      return new Date(b.created_at) - new Date(a.created_at)
    })[0]
})

// Last activity indicator
const sanitizePreview = (text, maxLength = 140) => {
  if (!text) return ''
  const stripped = text.replace(/<[^>]*>/g, '').trim()
  if (stripped.length <= maxLength) return stripped
  return `${stripped.substring(0, maxLength).trim()}…`
}

const lastActivity = computed(() => {
  if (!order.value) return null
  
  const activities = []
  
  // Latest message, prefer thread metadata to avoid extra fetch
  if (threads.value && threads.value.length > 0) {
    let latestMessageEntry = null
    
    threads.value.forEach(thread => {
      const threadMessagesList = threadMessages.value[thread.id]
      const latestMessage = thread.last_message || (threadMessagesList && threadMessagesList[0])
      const messageTimestamp = latestMessage?.created_at || latestMessage?.timestamp || thread.updated_at
      
      if (!messageTimestamp || (!latestMessage && !thread.last_message)) {
        return
      }
      
      const descriptionSource = latestMessage?.preview || latestMessage?.message || thread.last_message?.preview || ''
      const description = sanitizePreview(descriptionSource) || `Message update in thread`
      const sender = latestMessage?.sender_display_name || latestMessage?.sender_name || latestMessage?.sender || thread.last_message?.sender_display_name
      
      const candidate = {
        type: 'message',
        timestamp: messageTimestamp,
        description: sender ? `${description} — ${sender}` : description,
        id: latestMessage?.id || thread.id,
        meta: {
          threadId: thread.id,
          sender
        }
      }
      
      if (!latestMessageEntry || new Date(messageTimestamp) > new Date(latestMessageEntry.timestamp)) {
        latestMessageEntry = candidate
      }
    })
    
    if (latestMessageEntry) {
      activities.push(latestMessageEntry)
    }
  }
  
  // Latest file upload
  if (files.value && files.value.length > 0) {
    const latestFile = files.value.reduce((latest, file) => {
      if (!file.created_at) return latest
      if (!latest) return file
      return new Date(file.created_at) > new Date(latest.created_at) ? file : latest
    }, null)
    
    if (latestFile) {
      activities.push({
        type: 'file',
        timestamp: latestFile.created_at,
        description: `${latestFile.category?.name || 'File'} • ${latestFile.file_name || latestFile.file?.name || 'Uploaded file'}`,
        id: latestFile.id
      })
    }
  }
  
  if (activities.length === 0) return null
  activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  return activities[0]
})

// Comprehensive status label mapping (covers all OrderStatus enum values)
const statusLabelMap = {
  // Initial states
  created: 'Order Created',
  pending: 'Pending',
  unpaid: 'Unpaid',
  
  // Assignment states
  available: 'Available for Writers',
  assigned: 'Writer Assigned',
  pending_writer_assignment: 'Pending Writer Assignment',
  pending_preferred: 'Pending Preferred Writer',
  reassigned: 'Reassigned',
  
  // Active work states
  in_progress: 'In Progress',
  draft: 'Draft Saved',
  on_hold: 'On Hold',
  under_editing: 'Under Editing',
  critical: 'Critical',
  late: 'Late',
  
  // Submission and review states
  submitted: 'Submitted for Review',
  in_review: 'In Review',
  under_review: 'Under Review',
  reviewed: 'Reviewed',
  rated: 'Rated',
  
  // Revision states
  revision_requested: 'Revision Requested',
  revision_in_progress: 'Revision In Progress',
  on_revision: 'On Revision',
  revised: 'Revision Submitted',
  
  // Completion states
  approved: 'Approved',
  completed: 'Completed',
  closed: 'Closed',
  archived: 'Archived',
  
  // Cancellation/refund states
  cancelled: 'Cancelled',
  refunded: 'Refunded',
  disputed: 'Disputed',
  
  // System states
  expired: 'Expired',
  re_opened: 'Reopened',
  rejected: 'Rejected'
}

// Status icon mapping
const statusIconMap = {
  created: '🟢',
  pending: '⏳',
  unpaid: '💳',
  available: '📋',
  assigned: '👤',
  pending_writer_assignment: '⏳',
  pending_preferred: '⭐',
  reassigned: '🔄',
  in_progress: '⚙️',
  draft: '📝',
  on_hold: '⏸️',
  under_editing: '✏️',
  critical: '🚨',
  late: '⏰',
  submitted: '📤',
  in_review: '🔍',
  under_review: '🔍',
  reviewed: '✅',
  rated: '⭐',
  revision_requested: '🔁',
  revision_in_progress: '✏️',
  on_revision: '🔁',
  revised: '✅',
  approved: '🎉',
  completed: '🏁',
  closed: '🔒',
  archived: '📦',
  cancelled: '✖️',
  refunded: '💰',
  disputed: '⚠️',
  expired: '⏱️',
  re_opened: '🔓',
  rejected: '❌'
}

const formatStatusLabel = (value) => {
  if (!value) return 'Status Update'
  return value
    .toString()
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

/**
 * Stable Status Timeline Logic
 * 
 * Priority order:
 * 1. OrderTransitionLog entries (most reliable, authoritative source)
 * 2. Milestone timestamps (fallback for legacy data or missing transitions)
 * 3. Created timestamp (always included)
 * 
 * Deduplication: Entries with same status and timestamp (within 1 second) are merged
 */
const statusTimeline = computed(() => {
  if (!order.value) return []

  const entries = []
  const seenEntries = new Set() // For deduplication: "status|timestamp"
  
  /**
   * Add entry with deduplication
   * @param {string} key - Unique identifier
   * @param {string} status - Order status
   * @param {string|Date} timestamp - Timestamp
   * @param {object} extra - Additional metadata (label, description, icon)
   */
  const pushEntry = (key, status, timestamp, extra = {}) => {
    if (!timestamp) return
    
    // Normalize timestamp to ISO string for comparison
    const timestampDate = new Date(timestamp)
    if (isNaN(timestampDate.getTime())) return // Invalid date
    
    const normalizedStatus = status?.toLowerCase()?.trim()
    if (!normalizedStatus) return
    
    // Create deduplication key: status + timestamp (rounded to nearest second)
    const timestampKey = Math.floor(timestampDate.getTime() / 1000)
    const dedupeKey = `${normalizedStatus}|${timestampKey}`
    
    // Skip if we've already seen this status at this timestamp
    if (seenEntries.has(dedupeKey)) return
    seenEntries.add(dedupeKey)
    
    entries.push({
      key,
      status: normalizedStatus,
      label: extra.label || statusLabelMap[normalizedStatus] || formatStatusLabel(status),
      timestamp: timestampDate.toISOString(),
      relativeTime: formatRelativeTime(timestamp),
      description: extra.description || null,
      icon: extra.icon || statusIconMap[normalizedStatus] || '•',
      source: extra.source || 'unknown' // Track data source for debugging
    })
  }

  // 1. Always include creation timestamp
  if (order.value.created_at) {
    pushEntry('created', 'created', order.value.created_at, {
      description: 'Order placed',
      source: 'created_at'
    })
  }

  // 2. Process transition logs (primary source of truth)
  const transitionLogs = Array.isArray(order.value.transitions) ? order.value.transitions : []
  transitionLogs.forEach(log => {
    if (!log || !log.timestamp) return
    
    const newStatus = (log.new_status || log.action || '').toLowerCase().trim()
    if (!newStatus) return
    
    const descriptionParts = []
    
    // Add action context if available
    if (log.action && log.action !== newStatus) {
      descriptionParts.push(formatStatusLabel(log.action))
    }
    
    // Add automatic transition indicator
    if (log.is_automatic) {
      descriptionParts.push('Automatic transition')
    }
    
    // Add user context if available
    if (log.user) {
      const userName = log.user?.username || log.user?.full_name || log.user?.email || 'System'
      descriptionParts.push(`by ${userName}`)
    }
    
    // Add old status context if available
    if (log.old_status && log.old_status.toLowerCase() !== newStatus) {
      descriptionParts.push(`from ${formatStatusLabel(log.old_status)}`)
    }
    
    pushEntry(`transition-${log.id || Date.now()}`, newStatus, log.timestamp, {
      description: descriptionParts.length > 0 ? descriptionParts.join(' • ') : null,
      source: 'transition_log'
    })
  })

  // 3. Fallback to milestone timestamps (only if not already covered by transitions)
  // These are checked against seenEntries to avoid duplicates
  const milestoneTimestamps = [
    { 
      key: 'submitted_at', 
      status: 'submitted', 
      timestamp: order.value.submitted_at, 
      description: 'Writer submitted deliverables' 
    },
    { 
      key: 'completed_at', 
      status: 'completed', 
      timestamp: order.value.completed_at, 
      description: 'Order marked as completed' 
    },
    { 
      key: 'approved_at', 
      status: 'approved', 
      timestamp: order.value.approved_at, 
      description: 'Order approved' 
    },
    { 
      key: 'closed_at', 
      status: 'closed', 
      timestamp: order.value.closed_at, 
      description: 'Order closed' 
    },
    { 
      key: 'cancelled_at', 
      status: 'cancelled', 
      timestamp: order.value.cancelled_at, 
      description: 'Order cancelled' 
    }
  ]
  
  milestoneTimestamps.forEach(entry => {
    if (entry.timestamp) {
      pushEntry(entry.key, entry.status, entry.timestamp, { 
        description: entry.description,
        source: 'milestone_timestamp'
      })
    }
  })

  // 4. Include current status if it's not already in the timeline
  // This ensures the timeline always shows the current state
  const currentStatus = order.value.status?.toLowerCase()?.trim()
  if (currentStatus && currentStatus !== 'created') {
    const hasCurrentStatus = entries.some(e => e.status === currentStatus)
    if (!hasCurrentStatus && order.value.updated_at) {
      pushEntry('current_status', currentStatus, order.value.updated_at, {
        description: 'Current status',
        source: 'current_status'
      })
    }
  }

  // 5. Sort by timestamp (chronological order)
  const sorted = entries.sort((a, b) => {
    const dateA = new Date(a.timestamp)
    const dateB = new Date(b.timestamp)
    return dateA.getTime() - dateB.getTime()
  })

  return sorted
})

const outstandingBalance = computed(() => parseAmount(paymentSummary.value?.balance_due))
const hasOutstandingBalance = computed(() => outstandingBalance.value > 0.01)
const paymentTransactions = computed(() => paymentSummary.value?.payments || [])
const paymentInstallments = computed(() => paymentSummary.value?.installments || [])

const hasReview = ref(false)
const orderReview = ref(null)
const showRevisionModal = ref(false)
const revisionReason = ref('')
const requestingRevision = ref(false)
const showTipModal = ref(false)
const tipAmount = ref(null)
const tipReason = ref('')
const tipPaymentMethod = ref('wallet')
const tipping = ref(false)
const showDeadlineExtensionModal = ref(false)
const showHoldRequestModal = ref(false)
const submittingDeadlineExtension = ref(false)
const deadlineExtensionForm = ref({
  requested_deadline: '',
  reason: ''
})
const showOrderRequestModal = ref(false)
const orderRequestReason = ref('')
const takingOrder = ref(false)
const requestingOrder = ref(false)
const isOrderRequested = ref(false)
const canTakeOrders = ref(true)
const takesEnabled = ref(false)
const writerProfile = ref(null)
const activeAssignmentCount = ref(0)
const paymentSummary = ref(null)
const loadingPaymentSummary = ref(false)
const paymentSummaryError = ref('')

// Progress state
const latestProgressPercentage = ref(0)
const latestProgressUpdate = ref(null)
const progressHistoryRef = ref(null)

const canSubmitProgress = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  return isWriter && isAssignedWriter && ['in_progress', 'assigned'].includes(status)
})

const loadLatestProgress = async () => {
  if (!order.value) return
  
  try {
    const response = await progressAPI.getLatestProgress(order.value.id)
    if (response.data.latest_report) {
      latestProgressPercentage.value = response.data.progress_percentage || 0
      latestProgressUpdate.value = response.data.latest_report.timestamp
    } else {
      latestProgressPercentage.value = 0
      latestProgressUpdate.value = null
    }
  } catch (error) {
    console.error('Failed to load latest progress:', error)
    latestProgressPercentage.value = 0
    latestProgressUpdate.value = null
  }
}

const handleProgressSubmitted = async (data) => {
  actionSuccess.value = 'Progress report submitted successfully!'
  actionError.value = ''
  await loadLatestProgress()
  if (progressHistoryRef.value) {
    progressHistoryRef.value.refresh()
  }
}

const handleProgressError = (error) => {
  const errorMsg = getErrorMessage(error, 'Failed to submit progress report', 'Unable to submit progress report')
  actionError.value = errorMsg
  actionSuccess.value = ''
  showErrorToast(errorMsg)
}

// Order action functions
const submitOrder = async () => {
  if (!order.value) return
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.executeAction(order.value.id, 'submit_order')
    const message = getSuccessMessage('submit', 'order')
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to submit order', 'Unable to submit order')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const startOrder = async () => {
  if (!order.value) return
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.executeAction(order.value.id, 'start_order')
    const message = 'Order started successfully'
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to start order', 'Unable to start order')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const startRevision = async () => {
  if (!order.value) return
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.executeAction(order.value.id, 'start_revision')
    const message = 'Revision started successfully'
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to start revision', 'Unable to start revision')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const resumeOrder = async () => {
  if (!order.value) return
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.resumeOrder(order.value.id)
    const message = 'Order resumed successfully'
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to resume order', 'Unable to resume order')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const completeOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    'Are you sure you want to mark this order as complete?',
    'Complete Order',
    {
      variant: 'default',
      confirmText: 'Complete Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.completeOrder(order.value.id)
    const message = getSuccessMessage('complete', 'order')
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to complete order', 'Unable to complete order')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const cancelOrder = async () => {
  if (!order.value) return
  
  // First confirm cancellation
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to cancel Order #${order.value.id}? This action cannot be undone.`,
    'Cancel Order'
  )
  
  if (!confirmed) return
  
  // Then ask for reason (optional)
  const reason = await inputModal.showModal(
    'Please provide a reason for cancellation (optional)',
    'Cancellation Reason',
    {
      label: 'Reason',
      placeholder: 'Enter reason for cancellation...',
      multiline: true,
      rows: 4,
      required: false
    }
  )
  
  if (reason === null) return // User cancelled
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.cancelOrder(order.value.id, reason || '')
    const message = getSuccessMessage('cancel', 'order')
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to cancel order', 'Unable to cancel order')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const reopenOrder = async () => {
  if (!order.value) return
  if (!confirm('Are you sure you want to reopen this order?')) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.reopenOrder(order.value.id)
    const message = 'Order reopened successfully!'
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to reopen order', 'Unable to reopen order')
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Order Action Modal functions (for admin/superadmin/support)
const openActionModal = async (action = null) => {
  if (!order.value) return
  
  selectedAction.value = action
  
  // Load available actions for this order
  try {
    const response = await ordersAPI.getAvailableActions(order.value.id)
    if (response.data && response.data.available_actions) {
      availableActions.value = response.data.available_actions
    }
  } catch (error) {
    console.error('Failed to load available actions:', error)
    availableActions.value = []
  }
  
  // Load writers if needed for assign/reassign
  if ((action === 'assign_order' || action === 'reassign_order') && availableWriters.value.length === 0) {
    try {
      const writersResponse = await usersAPI.list({ role: 'writer', website: order.value.website_id })
      availableWriters.value = writersResponse.data?.results || writersResponse.data || []
    } catch (error) {
      console.error('Failed to load writers:', error)
      availableWriters.value = []
    }
  }
  
  showActionModal.value = true
}

const handleActionSuccess = async (data) => {
  const message = data.message || 'Action completed successfully'
  actionSuccess.value = message
  actionError.value = ''
  showSuccessToast(message)
  await loadOrder()
  
  // Clear success message after 5 seconds
  setTimeout(() => {
    actionSuccess.value = ''
  }, 5000)
}

const handleActionError = (error) => {
  const errorMessage = getErrorMessage(error, 'Failed to execute action', 'Unable to perform action')
  actionError.value = errorMessage
  actionSuccess.value = ''
  showErrorToast(errorMessage)
  
  // Clear error message after 5 seconds
  setTimeout(() => {
    actionError.value = ''
  }, 5000)
}

const files = ref([])
const extraServiceFiles = ref([])
const links = ref([])
const processingLink = ref(null)
const categories = ref([])
const uploadError = ref('')
const uploadSuccess = ref('')
const uploadingFiles = ref(false)
const loadingExtraServiceFiles = ref(false)
const submittingLink = ref(false)
const linkError = ref('')
const linkSuccess = ref('')
const uploadedFiles = ref([])
const uploadForm = ref({
  category: null,
  fileType: 'regular'
})
const linkForm = ref({
  link: '',
  description: '',
})

const loadOrder = async () => {
  loading.value = true
  try {
    const orderId = route.params.id
    const res = await ordersAPI.get(orderId)
    order.value = res.data
    paymentSummary.value = null
    // Load files, links, categories, wallet balance, and review after order is loaded
    await Promise.all([
      loadFiles(),
      loadExtraServiceFiles(),
      loadLinks(),
      loadCategories(),
      loadWalletBalance(),
      loadOrderReview(),
      loadPaymentSummary()
    ])
    
    // Start polling for unread messages every 30 seconds
    if (unreadMessageInterval) {
      clearInterval(unreadMessageInterval)
    }
    unreadMessageInterval = setInterval(async () => {
      if (order.value) {
        try {
          const count = await loadUnreadMessageCount(order.value.id)
          unreadMessageCount.value = count
        } catch (error) {
          // Silently handle errors - function already handles them internally
          unreadMessageCount.value = 0
        }
      }
    }, 30000)
    
    // Load initial unread message count
    if (order.value) {
      try {
        const count = await loadUnreadMessageCount(order.value.id)
        unreadMessageCount.value = count
      } catch (error) {
        // Silently handle errors - function already handles them internally
        unreadMessageCount.value = 0
      }
    }
  } catch (error) {
    console.error('Failed to load order:', error)
  } finally {
    loading.value = false
  }
}

const loadOrderReview = async () => {
  if (!order.value || !canSubmitReview.value) return
  try {
    const res = await reviewsAPI.listOrderReviews({ 
      order: order.value.id,
      client: userId.value
    })
    const reviews = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    if (reviews.length > 0) {
      hasReview.value = true
      orderReview.value = reviews[0]
    } else {
      hasReview.value = false
      orderReview.value = null
    }
  } catch (error) {
    console.error('Failed to load review:', error)
    hasReview.value = false
  }
}

const handleReviewSubmitted = (reviewData) => {
  hasReview.value = true
  orderReview.value = reviewData
  actionSuccess.value = 'Review submitted successfully!'
}

const scrollToReview = () => {
  activeTab.value = 'overview'
  nextTick(() => {
    const reviewSection = document.querySelector('[data-review-section]')
    if (reviewSection) {
      reviewSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

const requestRevision = async () => {
  if (!revisionReason.value.trim()) {
    showErrorToast('Please provide a reason for the revision request')
    return
  }
  
  requestingRevision.value = true
  try {
    await ordersAPI.executeAction(order.value.id, 'request_revision', {
      reason: revisionReason.value
    })
    showSuccessToast('Revision request submitted successfully!')
    showRevisionModal.value = false
    revisionReason.value = ''
    await loadOrder()
  } catch (error) {
    showErrorToast(getErrorMessage(error, 'Failed to request revision', 'Unable to submit revision request'))
  } finally {
    requestingRevision.value = false
  }
}

const submitTip = async () => {
  if (!tipAmount.value || tipAmount.value <= 0) {
    showErrorToast('Please enter a valid tip amount')
    return
  }
  
  if (tipPaymentMethod.value === 'wallet' && tipAmount.value > walletBalance.value) {
    showErrorToast('Insufficient wallet balance. Please use credit card or add funds.')
    return
  }
  
  if (!order.value.writer_id && !order.value.writer?.id) {
    showErrorToast('No writer assigned to this order')
    return
  }
  
  tipping.value = true
  try {
    const writerTipsAPI = (await import('@/api/writer-tips')).default
    await writerTipsAPI.create({
      writer_id: order.value.writer_id || order.value.writer?.id,
      order_id: order.value.id,
      tip_amount: tipAmount.value,
      tip_reason: tipReason.value || '',
      payment_method: tipPaymentMethod.value
    })
    showSuccessToast(`Tip of $${tipAmount.value.toFixed(2)} sent successfully!`)
    showTipModal.value = false
    tipAmount.value = null
    tipReason.value = ''
    tipPaymentMethod.value = 'wallet'
    await loadWalletBalance() // Refresh wallet balance
  } catch (error) {
    showErrorToast(getErrorMessage(error, 'Failed to send tip', 'Unable to process tip'))
  } finally {
    tipping.value = false
  }
}


const loadWalletBalance = async () => {
  if (userRole.value !== 'client') return
  try {
    const res = await walletAPI.getBalance()
    walletBalance.value = parseFloat(res.data.balance || res.data.wallet?.balance || 0)
  } catch (error) {
    console.error('Failed to load wallet balance:', error)
    walletBalance.value = 0
  }
}

const loadPaymentSummary = async () => {
  if (!order.value) return
  loadingPaymentSummary.value = true
  paymentSummaryError.value = ''
  try {
    const res = await ordersAPI.getPaymentSummary(order.value.id)
    paymentSummary.value = res.data
  } catch (error) {
    console.error('Failed to load payment summary:', error)
    paymentSummaryError.value = getErrorMessage(error, 'Failed to load payment summary', 'Unable to load payment summary')
  } finally {
    loadingPaymentSummary.value = false
  }
}

const handlePaymentSuccess = async () => {
  actionSuccess.value = 'Payment processed successfully!'
  showPaymentModal.value = false
  await loadOrder()
  await loadPaymentSummary()
  loadWalletBalance()
}

const handlePaymentError = (error) => {
  actionError.value = error.response?.data?.message || error.response?.data?.detail || 'Payment failed'
}

const loadCategories = async () => {
  if (!order.value) return
  try {
    const websiteId = order.value.website?.id || order.value.website_id
    const res = await orderFilesAPI.listCategories({ website_id: websiteId })
    categories.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load categories:', error)
    categories.value = []
  }
}

const loadFiles = async () => {
  if (!order.value) return
  loadingFiles.value = true
  try {
    const res = await orderFilesAPI.list({ order: order.value.id })
    const rawFiles = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    files.value = rawFiles
      .filter(Boolean)
      .sort((a, b) => {
        const timeA = a?.created_at || a?.updated_at || 0
        const timeB = b?.created_at || b?.updated_at || 0
        return new Date(timeB) - new Date(timeA)
      })
  } catch (error) {
    console.error('Failed to load files:', error)
    files.value = []
    showMessage('Failed to load files: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingFiles.value = false
  }
}

const loadExtraServiceFiles = async () => {
  if (!order.value) return
  loadingExtraServiceFiles.value = true
  try {
    const res = await orderFilesAPI.listExtraServiceFiles({ order: order.value.id })
    extraServiceFiles.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load extra service files:', error)
    extraServiceFiles.value = []
  } finally {
    loadingExtraServiceFiles.value = false
  }
}

// Group files by category (legacy - kept for compatibility)
const filesByCategory = computed(() => {
  const grouped = {}
  
  files.value.forEach(file => {
    const categoryName = file.category_name || 'Uncategorized'
    if (!grouped[categoryName]) {
      grouped[categoryName] = {
        category: categoryName,
        files: []
      }
    }
    grouped[categoryName].files.push(file)
  })
  
  return Object.values(grouped)
})

// Categorize files by uploader role
const staffFiles = computed(() => {
  return files.value.filter(file => {
    const uploaderRole = file.uploaded_by_role || 
                        (file.uploaded_by?.role) || 
                        getUploaderRole(file)
    return ['admin', 'superadmin', 'support', 'editor'].includes(uploaderRole)
  })
})

const clientFiles = computed(() => {
  return files.value.filter(file => {
    const uploaderRole = file.uploaded_by_role || 
                        (file.uploaded_by?.role) || 
                        getUploaderRole(file)
    return uploaderRole === 'client'
  })
})

const writerFiles = computed(() => {
  return files.value.filter(file => {
    const uploaderRole = file.uploaded_by_role || 
                        (file.uploaded_by?.role) || 
                        getUploaderRole(file)
    return uploaderRole === 'writer'
  })
})

const otherFiles = computed(() => {
  return files.value.filter(file => {
    const uploaderRole = file.uploaded_by_role || 
                        (file.uploaded_by?.role) || 
                        getUploaderRole(file)
    return !['admin', 'superadmin', 'support', 'editor', 'client', 'writer'].includes(uploaderRole)
  })
})

// Helper function to determine uploader role from file data
const getUploaderRole = (file) => {
  // Check if uploaded_by is an object with role
  if (file.uploaded_by && typeof file.uploaded_by === 'object' && file.uploaded_by.role) {
    return file.uploaded_by.role
  }
  // Check if uploaded_by_id matches order participants
  if (order.value) {
    if (order.value.client_id && file.uploaded_by_id === order.value.client_id) {
      return 'client'
    }
    if (order.value.writer_id && file.uploaded_by_id === order.value.writer_id) {
      return 'writer'
    }
  }
  // Default: try to infer from username or other fields
  // If we can't determine, return null (will be categorized as "other")
  return null
}

// Categorize threads by participant types
const clientWriterThreads = computed(() => {
  return threads.value.filter(thread => {
    // Check if thread has both client and writer (and no staff)
    const participants = thread.participants || []
    
    // Extract roles from participants (handle both object and ID formats)
    const participantRoles = participants.map(p => {
      if (typeof p === 'object' && p !== null) {
        return p.role
      }
      return null
    }).filter(Boolean)
    
    // Also check by ID matching
    const participantIds = participants.map(p => {
      if (typeof p === 'object' && p !== null) {
        return p.id
      }
      return p
    })
    
    const hasClient = participantRoles.includes('client') || 
                     (order.value?.client_id && participantIds.includes(order.value.client_id))
    const hasWriter = participantRoles.includes('writer') || 
                     (order.value?.writer_id && participantIds.includes(order.value.writer_id))
    const hasStaff = participantRoles.some(r => ['admin', 'superadmin', 'support', 'editor'].includes(r))
    
    // Client-Writer thread: has both client and writer, but no staff
    return hasClient && hasWriter && !hasStaff
  })
})

const staffClientThreads = computed(() => {
  return threads.value.filter(thread => {
    // Check if thread has staff members
    const participants = thread.participants || []
    
    // Extract roles from participants
    const participantRoles = participants.map(p => {
      if (typeof p === 'object' && p !== null) {
        return p.role
      }
      return null
    }).filter(Boolean)
    
    const hasStaff = participantRoles.some(r => ['admin', 'superadmin', 'support', 'editor'].includes(r))
    
    // Staff-Client thread: has staff members (may also have client/writer)
    return hasStaff
  })
})

// Helper function to get thread title
const getThreadTitle = (thread) => {
  if (thread.subject) return thread.subject
  if (thread.participants && thread.participants.length > 0) {
    const participantNames = thread.participants
      .filter(p => {
        const id = p.id || p
        return id !== authStore.user?.id
      })
      .map(p => {
        if (typeof p === 'object') {
          return p.username || p.email || `User #${p.id || p}`
        }
        return `User #${p}`
      })
      .slice(0, 2)
    if (participantNames.length > 0) {
      return participantNames.join(', ')
    }
  }
  return `Thread #${thread.id}`
}

const getCategoryById = (categoryId) => {
  if (!categoryId) return null
  return categories.value.find(c => c.id === categoryId)
}

const canDownloadFile = (file) => {
  if (!file || !order.value) return false
  
  // Admins, editors, support can always download
  if (isAdmin.value || userRole.value === 'editor' || userRole.value === 'support') {
    return true
  }
  
  // Check if file is downloadable
  if (!file.is_downloadable) {
    return false
  }
  
  // Check if it's a final draft and payment is required
  const category = getCategoryById(file.category)
  if (category?.is_final_draft) {
    // Final drafts require payment
    return order.value.is_paid || false
  }
  
  return true
}

const canDeleteFile = (file) => {
  if (!file) return false
  // Users can request deletion of files they uploaded, or admins can delete any
  const isUploader = file.uploaded_by === userId.value || file.uploaded_by_id === userId.value
  return isUploader || isAdmin.value
}

const downloadFile = async (file) => {
  try {
    const url = getFileUrl(file)
    window.open(url, '_blank')
  } catch (error) {
    showMessage('Failed to download file: ' + (error.response?.data?.detail || error.message), false)
  }
}

const downloadExtraServiceFile = async (file) => {
  try {
    const url = `/api/v1/order-files/extra-service-files/${file.id}/download/`
    window.open(url, '_blank')
  } catch (error) {
    showMessage('Failed to download file: ' + (error.response?.data?.detail || error.message), false)
  }
}

const requestFileDeletion = async (file) => {
  if (!confirm(`Request deletion of "${file.file_name}"?\n\nThis will send a deletion request to administrators.`)) {
    return
  }
  
  try {
    await orderFilesAPI.createDeletionRequest({
      file: file.id,
      reason: prompt('Reason for deletion (optional):') || ''
    })
    showMessage('Deletion request submitted successfully', true)
  } catch (error) {
    showMessage('Failed to submit deletion request: ' + (error.response?.data?.detail || error.message), false)
  }
}

const uploadSelectedFiles = async () => {
  if (uploadedFiles.value.length === 0 || !order.value) return
  
  uploadingFiles.value = true
  uploadError.value = ''
  uploadSuccess.value = ''
  
  // Store file type before clearing form
  const fileType = uploadForm.value.fileType
  
  try {
    const uploadPromises = uploadedFiles.value.map(async (fileObj) => {
      const formData = new FormData()
      formData.append('file', fileObj.file || fileObj)
      formData.append('order', order.value.id)
      if (uploadForm.value.category) {
        formData.append('category', uploadForm.value.category)
      }
      
      if (fileType === 'extra_service') {
        return await orderFilesAPI.uploadExtraServiceFile(formData)
      } else {
        return await orderFilesAPI.upload(formData)
      }
    })
    
    await Promise.all(uploadPromises)
    uploadSuccess.value = `Successfully uploaded ${uploadedFiles.value.length} file(s)!`
    
    // Clear form
    uploadedFiles.value = []
    uploadForm.value.category = null
    uploadForm.value.fileType = 'regular'
    
    // Reload files based on what was uploaded
    await loadFiles()
    if (fileType === 'extra_service') {
      await loadExtraServiceFiles()
    }
    
    setTimeout(() => {
      uploadSuccess.value = ''
    }, 5000)
  } catch (error) {
    uploadError.value = 'Failed to upload files: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => {
      uploadError.value = ''
    }, 5000)
  } finally {
    uploadingFiles.value = false
  }
}

const handleFileUpload = (fileObj) => {
  // File selected, will be uploaded when user clicks "Upload" button
  // This is handled by uploadSelectedFiles
}

const clearUploadForm = () => {
  uploadedFiles.value = []
  uploadForm.value.category = null
  uploadForm.value.fileType = 'regular'
  uploadError.value = ''
  uploadSuccess.value = ''
}

const showMessage = (msg, success) => {
  if (success) {
    uploadSuccess.value = msg
    setTimeout(() => { uploadSuccess.value = '' }, 5000)
  } else {
    uploadError.value = msg
    setTimeout(() => { uploadError.value = '' }, 5000)
  }
}

const loadLinks = async () => {
  if (!order.value) return
  loadingLinks.value = true
  try {
    const res = await orderFilesAPI.listExternalLinks({ order: order.value.id })
    links.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load links:', error)
    links.value = []
  } finally {
    loadingLinks.value = false
  }
}

const getFileUrl = (file) => {
  // Construct file download URL
  return `/api/v1/order-files/order-files/${file.id}/download/`
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const toggleFileDownload = async (file) => {
  try {
    await orderFilesAPI.toggleDownload(file.id)
    await loadFiles() // Reload files to get updated status
  } catch (error) {
    console.error('Failed to toggle file download:', error)
    alert('Failed to update file download status')
  }
}

const approveLink = async (link) => {
  processingLink.value = link.id
  try {
    await orderFilesAPI.approveExternalLink(link.id)
    await loadLinks() // Reload links to get updated status
  } catch (error) {
    console.error('Failed to approve link:', error)
    alert('Failed to approve link')
  } finally {
    processingLink.value = null
  }
}

const rejectLink = async (link) => {
  if (!confirm(`Reject this link?\n\n${link.link}`)) return
  processingLink.value = link.id
  try {
    await orderFilesAPI.rejectExternalLink(link.id)
    await loadLinks() // Reload links to get updated status
  } catch (error) {
    console.error('Failed to reject link:', error)
    alert('Failed to reject link')
  } finally {
    processingLink.value = null
  }
}

const getStatusClass = (status) => {
  const classes = {
    'in_progress': 'bg-blue-100 text-blue-800',
    'under_editing': 'bg-yellow-100 text-yellow-800',
    'disputed': 'bg-red-100 text-red-800',
    'completed': 'bg-green-100 text-green-800',
    'archived': 'bg-gray-100 text-gray-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPaymentStatusClass = (status) => {
  const classes = {
    completed: 'bg-green-100 text-green-800',
    succeeded: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-yellow-100 text-yellow-800',
    under_review: 'bg-yellow-100 text-yellow-800',
    unpaid: 'bg-orange-100 text-orange-700',
    failed: 'bg-red-100 text-red-700',
    cancelled: 'bg-gray-100 text-gray-700',
    refunded: 'bg-blue-100 text-blue-700',
    partially_refunded: 'bg-blue-100 text-blue-700',
    fully_refunded: 'bg-blue-100 text-blue-700'
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

// Legacy file upload handlers (kept for compatibility)
const handleFileUploadSuccess = (fileObj, response) => {
  uploadSuccess.value = `File "${fileObj.name}" uploaded successfully!`
    uploadError.value = ''
  loadFiles()
  setTimeout(() => {
    uploadedFiles.value = []
    uploadSuccess.value = ''
  }, 3000)
}

const handleFileUploadError = (fileObj, error) => {
  uploadError.value = `Failed to upload "${fileObj.name}": ${error.message || 'Unknown error'}`
  uploadSuccess.value = ''
    setTimeout(() => {
      uploadError.value = ''
    }, 5000)
}

const submitLink = async () => {
  if (!linkForm.value.link || !order.value) return
  
  submittingLink.value = true
  linkError.value = ''
  linkSuccess.value = ''
  
  try {
    await orderFilesAPI.createExternalLink({
      order: order.value.id,
      link: linkForm.value.link,
      description: linkForm.value.description || '',
    })
    linkSuccess.value = 'Link submitted successfully! It will be reviewed by an admin.'
    linkForm.value = { link: '', description: '' }
    await loadLinks() // Reload links list
    setTimeout(() => {
      linkSuccess.value = ''
    }, 5000)
  } catch (error) {
    linkError.value = error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to submit link'
    setTimeout(() => {
      linkError.value = ''
    }, 5000)
  } finally {
    submittingLink.value = false
  }
}

const openSendMessageModal = async () => {
  showSendMessageModal.value = true
  sendMessageError.value = ''
  recipientSearch.value = ''
  selectedRecipient.value = null
  initialMessage.value = ''
  await loadAvailableRecipients()
}

const filteredRecipients = computed(() => {
  if (!recipientSearch.value) return availableRecipients.value
  const search = recipientSearch.value.toLowerCase()
  return availableRecipients.value.filter(r => 
    (r.username || '').toLowerCase().includes(search) ||
    (r.email || '').toLowerCase().includes(search) ||
    (r.role || '').toLowerCase().includes(search)
  )
})

const getRecipientInitials = (recipient) => {
  const name = recipient.username || recipient.email || ''
  const words = name.split(' ')
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase() || '?'
}

const selectRecipient = (recipient) => {
  selectedRecipient.value = recipient
  showSendMessageModal.value = false
  showInitialMessageModal.value = true
  initialMessage.value = ''
  sendMessageError.value = ''
}

const loadAvailableRecipients = async () => {
  if (!order.value) return
  loadingRecipientsForModal.value = true
  try {
    const res = await communicationsAPI.getOrderRecipients(order.value.id)
    availableRecipients.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('Failed to load recipients:', error)
    sendMessageError.value = 'Failed to load recipients: ' + (error.response?.data?.detail || error.message)
    availableRecipients.value = []
  } finally {
    loadingRecipientsForModal.value = false
  }
}

const startChatWithMessage = async () => {
  if (!order.value || !selectedRecipient.value) return
  
  sendingNewMessage.value = true
  sendMessageError.value = ''
  
  try {
    // Use simplified endpoint that auto-determines participants
    const threadRes = await communicationsAPI.startThreadForOrder(order.value.id)
    
    // Handle response format (could be { thread: {...} } or direct thread object)
    const newThread = threadRes.data.thread || threadRes.data
    createdThreadId.value = newThread.id
    
    // Send the first message if provided
    if (initialMessage.value.trim()) {
      const messageData = {
        recipient: selectedRecipient.value.id,
        message: initialMessage.value.trim(),
        message_type: 'text'
      }
      
      await communicationsAPI.sendMessage(newThread.id, messageData)
    }
    
    // Close modals and refresh threads
    showInitialMessageModal.value = false
    showSendMessageModal.value = false
    await loadThreads()
    
    // Reset form
    selectedRecipient.value = null
    initialMessage.value = ''
    recipientSearch.value = ''
  } catch (error) {
    console.error('Failed to start chat:', error)
    sendMessageError.value = error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to start chat'
  } finally {
    sendingNewMessage.value = false
  }
}


const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const parseAmount = (value) => {
  const numeric = typeof value === 'number' ? value : parseFloat(value ?? 0)
  return Number.isFinite(numeric) ? numeric : 0
}

const formatCurrency = (value, currency = 'USD') => {
  const numeric = parseAmount(value)
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(numeric)
}


const isCurrentUser = (sender) => {
  return sender?.id === authStore.user?.id
}

const loadThreads = async () => {
  if (!order.value) return
  loadingThreads.value = true
  try {
    const res = await communicationsAPI.listThreads({ order: order.value.id })
    threads.value = res.data.results || res.data || []
    // Sort by last message time (most recent first)
    threads.value.sort((a, b) => {
      const timeA = a.last_message?.sent_at || a.updated_at
      const timeB = b.last_message?.sent_at || b.updated_at
      return new Date(timeB) - new Date(timeA)
    })
    // Initialize forms and state for each thread
    threads.value.forEach(thread => {
      if (!threadMessageForms.value[thread.id]) {
        threadMessageForms.value[thread.id] = {
          recipient: '',
          message: '',
          reply_to: null
        }
      }
      if (!threadSelectedFiles.value[thread.id]) {
        threadSelectedFiles.value[thread.id] = null
      }
      if (!threadErrors.value[thread.id]) {
        threadErrors.value[thread.id] = ''
      }
    })
  } catch (error) {
    console.error('Failed to load threads:', error)
  } finally {
    loadingThreads.value = false
  }
}

const toggleThreadExpanded = async (threadId) => {
  expandedThreads.value[threadId] = !expandedThreads.value[threadId]
  if (expandedThreads.value[threadId]) {
    await Promise.all([
      loadThreadMessages(threadId),
      loadThreadRecipients(threadId)
    ])
    
    // Auto-select recipient (first participant that's not the current user)
    const thread = threads.value.find(t => t.id === threadId)
    if (thread && thread.participants && thread.participants.length > 0) {
      const otherParticipant = thread.participants.find(p => {
        const id = typeof p === 'object' ? p.id : p
        return id !== authStore.user?.id
      })
      if (otherParticipant && threadMessageForms.value[threadId]) {
        const recipientId = typeof otherParticipant === 'object' ? otherParticipant.id : otherParticipant
        threadMessageForms.value[threadId].recipient = recipientId
      }
    }
    
    // Start polling for this thread
    startThreadPolling(threadId)
    // Auto-scroll to bottom
    await nextTick()
    scrollThreadToBottom(threadId)
  } else {
    // Stop polling when collapsed
    stopThreadPolling(threadId)
  }
}

const jumpToActivity = async (activity) => {
  if (!activity) return
  
  if (activity.type === 'message') {
    activeTab.value = 'messages'
    await nextTick()
    const threadId = activity.meta?.threadId
    if (threadId) {
      if (!expandedThreads.value[threadId]) {
        await toggleThreadExpanded(threadId)
      } else {
        await loadThreadMessages(threadId)
      }
      await nextTick()
      scrollThreadToBottom(threadId)
    }
  } else if (activity.type === 'file') {
    activeTab.value = 'files'
  }
}

const loadThreadMessages = async (threadId, url = null, silent = false) => {
  if (!silent) loadingMessages.value[threadId] = true
  try {
    let response
    if (url) {
      const urlObj = new URL(url)
      const path = urlObj.pathname + urlObj.search
      const apiClient = (await import('@/api/client')).default
      response = await apiClient.get(path)
    } else {
      response = await communicationsAPI.listMessages(threadId, { page_size: 20 })
    }
    
    const messages = response.data?.results || response.data || []
    const newMessages = Array.isArray(messages) ? [...messages].reverse() : []
    
    // Check if we have new messages (for silent updates)
    if (silent && lastMessageIds.value[threadId]) {
      const hasNew = newMessages.some(m => m.id > lastMessageIds.value[threadId])
      if (hasNew) {
        // Check if user is near bottom before auto-scrolling
        const container = messageContainers.value[threadId]
        if (container) {
          const isNearBottom = container.scrollHeight - container.scrollTop < container.clientHeight + 100
          threadMessages.value[threadId] = newMessages
          if (isNearBottom) {
            await nextTick()
            scrollThreadToBottom(threadId)
          }
        } else {
          threadMessages.value[threadId] = newMessages
        }
      } else {
        threadMessages.value[threadId] = newMessages
      }
    } else {
      threadMessages.value[threadId] = newMessages
      await nextTick()
      scrollThreadToBottom(threadId)
    }
    
    // Update last message ID
    if (newMessages.length > 0) {
      lastMessageIds.value[threadId] = Math.max(...newMessages.map(m => m.id))
    }
    
    // Update pagination
    if (response.data) {
      const count = response.data.count || messages.length
      const pageSize = 20
      threadPagination.value[threadId] = {
        count: count,
        next: response.data.next || null,
        previous: response.data.previous || null,
        current: url ? parseInt(new URL(url).searchParams.get('page') || '1') : 1,
        total: Math.ceil(count / pageSize) || 1
      }
    }
  } catch (error) {
    console.error('Failed to load messages:', error)
    threadMessages.value[threadId] = []
    threadErrors.value[threadId] = 'Failed to load messages'
  } finally {
    loadingMessages.value[threadId] = false
  }
}

const loadThreadRecipients = async (threadId) => {
  loadingRecipientsForThread.value[threadId] = true
  try {
    const res = await communicationsAPI.getAvailableRecipients(threadId)
    threadRecipients.value[threadId] = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('Failed to load recipients:', error)
    threadRecipients.value[threadId] = []
  } finally {
    loadingRecipientsForThread.value[threadId] = false
  }
}

const handleThreadFileSelect = (threadId, event) => {
  const file = event.target.files?.[0]
  if (file) {
    threadSelectedFiles.value[threadId] = file
    threadErrors.value[threadId] = ''
  }
}

const sendMessageToThread = async (threadId) => {
  const form = threadMessageForms.value[threadId]
  if (!form.message.trim() && !threadSelectedFiles.value[threadId]) {
    threadErrors.value[threadId] = 'Please enter a message or attach a file.'
    return
  }
  if (!form.recipient) {
    threadErrors.value[threadId] = 'Please select a recipient.'
    return
  }
  
  sendingMessageToThreads.value[threadId] = true
  threadErrors.value[threadId] = ''
  
  try {
    // If file is selected, upload as attachment
    if (threadSelectedFiles.value[threadId]) {
      const formData = new FormData()
      formData.append('file', threadSelectedFiles.value[threadId])
      formData.append('thread_id', threadId)
      formData.append('recipient_id', form.recipient)
      
      if (form.message.trim()) {
        // Send attachment first, then text message
        await communicationsAPI.uploadAttachment(formData)
        const messageData = {
          recipient: form.recipient,
          message: form.message,
          message_type: 'text',
        }
        if (form.reply_to) {
          messageData.reply_to = form.reply_to
        }
        await communicationsAPI.sendMessage(threadId, messageData)
      } else {
        await communicationsAPI.uploadAttachment(formData)
      }
    } else {
      // Regular text message
      const messageData = {
        recipient: form.recipient,
        message: form.message,
        message_type: 'text',
      }
      if (form.reply_to) {
        messageData.reply_to = form.reply_to
      }
      await communicationsAPI.sendMessage(threadId, messageData)
    }
    
    // Reset form
    form.message = ''
    form.reply_to = null
    threadSelectedFiles.value[threadId] = null
    if (threadFileInputs.value[threadId]) {
      threadFileInputs.value[threadId].value = ''
    }
    
    // Reload messages and threads
    await Promise.all([
      loadThreadMessages(threadId),
      loadThreads()
    ])
  } catch (error) {
    console.error('Failed to send message:', error)
    threadErrors.value[threadId] = error.response?.data?.detail || 
                                   error.response?.data?.error || 
                                   error.message || 
                                   'Failed to send message'
  } finally {
    sendingMessageToThreads.value[threadId] = false
  }
}

const scrollThreadToBottom = (threadId) => {
  const container = messageContainers.value[threadId]
  if (container) {
    nextTick(() => {
      container.scrollTop = container.scrollHeight
    })
  }
}

const startThreadPolling = (threadId) => {
  // Clear existing interval
  if (pollingIntervals.value[threadId]) {
    clearInterval(pollingIntervals.value[threadId])
  }
  
  // Start polling every 5 seconds
  pollingIntervals.value[threadId] = setInterval(() => {
    if (expandedThreads.value[threadId]) {
      loadThreadMessages(threadId, null, true) // Silent update
    }
  }, 5000)
}

const stopThreadPolling = (threadId) => {
  if (pollingIntervals.value[threadId]) {
    clearInterval(pollingIntervals.value[threadId])
    delete pollingIntervals.value[threadId]
  }
}

const replyToMessage = (threadId, messageId) => {
  if (!threadMessageForms.value[threadId]) {
    threadMessageForms.value[threadId] = {
      recipient: '',
      message: '',
      reply_to: null
    }
  }
  threadMessageForms.value[threadId].reply_to = messageId
  // Scroll to message input
  nextTick(() => {
    const container = messageContainers.value[threadId]
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

const getRepliedToMessage = (threadId, messageId) => {
  return threadMessages.value[threadId]?.find(m => m.id === messageId)
}

const getRepliedToSender = (threadId, messageId) => {
  const msg = getRepliedToMessage(threadId, messageId)
  return msg?.sender_display_name || msg?.sender?.username || 'Unknown'
}

const getRepliedToContent = (threadId, messageId) => {
  const msg = getRepliedToMessage(threadId, messageId)
  if (!msg) return 'Message not found'
  if (msg.attachment) return `📎 ${msg.attachment.filename}`
  return msg.message?.substring(0, 50) + (msg.message?.length > 50 ? '...' : '') || 'No content'
}

const downloadAttachment = async (threadId, messageId, filename) => {
  try {
    const url = `/api/v1/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/download_attachment/`
    const link = document.createElement('a')
    link.href = url
    link.download = filename || 'attachment'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download attachment:', error)
    alert('Failed to download file')
  }
}

const getAttachmentUrl = (threadId, messageId) => {
  return `/api/v1/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/download_attachment/`
}

const formatRelativeTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const openImagePreview = (url) => {
  window.open(url, '_blank')
}

const deleteMessage = async (threadId, messageId) => {
  if (!confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
    return
  }
  
  const key = `${threadId}-${messageId}`
  deletingMessage.value[key] = true
  
  try {
    await communicationsAPI.deleteMessage(threadId, messageId)
    await loadThreadMessages(threadId)
    await loadThreads()
  } catch (error) {
    console.error('Failed to delete message:', error)
    alert('Failed to delete message: ' + (error.response?.data?.detail || error.message))
  } finally {
    deletingMessage.value[key] = false
  }
}

const deleteThread = async (threadId) => {
  if (!confirm('Are you sure you want to delete this thread? All messages in this thread will be deleted. This action cannot be undone.')) {
    return
  }
  
  deletingThread.value[threadId] = true
  
  try {
    await communicationsAPI.deleteThread(threadId)
    await loadThreads()
    // Close the thread if it was expanded
    expandedThreads.value[threadId] = false
    stopThreadPolling(threadId)
  } catch (error) {
    console.error('Failed to delete thread:', error)
    alert('Failed to delete thread: ' + (error.response?.data?.detail || error.message))
  } finally {
    deletingThread.value[threadId] = false
  }
}

// Cleanup polling on unmount
onUnmounted(() => {
  Object.keys(pollingIntervals.value).forEach(threadId => {
    stopThreadPolling(threadId)
  })
  // Clear unread message polling interval
  if (unreadMessageInterval) {
    clearInterval(unreadMessageInterval)
    unreadMessageInterval = null
  }
})

// Initialize online status tracking
useOnlineStatus()

// Draft Request Functions
const loadDraftRequests = async () => {
  if (!order.value) return
  loadingDraftRequests.value = true
  try {
    const res = await draftRequestsAPI.listDraftRequests({ order_id: order.value.id })
    draftRequests.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load draft requests:', error)
    draftRequests.value = []
  } finally {
    loadingDraftRequests.value = false
  }
}

const checkDraftEligibility = async () => {
  if (!order.value) return
  loadingDraftEligibility.value = true
  try {
    const res = await draftRequestsAPI.checkEligibility(order.value.id)
    draftEligibility.value = res.data
  } catch (error) {
    console.error('Failed to check eligibility:', error)
    showErrorToast('Failed to check eligibility: ' + (error.response?.data?.error || error.message))
  } finally {
    loadingDraftEligibility.value = false
  }
}

const createDraftRequest = async () => {
  if (!order.value) return
  
  try {
    await draftRequestsAPI.createDraftRequest({
      order: order.value.id,
      message: draftRequestForm.value.message || ''
    })
    showSuccessToast('Draft request submitted successfully!')
    showDraftRequestModal.value = false
    draftRequestForm.value.message = ''
    await loadDraftRequests()
    await checkDraftEligibility()
  } catch (error) {
    showErrorToast('Failed to create draft request: ' + (error.response?.data?.error || error.message))
  }
}

const cancelDraftRequest = async (requestId) => {
  if (!confirm('Are you sure you want to cancel this draft request?')) return
  
  try {
    await draftRequestsAPI.cancelDraftRequest(requestId)
    showSuccessToast('Draft request cancelled')
    await loadDraftRequests()
    await checkDraftEligibility()
  } catch (error) {
    showErrorToast('Failed to cancel draft request: ' + (error.response?.data?.error || error.message))
  }
}

const handleDraftFileSelect = (requestId, event) => {
  const file = event.target.files?.[0]
  if (file) {
    draftSelectedFiles.value[requestId] = file
  }
}

const uploadDraftFile = async (requestId) => {
  const file = draftSelectedFiles.value[requestId]
  if (!file) return
  
  uploadingDraft.value[requestId] = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (draftFileDescriptions.value[requestId]) {
      formData.append('description', draftFileDescriptions.value[requestId])
    }
    
    await draftRequestsAPI.uploadDraft(requestId, formData)
    showSuccessToast('Draft uploaded successfully!')
    
    // Clear form
    draftSelectedFiles.value[requestId] = null
    draftFileDescriptions.value[requestId] = ''
    if (draftFileInputs.value[requestId]) {
      draftFileInputs.value[requestId].value = ''
    }
    
    await loadDraftRequests()
  } catch (error) {
    showErrorToast('Failed to upload draft: ' + (error.response?.data?.error || error.message))
  } finally {
    uploadingDraft.value[requestId] = false
  }
}

const downloadDraftFile = async (fileId) => {
  try {
    const response = await draftRequestsAPI.downloadDraftFile(fileId)
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `draft-${fileId}.pdf` // You might want to get the actual filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    showErrorToast('Failed to download draft file: ' + (error.response?.data?.error || error.message))
  }
}

const pendingDraftRequests = computed(() => {
  return draftRequests.value.filter(r => r.status === 'pending' || r.status === 'in_progress')
})

// Deadline Extension Functions
const getMinDeadlineDate = () => {
  if (!order.value) return ''
  const currentDeadline = order.value.writer_deadline || order.value.deadline
  if (!currentDeadline) return ''
  const date = new Date(currentDeadline)
  date.setHours(date.getHours() + 1) // At least 1 hour from current deadline
  return date.toISOString().slice(0, 16)
}

const closeDeadlineExtensionModal = () => {
  showDeadlineExtensionModal.value = false
  deadlineExtensionForm.value = {
    requested_deadline: '',
    reason: ''
  }
}

const submitDeadlineExtension = async () => {
  if (!order.value) return
  
  submittingDeadlineExtension.value = true
  try {
    const data = {
      order: order.value.id,
      old_deadline: order.value.writer_deadline || order.value.deadline,
      requested_deadline: deadlineExtensionForm.value.requested_deadline,
      reason: deadlineExtensionForm.value.reason
    }
    
    await writerManagementAPI.createDeadlineExtensionRequest(data)
    showSuccessToast('Deadline extension request submitted successfully!')
    closeDeadlineExtensionModal()
    await loadOrder() // Reload order to get updated info
  } catch (error) {
    showErrorToast(getErrorMessage(error, 'Failed to submit deadline extension request'))
  } finally {
    submittingDeadlineExtension.value = false
  }
}

// Order Take/Request Functions
const loadWriterContext = async () => {
  if (!authStore.isWriter) return
  
  try {
    const profileResponse = await writerManagementAPI.getMyProfile()
    writerProfile.value = profileResponse.data
    
    // Load active assignments count
    const response = await ordersAPI.list({
      assigned_writer: true,
      status__in: 'in_progress,under_editing,revision_requested,on_hold',
      page_size: 1,
    })
    if (typeof response.data?.count === 'number') {
      activeAssignmentCount.value = response.data.count
    } else {
      const results = response.data?.results || response.data || []
      activeAssignmentCount.value = results.length
    }
    
    // Check if takes are enabled and calculate capacity
    const queueResponse = await writerDashboardAPI.getOrderQueue()
    const queueData = queueResponse.data
    takesEnabled.value = queueData.takes_enabled || false
    
    const levelDetails = writerProfile.value?.writer_level_details || null
    const maxOrders = levelDetails?.max_orders || 0
    const remaining = Math.max(0, maxOrders - activeAssignmentCount.value)
    canTakeOrders.value = takesEnabled.value && remaining > 0
    
    // Check if this order is already requested
    const requestedOrderIds = queueData.requested_order_ids || []
    isOrderRequested.value = requestedOrderIds.includes(order.value?.id) || order.value?.is_requested || false
  } catch (error) {
    console.error('Failed to load writer context:', error)
  }
}

const openRequestModal = () => {
  if (!order.value) return
  orderRequestReason.value = ''
  showOrderRequestModal.value = true
}

const closeOrderRequestModal = () => {
  showOrderRequestModal.value = false
  orderRequestReason.value = ''
}

const submitOrderRequest = async () => {
  if (!order.value) return
  
  const reason = orderRequestReason.value?.trim() || ''
  if (!reason) {
    showErrorToast('Please provide a reason for requesting this order.')
    return
  }
  
  if (reason.length < 10) {
    showErrorToast('Please provide a more detailed reason (at least 10 characters).')
    return
  }
  
  if (reason.length > 2000) {
    showErrorToast('Reason is too long (maximum 2000 characters).')
    return
  }
  
  if (isOrderRequested.value) {
    showErrorToast('You have already requested this order. Please wait for admin review.')
    closeOrderRequestModal()
    return
  }
  
  requestingOrder.value = true
  
  try {
    await writerOrderRequestsAPI.create({
      order: order.value.id,
      reason: reason
    })
    
    showSuccessToast('Order request submitted successfully! Waiting for admin review.')
    isOrderRequested.value = true
    closeOrderRequestModal()
    await loadOrder() // Reload order to get updated info
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to submit order request. Please try again.')
    showErrorToast(errorMsg)
  } finally {
    requestingOrder.value = false
  }
}

const takeOrder = async () => {
  if (!order.value) return
  
  // Check if already requested
  if (isOrderRequested.value) {
    showErrorToast('You have already requested this order. Please wait for admin review.')
    return
  }
  
  // Validate capacity
  if (!canTakeOrders.value) {
    if (!takesEnabled.value) {
      showErrorToast('Taking orders directly is currently disabled. Please submit a request instead.')
    } else {
      showErrorToast(
        `You have reached your current take limit. ` +
        'Submit existing work or request a hold before taking another order.'
      )
    }
    return
  }
  
  // Confirm action
  if (!confirm(
    `Are you sure you want to take Order #${order.value.id}?\n\n` +
    `This will assign it to you immediately and you'll be responsible for completing it by the deadline.`
  )) {
    return
  }
  
  takingOrder.value = true
  
  try {
    await writerOrderRequestsAPI.createTake({
      order: order.value.id,
    })
    
    showSuccessToast(`Order #${order.value.id} taken successfully! It has been assigned to you.`)
    await loadOrder() // Reload order to get updated info
    await loadWriterContext() // Refresh writer context
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to take order. Please try again.')
    
    // Provide more specific error messages
    if (errorMsg.includes('already assigned') || errorMsg.includes('already taken')) {
      showErrorToast(errorMsg)
    } else if (errorMsg.includes('not available') || errorMsg.includes('status')) {
      showErrorToast(errorMsg)
    } else if (errorMsg.includes('limit') || errorMsg.includes('maximum')) {
      showErrorToast(errorMsg)
    } else if (errorMsg.includes('disabled')) {
      showErrorToast(errorMsg)
    } else {
      showErrorToast(errorMsg)
    }
  } finally {
    takingOrder.value = false
  }
}

onMounted(async () => {
  await loadOrder()
  await loadOrderReview()
  await loadLatestProgress()
  // Load threads after order is loaded (if needed for unread count)
  if (order.value) {
    await loadThreads()
    await loadDraftRequests()
    if (authStore.isClient) {
      await checkDraftEligibility()
    }
    if (authStore.isWriter && order.value.status === 'available') {
      await loadWriterContext()
    }
  }
})
</script>


