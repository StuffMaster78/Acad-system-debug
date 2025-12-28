<template>
  <div class="space-y-6 p-6">
    <!-- Header with Back Button -->
    <div class="flex items-center gap-4 mb-2">
      <router-link
        :to="getBackRoute()"
        class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="text-sm font-medium">{{ getBackButtonText() }}</span>
      </router-link>
    </div>
    
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Order Details</h1>
        <p v-if="order" class="text-sm text-gray-500 dark:text-gray-400 mt-1 flex flex-wrap items-center gap-2">
          <span>Order #{{ order.id }} • {{ order.topic || 'N/A' }}</span>
          <EnhancedStatusBadge
            v-if="order.status"
            :status="order.status"
            :show-tooltip="true"
            :show-priority="true"
          />
          <span
            v-if="order.is_paid !== undefined && (authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
            :class="[
              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
              order.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            ]"
          >
            {{ order.is_paid ? 'Paid' : 'Unpaid' }}
          </span>
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
        <!-- Soft Deleted Banner -->
        <div v-if="order.is_deleted" class="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🗑️</span>
              <div>
                <h3 class="text-lg font-semibold text-red-900">This order has been soft-deleted</h3>
                <p class="text-sm text-red-700 mt-1">
                  Deleted on {{ formatDateTime(order.deleted_at) }}
                  <span v-if="order.deleted_by"> by {{ order.deleted_by?.username || order.deleted_by?.email || 'Unknown' }}</span>
                  <span v-if="order.delete_reason"> - {{ order.delete_reason }}</span>
                </p>
                <p v-if="order.restored_at" class="text-sm text-green-700 mt-1">
                  Restored on {{ formatDateTime(order.restored_at) }}
                  <span v-if="order.restored_by"> by {{ order.restored_by?.username || order.restored_by?.email || 'Unknown' }}</span>
                </p>
              </div>
            </div>
            <div v-if="authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport" class="flex gap-2">
              <button
                @click="restoreOrder"
                :disabled="processingAction"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                Restore
              </button>
            </div>
          </div>
        </div>
        
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
              <div class="shrink-0">
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
          
          <!-- Revision Eligibility Banner (client view, also visible to admin/support for full context) -->
          <div
            v-if="(authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) && revisionEligibility"
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
              @click="showRevisionForm = !showRevisionForm"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-orange-300 text-orange-700 rounded-lg hover:bg-orange-50 hover:border-orange-400 transition-all font-medium shadow-sm"
            >
              <span>🔄</span>
              <span>{{ showRevisionForm ? 'Cancel Revision Request' : 'Request Revision' }}</span>
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
              v-if="order.assigned_writer || order.writer_id"
              @click="activeTab = 'messages'"
              class="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 hover:border-blue-400 transition-all font-medium shadow-sm relative"
            >
              <span>💬</span>
              <span>View Messages</span>
              <span
                v-if="unreadMessageCount > 0"
                class="absolute -top-2 -right-2 flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-red-600 rounded-full ring-2 ring-white"
              >
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
          
          <!-- Inline Revision Request Form -->
          <div v-if="showRevisionForm && canRequestRevision && order.status !== 'revision_requested'" class="mt-6 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl border-2 border-orange-300 dark:border-orange-700 shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/50 flex items-center justify-center text-xl">
                  🔄
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Request Revision</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Provide details about what needs to be revised</p>
                </div>
              </div>
              <button
                @click="showRevisionForm = false; resetRevisionForm()"
                class="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Close"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div class="space-y-4">
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 text-sm text-blue-800 dark:text-blue-200">
                <p><strong>Note:</strong> Please provide specific details about what needs to be revised. You can specify sections, issues, and what you'd like changed. This helps the writer make the necessary changes quickly.</p>
              </div>
              
              <!-- General Revision Description -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  General Revision Description <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="revisionReason"
                  rows="4"
                  class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
                  placeholder="Provide an overview of what needs to be revised..."
                  required
                ></textarea>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">This will be the main description of your revision request.</p>
              </div>
              
              <!-- Section-Specific Changes -->
              <div>
                <div class="flex items-center justify-between mb-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Specific Sections to Address (Optional)
                  </label>
                  <button
                    type="button"
                    @click="addRevisionSection"
                    class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium flex items-center gap-1 px-3 py-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Add Section
                  </button>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">Specify particular sections, pages, or areas that need changes.</p>
                
                <div v-if="revisionSections.length === 0" class="text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-dashed border-gray-300 dark:border-gray-600">
                  No specific sections added. Click "Add Section" to specify particular areas that need revision.
                </div>
                
                <div v-else class="space-y-3">
                  <div
                    v-for="(section, index) in revisionSections"
                    :key="index"
                    class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 space-y-3"
                  >
                    <div class="flex items-start justify-between">
                      <h4 class="text-sm font-semibold text-gray-900 dark:text-white">Section {{ index + 1 }}</h4>
                      <button
                        type="button"
                        @click="removeRevisionSection(index)"
                        class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm px-2 py-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                    
                    <div>
                      <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Section/Area Name
                      </label>
                      <input
                        v-model="section.section"
                        type="text"
                        class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
                        placeholder="e.g., Introduction, Methodology, Page 5, Table 2"
                      />
                    </div>
                    
                    <div>
                      <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Issue/Problem
                      </label>
                      <textarea
                        v-model="section.issue"
                        rows="2"
                        class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
                        placeholder="Describe the issue or problem with this section..."
                      ></textarea>
                    </div>
                    
                    <div>
                      <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                        What You Want Changed
                      </label>
                      <textarea
                        v-model="section.request"
                        rows="2"
                        class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
                        placeholder="Describe what changes you'd like to see..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  @click="showRevisionForm = false; resetRevisionForm()"
                  class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
                  :disabled="requestingRevision"
                >
                  Cancel
                </button>
                <button
                  @click="requestRevision"
                  :disabled="requestingRevision || !revisionReason.trim()"
                  class="px-4 py-2 bg-orange-600 dark:bg-orange-700 text-white rounded-lg hover:bg-orange-700 dark:hover:bg-orange-800 disabled:opacity-50 transition-colors font-medium flex items-center gap-2"
                >
                  <span v-if="requestingRevision" class="animate-spin">⏳</span>
                  <span>{{ requestingRevision ? 'Submitting...' : 'Submit Revision Request' }}</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Disputed Order Section -->
          <div v-if="order.status === 'disputed'" class="mt-4 bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-xl p-6 shadow-lg">
            <div class="flex items-start gap-3 mb-4">
              <div class="w-10 h-10 rounded-full bg-red-500 flex items-center justify-center text-white text-xl font-bold">
                ⚠️
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-bold text-gray-900">Order Disputed</h3>
                <p class="text-sm text-gray-600 mt-1">This order has been disputed. You can work together to resolve the issue.</p>
              </div>
            </div>
            
            <!-- Client View: Agree to let writer continue -->
            <div v-if="authStore.isClient && order.dispute && !order.dispute.client_agreed_to_continue" class="bg-white rounded-lg p-4 border border-red-200">
              <div class="space-y-3">
                <p class="text-sm text-gray-700">
                  If you'd like the writer to fix the issues and continue working on this order, you can agree to let them proceed. The writer will be able to submit their work once you agree.
                </p>
                <button
                  @click="agreeToContinueDisputedOrder"
                  :disabled="processingDisputeAction"
                  class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <span>✅</span>
                  <span>{{ processingDisputeAction ? 'Processing...' : 'Agree to Let Writer Continue & Submit' }}</span>
                </button>
              </div>
            </div>
            
            <!-- Client View: Already agreed -->
            <div v-if="authStore.isClient && order.dispute && order.dispute.client_agreed_to_continue" class="bg-green-50 rounded-lg p-4 border border-green-200">
              <div class="flex items-center gap-2 text-sm text-green-800">
                <span>✅</span>
                <span>You've agreed to let the writer continue working. They can now submit their work.</span>
              </div>
            </div>
            
            <!-- Writer View: Client agreed, can submit -->
            <div v-if="authStore.isWriter && order.dispute && order.dispute.client_agreed_to_continue" class="bg-green-50 rounded-lg p-4 border border-green-200">
              <div class="space-y-3">
                <div class="flex items-center gap-2 text-sm text-green-800">
                  <span>✅</span>
                  <span class="font-semibold">The client has agreed to let you continue working on this order.</span>
                </div>
                <p class="text-sm text-gray-700">
                  You can now work on fixing the issues and submit your work. The order will move forward once you submit.
                </p>
                <button
                  v-if="canSubmitOrder"
                  @click="submitOrder"
                  :disabled="processingAction"
                  class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <span>📤</span>
                  <span>{{ processingAction ? 'Submitting...' : 'Submit Fixed Work' }}</span>
                </button>
              </div>
            </div>
            
            <!-- Writer View: Waiting for client agreement -->
            <div v-if="authStore.isWriter && order.dispute && !order.dispute.client_agreed_to_continue" class="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div class="flex items-center gap-2 text-sm text-yellow-800">
                <span>⏳</span>
                <span>Waiting for client to agree to let you continue working on this order.</span>
              </div>
            </div>
            
            <!-- Dispute Reason Display -->
            <div v-if="order.dispute && order.dispute.reason" class="mt-4 bg-white rounded-lg p-4 border border-gray-200">
              <h4 class="font-semibold text-gray-900 mb-2">Dispute Reason</h4>
              <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ order.dispute.reason }}</p>
            </div>
          </div>
          
          <!-- Revision Requested Notice -->
          <div v-if="order.status === 'revision_requested'" class="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div class="flex items-center gap-2 text-sm text-orange-800">
              <span>⏳</span>
              <span>Revision request submitted. The writer is working on your changes.</span>
            </div>
          </div>

          <!-- Revision Instructions Section (Inline Editable) -->
          <div v-if="order.status === 'revision_requested'" class="mt-4 bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 rounded-xl p-6 shadow-lg">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center text-white text-xl font-bold">
                  📝
                </div>
                <div>
                  <h3 class="text-lg font-bold text-gray-900">Revision Instructions</h3>
                  <p class="text-sm text-gray-600 mt-1">Provide detailed instructions to guide the writer on how to revise the order/paper</p>
                </div>
              </div>
              <button
                v-if="canEditRevisionInstructions && !editingRevisionInstructions"
                @click="startEditRevisionInstructions"
                class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-semibold flex items-center gap-2"
              >
                <span>{{ order.revision_instructions ? '✏️ Edit' : '➕ Add' }}</span>
                <span>Instructions</span>
              </button>
            </div>

            <!-- View Mode -->
            <div v-if="!editingRevisionInstructions && order.revision_instructions" class="bg-white rounded-lg p-4 border border-orange-200">
              <div class="prose max-w-none">
                <SafeHtml :html="order.revision_instructions" />
              </div>
            </div>
            
            <!-- Edit Mode -->
            <div v-if="editingRevisionInstructions && canEditRevisionInstructions" class="bg-white rounded-lg p-4 border border-orange-200 space-y-4">
              <div>
                <RichTextEditor
                  v-model="revisionInstructions"
                  label="Revision Instructions"
                  :required="true"
                  placeholder="Provide detailed instructions to guide the writer on how to revise the order..."
                  height="250px"
                />
              </div>
              <div class="flex gap-2 justify-end pt-4 border-t border-gray-200">
                <button
                  @click="cancelEditRevisionInstructions"
                  class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                  :disabled="savingRevisionInstructions"
                >
                  Cancel
                </button>
                <button
                  @click="saveRevisionInstructions"
                  :disabled="savingRevisionInstructions || !revisionInstructions.trim()"
                  class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 transition-colors"
                >
                  {{ savingRevisionInstructions ? 'Saving...' : 'Save Instructions' }}
                </button>
              </div>
            </div>
            
            <div v-if="!editingRevisionInstructions && !order.revision_instructions" class="bg-white/50 rounded-lg p-4 border-2 border-dashed border-orange-300 text-center">
              <p class="text-gray-600 text-sm">
                <span v-if="canEditRevisionInstructions">
                  No revision instructions provided yet. Click "Add Instructions" above to provide guidance for the writer.
                </span>
                <span v-else>
                  Waiting for revision instructions from the client or support team.
                </span>
              </p>
            </div>

            <!-- Display existing revision request details if available -->
            <div v-if="order.revision_request" class="mt-4 space-y-3">
              <div v-if="order.revision_request.title || order.revision_request.description" class="bg-white rounded-lg p-4 border border-orange-200">
                <h4 class="font-semibold text-gray-900 mb-2">Revision Request Details</h4>
                <p v-if="order.revision_request.title" class="font-medium text-gray-800 mb-2">{{ order.revision_request.title }}</p>
                <p v-if="order.revision_request.description" class="text-sm text-gray-700 whitespace-pre-wrap">{{ order.revision_request.description }}</p>
              </div>
              <div v-if="order.revision_request.changes_required && order.revision_request.changes_required.length > 0" class="bg-white rounded-lg p-4 border border-orange-200">
                <h4 class="font-semibold text-gray-900 mb-2">Specific Changes Required</h4>
                <ul class="list-disc list-inside space-y-1 text-sm text-gray-700">
                  <li v-for="(change, idx) in order.revision_request.changes_required" :key="idx">
                    <span v-if="change.section" class="font-medium">{{ change.section }}:</span>
                    <span v-if="change.issue">{{ change.issue }}</span>
                    <span v-if="change.request" class="text-gray-600"> - {{ change.request }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card p-6">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Edit Mode Toggle Button (Admin/SuperAdmin/Support) -->
        <div v-if="authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport" class="flex justify-end">
          <button
            @click="editingOrderDetails = !editingOrderDetails"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2',
              editingOrderDetails
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            ]"
          >
            <svg v-if="!editingOrderDetails" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>{{ editingOrderDetails ? 'Cancel Edit' : 'Edit Order Details' }}</span>
          </button>
        </div>

        <!-- Inline Edit Form (Admin/SuperAdmin/Support) -->
        <div v-if="editingOrderDetails && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-blue-300 dark:border-blue-700 shadow-lg p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-xl">
              ✏️
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">Edit Order Details</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">Modify order information, deadlines, pricing, and instructions</p>
            </div>
          </div>
          <EditOrderInline
            :order="order"
            @success="handleEditOrderSuccess"
            @error="handleEditOrderError"
          />
        </div>

        <!-- Order Details Grid (Read-only view when not editing) -->
        <div v-if="!editingOrderDetails" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                      <div class="flex items-center gap-1.5 shrink-0">
                        <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span class="whitespace-nowrap">{{ formatDateTime(entry.timestamp) }}</span>
                  </div>
                      <span v-if="entry.relativeTime" class="flex items-center gap-1.5 text-gray-400 dark:text-gray-500 shrink-0">
                        <span class="w-1 h-1 rounded-full bg-gray-400 dark:bg-gray-500 shrink-0"></span>
                        <span class="italic">{{ entry.relativeTime }}</span>
                      </span>
                    </div>
                    
                    <!-- Description with enhanced styling and proper spacing -->
                    <div 
                      v-if="entry.description" 
                      class="text-sm text-gray-600 dark:text-gray-300 mt-3.5 pl-4 pr-3 py-2.5 border-l-2 border-primary-200 dark:border-primary-700 bg-gray-50 dark:bg-gray-900/50 rounded-r-md"
                    >
                      <div class="flex items-start gap-2.5">
                        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <!-- Payment & Installments (Clients/Admins/Support only) -->
            <div
              v-if="authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport"
              class="bg-white rounded-lg border border-gray-200 p-4"
            >
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

            <!-- Writer Earnings (Writer-only view) -->
            <div
              v-if="authStore.isWriter && (order.writer_compensation || order.writer_compensation === 0)"
              class="bg-white rounded-lg border border-gray-200 p-4"
            >
              <h3 class="text-lg font-semibold mb-3 text-gray-900">Your Earnings for This Order</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Base Compensation</span>
                  <span class="text-gray-900 font-semibold">
                    {{ formatCurrency(order.writer_compensation || 0) }}
                  </span>
                </div>
                <p class="text-xs text-gray-500">
                  This is your agreed payout for this order. Tips and bonuses (if any) will appear in your wallet and earnings dashboards; client payment totals and installment plans remain private.
                </p>
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

        <!-- Revision Notes & Instructions Section -->
        <div v-if="order.status === 'revision_requested' || orderReasons.length > 0 || canAddRevisionNotes" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-xl">
                📝
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Revision Notes & Instructions</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Additional notes and instructions for revisions</p>
              </div>
            </div>
            <!-- Add Revision Note Button (Client, Admin, Support) -->
            <button
              v-if="canAddRevisionNotes"
              @click="addNewReasonInline"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Add Note
            </button>
          </div>
          
          <!-- Add New Revision Note Inline Editor -->
          <div v-if="showAddReasonInline && canAddRevisionNotes" class="mb-6 bg-blue-50 dark:bg-blue-900/10 border-2 border-blue-300 dark:border-blue-700 rounded-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <h4 class="font-semibold text-gray-900 dark:text-white">Add Revision Note</h4>
              <button
                @click="cancelAddReason"
                class="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div class="space-y-4">
              <div>
                <RichTextEditor
                  v-model="reasonForm.reason"
                  label="Revision Note/Instructions"
                  :required="true"
                  placeholder="Enter additional notes or instructions for the revision..."
                  height="200px"
                />
              </div>
              
              <div class="flex gap-2 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  @click="cancelAddReason"
                  class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                  :disabled="savingReason"
                >
                  Cancel
                </button>
                <button
                  @click="saveReason"
                  :disabled="savingReason || !reasonForm.reason.trim()"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {{ savingReason ? 'Saving...' : 'Save Note' }}
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="orderReasons.length === 0 && !showAddReasonInline" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>No revision notes added yet.</p>
            <p v-if="canAddRevisionNotes" class="text-sm mt-2">
              Click "Add Note" to provide additional revision instructions or notes.
            </p>
          </div>
          
          <div v-else class="space-y-4">
            <div
              v-for="(reason, index) in orderReasons"
              :key="index"
              class="border-l-4 pl-4 py-3 rounded-r-lg relative"
              :class="getReasonBorderClass(reason.type)"
            >
              <!-- View Mode -->
              <div v-if="editingReasonIndex !== index" class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-lg">📝</span>
                    <h4 class="font-semibold text-gray-900 dark:text-white">Revision Note</h4>
                    <span v-if="reason.user" class="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                      {{ reason.user }}
                    </span>
                  </div>
                  <div class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm max-w-none">
                    <SafeHtml :html="reason.reason || reason.notes || 'No reason provided'" />
                  </div>
                  <div v-if="reason.timestamp" class="mt-2 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{{ formatDateTime(reason.timestamp) }}</span>
                    <span v-if="reason.user" class="text-gray-400">•</span>
                    <span v-if="reason.user" class="font-medium">{{ reason.user }}</span>
                  </div>
                  <div v-if="reason.resolution" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                    <p class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Resolution:</p>
                    <div class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm max-w-none">
                      <SafeHtml :html="reason.resolution" />
                    </div>
                  </div>
                </div>
                <!-- Edit Button (Admin, Support, or original author) -->
                <button
                  v-if="canEditRevisionNote(reason)"
                  @click="startEditReason(reason, index)"
                  class="p-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  title="Edit note"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
              
              <!-- Edit Mode -->
              <div v-else-if="canEditRevisionNote(reason)" class="space-y-4">
                <div class="flex items-center justify-between">
                  <h4 class="font-semibold text-gray-900 dark:text-white">Edit Revision Note</h4>
                  <button
                    @click="cancelEditReason"
                    class="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div>
                  <RichTextEditor
                    v-model="reasonForm.reason"
                    label="Revision Note/Instructions"
                    :required="true"
                    placeholder="Enter revision notes or instructions..."
                    height="200px"
                  />
                </div>
                
                <div class="flex gap-2 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    @click="cancelEditReason"
                    class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                    :disabled="savingReason"
                  >
                    Cancel
                  </button>
                  <button
                    @click="saveReason"
                    :disabled="savingReason || !reasonForm.reason.trim()"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {{ savingReason ? 'Saving...' : 'Update Note' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Instructions - Full Width -->
        <div
          v-if="order.instructions || order.order_instructions || (isAdmin && editingInstructions)"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Order Instructions
            </h3>
            <button
              v-if="isAdmin"
              type="button"
              @click="toggleInstructionsEdit"
              class="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <span v-if="editingInstructions">Done</span>
              <span v-else>Edit</span>
            </button>
          </div>

          <!-- Admin editable instructions -->
          <div v-if="isAdmin && editingInstructions" class="space-y-3">
            <RichTextEditor
              v-model="editableInstructions"
              placeholder="Edit order instructions..."
              toolbar="full"
              height="220px"
              :allow-images="true"
            />
            <div class="flex justify-end gap-2">
              <button
                type="button"
                @click="cancelInstructionsEdit"
                class="px-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                :disabled="savingInstructions"
              >
                Cancel
              </button>
              <button
                type="button"
                @click="saveInstructions"
                class="px-4 py-1.5 text-xs bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                :disabled="savingInstructions"
              >
                {{ savingInstructions ? 'Saving...' : 'Save Instructions' }}
              </button>
            </div>
          </div>

          <!-- Read-only instructions (all roles) -->
          <div v-else class="prose prose-sm max-w-none dark:prose-invert">
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
        
        <!-- Progress Bar (for clients, also visible to admin/support) -->
        <div
          v-if="(authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) && order.assigned_writer"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Order Progress</h3>
          <ProgressBar
            :progress-percentage="displayProgressPercentage"
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
            
            <!-- Extend Deadline -->
            <button
              v-if="canRequestDeadlineExtension"
              @click="showDeadlineExtensionModal = true"
              class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
            >
              <span>⏰</span>
              <span>Extend Deadline</span>
            </button>
            
            <!-- Put on Hold -->
            <button
              v-if="canRequestHold"
              @click="showHoldRequestModal = true"
              class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2"
            >
              <span>🛑</span>
              <span>Put on Hold</span>
            </button>
            </template>
          </div>
          
          <!-- Admin/Superadmin/Support Actions - Use Modal -->
          <div
            v-if="(authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) && order"
            class="flex flex-wrap gap-2"
          >
            <!-- Auto-Assign Button (primary) -->
            <NaiveButton
              v-if="canAutoAssign"
              type="primary"
              size="small"
              :loading="autoAssigning"
              @click="showAutoAssignModal = true"
            >
              <template #icon>
                <span>🤖</span>
              </template>
              {{ autoAssigning ? 'Assigning…' : 'Auto-Assign' }}
            </NaiveButton>

            <!-- Smart Match Button (secondary) -->
            <NaiveButton
              v-if="canAutoAssign"
              type="info"
              size="small"
              :loading="loadingSmartMatches"
              @click="loadSmartMatches"
            >
              <template #icon>
                <span>🎯</span>
              </template>
              {{ loadingSmartMatches ? 'Loading…' : 'Smart Match' }}
            </NaiveButton>

            <!-- Order Actions - Navigate to Actions Tab -->
            <NaiveButton
              type="default"
              size="small"
              @click="activeTab = 'actions'"
            >
              <template #icon>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                  />
                </svg>
              </template>
              Order Actions
            </NaiveButton>
          </div>
          
          <!-- Soft Delete / Restore Actions (Admin/Support only) -->
          <div v-if="(authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) && order" class="flex flex-wrap gap-2 w-full mt-2 pt-2 border-t border-gray-200">
            <button
              v-if="!order.is_deleted"
              @click="softDeleteOrder"
              :disabled="processingAction"
              class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span>🗑️</span>
              <span>{{ processingAction ? 'Processing...' : 'Soft Delete' }}</span>
            </button>
            
            <button
              v-if="order.is_deleted"
              @click="restoreOrder"
              :disabled="processingAction"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span>♻️</span>
              <span>{{ processingAction ? 'Processing...' : 'Restore Order' }}</span>
            </button>
            
            <button
              v-if="order.is_deleted && (authStore.isAdmin || authStore.isSuperAdmin)"
              @click="hardDeleteOrder"
              :disabled="processingAction"
              class="px-4 py-2 bg-red-700 text-white rounded-lg hover:bg-red-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span>⚠️</span>
              <span>{{ processingAction ? 'Processing...' : 'Permanently Delete' }}</span>
            </button>
          </div>
          
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
        <!-- Progress Bar (for clients, also visible to admin/support) -->
        <div
          v-if="authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport"
          class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
        >
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
            :progress-percentage="displayProgressPercentage"
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
              class="mt-4 p-5 bg-gradient-to-r from-green-50 via-emerald-50 to-green-50 dark:from-green-900/30 dark:via-emerald-900/30 dark:to-green-900/30 border-3 border-green-400 dark:border-green-600 rounded-xl flex items-center justify-between shadow-lg animate-pulse-once"
            >
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-green-200 dark:bg-green-800 rounded-xl flex items-center justify-center shadow-md">
                  <svg class="w-8 h-8 text-green-700 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <p class="text-base font-bold text-green-900 dark:text-green-100">
                      ✅ Final Paper Ready
                    </p>
                    <span class="px-2 py-0.5 bg-green-200 dark:bg-green-800 text-green-900 dark:text-green-100 rounded-full text-xs font-bold uppercase tracking-wide">
                      Final Draft
                    </span>
                  </div>
                  <p class="text-sm text-green-700 dark:text-green-300">
                    Version {{ finalPaperFile.version || '1' }} • 
                    {{ formatDateTime(finalPaperFile.created_at) }}
                    <span v-if="finalPaperFile.download_count" class="ml-2">
                      • Downloaded {{ finalPaperFile.download_count }} time{{ finalPaperFile.download_count !== 1 ? 's' : '' }}
                    </span>
                  </p>
                  <p v-if="finalPaperFile.file_name" class="text-xs text-green-600 dark:text-green-400 mt-1 font-mono">
                    📄 {{ finalPaperFile.file_name }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <button
                  v-if="authStore.isAdmin || authStore.isSuperAdmin"
                  @click="toggleFileDownload(finalPaperFile)"
                  :class="[
                    'px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                    finalPaperFile.is_downloadable 
                      ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' 
                      : 'bg-red-100 text-red-800 hover:bg-red-200'
                  ]"
                  :title="finalPaperFile.is_downloadable ? 'Lock file' : 'Unlock file'"
                >
                  {{ finalPaperFile.is_downloadable ? '🔓 Unlock' : '🔒 Lock' }}
                </button>
                <button
                  @click="downloadFile(finalPaperFile)"
                  class="px-5 py-3 bg-green-600 dark:bg-green-700 text-white rounded-lg hover:bg-green-700 dark:hover:bg-green-600 text-sm font-bold flex items-center gap-2 shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download Final Paper
                </button>
              </div>
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

        <!-- Quick Upload Button (Writers) -->
        <div v-if="authStore.isWriter" class="mb-4">
          <button
            @click="showQuickUpload = !showQuickUpload"
            class="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 font-semibold flex items-center justify-center gap-2 shadow-md transition-all transform hover:scale-[1.02]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            {{ showQuickUpload ? 'Hide Quick Upload' : 'Quick Upload Files' }}
          </button>
        </div>

        <!-- File Upload Form -->
        <div v-if="!authStore.isWriter || showQuickUpload" class="mb-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 shadow-sm">
          <h4 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            {{ authStore.isWriter ? 'Quick Upload' : 'Upload Files' }}
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
                  <!-- Role-based category suggestions -->
                  <optgroup v-if="authStore.isWriter && writerCategorySuggestions.length > 0" label="Suggested for Writers">
                    <option v-for="suggestion in writerCategorySuggestions" :key="`suggest-${suggestion}`" :value="null" disabled class="text-gray-500 italic">
                      {{ suggestion }} (create category to use)
                    </option>
                  </optgroup>
                  <optgroup v-if="authStore.isClient && clientCategorySuggestions.length > 0" label="Suggested for Clients">
                    <option v-for="suggestion in clientCategorySuggestions" :key="`suggest-${suggestion}`" :value="null" disabled class="text-gray-500 italic">
                      {{ suggestion }} (create category to use)
                    </option>
                  </optgroup>
                  <!-- Universal categories (available to all websites) -->
                  <optgroup v-if="universalCategories.length > 0" label="Universal Categories">
                    <option v-for="category in universalCategories" :key="category.id" :value="category.id">
                      {{ category.name }}
                      <span v-if="category.is_final_draft"> (Final Draft)</span>
                      <span v-if="category.is_extra_service"> (Extra Service)</span>
                    </option>
                  </optgroup>
                  <!-- Website-specific categories -->
                  <optgroup v-if="websiteSpecificCategories.length > 0" label="Website-Specific Categories">
                    <option v-for="category in websiteSpecificCategories" :key="category.id" :value="category.id">
                      {{ category.name }}
                      <span v-if="category.is_final_draft"> (Final Draft)</span>
                      <span v-if="category.is_extra_service"> (Extra Service)</span>
                    </option>
                  </optgroup>
                </select>
                <p class="text-xs text-gray-500 mt-1">
                  <span v-if="authStore.isWriter">Common categories: Final Draft, First Draft, DRAFT, Outline, Resource, Plagiarism Report, AI Similarity Report</span>
                  <span v-else-if="authStore.isClient">Common categories: Materials, Sample, My Previous Papers, Friends Paper, Reading Materials, Syllabus, Rubric, Guidelines</span>
                </p>
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
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ uploadSuccess }}
            </div>
            <div v-if="uploadError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300 flex items-center gap-2">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

        <!-- Eligibility Check (Client; also visible read-only to admin/support) -->
        <div
          v-if="(authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) && draftEligibility"
          class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border-2 border-blue-200 dark:border-blue-800 p-6 shadow-sm"
        >
          <div class="flex items-start gap-4">
            <div class="shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
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
                    <span v-if="request.deadline" class="ml-2 font-semibold text-orange-600">
                      • Deadline: {{ formatDateTime(request.deadline) }}
                    </span>
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

      <!-- Actions Tab -->
      <div v-if="activeTab === 'actions'" class="space-y-6">
        <div class="bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-xl border-2 border-primary-200 dark:border-primary-800 p-6 mb-6">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-2xl">
              ⚡
            </div>
            <div class="flex-1">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">Order Actions</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Manage this order with inline actions. Expand any section to perform actions. All actions are logged and tracked.
              </p>
            </div>
          </div>
        </div>

        <!-- Inline Actions Component (Admin/SuperAdmin/Support) -->
        <div v-if="authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport">
          <InlineOrderActions
            :order="order"
            :available-actions="availableActions"
            @success="handleInlineActionSuccess"
            @error="handleInlineActionError"
          />
        </div>

        <!-- Admin/SuperAdmin/Support Actions (Legacy - keeping for reference) -->
        <div v-if="false && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)" class="space-y-6">
          <!-- Status Management -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                <span class="text-xl">🔄</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Status Management</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Change order status and workflow state</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <button
                v-if="order.status !== 'on_hold'"
                @click="handleStatusChange('on_hold')"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 text-yellow-700 dark:text-yellow-300 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">⏸️</span>
                <span>Put on Hold</span>
              </button>
              <button
                v-if="order.status === 'on_hold'"
                @click="handleStatusChange('in_progress')"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-green-50 dark:bg-green-900/20 border-2 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">▶️</span>
                <span>Resume Order</span>
              </button>
              <button
                v-if="!['cancelled', 'completed', 'closed'].includes(order.status)"
                @click="handleCancelOrder"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">❌</span>
                <span>Cancel Order</span>
              </button>
              <button
                v-if="!['archived', 'cancelled'].includes(order.status)"
                @click="handleArchiveOrder"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-gray-50 dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">📦</span>
                <span>Archive Order</span>
              </button>
            </div>
          </div>

          <!-- Writer Assignment -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                <span class="text-xl">👤</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Writer Assignment</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Assign or reassign a writer to this order</p>
              </div>
            </div>
            <div class="space-y-4">
              <div v-if="order.assigned_writer || order.writer_id" class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Current Writer</p>
                    <p class="text-base font-semibold text-gray-900 dark:text-white mt-1">
                      {{ order.assigned_writer?.username || order.writer_username || 'Unknown' }}
                    </p>
                  </div>
                  <button
                    v-if="order.is_paid"
                    @click="showReassignModal = true"
                    :disabled="processingAction"
                    class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium disabled:opacity-50"
                  >
                    Reassign
                  </button>
                  <button
                    v-else
                    @click="showUnpaidWarningModal = true"
                    class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium"
                    title="Order must be paid before reassigning"
                  >
                    ⚠️ Reassign
                  </button>
                </div>
              </div>
              <div v-else class="space-y-3">
                <button
                  v-if="!order.assigned_writer && !order.writer_id && !order.writer_username && order.is_paid"
                  @click="showAssignModal = true"
                  :disabled="processingAction"
                  class="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <span>➕</span>
                  <span>Assign Writer</span>
                </button>
                <div v-else-if="!order.assigned_writer && !order.writer_id && !order.writer_username && !order.is_paid" class="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <div class="flex items-start gap-3">
                    <span class="text-xl">⚠️</span>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                        Order Not Paid
                      </p>
                      <p class="text-xs text-yellow-700 dark:text-yellow-300">
                        Only paid orders can be assigned to writers. Please mark this order as paid first.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
                <span class="text-xl">⚡</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Common administrative tasks</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                @click="activeTab = 'messages'"
                class="flex items-center gap-3 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-all font-medium"
              >
                <span class="text-xl">💬</span>
                <span>View Messages</span>
              </button>
              <button
                @click="activeTab = 'files'"
                class="flex items-center gap-3 px-4 py-3 bg-green-50 dark:bg-green-900/20 border-2 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-all font-medium"
              >
                <span class="text-xl">📁</span>
                <span>Manage Files</span>
              </button>
              <button
                v-if="authStore.isAdmin || authStore.isSuperAdmin"
                @click="activeTab = 'history'"
                class="flex items-center gap-3 px-4 py-3 bg-gray-50 dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-all font-medium"
              >
                <span class="text-xl">🕒</span>
                <span>View Timeline</span>
              </button>
              <button
                @click="showEditInstructions = true"
                class="flex items-center gap-3 px-4 py-3 bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-300 dark:border-orange-700 text-orange-700 dark:text-orange-300 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-all font-medium"
              >
                <span class="text-xl">✏️</span>
                <span>Edit Instructions</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Writer Actions -->
        <div v-if="authStore.isWriter" class="space-y-6">
          <!-- Order Status Actions -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                <span class="text-xl">📝</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Work Status</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Update your progress on this order</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                v-if="order.status === 'pending_writer_assignment' || order.status === 'available'"
                @click="handleStatusChange('in_progress')"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-green-50 dark:bg-green-900/20 border-2 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">▶️</span>
                <span>Start Working</span>
              </button>
              <button
                v-if="order.status === 'in_progress'"
                @click="handleSubmitOrder"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">✅</span>
                <span>Submit Order</span>
              </button>
            </div>
          </div>

          <!-- Communication -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                <span class="text-xl">💬</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Communication</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Contact client or admin about this order</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                @click="activeTab = 'messages'"
                class="flex items-center gap-3 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-all font-medium"
              >
                <span class="text-xl">💬</span>
                <span>View Messages</span>
              </button>
              <button
                @click="activeTab = 'files'"
                class="flex items-center gap-3 px-4 py-3 bg-green-50 dark:bg-green-900/20 border-2 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-all font-medium"
              >
                <span class="text-xl">📁</span>
                <span>Upload Files</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Client Actions -->
        <div v-if="authStore.isClient" class="space-y-6">
          <!-- Order Management -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center">
                <span class="text-xl">📋</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Order Management</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Manage your order</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                v-if="canRequestRevision"
                @click="showRevisionForm = !showRevisionForm"
                class="flex items-center gap-3 px-4 py-3 bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-300 dark:border-orange-700 text-orange-700 dark:text-orange-300 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-all font-medium"
              >
                <span class="text-xl">🔄</span>
                <span>{{ showRevisionForm ? 'Cancel Revision Request' : 'Request Revision' }}</span>
              </button>
              <button
                v-if="['pending', 'in_progress'].includes(order.status)"
                @click="handleCancelOrder"
                :disabled="processingAction"
                class="flex items-center gap-3 px-4 py-3 bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-all font-medium disabled:opacity-50"
              >
                <span class="text-xl">❌</span>
                <span>Cancel Order</span>
              </button>
            </div>
          </div>

          <!-- Communication -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                <span class="text-xl">💬</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Communication</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Contact your writer or support</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                @click="activeTab = 'messages'"
                class="flex items-center gap-3 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-all font-medium"
              >
                <span class="text-xl">💬</span>
                <span>Message Writer</span>
              </button>
              <button
                v-if="order.status === 'completed' || order.status === 'submitted'"
                @click="activeTab = 'files'"
                class="flex items-center gap-3 px-4 py-3 bg-green-50 dark:bg-green-900/20 border-2 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-all font-medium"
              >
                <span class="text-xl">📥</span>
                <span>Download Files</span>
              </button>
            </div>
          </div>

          <!-- Payment Actions -->
          <div v-if="order.payment_status !== 'paid'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-yellow-100 dark:bg-yellow-900/50 flex items-center justify-center">
                <span class="text-xl">💳</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Payment</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Complete payment to start your order</p>
              </div>
            </div>
            <button
              @click="handlePayment"
              class="w-full px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center justify-center gap-2"
            >
              <span>💳</span>
              <span>Pay Now</span>
            </button>
          </div>
        </div>

        <!-- Action Status Messages -->
        <div v-if="actionError" class="bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-700 rounded-lg p-4">
          <div class="flex items-center gap-3">
            <span class="text-xl">⚠️</span>
            <p class="text-sm font-medium text-red-700 dark:text-red-300">{{ actionError }}</p>
          </div>
        </div>
        <div v-if="actionSuccess" class="bg-green-50 dark:bg-green-900/20 border-2 border-green-300 dark:border-green-700 rounded-lg p-4">
          <div class="flex items-center gap-3">
            <span class="text-xl">✅</span>
            <p class="text-sm font-medium text-green-700 dark:text-green-300">{{ actionSuccess }}</p>
          </div>
        </div>
      </div>

      <!-- History Tab (Admin / Support) -->
      <div
        v-if="activeTab === 'history' && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
        class="space-y-6"
      >
        <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
          <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100 tracking-wide uppercase">
                Order History
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                Timeline of status changes and key system actions for this order.
              </p>
            </div>
          </div>
          <div class="p-4">
            <div
              v-if="!statusTimeline.length"
              class="text-center py-8 text-sm text-gray-500 dark:text-gray-400"
            >
              No history entries available.
            </div>
            <ol v-else class="relative border-l border-gray-200 dark:border-gray-700">
              <li
                v-for="item in statusTimeline"
                :key="item.key"
                class="mb-6 ml-6"
              >
                <span
                  class="absolute flex items-center justify-center w-6 h-6 rounded-full -left-3 ring-4 ring-white dark:ring-gray-900 bg-primary-100 dark:bg-primary-900 text-xs"
                >
                  {{ item.icon }}
                </span>
                <h3 class="flex items-center text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ item.label }}
                  <span
                    v-if="item.source === 'transition_log'"
                    class="ml-2 px-2 py-0.5 text-[10px] font-semibold rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
                  >
                    Log
                  </span>
                </h3>
                <time class="block mb-1 text-xs font-normal leading-none text-gray-400 dark:text-gray-500">
                  {{ formatDateTime(item.timestamp) }} • {{ item.relativeTime }}
                </time>
                <p
                  v-if="item.description"
                  class="mb-2 text-xs font-normal text-gray-600 dark:text-gray-300"
                >
                  {{ item.description }}
                </p>
              </li>
            </ol>
          </div>
        </div>
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
                <div class="shrink-0">
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
                <div class="shrink-0 text-gray-400">
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
              <div class="shrink-0">
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

    <!-- Order Action Modal - Disabled for Admin/Superadmin/Support (using inline actions instead) -->
    <!-- <OrderActionModal
      v-if="false && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
      v-model:visible="showActionModal"
      :order="order"
      :selected-action="selectedAction"
      :available-actions="availableActions"
      :available-writers="availableWriters"
      @success="handleActionSuccess"
      @error="handleActionError"
    /> -->
    
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
    
    <!-- Draft Request Modal -->
    <Modal
      v-model:visible="showDraftRequestModal"
      title="Request Draft"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <p><strong>Note:</strong> Request a draft to see order progress before final submission. The writer will be notified and can upload a draft file for your review.</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Message (Optional)
          </label>
          <textarea
            v-model="draftRequestForm.message"
            rows="4"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Optional message about what you'd like to see in the draft..."
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Draft Deadline <span class="text-gray-400">(Optional)</span>
          </label>
          <input
            v-model="draftRequestForm.deadline"
            type="datetime-local"
            :min="new Date().toISOString().slice(0, 16)"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Select deadline for draft delivery"
          />
          <p class="text-xs text-gray-500 mt-1">If not specified, the writer will deliver the draft at their convenience.</p>
        </div>
        
        <div class="flex gap-2 justify-end">
          <button
            @click="showDraftRequestModal = false"
            class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            :disabled="creatingDraftRequest"
          >
            Cancel
          </button>
          <button
            @click="createDraftRequest"
            :disabled="creatingDraftRequest"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {{ creatingDraftRequest ? 'Submitting...' : 'Submit Request' }}
          </button>
        </div>
      </div>
    </Modal>

    <!-- Unpaid Order Warning Modal -->
    <Modal
      v-model:visible="showUnpaidWarningModal"
      title="Order Not Paid"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div class="flex items-start gap-3">
            <span class="text-2xl">⚠️</span>
            <div class="flex-1">
              <p class="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                Cannot Assign Writer
              </p>
              <p class="text-sm text-yellow-700 dark:text-yellow-300">
                Only paid orders can be assigned to writers. This order has not been marked as paid yet.
              </p>
            </div>
          </div>
        </div>
        
        <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
          <p class="text-sm text-gray-700 dark:text-gray-300 mb-2">
            <strong>To assign a writer:</strong>
          </p>
          <ol class="list-decimal list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>Mark this order as paid first</li>
            <li>Then proceed with writer assignment</li>
          </ol>
        </div>
        
        <div class="flex gap-2 justify-end">
          <button
            @click="showUnpaidWarningModal = false"
            class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
          <button
            v-if="authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport"
            @click="showUnpaidWarningModal = false; activeTab = 'actions'"
            class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            Go to Actions Tab
          </button>
        </div>
      </div>
    </Modal>

    <!-- Extend Deadline Modal -->
    <Modal
      v-model:visible="showDeadlineExtensionModal"
      title="Extend Deadline"
      size="md"
    >
      <div class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <p><strong>Note:</strong> Please provide a clear reason for extending the deadline. The client will review and approve this change.</p>
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
            New Deadline <span class="text-red-500">*</span>
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
            placeholder="Explain why you need to extend the deadline..."
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
            {{ submittingDeadlineExtension ? 'Submitting...' : 'Submit' }}
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

    <!-- Submit Order Checklist Modal -->
    <Modal
      v-model:visible="showSubmitChecklist"
      title="Pre-Submission Checklist"
      size="lg"
    >
      <div class="space-y-6">
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <p class="text-sm text-blue-800">
            <strong>Before submitting:</strong> Please verify that you've completed all the items below. This ensures quality and helps avoid revision requests.
          </p>
        </div>

        <div class="space-y-4">
          <!-- Word Count Check -->
          <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 :class="submitChecklist.wordCountMet ? 'border-green-500 bg-green-50' : 'border-gray-200'">
            <input
              type="checkbox"
              v-model="submitChecklist.wordCountMet"
              class="mt-1 w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <div class="flex-1">
              <p class="font-semibold text-gray-900">Word Count Met</p>
              <p class="text-sm text-gray-600 mt-1">I have verified that the paper meets the required word count/page count specified in the order.</p>
            </div>
          </label>

          <!-- Revised Check -->
          <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 :class="submitChecklist.revised ? 'border-green-500 bg-green-50' : 'border-gray-200'">
            <input
              type="checkbox"
              v-model="submitChecklist.revised"
              class="mt-1 w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <div class="flex-1">
              <p class="font-semibold text-gray-900">Revised</p>
              <p class="text-sm text-gray-600 mt-1">I have reviewed and revised the paper to ensure it meets all requirements and quality standards.</p>
            </div>
          </label>

          <!-- Edited Check -->
          <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 :class="submitChecklist.edited ? 'border-green-500 bg-green-50' : 'border-gray-200'">
            <input
              type="checkbox"
              v-model="submitChecklist.edited"
              class="mt-1 w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <div class="flex-1">
              <p class="font-semibold text-gray-900">Edited</p>
              <p class="text-sm text-gray-600 mt-1">I have edited the paper for grammar, spelling, punctuation, and style consistency.</p>
            </div>
          </label>

          <!-- Requirements Met Check -->
          <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                 :class="submitChecklist.requirementsMet ? 'border-green-500 bg-green-50' : 'border-gray-200'">
            <input
              type="checkbox"
              v-model="submitChecklist.requirementsMet"
              class="mt-1 w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <div class="flex-1">
              <p class="font-semibold text-gray-900">All Requirements Met</p>
              <p class="text-sm text-gray-600 mt-1">I have reviewed the order instructions and confirmed that all requirements, guidelines, and specifications have been met.</p>
            </div>
          </label>

          <!-- Final File Selected Check -->
          <label class="flex items-start gap-3 p-4 border-2 rounded-lg"
                 :class="submitChecklist.finalFileSelected ? 'border-green-500 bg-green-50' : 'border-red-200 bg-red-50'">
            <input
              type="checkbox"
              v-model="submitChecklist.finalFileSelected"
              disabled
              class="mt-1 w-5 h-5 text-green-600 border-gray-300 rounded"
            />
            <div class="flex-1">
              <p class="font-semibold" :class="submitChecklist.finalFileSelected ? 'text-gray-900' : 'text-red-900'">
                Final File Marked
              </p>
              <p class="text-sm mt-1" :class="submitChecklist.finalFileSelected ? 'text-gray-600' : 'text-red-700'">
                <span v-if="submitChecklist.finalFileSelected">
                  ✓ A file has been marked as the final paper.
                </span>
                <span v-else>
                  ⚠️ You must upload and mark a file as "Final Paper" before submitting. Go to the Files tab to upload and mark your final file.
                </span>
              </p>
            </div>
          </label>
        </div>

        <div v-if="!canProceedWithSubmission" class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
          <p class="text-sm text-yellow-800">
            Please complete all checklist items above before proceeding with submission.
          </p>
        </div>
      </div>

      <template #footer>
        <button
          @click="closeSubmitChecklist"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="submitOrder"
          :disabled="!canProceedWithSubmission || processingAction"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ processingAction ? 'Submitting...' : 'Submit Order' }}
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
import { useRoute, useRouter } from 'vue-router'
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
// import OrderActionModal from '@/components/order/OrderActionModal.vue' // Disabled - using inline actions instead
import InlineOrderActions from '@/components/order/InlineOrderActions.vue'
import EditOrderInline from '@/components/order/actions/EditOrderInline.vue'
import usersAPI from '@/api/users'
import { getErrorMessage, getSuccessMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useInputModal } from '@/composables/useInputModal'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import EnhancedStatusBadge from '@/components/common/EnhancedStatusBadge.vue'
import { getStatusConfig, getStatusLabel, getStatusIcon } from '@/utils/orderStatus'
import EnhancedOrderStatus from '@/components/client/EnhancedOrderStatus.vue'
import InputModal from '@/components/common/InputModal.vue'
import draftRequestsAPI from '@/api/draft-requests'
import writerManagementAPI from '@/api/writer-management'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import writerDashboardAPI from '@/api/writer-dashboard'
import { loadUnreadMessageCount } from '@/utils/messageUtils'
import NaiveButton from '@/components/naive/NaiveButton.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Helper functions for admin route detection
const isAdminRoute = computed(() => {
  return route.path.startsWith('/admin/orders/')
})

