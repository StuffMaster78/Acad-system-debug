<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
      <h1 class="text-3xl font-bold text-gray-900">Order Details</h1>
        <p v-if="order" class="text-sm text-gray-500 mt-1">Order #{{ order.id }} • {{ order.topic || 'N/A' }}</p>
      </div>
      <div v-if="order" class="flex gap-2">
        <router-link
          :to="`/orders/${order.id}/messages`"
          class="relative px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
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
    <div v-if="order" class="border-b border-gray-200">
      <nav class="flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors relative',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
                  <UserDisplayName :user="order.client || { id: order.client_id, role: 'client', registration_id: order.client_registration_id }" />
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
                    <UserDisplayName :user="order.writer || order.assigned_writer || { id: order.writer_id, role: 'writer', pen_name: order.writer_pen_name, registration_id: order.writer_registration_id }" />
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
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">Status Timeline</h3>
                  <p class="text-sm text-gray-500">Key checkpoints from creation to completion</p>
                </div>
                <span class="text-xs text-gray-500">{{ statusTimeline.length }} {{ statusTimeline.length === 1 ? 'event' : 'events' }}</span>
              </div>
              <div v-if="statusTimeline.length === 0" class="text-sm text-gray-500">
                No status updates recorded yet.
              </div>
              <ol v-else class="relative border-l border-gray-200 pl-6 space-y-6">
                <li
                  v-for="entry in statusTimeline"
                  :key="entry.key"
                  class="relative"
                >
                  <span class="absolute -left-3 top-1 w-6 h-6 rounded-full bg-primary-50 text-primary-700 flex items-center justify-center text-xs font-semibold">
                    {{ entry.icon }}
                  </span>
                  <div class="text-sm font-semibold text-gray-900">
                    {{ entry.label }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatDateTime(entry.timestamp) }}
                    <span v-if="entry.relativeTime">• {{ entry.relativeTime }}</span>
                  </div>
                  <div v-if="entry.description" class="text-sm text-gray-600 mt-1">
                    {{ entry.description }}
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

        <!-- Order Instructions & Notes -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-if="order.instructions || order.order_instructions" class="bg-white rounded-lg border border-gray-200 p-4">
            <h3 class="text-lg font-semibold mb-3 text-gray-900">Order Instructions</h3>
            <SafeHtml 
              :content="order.instructions || order.order_instructions"
              container-class="text-gray-700 text-sm"
            />
          </div>
          <div v-if="order.completion_notes || (authStore.isAdmin || authStore.isSuperAdmin)" class="bg-white rounded-lg border border-gray-200 p-4">
            <h3 class="text-lg font-semibold mb-3 text-gray-900">Notes</h3>
            <div v-if="order.completion_notes" class="text-gray-700 text-sm whitespace-pre-wrap">{{ order.completion_notes }}</div>
            <div v-else class="text-gray-400 text-sm italic">No notes available</div>
          </div>
        </div>
        
        <!-- Progress Bar (for clients) -->
        <div v-if="authStore.isClient && order.assigned_writer" class="border-t pt-4">
          <h3 class="text-lg font-semibold mb-3">Order Progress</h3>
          <ProgressBar
            :progress-percentage="latestProgressPercentage"
            :last-update="latestProgressUpdate"
          />
        </div>
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

      <div v-if="order.instructions || order.order_instructions" class="border-t pt-4">
        <h3 class="text-lg font-semibold mb-2">Instructions</h3>
        <SafeHtml 
          :content="order.instructions || order.order_instructions"
          container-class="text-gray-700"
        />
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
        <h3 class="text-lg font-semibold mb-3">Order Actions</h3>
        <div class="flex flex-wrap gap-2">
          <!-- Writer Actions -->
          <button
            v-if="canSubmitOrder"
            @click="submitOrder"
            :disabled="processingAction"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ processingAction ? 'Processing...' : 'Submit Order' }}
          </button>
          
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
        <div v-if="authStore.isClient" class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4">Order Progress</h3>
          <ProgressBar
            :progress-percentage="latestProgressPercentage"
            :last-update="latestProgressUpdate"
          />
        </div>

        <!-- Progress Report Form (for writers) -->
        <div v-if="canSubmitProgress" class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4">Report Progress</h3>
          <ProgressReportForm
            :order-id="order.id"
            :initial-progress="latestProgressPercentage"
            @success="handleProgressSubmitted"
            @error="handleProgressError"
          />
        </div>

        <!-- Progress History -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4">Progress History</h3>
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
        <div class="flex items-center justify-between mb-4">
          <div>
          <h3 class="text-lg font-semibold">Files</h3>
            <p class="text-sm text-gray-500 mt-1">Upload and manage order files</p>
          </div>
          <button
            @click="loadFiles"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            :disabled="loadingFiles"
          >
            {{ loadingFiles ? 'Loading...' : '🔄 Refresh' }}
          </button>
        </div>

        <!-- File Upload Form -->
        <div class="mb-6 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
          <h4 class="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span>📤</span>
            <span>Upload Files</span>
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
            
            <div v-if="uploadSuccess" class="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
              ✓ {{ uploadSuccess }}
            </div>
            <div v-if="uploadError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              ✗ {{ uploadError }}
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
        
        <div v-else-if="files.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <div class="text-4xl mb-3">📁</div>
          <p class="text-gray-500 text-sm mb-2">No files uploaded yet</p>
          <p class="text-gray-400 text-xs">Upload files using the form above</p>
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
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold">Draft Requests</h3>
            <p class="text-sm text-gray-500 mt-1">Request drafts to see order progress (requires Progressive Delivery)</p>
          </div>
          <button
            v-if="authStore.isClient"
            @click="checkDraftEligibility"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            :disabled="loadingDraftEligibility"
          >
            {{ loadingDraftEligibility ? 'Checking...' : '🔄 Check Eligibility' }}
          </button>
        </div>

        <!-- Eligibility Check (Client) -->
        <div v-if="authStore.isClient && draftEligibility" class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <span class="text-2xl">{{ draftEligibility.can_request ? '✅' : '⚠️' }}</span>
            </div>
            <div class="ml-4 flex-1">
              <h4 class="text-lg font-semibold text-gray-900 mb-2">
                {{ draftEligibility.can_request ? 'You can request drafts!' : 'Cannot request drafts' }}
              </h4>
              <p v-if="draftEligibility.reason" class="text-sm text-gray-700 mb-4">
                {{ draftEligibility.reason }}
              </p>
              <p v-if="draftEligibility.has_pending_request" class="text-sm text-orange-700 mb-4">
                You already have a pending draft request for this order.
              </p>
              <button
                v-if="draftEligibility.can_request && !draftEligibility.has_pending_request"
                @click="showDraftRequestModal = true"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
              >
                Request Draft
              </button>
            </div>
          </div>
        </div>

        <!-- Draft Requests List -->
        <div class="bg-white rounded-lg shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h4 class="text-lg font-semibold">Draft Request History</h4>
          </div>

          <div v-if="loadingDraftRequests" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>

          <div v-else-if="draftRequests.length === 0" class="p-12 text-center">
            <p class="text-gray-500">No draft requests yet</p>
          </div>

          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="request in draftRequests"
              :key="request.id"
              class="p-6 hover:bg-gray-50 transition-colors"
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
        <div v-if="authStore.isWriter && order.assigned_writer_id === authStore.user?.id" class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
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
        <div class="flex items-center justify-between mb-4">
          <div>
          <h3 class="text-lg font-semibold">External Links</h3>
            <p class="text-sm text-gray-500 mt-1">Submit and manage external file links</p>
          </div>
          <button
            @click="loadLinks"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            :disabled="loadingLinks"
          >
            {{ loadingLinks ? 'Loading...' : '🔄 Refresh' }}
          </button>
        </div>

        <!-- External Link Submission Form -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 class="text-sm font-semibold text-gray-700 mb-3">Submit External Link</h4>
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
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Link</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewed By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="link in links" :key="link.id" class="hover:bg-gray-50">
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
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
import draftRequestsAPI from '@/api/draft-requests'