const getBackRoute = () => {
  if (isAdminRoute.value) {
    return { name: 'OrderManagement' }
  }
  return authStore.isWriter ? { name: 'WriterMyOrders' } : { name: 'Orders' }
}

const getBackButtonText = () => {
  if (isAdminRoute.value) {
    return 'Back to Order Management'
  }
  return 'Back to Orders'
}
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
const tabs = computed(() => {
  const baseTabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'enhanced-status', label: 'Enhanced Status', icon: '📈' },
    { id: 'progress', label: 'Progress', icon: '📊' },
    { id: 'messages', label: 'Messages', icon: '💬' },
    { id: 'files', label: 'Files', icon: '📁' },
    { id: 'draft-requests', label: 'Draft Requests', icon: '📝' },
    { id: 'links', label: 'External Links', icon: '🔗' },
    { id: 'actions', label: 'Actions', icon: '⚡' }, // Actions tab for all users
  ]

  // Admins and support see an additional "History" tab
  if (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) {
    baseTabs.push({ id: 'history', label: 'History', icon: '🕒' })
  }

  return baseTabs
})
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

// Inline edit mode for Overview tab (admin/superadmin/support)
const editingOrderDetails = ref(false)

// Load available actions for the order
const loadAvailableActions = async () => {
  if (!order.value) return
  try {
    const response = await ordersAPI.getAvailableActions(order.value.id)
    if (response.data && response.data.available_actions) {
      availableActions.value = response.data.available_actions
    }
  } catch (error) {
    console.error('Failed to load available actions:', error)
    availableActions.value = []
  }
}

// Draft Request state
const draftRequests = ref([])
const loadingDraftRequests = ref(false)
const draftEligibility = ref(null)
const loadingDraftEligibility = ref(false)
const showDraftRequestModal = ref(false)
const draftRequestForm = ref({ message: '', deadline: '' })
const creatingDraftRequest = ref(false)
const uploadingDraft = ref({})
const draftSelectedFiles = ref({})
const draftFileDescriptions = ref({})
const draftFileInputs = ref({})

const isAdmin = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'superadmin'
})

// Admin instructions editing state
const editingInstructions = ref(false)
const editableInstructions = ref('')
const savingInstructions = ref(false)

const toggleInstructionsEdit = () => {
  if (!order.value) return
  // Initialize editor with current instructions when entering edit mode
  if (!editingInstructions.value) {
    editableInstructions.value = order.value.instructions || order.value.order_instructions || ''
  }
  editingInstructions.value = !editingInstructions.value
}

const cancelInstructionsEdit = () => {
  editingInstructions.value = false
  editableInstructions.value = ''
}

const saveInstructions = async () => {
  if (!order.value) return
  savingInstructions.value = true
  try {
    const payload = {
      order_instructions: editableInstructions.value,
    }
    const response = await ordersAPI.patch(order.value.id, payload)
    // Update local order object with latest data
    order.value = response.data || { ...order.value, order_instructions: editableInstructions.value }
    showSuccessToast?.('Instructions updated successfully')
    editingInstructions.value = false
  } catch (error) {
    const msg =
      error?.response?.data?.detail ||
      error?.response?.data?.error ||
      'Failed to update instructions'
    showErrorToast?.(msg)
    if (import.meta.env.DEV) {
      console.error('Failed to update order instructions:', error)
    }
  } finally {
    savingInstructions.value = false
  }
}

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
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isAssignedWriter =
    order.value.writer?.id === userId.value ||
    order.value.writer_id === userId.value ||
    order.value.assigned_writer_id === userId.value

  // Submit is only allowed when at least one Final Paper file has been uploaded.
  // Writers must be the assigned writer; admins/superadmins can submit on behalf of the writer.
  if (!hasFinalPaperFile.value) return false

  const writerCanSubmit =
    isWriter &&
    isAssignedWriter &&
    ['in_progress', 'assigned', 'draft', 'revision_in_progress'].includes(status)

  const adminCanSubmit =
    isAdminLike &&
    ['in_progress', 'assigned', 'draft', 'revision_in_progress', 'submitted'].includes(status)

  return writerCanSubmit || adminCanSubmit
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
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  // Admins/Superadmins can always submit a review on behalf of the client for completed orders
  return (isClient && isOrderClient && order.value.status === 'completed') || (isAdminLike && order.value.status === 'completed')
})