const route = useRoute()
const authStore = useAuthStore()
const { success: showSuccessToast, error: showErrorToast } = useToast()
const order = ref(null)
const loading = ref(true)
const activeTab = ref('overview')
const unreadMessageCount = ref(0)
let unreadMessageInterval = null

// Tabs configuration
const tabs = [
  { id: 'overview', label: 'Overview', icon: '📋' },
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

const isAdmin = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'superadmin'
})

const userRole = computed(() => authStore.user?.role)
const userId = computed(() => authStore.user?.id)

// Order action permissions
const canSubmitOrder = computed(() => {
  if (!order.value) return false
  const status = order.value.status?.toLowerCase()
  const isWriter = userRole.value === 'writer'
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value
  return isWriter && isAssignedWriter && ['in_progress', 'assigned', 'draft'].includes(status)
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

const hasDownloadableFiles = computed(() => {
  if (!files.value || files.value.length === 0) return false
  return files.value.some(f => f.is_downloadable && canDownloadFile(f))
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

const statusLabelMap = {
  created: 'Order Created',
  pending: 'Pending',
  draft: 'Draft Saved',
  assigned: 'Writer Assigned',
  in_progress: 'In Progress',
  submitted: 'Submitted for Review',
  revision_requested: 'Revision Requested',
  revision_in_progress: 'Revision In Progress',
  revised: 'Revision Submitted',
  approved: 'Approved',
  completed: 'Completed',
  closed: 'Closed',
  cancelled: 'Cancelled'
}

const statusIconMap = {
  created: '🟢',
  pending: '⏳',
  draft: '📝',
  assigned: '👤',
  in_progress: '⚙️',
  submitted: '📤',
  revision_requested: '🔁',
  revision_in_progress: '✏️',
  revised: '✅',
  approved: '🎉',
  completed: '🏁',
  closed: '🔒',
  cancelled: '✖️'
}

const formatStatusLabel = (value) => {
  if (!value) return 'Status Update'
  return value
    .toString()
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

const statusTimeline = computed(() => {
  if (!order.value) return []

  const entries = []
  const pushEntry = (key, status, timestamp, extra = {}) => {
    if (!timestamp) return
    const normalizedStatus = status?.toLowerCase()
    entries.push({
      key,
      status: normalizedStatus,
      label: extra.label || statusLabelMap[normalizedStatus] || formatStatusLabel(status),
      timestamp,
      relativeTime: formatRelativeTime(timestamp),
      description: extra.description,
      icon: extra.icon || statusIconMap[normalizedStatus] || '•'
    })
  }

  pushEntry('created', 'created', order.value.created_at, {
    description: 'Order placed'
  })

  const transitionLogs = Array.isArray(order.value.transitions) ? order.value.transitions : []
  transitionLogs.forEach(log => {
    const descriptionParts = []
    if (log.action) {
      descriptionParts.push(formatStatusLabel(log.action))
    }
    if (log.is_automatic) {
      descriptionParts.push('Auto transition')
    }
    pushEntry(`transition-${log.id}`, log.new_status || log.action, log.timestamp, {
      description: descriptionParts.join(' • ')
    })
  })

  const milestoneTimestamps = [
    { key: 'submitted_at', status: 'submitted', timestamp: order.value.submitted_at, description: 'Writer submitted deliverables' },
    { key: 'completed_at', status: 'completed', timestamp: order.value.completed_at, description: 'Order marked as completed' },
    { key: 'approved_at', status: 'approved', timestamp: order.value.approved_at, description: 'Order approved' },
    { key: 'closed_at', status: 'closed', timestamp: order.value.closed_at, description: 'Order closed' }
  ]
  milestoneTimestamps.forEach(entry => pushEntry(entry.key, entry.status, entry.timestamp, { description: entry.description }))

  return entries
    .filter(entry => !!entry.timestamp)
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
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

const completeOrder = async () => {
  if (!order.value) return
  if (!confirm('Are you sure you want to mark this order as complete?')) return
  
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
  const reason = prompt('Please provide a reason for cancellation (optional):')
  if (reason === null) return // User cancelled prompt
  
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
      loadUnreadMessageCount(),
      loadPaymentSummary()
    ])
    
    // Start polling for unread messages every 30 seconds
    if (unreadMessageInterval) {
      clearInterval(unreadMessageInterval)
    }
    unreadMessageInterval = setInterval(() => {
      if (order.value) {
        loadUnreadMessageCount()
      }
    }, 30000)
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
  }
})
</script>