const canRequestRevision = computed(() => {
  if (!order.value) return false
  const isClient = userRole.value === 'client'
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can request revision if order is completed, submitted, or approved
  // Admins/Superadmins can request revision on behalf of client for valid statuses
  return (isClient && isOrderClient && ['completed', 'submitted', 'approved'].includes(status)) ||
    (isAdminLike && ['completed', 'submitted', 'approved'].includes(status))
})

const canTipWriter = computed(() => {
  if (!order.value) return false
  const isClient = userRole.value === 'client'
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isOrderClient = order.value.client?.id === userId.value || order.value.client_id === userId.value
  const hasWriter = order.value.writer_id || order.value.writer?.id
  const status = order.value.status?.toLowerCase()
  // Can tip for completed, submitted, approved, or closed orders
  // Admins/Superadmins can tip on behalf of the client for valid statuses
  return ((isClient && isOrderClient && hasWriter && ['completed', 'submitted', 'approved', 'closed'].includes(status))) ||
    (isAdminLike && hasWriter && ['completed', 'submitted', 'approved', 'closed'].includes(status))
})

const canAutoAssign = computed(() => {
  if (!order.value) return false
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport
  const status = order.value.status?.toLowerCase()
  // Can auto-assign if order is available, pending, or unassigned, and user is admin/support
  return isAdminLike && ['available', 'pending', 'created', 'unpaid'].includes(status) && !order.value.writer_id
})

const canRequestDeadlineExtension = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can request extension for in_progress, assigned, or draft orders
  // Admins/Superadmins can also request extensions for assigned writer orders
  return (isWriter && isAssignedWriter && ['in_progress', 'assigned', 'draft'].includes(status)) ||
    (isAdminLike && ['in_progress', 'assigned', 'draft'].includes(status))
})

const canRequestHold = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can request hold for in_progress, assigned, or draft orders
  // Admins/Superadmins can also request holds for any assigned orders in valid statuses
  return (isWriter && isAssignedWriter && ['in_progress', 'assigned', 'draft'].includes(status)) ||
    (isAdminLike && ['in_progress', 'assigned', 'draft'].includes(status))
})

const canStartOrder = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can start order when it's available or reassigned
  // Admins/Superadmins can also start orders in valid statuses
  return (isWriter && isAssignedWriter && ['available', 'reassigned'].includes(status)) ||
    (isAdminLike && ['available', 'reassigned'].includes(status))
})

const canStartRevision = computed(() => {
  if (!order.value) return false
  const isWriter = userRole.value === 'writer'
  const isAdminLike = authStore.isAdmin || authStore.isSuperAdmin
  const isAssignedWriter = order.value.writer?.id === userId.value || order.value.writer_id === userId.value || order.value.assigned_writer_id === userId.value
  const status = order.value.status?.toLowerCase()
  // Can start revision when revision is requested
  // Admins/Superadmins can also start revisions
  return (isWriter && isAssignedWriter && status === 'revision_requested') ||
    (isAdminLike && status === 'revision_requested')
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

// Status mappings now use centralized orderStatus utility
// Helper functions for backward compatibility
const getStatusLabelFromMap = (status) => getStatusLabel(status)
const getStatusIconFromMap = (status) => getStatusIcon(status)

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
      label: extra.label || getStatusLabel(normalizedStatus) || formatStatusLabel(status),
      timestamp: timestampDate.toISOString(),
      relativeTime: formatRelativeTime(timestamp),
      description: extra.description || null,
      icon: extra.icon || getStatusIcon(normalizedStatus) || '•',
      source: extra.source || 'unknown', // Track data source for debugging
    })
  }

  // 1. Always include creation timestamp
  if (order.value.created_at) {
    pushEntry('created', 'created', order.value.created_at, {
      description: 'Order placed',
      source: 'created_at',
    })
  }

  // 2. Process transition logs (primary source of truth)
  const transitionLogs = Array.isArray(order.value.transitions)
    ? order.value.transitions
    : []
  transitionLogs.forEach((log) => {
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
      const userName =
        log.user?.username || log.user?.full_name || log.user?.email || 'System'
      descriptionParts.push(`by ${userName}`)
    }

    // Add old status context if available
    if (log.old_status && log.old_status.toLowerCase() !== newStatus) {
      descriptionParts.push(`from ${formatStatusLabel(log.old_status)}`)
    }

    pushEntry(`transition-${log.id || Date.now()}`, newStatus, log.timestamp, {
      description:
        descriptionParts.length > 0 ? descriptionParts.join(' • ') : null,
      source: 'transition_log',
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

// Extract reasons from order for display
// Only show revision-related notes (not cancellation, dispute, refund reasons - those are in transitions)
const orderReasons = computed(() => {
  if (!order.value) return []
  
  const reasons = []
  
  // Only check for revision-related notes from completion_notes (primary location)
  if (order.value.completion_notes) {
    try {
      const notesObj = typeof order.value.completion_notes === 'string' 
        ? JSON.parse(order.value.completion_notes) 
        : order.value.completion_notes
      
      // Only include revision notes (not cancellation, dispute, refund - those are captured in transitions)
      if (notesObj.revision_notes && Array.isArray(notesObj.revision_notes)) {
        notesObj.revision_notes.forEach((note) => {
          if (note.reason || note.notes) {
            reasons.push({
              type: 'revision',
              label: 'Revision Note',
              reason: note.reason || note.notes,
              timestamp: note.timestamp || order.value.updated_at,
              user: note.added_by?.username || note.user || 'Unknown',
              added_by_id: note.added_by?.id || note.added_by_id,
              is_admin_added: note.is_admin_added || false
            })
          }
        })
      }
      
      // Legacy: check admin_reasons but filter to only revision-related
      if (notesObj.admin_reasons && Array.isArray(notesObj.admin_reasons)) {
        notesObj.admin_reasons.forEach((adminReason) => {
          // Only include if it's revision-related
          if (adminReason.type === 'revision' && (adminReason.reason || adminReason.notes)) {
            reasons.push({
              type: 'revision',
              label: 'Revision Note',
              reason: adminReason.reason || adminReason.notes,
              timestamp: adminReason.timestamp || order.value.updated_at,
              user: adminReason.added_by?.username || 'Admin',
              added_by_id: adminReason.added_by?.id || adminReason.added_by_id,
              is_admin_added: adminReason.is_admin_added || true,
              admin_reason_id: adminReason.id
            })
          }
        })
      }
    } catch (e) {
      // If completion_notes is not JSON, that's okay - it might be plain text
      if (import.meta.env.DEV && order.value.completion_notes && typeof order.value.completion_notes === 'string' && order.value.completion_notes.length > 0) {
        console.warn('Failed to parse completion_notes for revision notes:', e)
      }
    }
  }
  
  // Sort by timestamp (most recent first)
  return reasons.sort((a, b) => {
    const dateA = a.timestamp ? new Date(a.timestamp).getTime() : 0
    const dateB = b.timestamp ? new Date(b.timestamp).getTime() : 0
    return dateB - dateA
  })
})

// Computed properties for revision notes permissions
const canAddRevisionNotes = computed(() => {
  if (!order.value) return false
  // Only show for revision-related statuses or if order has been in revision
  const revisionStatuses = ['revision_requested', 'revision_in_progress']
  const canEdit = authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport
  return canEdit && (revisionStatuses.includes(order.value.status) || order.value.status_history?.some(s => revisionStatuses.includes(s)))
})

const canEditRevisionInstructions = computed(() => {
  if (!order.value) return false
  return authStore.isClient || authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport
})

const canEditRevisionNote = (note) => {
  if (!note) return false
  // Admin/Support can always edit
  if (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) return true
  // Client can edit their own notes
  if (authStore.isClient && note.added_by_id === userId.value) return true
  return false
}

// Helper functions for reason display
const getReasonLabel = (type) => {
  const labels = {
    'cancelled': 'Cancellation Reason',
    'cancel_order': 'Cancellation Reason',
    'disputed': 'Dispute Reason',
    'dispute': 'Dispute Reason',
    'refunded': 'Refund Reason',
    'refund': 'Refund Reason',
    'on_hold': 'Hold Reason',
    'hold_order': 'Hold Reason',
    'archived': 'Archive Reason',
    'archive_order': 'Archive Reason'
  }
  return labels[type] || 'Reason'
}

const getReasonIcon = (type) => {
  const icons = {
    'cancelled': '❌',
    'cancel_order': '❌',
    'disputed': '⚠️',
    'dispute': '⚠️',
    'refunded': '💰',
    'refund': '💰',
    'on_hold': '⏸️',
    'hold_order': '⏸️',
    'archived': '📦',
    'archive_order': '📦'
  }
  return icons[type] || '📝'
}

const getReasonBorderClass = (type) => {
  const classes = {
    'cancelled': 'border-red-500 bg-red-50 dark:bg-red-900/10',
    'cancel_order': 'border-red-500 bg-red-50 dark:bg-red-900/10',
    'disputed': 'border-orange-500 bg-orange-50 dark:bg-orange-900/10',
    'dispute': 'border-orange-500 bg-orange-50 dark:bg-orange-900/10',
    'refunded': 'border-blue-500 bg-blue-50 dark:bg-blue-900/10',
    'refund': 'border-blue-500 bg-blue-50 dark:bg-blue-900/10',
    'on_hold': 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/10',
    'hold_order': 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/10',
    'archived': 'border-gray-500 bg-gray-50 dark:bg-gray-900/10',
    'archive_order': 'border-gray-500 bg-gray-50 dark:bg-gray-900/10'
  }
  return classes[type] || 'border-gray-300 bg-gray-50 dark:bg-gray-900/10'
}

const getReasonBadgeClass = (type) => {
  const classes = {
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'cancel_order': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'disputed': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'dispute': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'refunded': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'refund': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'on_hold': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'hold_order': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'archived': 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
    'archive_order': 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
  }
  return classes[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
}

const hasReview = ref(false)
const orderReview = ref(null)
const showRevisionForm = ref(false)
const editingRevisionInstructions = ref(false)
const revisionInstructions = ref('')
const savingRevisionInstructions = ref(false)
const revisionReason = ref('')
const requestingRevision = ref(false)
const revisionSections = ref([])
const processingDisputeAction = ref(false)
const showAssignModal = ref(false)
const showAddReasonInline = ref(false)
const editingReasonIndex = ref(null)
const savingReason = ref(false)
const reasonForm = ref({
  type: '',
  reason: '',
  resolution: ''
})
const showReassignModal = ref(false)
const showUnpaidWarningModal = ref(false)
const showEditInstructions = ref(false)
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

// statusBadgeClass removed - using EnhancedStatusBadge component instead

// Auto-Assignment
const showAutoAssignModal = ref(false)
const autoAssigning = ref(false)
const autoAssignForm = ref({
  min_rating: 4.0,
  max_candidates: 10,
  reason: 'Auto-assigned by system'
})

// Smart Matching
const showSmartMatchModal = ref(false)
const loadingSmartMatches = ref(false)
const smartMatches = ref([])
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

// Computed progress that shows 100% for completed orders, but adjusts if order returns to revision/in progress
const displayProgressPercentage = computed(() => {
  if (!order.value) return 0
  
  const status = order.value.status?.toLowerCase()
  
  // Completed/approved/closed orders show 100%
  if (['completed', 'approved', 'closed'].includes(status)) {
    return 100
  }
  
  // If order is in revision or returned to progress, show actual progress
  // This handles cases where a completed order goes back to revision_requested or in_progress
  if (['revision_requested', 'revision_in_progress', 'in_progress', 'assigned', 'draft', 'submitted', 'under_editing'].includes(status)) {
    return latestProgressPercentage.value
  }
  
  // For other statuses, return the actual progress
  return latestProgressPercentage.value
})

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
    if (import.meta.env.DEV) {
      console.error('Failed to load latest progress:', error)
    }
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
// Pre-submission checklist state
const showSubmitChecklist = ref(false)
const submitChecklist = ref({
  wordCountMet: false,
  revised: false,
  edited: false,
  requirementsMet: false,
  finalFileSelected: false
})

const openSubmitChecklist = () => {
  if (!order.value) return
  
  // Pre-populate checklist based on current state
  submitChecklist.value.finalFileSelected = hasFinalPaperFile.value
  
  // Reset other checks (user must confirm)
  submitChecklist.value.wordCountMet = false
  submitChecklist.value.revised = false
  submitChecklist.value.edited = false
  submitChecklist.value.requirementsMet = false
  
  showSubmitChecklist.value = true
}

const closeSubmitChecklist = () => {
  showSubmitChecklist.value = false
}

const canProceedWithSubmission = computed(() => {
  return submitChecklist.value.wordCountMet &&
         submitChecklist.value.revised &&
         submitChecklist.value.edited &&
         submitChecklist.value.requirementsMet &&
         submitChecklist.value.finalFileSelected
})

const submitOrder = async () => {
  if (!order.value) return
  
  // If checklist not shown, show it first
  if (!showSubmitChecklist.value) {
    openSubmitChecklist()
    return
  }
  
  // Validate checklist
  if (!canProceedWithSubmission.value) {
    showErrorToast('Please complete all checklist items before submitting.')
    return
  }
  
  // Final confirmation
  const confirmed = await confirm.showDialog(
    `Submit Order #${order.value.id} for review?`,
    'Final Confirmation',
    {
      details: `Once submitted, "${order.value.topic || 'Untitled'}" will be sent to the client for review. You won't be able to make further changes until the client responds.`,
      variant: 'default',
      icon: '📤',
      confirmText: 'Submit Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  showSubmitChecklist.value = false
  
  try {
    // Use unified transition endpoint
    const response = await ordersAPI.transition(order.value.id, 'submitted', 'Order submitted by writer')
    const message = response.data.message || `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been submitted successfully! The client will be notified for review.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to submit order', `Unable to submit Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const startOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Start working on Order #${order.value.id}?`,
    'Start Order',
    {
      details: `You are about to begin working on "${order.value.topic || 'Untitled'}". The order status will change to "In Progress" and the deadline timer will start.`,
      variant: 'default',
      icon: '🚀',
      confirmText: 'Start Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, 'in_progress', 'Order started by writer')
    const message = response.data.message || `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been started! You can now begin working on it.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to start order', `Unable to start Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const startRevision = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Start revision for Order #${order.value.id}?`,
    'Start Revision',
    {
      details: `You are about to begin working on revisions for "${order.value.topic || 'Untitled'}". The revision deadline will be set and the client will be notified.`,
      variant: 'default',
      icon: '✏️',
      confirmText: 'Start Revision',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, 'revision_in_progress', 'Revision started by writer')
    const message = response.data.message || `Revision for Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been started! Please address the client's feedback.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to start revision', `Unable to start revision for Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const resumeOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Resume Order #${order.value.id}?`,
    'Resume Order',
    {
      details: `You are about to resume work on "${order.value.topic || 'Untitled'}". The order will be moved from "On Hold" back to active status.`,
      variant: 'default',
      icon: '▶️',
      confirmText: 'Resume Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, 'in_progress', 'Order resumed from hold')
    const message = response.data.message || `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been resumed! You can continue working on it.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to resume order', `Unable to resume Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const completeOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Mark Order #${order.value.id} as complete?`,
    'Complete Order',
    {
      details: `You are about to mark "${order.value.topic || 'Untitled'}" as complete. This will finalize the order and notify the client. Make sure all work has been submitted and reviewed.`,
      variant: 'default',
      icon: '✅',
      confirmText: 'Mark as Complete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, 'completed', 'Order completed by writer')
    const message = response.data.message || `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been marked as complete! The client has been notified.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to complete order', `Unable to complete Order #${order.value.id}. Please try again or contact support if the issue persists.`)
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
    `Cancel Order #${order.value.id}?`,
    'Cancel Order',
    {
      details: `You are about to cancel "${order.value.topic || 'Untitled'}". This action cannot be undone. The order will be permanently cancelled and the client will be notified.`,
      icon: '⚠️'
    }
  )
  
  if (!confirmed) return
  
  // Then ask for reason (optional)
  const reason = await inputModal.showModal(
    `Please provide a reason for cancelling Order #${order.value.id} (optional)`,
    'Cancellation Reason',
    {
      label: 'Reason',
      placeholder: 'Enter reason for cancellation...',
      multiline: true,
      rows: 4,
      required: false,
      hint: 'This reason will be recorded in the order history and may be shared with the client.'
    }
  )
  
  if (reason === null) return // User cancelled
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, 'cancelled', reason || 'Order cancelled')
    const message = response.data.message || `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been cancelled. The client has been notified.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to cancel order', `Unable to cancel Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

const reopenOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Reopen Order #${order.value.id}?`,
    'Reopen Order',
    {
      details: `You are about to reopen "${order.value.topic || 'Untitled'}". This will change the order status back to active, allowing further work to be done. The writer and client will be notified.`,
      variant: 'warning',
      icon: '🔄',
      confirmText: 'Reopen Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    // Reopen typically transitions to 'unpaid' or 'available' depending on order state
    const targetStatus = order.value.is_paid ? 'available' : 'unpaid'
    const response = await ordersAPI.transition(order.value.id, targetStatus, 'Order reopened')
    const message = response.data.message || `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been reopened! You can now continue working on it.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to reopen order', `Unable to reopen Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Soft Delete Order
const softDeleteOrder = async () => {
  if (!order.value) return
  
  const { useInputModal } = await import('@/composables/useInputModal')
  const inputModal = useInputModal()
  
  const reason = await inputModal.showModal(
    'Soft Delete Order',
    'Enter a reason for soft-deleting this order (optional):',
    {
      placeholder: 'e.g., Order cancelled, duplicate order, etc.',
      required: false
    }
  )
  
  if (reason === null) return // User cancelled
  
  const confirmed = await confirm.showDestructive(
    `Soft Delete Order #${order.value.id}?`,
    'Soft Delete Order',
    {
      details: `You are about to soft-delete "${order.value.topic || 'Untitled'}". The order will be hidden from normal queries but can be restored later.${reason ? `\n\nReason: ${reason}` : ''}`,
      icon: '🗑️',
      confirmText: 'Soft Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.softDelete(order.value.id, reason || '')
    const message = `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been soft-deleted.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to soft delete order', `Unable to soft delete Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Restore Order
const restoreOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Restore Order #${order.value.id}?`,
    'Restore Order',
    {
      details: `You are about to restore "${order.value.topic || 'Untitled'}". The order will be visible again in normal queries.`,
      variant: 'info',
      icon: '♻️',
      confirmText: 'Restore',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.restore(order.value.id)
    const message = `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been restored!`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to restore order', `Unable to restore Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Hard Delete Order (Permanent)
const hardDeleteOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDestructive(
    `Permanently Delete Order #${order.value.id}?`,
    'Permanent Delete',
    {
      details: `⚠️ WARNING: You are about to PERMANENTLY delete "${order.value.topic || 'Untitled'}". This action CANNOT be undone. All data associated with this order will be permanently removed from the database.`,
      icon: '⚠️',
      confirmText: 'Delete Permanently',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.hardDelete(order.value.id)
    const message = `Order #${order.value.id} has been permanently deleted.`
    actionSuccess.value = message
    showSuccessToast(message)
    // Redirect to orders list after hard delete
    setTimeout(() => {
      router.push('/admin/orders')
    }, 2000)
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to permanently delete order', `Unable to permanently delete Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Order Action Modal functions (for admin/superadmin/support)
const openActionModal = async (action = null) => {
  if (!order.value) return
  
  // Check payment status for assign/reassign actions
  if ((action === 'assign_order' || action === 'reassign_order') && !order.value.is_paid) {
    showUnpaidWarningModal.value = true
    return
  }
  
  selectedAction.value = action
  
  // Load available actions for this order
  try {
    const response = await ordersAPI.getAvailableActions(order.value.id)
    if (response.data && response.data.available_actions) {
      availableActions.value = response.data.available_actions
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load available actions:', error)
    }
    availableActions.value = []
  }
  
  // Load writers if needed for assign/reassign
  if ((action === 'assign_order' || action === 'reassign_order') && availableWriters.value.length === 0) {
    try {
      const writersResponse = await usersAPI.list({ role: 'writer', website: order.value.website_id })
      availableWriters.value = writersResponse.data?.results || writersResponse.data || []
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Failed to load writers:', error)
      }
      availableWriters.value = []
    }
  }
  
  showActionModal.value = true
}

// Auto-Assignment Functions
const performAutoAssign = async () => {
  if (!order.value) return
  
  autoAssigning.value = true
  try {
    const response = await ordersAPI.autoAssign(order.value.id, {
      min_rating: autoAssignForm.value.min_rating,
      max_candidates: autoAssignForm.value.max_candidates,
      reason: autoAssignForm.value.reason || 'Auto-assigned by system'
    })
    
    showSuccessToast(response.data?.message || 'Writer auto-assigned successfully')
    showAutoAssignModal.value = false
    
    // Refresh order data
    await loadOrder()
  } catch (error) {
    showErrorToast(getErrorMessage(error))
  } finally {
    autoAssigning.value = false
  }
}

// Smart Matching Functions
const loadSmartMatches = async () => {
  if (!order.value) return
  
  loadingSmartMatches.value = true
  showSmartMatchModal.value = true
  
  try {
    const response = await ordersAPI.getSmartMatches(order.value.id, {
      max_results: 10,
      min_rating: 4.0
    })
    
    smartMatches.value = response.data?.matches || []
  } catch (error) {
    showErrorToast(getErrorMessage(error))
    smartMatches.value = []
  } finally {
    loadingSmartMatches.value = false
  }
}

const assignFromSmartMatch = async (writerId) => {
  if (!order.value) return
  
  autoAssigning.value = true
  try {
    // Use regular assign action
    await ordersAPI.assignWriter(order.value.id, writerId, 'Assigned from smart match recommendations')
    
    showSuccessToast('Writer assigned successfully')
    showSmartMatchModal.value = false
    
    // Refresh order data
    await loadOrder()
  } catch (error) {
    showErrorToast(getErrorMessage(error))
  } finally {
    autoAssigning.value = false
  }
}

const handleActionSuccess = async (data) => {
  // Use the enhanced message from OrderActionModal or create a detailed one
  const orderId = order.value?.id || data.order?.id || 'this order'
  const orderTopic = order.value?.topic || data.order?.topic || 'Untitled'
  const actionName = data.action ? data.action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Action'
  
  let message = data.message
  if (!message) {
    // Build a detailed success message
    const statusInfo = data.old_status && data.new_status
      ? ` Status changed from "${data.old_status.replace('_', ' ')}" to "${data.new_status.replace('_', ' ')}".`
      : data.new_status
        ? ` Status changed to "${data.new_status.replace('_', ' ')}".`
        : '.'
    
    message = `${actionName} completed successfully for Order #${orderId} "${orderTopic}".${statusInfo}`
  }
  
  actionSuccess.value = message
  actionError.value = ''
  showSuccessToast(message)
  await loadOrder()
  
  // Clear success message after 8 seconds (longer for detailed messages)
  setTimeout(() => {
    actionSuccess.value = ''
  }, 8000)
}

const handleActionError = (error) => {
  const orderId = order.value?.id || 'this order'
  
  // Check if error is about payment requirement for assign/reassign actions
  const errorMessage = error?.detail || error?.message || (typeof error === 'string' ? error : '')
  const isPaymentError = errorMessage && (
    errorMessage.toLowerCase().includes('payment') ||
    errorMessage.toLowerCase().includes('must have a completed payment') ||
    errorMessage.toLowerCase().includes('order must be paid')
  )
  
  // Check if this is an assign/reassign action
  const isAssignAction = selectedAction.value === 'assign_order' || selectedAction.value === 'reassign_order'
  
  // If it's a payment error for assign/reassign, show the warning modal instead
  if (isPaymentError && isAssignAction && order.value && !order.value.is_paid) {
    showActionModal.value = false // Close the action modal
    showUnpaidWarningModal.value = true // Show the warning modal
    actionError.value = ''
    return
  }
  
  // Otherwise, show the generic error
  const finalErrorMessage = getErrorMessage(
    error, 
    'Failed to execute action', 
    `Unable to perform action on Order #${orderId}. Please try again or contact support if the issue persists.`
  )
  actionError.value = finalErrorMessage
  actionSuccess.value = ''
  showErrorToast(finalErrorMessage)
  
  // Clear error message after 8 seconds
  setTimeout(() => {
    actionError.value = ''
  }, 8000)
}

// Status change handler
const handleStatusChange = async (targetStatus) => {
  if (!order.value) return
  
  const statusLabels = {
    'on_hold': 'Put on Hold',
    'in_progress': 'Resume/Start',
    'cancelled': 'Cancel',
    'archived': 'Archive'
  }
  
  const confirmed = await confirm.showDialog(
    `${statusLabels[targetStatus] || 'Change status'} for Order #${order.value.id}?`,
    'Change Order Status',
    {
      details: `You are about to change the order status to "${targetStatus.replace('_', ' ')}". This will update the order workflow.`,
      variant: 'warning',
      icon: '🔄',
      confirmText: 'Confirm',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, targetStatus, `Status changed to ${targetStatus}`)
    const message = response.data.message || `Order status changed to "${targetStatus.replace('_', ' ')}" successfully.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to change status', `Unable to change status for Order #${order.value.id}.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Archive order handler
const handleArchiveOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Archive Order #${order.value.id}?`,
    'Archive Order',
    {
      details: `You are about to archive "${order.value.topic || 'Untitled'}". The order will be moved to archived status.`,
      variant: 'default',
      icon: '📦',
      confirmText: 'Archive',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    await ordersAPI.archiveOrder(order.value.id)
    const message = `Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been archived.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to archive order', `Unable to archive Order #${order.value.id}.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Submit order handler (for writers)
const handleSubmitOrder = async () => {
  if (!order.value) return
  
  const confirmed = await confirm.showDialog(
    `Submit Order #${order.value.id}?`,
    'Submit Order',
    {
      details: `You are about to submit "${order.value.topic || 'Untitled'}" for review. Make sure all work is complete and files are uploaded.`,
      variant: 'default',
      icon: '✅',
      confirmText: 'Submit',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingAction.value = true
  actionError.value = ''
  actionSuccess.value = ''
  
  try {
    const response = await ordersAPI.transition(order.value.id, 'submitted', 'Order submitted by writer')
    const message = response.data.message || `Order #${order.value.id} has been submitted for review.`
    actionSuccess.value = message
    showSuccessToast(message)
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to submit order', `Unable to submit Order #${order.value.id}.`)
    actionError.value = errorMsg
    showErrorToast(errorMsg)
  } finally {
    processingAction.value = false
  }
}

// Alias for cancelOrder to match Actions tab
const handleCancelOrder = cancelOrder

const files = ref([])
const extraServiceFiles = ref([])
const links = ref([])
const processingLink = ref(null)
const categories = ref([])
const showQuickUpload = ref(false)
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

// Handle inline action success
const handleInlineActionSuccess = async (data) => {
  showSuccessToast('Action completed successfully!')
  // Reload order to get updated data
  await loadOrder()
  // Reload related data
  await Promise.all([
    loadFiles(),
    loadLinks(),
    loadLatestProgress()
  ])
}

// Handle inline action error
const handleInlineActionError = (error) => {
  if (error?.cancelled) return // User cancelled, don't show error
  const errorMsg = error?.response?.data?.detail || error?.message || 'Action failed'
  showErrorToast(errorMsg)
}

// Handle edit order success (from Overview tab inline edit)
const handleEditOrderSuccess = async (data) => {
  showSuccessToast('Order details updated successfully!')
  // Reload order to get updated data
  await loadOrder()
  // Exit edit mode
  editingOrderDetails.value = false
  // Reload related data
  await Promise.all([
    loadFiles(),
    loadLinks(),
    loadLatestProgress(),
    loadAvailableActions()
  ])
}

// Handle edit order error (from Overview tab inline edit)
const handleEditOrderError = (error) => {
  if (error?.cancelled) {
    // User cancelled, just exit edit mode
    editingOrderDetails.value = false
    return
  }
  const errorMsg = error?.response?.data?.detail || error?.message || 'Failed to update order'
  showErrorToast(errorMsg)
}

const loadOrder = async () => {
  loading.value = true
  try {
    const orderId = route.params.id
    
    // Try to get from cache first
    const { getCachedOrder, cacheOrder } = await import('@/utils/orderCache')
    const cached = getCachedOrder(orderId)
    
    if (cached && cached.fromCache) {
      // Show cached data immediately
      order.value = cached.data
      paymentSummary.value = null
      
      // Load related data (these may also fail, but we have the order cached)
      try {
        await Promise.all([
          loadFiles(),
          loadExtraServiceFiles(),
          loadLinks(),
          loadCategories(),
          loadWalletBalance(),
          loadOrderReview(),
          loadPaymentSummary()
        ])
      } catch (relatedError) {
        // Silently handle related data errors when using cache
        if (import.meta.env.DEV) {
          console.warn('Some related data failed to load:', relatedError)
        }
      }
      
      // Show indicator that data is from cache
      if (import.meta.env.DEV) {
        console.log(`Loaded order ${orderId} from cache`)
      }
    }
    
    // Always try to fetch fresh data
    try {
      const res = await ordersAPI.get(orderId)
      order.value = res.data
      paymentSummary.value = null
      
      // Cache the order
      cacheOrder(orderId, res.data)
      
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
    } catch (apiError) {
      // If API call fails and we don't have cached data, show error
      if (!cached || !cached.fromCache) {
        throw apiError
      }
      // Otherwise, we already have cached data displayed, just log the error
      console.warn('Failed to fetch fresh order data, using cached data:', apiError)
    }
    
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
    if (import.meta.env.DEV) {
      console.error('Failed to load order:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load review:', error)
    }
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

// Revision section management
const addRevisionSection = () => {
  revisionSections.value.push({
    section: '',
    issue: '',
    request: ''
  })
}

const removeRevisionSection = (index) => {
  revisionSections.value.splice(index, 1)
}

const resetRevisionForm = () => {
  revisionReason.value = ''
  revisionSections.value = []
}

const requestRevision = async () => {
  if (!revisionReason.value.trim()) {
    showErrorToast('Please provide a reason for the revision request')
    return
  }
  
  // Confirm revision request
  const confirmed = await confirm.showDialog(
    `Request revision for Order #${order.value.id}?`,
    'Request Revision',
    {
      details: `You are about to request revisions for "${order.value.topic || 'Untitled'}". The writer will be notified and will need to address your feedback. Make sure your revision request is clear and specific.`,
      variant: 'default',
      icon: '✏️',
      confirmText: 'Submit Revision Request',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  requestingRevision.value = true
  try {
    // Prepare revision request data
    const revisionData = {
      reason: revisionReason.value.trim(),
      description: revisionReason.value.trim()
    }
    
    // Add section-specific changes if provided
    if (revisionSections.value.length > 0) {
      const changesRequired = revisionSections.value
        .filter(s => s.section || s.issue || s.request)
        .map(s => ({
          section: s.section || 'General',
          issue: s.issue || '',
          request: s.request || ''
        }))
      
      if (changesRequired.length > 0) {
        revisionData.changes_required = changesRequired
      }
    }
    
    await ordersAPI.executeAction(order.value.id, 'request_revision', revisionData)
    const message = `Revision request for Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been submitted successfully! The writer will be notified and will work on the requested changes.`
    showSuccessToast(message)
    showRevisionForm.value = false
    resetRevisionForm()
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to request revision', `Unable to submit revision request for Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    showErrorToast(errorMsg)
  } finally {
    requestingRevision.value = false
  }
}

const startEditRevisionInstructions = () => {
  editingRevisionInstructions.value = true
  revisionInstructions.value = order.value?.revision_instructions || ''
}

const cancelEditRevisionInstructions = () => {
  editingRevisionInstructions.value = false
  revisionInstructions.value = ''
}

const saveRevisionInstructions = async () => {
  // Get HTML content from rich text editor
  let instructionsText = revisionInstructions.value || ''
  
  // Import stripHtml to check if HTML content has actual text
  const { stripHtml } = await import('@/utils/htmlUtils')
  
  // Check if instructions have content
  const instructionsTextOnly = typeof instructionsText === 'string' ? stripHtml(instructionsText) : String(instructionsText || '')
  if (!instructionsTextOnly.trim()) {
    showErrorToast('Please provide revision instructions')
    return
  }
  
  savingRevisionInstructions.value = true
  try {
    // Try using executeAction first (if backend supports it)
    // Otherwise fallback to PUT
    try {
      await ordersAPI.executeAction(order.value.id, 'update_revision_instructions', {
        revision_instructions: typeof instructionsText === 'string' ? instructionsText : String(instructionsText)
      })
    } catch (actionError) {
      // If action doesn't exist, try PUT with minimal data
      const updateData = {
        revision_instructions: typeof instructionsText === 'string' ? instructionsText : String(instructionsText)
      }
      await ordersAPI.update(order.value.id, updateData)
    }
    showSuccessToast('Revision instructions saved successfully!')
    editingRevisionInstructions.value = false
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to save revision instructions', 'Unable to save revision instructions. Please try again.')
    showErrorToast(errorMsg)
  } finally {
    savingRevisionInstructions.value = false
  }
}

// Reason management functions
const startEditReason = (reason, index) => {
  editingReasonIndex.value = index
  reasonForm.value = {
    type: 'revision', // Always revision type
    reason: reason.reason || reason.notes || '',
    resolution: '' // No resolution field for revision notes
  }
}

const cancelEditReason = () => {
  editingReasonIndex.value = null
  reasonForm.value = {
    type: '',
    reason: '',
    resolution: ''
  }
}

const addNewReasonInline = () => {
  showAddReasonInline.value = true
  editingReasonIndex.value = null
  reasonForm.value = {
    type: '',
    reason: '',
    resolution: ''
  }
}

const cancelAddReason = () => {
  showAddReasonInline.value = false
  reasonForm.value = {
    type: '',
    reason: '',
    resolution: ''
  }
}

const saveReason = async () => {
  // Get HTML content from rich text editor (if it's HTML) or use plain text
  let reasonText = reasonForm.value.reason || ''
  
  // Import stripHtml to check if HTML content has actual text
  const { stripHtml } = await import('@/utils/htmlUtils')
  
  // Check if reason has content (strip HTML to check for actual text)
  const reasonTextOnly = typeof reasonText === 'string' ? stripHtml(reasonText) : String(reasonText || '')
  const hasReasonContent = reasonTextOnly.trim().length > 0
  
  if (!hasReasonContent) {
    showErrorToast('Please provide revision notes')
    return
  }
  
  if (!order.value) return
  
  savingReason.value = true
  try {
    // Prepare the revision note data (always revision type)
    const revisionNote = {
      type: 'revision',
      reason: typeof reasonText === 'string' ? reasonText : String(reasonText),
      timestamp: new Date().toISOString(),
      added_by: authStore.user?.id,
      added_by_id: authStore.user?.id,
      is_admin_added: authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport
    }
    
    // Get existing revision notes from completion_notes (primary location)
    let existingRevisionNotes = []
    if (order.value.completion_notes) {
      try {
        const notesObj = typeof order.value.completion_notes === 'string' 
          ? JSON.parse(order.value.completion_notes) 
          : order.value.completion_notes
        
        // Get revision_notes array
        if (notesObj.revision_notes && Array.isArray(notesObj.revision_notes)) {
          existingRevisionNotes = [...notesObj.revision_notes]
        }
      } catch (e) {
        // If parsing fails, start fresh
        if (import.meta.env.DEV) {
          console.warn('Failed to parse completion_notes for revision notes:', e)
        }
      }
    }
    
    // If editing, replace the existing note; otherwise add new
    if (editingReasonIndex.value !== null) {
      const originalNote = orderReasons.value[editingReasonIndex.value]
      const noteIndex = existingRevisionNotes.findIndex(n => 
        n.timestamp === originalNote.timestamp && 
        (n.added_by_id === originalNote.added_by_id || n.added_by?.id === originalNote.added_by_id)
      )
      if (noteIndex >= 0) {
        existingRevisionNotes[noteIndex] = revisionNote
      } else {
        existingRevisionNotes.push(revisionNote)
      }
    } else {
      existingRevisionNotes.push(revisionNote)
    }
    
    // Store the revision notes in completion_notes as JSON (this field exists on the Order model)
    // Preserve existing completion_notes if any
    const existingNotes = order.value.completion_notes || ''
    let notesObj = {}
    
    try {
      // Try to parse existing notes as JSON
      if (existingNotes) {
        const parsed = typeof existingNotes === 'string' ? JSON.parse(existingNotes) : existingNotes
        if (typeof parsed === 'object' && !Array.isArray(parsed)) {
          notesObj = { ...parsed }
        } else {
          // If it's not JSON, preserve it
          notesObj = { original_notes: existingNotes }
        }
      }
    } catch (e) {
      // If not JSON, preserve original notes
      notesObj = { original_notes: existingNotes }
    }
    
    // Add/update revision notes
    notesObj.revision_notes = existingRevisionNotes
    notesObj.revision_notes_updated = new Date().toISOString()
    notesObj.revision_notes_updated_by = authStore.user?.id
    
    const updateData = {
      completion_notes: JSON.stringify(notesObj)
    }
    
    // Use PUT (more commonly supported than PATCH)
    await ordersAPI.update(order.value.id, updateData)
    
    showSuccessToast(editingReasonIndex.value !== null ? 'Revision note updated successfully!' : 'Revision note added successfully!')
    
    // Reset form and close inline editors
    if (editingReasonIndex.value !== null) {
      cancelEditReason()
    } else {
      cancelAddReason()
    }
    
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to save reason', 'Unable to save reason. Please try again.')
    showErrorToast(errorMsg)
  } finally {
    savingReason.value = false
  }
}

// Dispute resolution: Client agrees to let writer continue
const agreeToContinueDisputedOrder = async () => {
  if (!order.value || !order.value.dispute) return
  
  const confirmed = await confirm.showDialog(
    `Agree to let writer continue working on Order #${order.value.id}?`,
    'Agree to Continue',
    {
      details: `By agreeing, you're allowing the writer to fix the issues and submit their work. The order will move forward once the writer submits their fixed work.`,
      variant: 'default',
      icon: '✅',
      confirmText: 'Agree & Allow Writer to Continue',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingDisputeAction.value = true
  try {
    // Call API to update dispute with client agreement
    await ordersAPI.executeAction(order.value.id, 'client_agree_continue_dispute', {
      dispute_id: order.value.dispute.id || order.value.dispute_id
    })
    showSuccessToast('You\'ve agreed to let the writer continue working. They can now submit their work.')
    await loadOrder()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to update dispute agreement', 'Unable to update dispute agreement. Please try again.')
    showErrorToast(errorMsg)
  } finally {
    processingDisputeAction.value = false
  }
}

const submitTip = async () => {
  if (!tipAmount.value || tipAmount.value <= 0) {
    showErrorToast('Please enter a valid tip amount')
    return
  }
  
  if (tipPaymentMethod.value === 'wallet' && tipAmount.value > walletBalance.value) {
    showErrorToast('Insufficient wallet balance. Please use credit card or add funds to your wallet.')
    return
  }
  
  if (!order.value.writer_id && !order.value.writer?.id) {
    showErrorToast('No writer assigned to this order')
    return
  }
  
  // Confirm tip submission
  const writerName = order.value.writer?.username || order.value.writer_name || 'the writer'
  const confirmed = await confirm.showDialog(
    `Send $${tipAmount.value.toFixed(2)} tip to ${writerName}?`,
    'Confirm Tip',
    {
      details: `You are about to send a $${tipAmount.value.toFixed(2)} tip for Order #${order.value.id} "${order.value.topic || 'Untitled'}". Payment will be processed using your ${tipPaymentMethod.value === 'wallet' ? 'wallet balance' : 'credit card'}.`,
      variant: 'default',
      icon: '💰',
      confirmText: `Send $${tipAmount.value.toFixed(2)}`,
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
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
    const message = `Tip of $${tipAmount.value.toFixed(2)} has been sent successfully to ${writerName}! They will be notified and the payment will be processed.`
    showSuccessToast(message)
    showTipModal.value = false
    tipAmount.value = null
    tipReason.value = ''
    tipPaymentMethod.value = 'wallet'
    await loadWalletBalance() // Refresh wallet balance
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to send tip', `Unable to process tip payment. Please check your payment method and try again, or contact support if the issue persists.`)
    showErrorToast(errorMsg)
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
    if (import.meta.env.DEV) {
      console.error('Failed to load wallet balance:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load payment summary:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load categories:', error)
    }
    categories.value = []
  }
}

// Separate universal and website-specific categories
const universalCategories = computed(() => {
  return categories.value.filter(cat => cat.is_universal || cat.website === null || cat.website_id === null)
})

const websiteSpecificCategories = computed(() => {
  return categories.value.filter(cat => !cat.is_universal && cat.website !== null && cat.website_id !== null)
})

// Role-based category suggestions
const writerCategorySuggestions = computed(() => {
  const common = ['Final Draft', 'First Draft', 'DRAFT', 'Outline', 'Resource', 'Plagiarism Report', 'AI Similarity Report']
  // Filter out suggestions that already exist as categories (check both universal and website-specific)
  return common.filter(suggestion => 
    !categories.value.some(cat => cat.name.toLowerCase() === suggestion.toLowerCase())
  )
})

const clientCategorySuggestions = computed(() => {
  const common = ['Materials', 'Sample', 'My Previous Papers', 'Friends Paper', 'Reading Materials', 'Syllabus', 'Rubric', 'Guidelines']
  // Filter out suggestions that already exist as categories (check both universal and website-specific)
  return common.filter(suggestion => 
    !categories.value.some(cat => cat.name.toLowerCase() === suggestion.toLowerCase())
  )
})

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
    if (import.meta.env.DEV) {
      console.error('Failed to load files:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load extra service files:', error)
    }
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
  const confirmed = await confirm.showDialog(
    `Request deletion of "${file.file_name}"?\n\nThis will send a deletion request to administrators.`,
    'Request File Deletion',
    {
      variant: 'warning',
      icon: '🗑️',
      confirmText: 'Request Deletion',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  // Get deletion reason using input modal
  const reason = await inputModal.showModal(
    'Reason for deletion (optional)',
    'Deletion Reason',
    {
      label: 'Reason',
      placeholder: 'Enter reason for deletion...',
      required: false,
      multiline: true,
      rows: 3
    }
  ) || ''
  
  try {
    await orderFilesAPI.createDeletionRequest({
      file: file.id,
      reason: reason
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
    if (import.meta.env.DEV) {
      console.error('Failed to load links:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to toggle file download:', error)
    }
    alert('Failed to update file download status')
  }
}

const approveLink = async (link) => {
  processingLink.value = link.id
  try {
    await orderFilesAPI.approveExternalLink(link.id)
    await loadLinks() // Reload links to get updated status
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to approve link:', error)
    }
    alert('Failed to approve link')
  } finally {
    processingLink.value = null
  }
}

const rejectLink = async (link) => {
  const confirmed = await confirm.showDialog(
    `Reject this link?\n\n${link.link}`,
    'Reject External Link',
    {
      variant: 'warning',
      icon: '❌',
      confirmText: 'Reject',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  processingLink.value = link.id
  try {
    await orderFilesAPI.rejectExternalLink(link.id)
    await loadLinks() // Reload links to get updated status
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to reject link:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load recipients:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to start chat:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load threads:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load messages:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to load recipients:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to send message:', error)
    }
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
    if (import.meta.env.DEV) {
      console.error('Failed to download attachment:', error)
    }
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
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this message? This action cannot be undone.',
    'Delete Message',
    {
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  const key = `${threadId}-${messageId}`
  deletingMessage.value[key] = true
  
  try {
    await communicationsAPI.deleteMessage(threadId, messageId)
    await loadThreadMessages(threadId)
    await loadThreads()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to delete message', 'Unable to delete message. Please try again or contact support if the issue persists.')
    showErrorToast(errorMsg)
  } finally {
    deletingMessage.value[key] = false
  }
}

const deleteThread = async (threadId) => {
  const confirmed = await confirm.showDestructive(
    'Delete this conversation thread?',
    'Delete Thread',
    {
      details: 'All messages in this thread will be permanently deleted. This action cannot be undone.',
      icon: '🗑️',
      confirmText: 'Delete Thread',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  deletingThread.value[threadId] = true
  
  try {
    await communicationsAPI.deleteThread(threadId)
    showSuccessToast('Conversation thread deleted successfully')
    await loadThreads()
    // Close the thread if it was expanded
    expandedThreads.value[threadId] = false
    stopThreadPolling(threadId)
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to delete thread', 'Unable to delete conversation thread. Please try again or contact support if the issue persists.')
    showErrorToast(errorMsg)
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
    if (import.meta.env.DEV) {
      console.error('Failed to load draft requests:', error)
    }
    draftRequests.value = []
  } finally {
    loadingDraftRequests.value = false
  }
}

const checkDraftEligibility = async (showError = true) => {
  if (!order.value) return
  loadingDraftEligibility.value = true
  try {
    const res = await draftRequestsAPI.checkEligibility(order.value.id)
    draftEligibility.value = res.data
  } catch (error) {
    // Only show error toast for user-initiated checks
    // Silent failures for automatic checks (e.g., after creating requests)
    if (showError) {
      const errorMsg = getErrorMessage(
        error,
        'Failed to check eligibility',
        'Unable to check draft eligibility. This feature may not be available for this order.'
      )
      showErrorToast(errorMsg)
    }
    // Clear eligibility on error
    draftEligibility.value = null
    if (import.meta.env.DEV) {
      console.error('Failed to check eligibility:', error)
    }
  } finally {
    loadingDraftEligibility.value = false
  }
}

const createDraftRequest = async () => {
  if (!order.value) return
  
  // Confirm draft request
  const confirmed = await confirm.showDialog(
    `Request a draft for Order #${order.value.id}?`,
    'Request Draft',
    {
      details: `You are about to request a draft for "${order.value.topic || 'Untitled'}". The writer will be notified and can upload a draft file for your review before the final submission.`,
      variant: 'default',
      icon: '📄',
      confirmText: 'Submit Request',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  creatingDraftRequest.value = true
  try {
    const requestData = {
      order: order.value.id,
      message: draftRequestForm.value.message || ''
    }
    // Add deadline if provided
    if (draftRequestForm.value.deadline) {
      requestData.deadline = draftRequestForm.value.deadline
    }
    
    await draftRequestsAPI.createDraftRequest(requestData)
    const message = `Draft request for Order #${order.value.id} "${order.value.topic || 'Untitled'}" has been submitted successfully! The writer will be notified and can upload a draft for your review.`
    showSuccessToast(message)
    showDraftRequestModal.value = false
    draftRequestForm.value = { message: '', deadline: '' }
    await loadDraftRequests()
    await checkDraftEligibility(false) // Silent check after creating request
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to create draft request', `Unable to submit draft request for Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    showErrorToast(errorMsg)
  } finally {
    creatingDraftRequest.value = false
  }
}

const cancelDraftRequest = async (requestId) => {
  const confirmed = await confirm.showDialog(
    `Cancel draft request for Order #${order.value.id}?`,
    'Cancel Draft Request',
    {
      details: `You are about to cancel a draft request for "${order.value.topic || 'Untitled'}". The writer will no longer be able to upload a draft for this request.`,
      variant: 'warning',
      icon: '❌',
      confirmText: 'Cancel Request',
      cancelText: 'Keep Request'
    }
  )
  
  if (!confirmed) return
  
  try {
    await draftRequestsAPI.cancelDraftRequest(requestId)
    const message = `Draft request for Order #${order.value.id} has been cancelled successfully.`
    showSuccessToast(message)
    await loadDraftRequests()
    await checkDraftEligibility(false) // Silent check after creating request
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to cancel draft request', `Unable to cancel draft request for Order #${order.value.id}. Please try again or contact support if the issue persists.`)
    showErrorToast(errorMsg)
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
  if (!file) {
    showErrorToast('Please select a file to upload')
    return
  }
  
  // Confirm upload
  const confirmed = await confirm.showDialog(
    `Upload draft file for Order #${order.value.id}?`,
    'Upload Draft',
    {
      details: `You are about to upload "${file.name}" as a draft for "${order.value.topic || 'Untitled'}". The client will be notified and can review the draft.`,
      variant: 'default',
      icon: '📤',
      confirmText: 'Upload Draft',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  uploadingDraft.value[requestId] = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (draftFileDescriptions.value[requestId]) {
      formData.append('description', draftFileDescriptions.value[requestId])
    }
    
    await draftRequestsAPI.uploadDraft(requestId, formData)
    const message = `Draft file "${file.name}" has been uploaded successfully for Order #${order.value.id}! The client has been notified and can review it.`
    showSuccessToast(message)
    
    // Clear form
    draftSelectedFiles.value[requestId] = null
    draftFileDescriptions.value[requestId] = ''
    if (draftFileInputs.value[requestId]) {
      draftFileInputs.value[requestId].value = ''
    }
    
    await loadDraftRequests()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to upload draft', `Unable to upload draft file for Order #${order.value.id}. Please check the file and try again, or contact support if the issue persists.`)
    showErrorToast(errorMsg)
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
    if (import.meta.env.DEV) {
      console.error('Failed to load writer context:', error)
    }
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
    // Reload both order and writer context to ensure state is updated
    await Promise.all([
      loadOrder(),
      loadWriterContext()
    ])
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
  const confirmed = await confirm.showDialog(
    `Are you sure you want to take Order #${order.value.id}?\n\n` +
    `This will assign it to you immediately and you'll be responsible for completing it by the deadline.`,
    'Take Order',
    {
      variant: 'default',
      icon: '✋',
      confirmText: 'Take Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
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
      await checkDraftEligibility(false) // Silent check on mount
    }
    if (authStore.isWriter && order.value.status === 'available') {
      await loadWriterContext()
    }
  }
})
</script>


