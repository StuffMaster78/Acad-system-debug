<template>
  <div class="space-y-6 p-6">
    <!-- Header with Back Button -->
    <div class="flex items-center gap-4 mb-2">
      <router-link
        to="/admin/special-orders"
        class="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="text-sm font-medium">Back to Special Orders</span>
      </router-link>
    </div>
    
    <LoadingState 
      v-if="loading" 
      type="spinner" 
      size="large"
      message="Loading special order details..."
    />

    <ErrorState 
      v-else-if="error" 
      :message="error"
      :retry-handler="loadOrder"
      retry-label="Reload"
    />

    <div v-else-if="order" class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
              ⭐
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Special Order #{{ order.id }}</h1>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ order.order_type === 'predefined' ? 'Predefined pricing structure' : 'Custom estimated pricing' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-wrap mt-2">
            <span 
              class="px-3 py-1.5 text-xs font-semibold rounded-full cursor-help relative group transition-all hover:scale-105" 
              :class="getStatusClass(order.status)"
            >
              <span class="flex items-center gap-1.5">
                <span>{{ getStatusIcon(order.status) }}</span>
                <span>{{ getStatusLabel(order.status) }}</span>
              </span>
              <!-- Tooltip -->
              <span class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-800 text-white text-xs rounded-lg shadow-xl whitespace-normal max-w-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                <div class="font-semibold mb-1">{{ getStatusLabel(order.status) }}</div>
                <div class="text-gray-300">{{ getStatusTooltip(order.status) }}</div>
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                  <div class="w-2 h-2 bg-gray-900 dark:bg-gray-800 transform rotate-45"></div>
                </div>
              </span>
            </span>
            <span class="px-3 py-1.5 text-xs font-medium rounded-full" :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'">
              {{ order.order_type === 'predefined' ? '📋 Predefined' : '💰 Estimated' }}
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="editingOrder = !editingOrder"
            :class="[
              'px-4 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2 shadow-sm',
              editingOrder
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md'
            ]"
            :title="editingOrder ? 'Cancel editing' : 'Edit order details'"
          >
            <svg v-if="!editingOrder" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>{{ editingOrder ? 'Cancel' : 'Edit' }}</span>
          </button>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div v-if="!editingOrder" class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors flex items-center gap-2',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <span>{{ tab.icon }}</span>
            <span>{{ tab.label }}</span>
            <span v-if="tab.badge" class="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              {{ tab.badge }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Edit Form -->
      <div v-if="editingOrder" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-blue-300 dark:border-blue-700 shadow-lg p-6">
        <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Edit Special Order</h3>
        <form @submit.prevent="saveOrder" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
              <select
                v-model="editForm.status"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="inquiry">Inquiry</option>
                <option value="awaiting_approval">Awaiting Approval</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Duration (Days)</label>
              <input
                v-model.number="editForm.duration_days"
                type="number"
                min="1"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Total Cost ($)</label>
              <input
                v-model.number="editForm.total_cost"
                type="number"
                step="0.01"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deposit Required ($)</label>
              <input
                v-model.number="editForm.deposit_required"
                type="number"
                step="0.01"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Inquiry Details</label>
            <textarea
              v-model="editForm.inquiry_details"
              rows="5"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Admin Notes</label>
            <textarea
              v-model="editForm.admin_notes"
              rows="4"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>
          <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              @click="cancelEdit"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Overview Tab -->
      <div v-if="!editingOrder && activeTab === 'overview'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Left Column -->
        <div class="space-y-6">
          <!-- Basic Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Basic Information</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Order ID:</span>
                <span class="font-mono text-gray-900 dark:text-white">#{{ order.id }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Status:</span>
                <span 
                  class="px-2 py-1 text-xs rounded-full cursor-help relative group" 
                  :class="getStatusClass(order.status)"
                >
                  {{ getStatusLabel(order.status) }}
                  <!-- Tooltip -->
                  <span class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                    {{ getStatusTooltip(order.status) }}
                    <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                      <div class="w-2 h-2 bg-gray-900 transform rotate-45"></div>
                    </div>
                  </span>
                </span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>🏷️</span>
                  <span>Order Type</span>
                </span>
                <span class="px-2 py-1 text-xs rounded-full font-medium" :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'">
                  {{ order.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
                </span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>⏱️</span>
                  <span>Duration</span>
                </span>
                <span class="text-gray-900 dark:text-white font-medium">{{ order.duration_days || 0 }} days</span>
              </div>
              <div class="flex justify-between items-center py-2">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>📅</span>
                  <span>Created</span>
                </span>
                <span class="text-gray-900 dark:text-white">{{ formatDate(order.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Client Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <span class="text-green-600 dark:text-green-400 text-lg">👤</span>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Client Information</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>👥</span>
                  <span>Client</span>
                </span>
                <span class="text-gray-900 dark:text-white font-medium">{{ order.client?.username || order.client?.email || 'N/A' }}</span>
              </div>
              <div v-if="order.client?.email" class="flex justify-between items-center py-2">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>✉️</span>
                  <span>Email</span>
                </span>
                <a :href="`mailto:${order.client.email}`" class="text-blue-600 dark:text-blue-400 hover:underline">{{ order.client.email }}</a>
              </div>
            </div>
          </div>

          <!-- Writer Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                  <span class="text-indigo-600 dark:text-indigo-400 text-lg">✍️</span>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Writer Information</h3>
              </div>
              <button
                @click="openAssignWriterModal"
                :class="[
                  'text-sm px-3 py-1.5 rounded-lg transition-all font-medium shadow-sm',
                  order.writer
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700 hover:shadow-md'
                    : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md'
                ]"
                :title="order.writer ? 'Reassign writer to this order' : 'Assign a writer to this order'"
              >
                {{ order.writer ? '🔄 Reassign' : '➕ Assign' }}
              </button>
            </div>
            <div v-if="order.writer" class="space-y-3 text-sm">
              <div class="flex justify-between items-center py-2">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>👤</span>
                  <span>Writer</span>
                </span>
                <span class="text-gray-900 dark:text-white font-medium">{{ order.writer?.username || order.writer?.email || 'N/A' }}</span>
              </div>
            </div>
            <div v-else class="text-sm text-gray-500 dark:text-gray-400 italic py-2 flex items-center gap-2">
              <span>⚠️</span>
              <span>No writer assigned</span>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="space-y-6">
          <!-- Financial Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                <span class="text-emerald-600 dark:text-emerald-400 text-lg">💰</span>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Financial Information</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>💵</span>
                  <span>Total Cost</span>
                </span>
                <span class="text-xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(order.total_cost || 0) }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>💳</span>
                  <span>Deposit Required</span>
                </span>
                <span class="text-gray-900 dark:text-white font-semibold">${{ formatCurrency(order.deposit_required || 0) }}</span>
              </div>
              <div v-if="order.is_approved" class="flex justify-between items-center py-2">
                <span class="font-medium text-gray-600 dark:text-gray-400 flex items-center gap-1">
                  <span>✅</span>
                  <span>Approved</span>
                </span>
                <span class="px-3 py-1 text-xs rounded-full font-semibold bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Yes</span>
              </div>
            </div>
          </div>

          <!-- Inquiry Details -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <span class="text-amber-600 dark:text-amber-400 text-lg">📝</span>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Inquiry Details</h3>
            </div>
            <div v-if="order.inquiry_details" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              {{ order.inquiry_details }}
            </div>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic py-2">No inquiry details provided</p>
          </div>

          <!-- Admin Notes -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                <span class="text-purple-600 dark:text-purple-400 text-lg">📋</span>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Admin Notes</h3>
            </div>
            <div v-if="order.admin_notes" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              {{ order.admin_notes }}
            </div>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic py-2">No admin notes</p>
          </div>
        </div>
      </div>

      <!-- Messages Tab -->
      <div v-if="!editingOrder && activeTab === 'messages'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm min-h-[500px]">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>💬</span>
                <span>Order Messages</span>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Communicate with client and writer about this order</p>
            </div>
            <button
              v-if="threads.length === 0"
              @click="createNewMessageThread"
              :disabled="creatingThread"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <span v-if="creatingThread">⏳</span>
              <span v-else>➕</span>
              <span>{{ creatingThread ? 'Creating...' : 'Start Conversation' }}</span>
            </button>
          </div>
        </div>
        <SimplifiedOrderMessages :order-id="order.id" :show-thread-list="true" @thread-created="handleThreadCreated" />
      </div>

      <!-- Files Tab -->
      <div v-if="!editingOrder && activeTab === 'files'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>📁</span>
                <span>Order Files</span>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Upload and manage files for this special order</p>
            </div>
            <button
              @click="showFileUploadModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span>➕</span>
              <span>Upload File</span>
            </button>
          </div>

          <LoadingState 
            v-if="loadingFiles" 
            type="spinner" 
            size="medium"
            message="Loading files..."
          />

          <EmptyState
            v-else-if="files.length === 0"
            icon="📄"
            title="No files uploaded yet"
            description="Get started by uploading your first file for this special order."
            action-label="Upload First File"
            :action-handler="() => showFileUploadModal = true"
          />

          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">File</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Category</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Uploaded By</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="file in files" :key="file.id" class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-2">
                      <span class="text-xl">📄</span>
                      <div>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">{{ file.file_name || 'Unnamed' }}</span>
                        <div v-if="file.file_size" class="text-xs text-gray-500 dark:text-gray-400">
                          {{ formatFileSize(file.file_size) }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    <span v-if="getCategoryById(file.category)?.is_final_draft" class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-xs font-medium">
                      Final Draft
                    </span>
                    <span v-else>{{ getCategoryName(file.category) || '—' }}</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {{ file.uploaded_by_username || file.uploaded_by?.username || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {{ formatDate(file.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex items-center gap-2">
                      <button
                        @click="downloadFile(file)"
                        class="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-medium flex items-center gap-1"
                        title="Download"
                      >
                        <span>⬇️</span>
                        <span>Download</span>
                      </button>
                      <button
                        @click="deleteFile(file.id)"
                        class="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-xs font-medium flex items-center gap-1"
                        title="Delete"
                      >
                        <span>🗑️</span>
                        <span>Delete</span>
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

      <!-- File Upload Modal -->
      <div v-if="showFileUploadModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showFileUploadModal = false">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between z-10">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>📤</span>
                <span>Upload Files</span>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Upload files for Special Order #{{ order.id }}</p>
            </div>
            <button
              @click="showFileUploadModal = false"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-6">
            <!-- Category Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Category <span class="text-gray-400">(Optional)</span>
              </label>
              <select
                v-model="uploadForm.category"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option :value="null">No Category</option>
                <optgroup v-if="universalCategories.length > 0" label="Universal Categories">
                  <option v-for="cat in universalCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                    <span v-if="cat.is_final_draft"> (Final Draft)</span>
                  </option>
                </optgroup>
                <optgroup v-if="websiteSpecificCategories.length > 0" label="Website-Specific Categories">
                  <option v-for="cat in websiteSpecificCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                    <span v-if="cat.is_final_draft"> (Final Draft)</span>
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- File Upload Component -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Files
              </label>
              <FileUpload
                v-model="uploadedFiles"
                :multiple="true"
                :auto-upload="false"
                :max-size="100 * 1024 * 1024"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.zip,.rar,.xls,.xlsx,.ppt,.pptx"
                label="Drop files here or click to browse"
                @upload="handleFileSelect"
              />
            </div>

            <!-- Upload Status -->
            <div v-if="uploadSuccess" class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2">
              <span class="text-green-600 dark:text-green-400 text-xl">✅</span>
              <span class="text-green-700 dark:text-green-300">{{ uploadSuccess }}</span>
            </div>
            <div v-if="uploadError" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2">
              <span class="text-red-600 dark:text-red-400 text-xl">❌</span>
              <span class="text-red-700 dark:text-red-300">{{ uploadError }}</span>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                @click="showFileUploadModal = false"
                class="flex-1 px-4 py-2.5 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                @click="uploadSelectedFiles"
                :disabled="uploadedFiles.length === 0 || uploadingFiles"
                class="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                <span v-if="uploadingFiles" class="animate-spin">⏳</span>
                <span v-else>📤</span>
                <span>{{ uploadingFiles ? 'Uploading...' : `Upload ${uploadedFiles.length} File(s)` }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- History Tab -->
      <div v-if="!editingOrder && activeTab === 'history'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
        <div class="flex items-center gap-2 mb-6">
          <div class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <span class="text-purple-600 dark:text-purple-400 text-lg">📜</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Activity History</h3>
        </div>
        <LoadingState 
          v-if="loadingHistory" 
          type="spinner" 
          size="medium"
          message="Loading history..."
        />
        <EmptyState
          v-else-if="history.length === 0"
          icon="📜"
          title="No activity history available"
          description="Activity logs will appear here as actions are taken on this order."
        />
        <div v-else class="space-y-3">
          <div
            v-for="item in history"
            :key="item.id || item.timestamp"
            class="flex items-start gap-4 p-4 border-l-4 border-blue-500 bg-gradient-to-r from-gray-50 to-white dark:from-gray-900/50 dark:to-gray-800 rounded-r-lg hover:shadow-md transition-all"
          >
            <div class="text-3xl shrink-0">{{ getHistoryIcon(item.action || item.action_type || 'updated') }}</div>
            <div class="flex-1 min-w-0">
              <div class="font-semibold text-gray-900 dark:text-white mb-1">
                {{ item.description || item.message || item.action || 'Activity' }}
              </div>
              <div class="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2 flex-wrap">
                <span>🕐 {{ formatDateTime(item.created_at || item.timestamp || item.date) }}</span>
                <span v-if="item.user || item.actor" class="flex items-center gap-1">
                  <span>👤</span>
                  <span>by {{ item.user_username || item.actor?.username || item.user || item.actor || 'System' }}</span>
                </span>
              </div>
              <div v-if="item.changes" class="mt-2 text-xs text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 rounded p-2">
                <span class="font-medium">Changes:</span> {{ JSON.stringify(item.changes) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Tab -->
      <div v-if="!editingOrder && activeTab === 'related'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <span class="text-indigo-600 dark:text-indigo-400 text-lg">🔗</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Related Items & Links</h3>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="order.client" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <span class="text-green-600 dark:text-green-400 text-xl">👤</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Client Profile</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ order.client?.username || order.client?.email }}</div>
                </div>
                <router-link
                  v-if="order.client?.id"
                  :to="`/admin/users/${order.client.id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 font-bold text-lg"
                  title="View client profile"
                >
                  →
                </router-link>
                <span v-else class="text-gray-400">—</span>
              </div>
            </div>
            <div v-if="order.writer" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                  <span class="text-indigo-600 dark:text-indigo-400 text-xl">✍️</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Writer Profile</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ order.writer?.username || order.writer?.email }}</div>
                </div>
                <router-link
                  v-if="order.writer?.id"
                  :to="`/admin/users/${order.writer.id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 font-bold text-lg"
                  title="View writer profile"
                >
                  →
                </router-link>
                <span v-else class="text-gray-400">—</span>
              </div>
            </div>
            <div v-if="order.website" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <span class="text-blue-600 dark:text-blue-400 text-xl">🌐</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Website</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ order.website?.name || order.website?.domain }}</div>
                </div>
                <router-link
                  v-if="order.website?.id"
                  :to="`/admin/websites/${order.website.id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 font-bold text-lg"
                  title="View website"
                >
                  →
                </router-link>
                <span v-else class="text-gray-400">—</span>
              </div>
            </div>
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                  <span class="text-purple-600 dark:text-purple-400 text-xl">📋</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">All Special Orders</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">View all special orders</div>
                </div>
                <router-link
                  to="/admin/special-orders"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View all special orders"
                >
                  →
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Actions -->
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-xl border-2 border-blue-200 dark:border-gray-600 p-6 shadow-lg">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <span class="text-white text-lg">⚡</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Admin Actions</h3>
        </div>
        <div class="flex gap-3 flex-wrap">
          <button
            v-if="order.status === 'awaiting_approval' || order.status === 'inquiry'"
            @click="approveOrder"
            :disabled="processing"
            class="px-4 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-all font-medium shadow-sm hover:shadow-md flex items-center gap-2"
            title="Approve this special order to proceed"
          >
            <span>✅</span>
            <span>Approve Order</span>
          </button>
          <button
            v-if="order.status === 'in_progress'"
            @click="completeOrder"
            :disabled="processing"
            class="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-all font-medium shadow-sm hover:shadow-md flex items-center gap-2"
            title="Mark this order as completed"
          >
            <span>🏁</span>
            <span>Complete Order</span>
          </button>
          <button
            @click="overridePayment"
            :disabled="processing"
            class="px-4 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all font-medium shadow-sm hover:shadow-md flex items-center gap-2"
            title="Manually override payment status"
          >
            <span>💳</span>
            <span>Override Payment</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Assign Writer Modal -->
    <div v-if="showAssignWriterModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ order?.writer ? 'Reassign Writer' : 'Assign Writer' }}
          </h3>
          <button
            @click="showAssignWriterModal = false"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
          >
            ✕
          </button>
        </div>

        <div v-if="loadingWriters" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading writers...</p>
        </div>

        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Writers</label>
            <input
              v-model="writerSearch"
              type="text"
              placeholder="Search by name or email..."
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div class="max-h-64 overflow-y-auto border rounded-lg">
            <div
              v-for="writer in filteredWriters"
              :key="writer.id"
              @click="selectWriter(writer.id)"
              :class="[
                'p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-200 dark:border-gray-700',
                assignForm.writer_id === writer.id ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700' : ''
              ]"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ writer.username || writer.email }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ writer.email }}</p>
                  <p v-if="writer.writer_level" class="text-xs text-gray-400 dark:text-gray-500">
                    Level: {{ writer.writer_level.name || writer.writer_level }}
                  </p>
                </div>
                <div v-if="assignForm.writer_id === writer.id" class="text-blue-600 dark:text-blue-400">
                  ✓
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Payment Amount ($) <span class="text-gray-400">(Optional)</span>
              </label>
              <input
                v-model.number="assignForm.payment_amount"
                type="number"
                step="0.01"
                placeholder="Fixed amount"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                @input="assignForm.payment_percentage = null"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Payment Percentage (%) <span class="text-gray-400">(Optional)</span>
              </label>
              <input
                v-model.number="assignForm.payment_percentage"
                type="number"
                step="0.1"
                placeholder="Percentage of total"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                @input="assignForm.payment_amount = null"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Admin Notes (Optional)</label>
            <textarea
              v-model="assignForm.admin_notes"
              rows="3"
              placeholder="Add notes about this assignment..."
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              @click="showAssignWriterModal = false"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="assignWriter"
              :disabled="!assignForm.writer_id || processing"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ processing ? 'Assigning...' : (order?.writer ? 'Reassign Writer' : 'Assign Writer') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import specialOrdersAPI from '@/api/special-orders'
import { writerAssignmentAPI, orderFilesAPI, communicationsAPI, activityLogsAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import SimplifiedOrderMessages from '@/components/order/SimplifiedOrderMessages.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import LoadingState from '@/components/common/LoadingState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success: showSuccessToast, error: showErrorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const order = ref(null)
const processing = ref(false)
const saving = ref(false)
const editingOrder = ref(false)
const showAssignWriterModal = ref(false)
const activeTab = ref('overview')
const files = ref([])
const loadingFiles = ref(false)
const history = ref([])
const loadingHistory = ref(false)
const showFileUploadModal = ref(false)
const fileCategories = ref([])
const uploadedFiles = ref([])
const uploadingFiles = ref(false)
const uploadSuccess = ref('')
const uploadError = ref('')
const uploadForm = ref({
  category: null
})
const threads = ref([])
const creatingThread = ref(false)

const universalCategories = computed(() => {
  return fileCategories.value.filter(cat => cat.is_universal || cat.website === null)
})

const websiteSpecificCategories = computed(() => {
  if (!order.value?.website) return []
  return fileCategories.value.filter(cat => !cat.is_universal && cat.website === order.value.website?.id)
})

const tabs = computed(() => {
  const baseTabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'messages', label: 'Messages', icon: '💬', badge: null },
    { id: 'files', label: 'Files', icon: '📁', badge: files.value.length || null },
    { id: 'history', label: 'History', icon: '📜' },
    { id: 'related', label: 'Related', icon: '🔗' },
  ]
  return baseTabs
})
const loadingWriters = ref(false)
const writerSearch = ref('')
const availableWriters = ref([])

const editForm = ref({
  status: '',
  duration_days: 0,
  total_cost: 0,
  deposit_required: 0,
  inquiry_details: '',
  admin_notes: ''
})

const assignForm = ref({
  writer_id: null,
  payment_amount: null,
  payment_percentage: null,
  admin_notes: ''
})

const filteredWriters = computed(() => {
  if (!writerSearch.value) return availableWriters.value
  
  const search = writerSearch.value.toLowerCase()
  return availableWriters.value.filter(writer => {
    const name = (writer.username || '').toLowerCase()
    const email = (writer.email || '').toLowerCase()
    return name.includes(search) || email.includes(search)
  })
})

const loadOrder = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await specialOrdersAPI.get(route.params.id)
    order.value = res.data
    initializeEditForm()
    // Load related data
    await Promise.all([
      loadFiles(),
      loadHistory(),
      loadCategories()
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load special order'
    console.error('Error loading special order:', err)
  } finally {
    loading.value = false
  }
}

const loadFiles = async () => {
  if (!order.value) return
  loadingFiles.value = true
  try {
    // Try different parameter names for special orders
    const params = { 
      order: order.value.id,
      order_id: order.value.id,
      special_order: order.value.id,
      special_order_id: order.value.id
    }
    const res = await orderFilesAPI.list(params)
    files.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading files:', err)
    files.value = []
  } finally {
    loadingFiles.value = false
  }
}

const loadHistory = async () => {
  if (!order.value) return
  loadingHistory.value = true
  try {
    // Try multiple possible endpoints/parameters
    const params = { 
      object_type: 'special_order', 
      object_id: order.value.id,
      ordering: '-created_at'
    }
    const res = await activityLogsAPI.list(params)
    history.value = res.data.results || res.data || []
    
    // If no results, try alternative approach - get order transitions
    if (history.value.length === 0) {
      // Fallback: create history from order data
      const orderHistory = []
      if (order.value.created_at) {
        orderHistory.push({
          id: 'created',
          action: 'created',
          description: `Special order #${order.value.id} was created`,
          created_at: order.value.created_at,
          user: order.value.client?.username || 'System'
        })
      }
      if (order.value.updated_at && order.value.updated_at !== order.value.created_at) {
        orderHistory.push({
          id: 'updated',
          action: 'updated',
          description: `Order was last updated`,
          created_at: order.value.updated_at,
          user: 'System'
        })
      }
      history.value = orderHistory
    }
  } catch (err) {
    console.error('Error loading history:', err)
    // Fallback history
    history.value = [{
      id: 'created',
      action: 'created',
      description: `Special order #${order.value.id} was created`,
      created_at: order.value.created_at,
      user: order.value.client?.username || 'System'
    }]
  } finally {
    loadingHistory.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await orderFilesAPI.listCategories()
    fileCategories.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading categories:', err)
    fileCategories.value = []
  }
}

const getCategoryName = (categoryId) => {
  const category = fileCategories.value.find(c => c.id === categoryId)
  return category?.name || null
}

const getCategoryById = (categoryId) => {
  return fileCategories.value.find(c => c.id === categoryId) || null
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleFileSelect = (fileList) => {
  // Files selected, ready for upload
}

const uploadSelectedFiles = async () => {
  if (uploadedFiles.value.length === 0 || !order.value) return
  
  uploadingFiles.value = true
  uploadError.value = ''
  uploadSuccess.value = ''
  
  try {
    const uploadPromises = uploadedFiles.value.map(async (fileObj) => {
      const formData = new FormData()
      formData.append('file', fileObj.file || fileObj)
      formData.append('order', order.value.id)
      
      // Try different field names for special orders
      formData.append('special_order', order.value.id)
      
      if (uploadForm.value.category) {
        formData.append('category', uploadForm.value.category)
      }
      
      return await orderFilesAPI.upload(formData)
    })
    
    await Promise.all(uploadPromises)
    uploadSuccess.value = `Successfully uploaded ${uploadedFiles.value.length} file(s)!`
    
    // Clear form
    uploadedFiles.value = []
    uploadForm.value.category = null
    
    // Reload files
    await loadFiles()
    
    setTimeout(() => {
      uploadSuccess.value = ''
      if (uploadedFiles.value.length === 0) {
        showFileUploadModal.value = false
      }
    }, 3000)
  } catch (error) {
    uploadError.value = 'Failed to upload files: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => {
      uploadError.value = ''
    }, 5000)
  } finally {
    uploadingFiles.value = false
  }
}

const downloadFile = async (file) => {
  try {
    if (file.download_url || file.url) {
      window.open(file.download_url || file.url, '_blank')
      return
    }
    
    // Try to get signed URL
    const res = await orderFilesAPI.getSignedUrl(file.id)
    if (res.data.url) {
      window.open(res.data.url, '_blank')
    } else {
      // Fallback: direct download
      const blob = await orderFilesAPI.download(file.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.file_name || 'download'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  } catch (err) {
    showErrorToast('Failed to download file: ' + (err.response?.data?.detail || err.message))
  }
}

const createNewMessageThread = async () => {
  creatingThread.value = true
  try {
    await communicationsAPI.startThreadForOrder(order.value.id)
    showSuccessToast('Conversation started!')
    // Reload threads in SimplifiedOrderMessages component
    await loadOrder()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to start conversation')
  } finally {
    creatingThread.value = false
  }
}

const handleThreadCreated = () => {
  // Thread was created, refresh if needed
  loadOrder()
}

const deleteFile = async (fileId) => {
  if (!confirm('Are you sure you want to delete this file?')) return
  try {
    await orderFilesAPI.delete(fileId)
    showSuccessToast('File deleted successfully')
    await loadFiles()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to delete file')
  }
}

const getHistoryIcon = (action) => {
  const icons = {
    'created': '✨',
    'updated': '✏️',
    'status_changed': '🔄',
    'assigned': '👤',
    'approved': '✅',
    'completed': '🏁',
    'cancelled': '❌',
  }
  return icons[action] || '📝'
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const initializeEditForm = () => {
  if (order.value) {
    editForm.value = {
      status: order.value.status || '',
      duration_days: order.value.duration_days || 0,
      total_cost: parseFloat(order.value.total_cost || 0),
      deposit_required: parseFloat(order.value.deposit_required || 0),
      inquiry_details: order.value.inquiry_details || '',
      admin_notes: order.value.admin_notes || ''
    }
  }
}

const saveOrder = async () => {
  saving.value = true
  try {
    await specialOrdersAPI.update(order.value.id, editForm.value)
    showSuccessToast('Special order updated successfully!')
    editingOrder.value = false
    await loadOrder()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to update order')
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  editingOrder.value = false
  initializeEditForm()
}

const approveOrder = async () => {
  if (!confirm('Are you sure you want to approve this special order?')) return
  
  processing.value = true
  try {
    await specialOrdersAPI.approve(order.value.id)
    showSuccessToast('Special order approved successfully!')
    await loadOrder()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to approve order')
  } finally {
    processing.value = false
  }
}

const completeOrder = async () => {
  if (!confirm('Are you sure you want to mark this order as completed?')) return
  
  processing.value = true
  try {
    await specialOrdersAPI.completeOrder(order.value.id)
    showSuccessToast('Special order marked as completed!')
    await loadOrder()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to complete order')
  } finally {
    processing.value = false
  }
}

const overridePayment = async () => {
  if (!confirm('Are you sure you want to override the payment status for this order?')) return
  
  processing.value = true
  try {
    await specialOrdersAPI.overridePayment(order.value.id)
    showSuccessToast('Payment status overridden successfully!')
    await loadOrder()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to override payment')
  } finally {
    processing.value = false
  }
}

const loadWriters = async () => {
  loadingWriters.value = true
  try {
    const res = await writerAssignmentAPI.getAvailableWriters()
    availableWriters.value = res.data.writers || res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading writers:', err)
    showErrorToast('Failed to load writers')
    availableWriters.value = []
  } finally {
    loadingWriters.value = false
  }
}

const selectWriter = (writerId) => {
  assignForm.value.writer_id = assignForm.value.writer_id === writerId ? null : writerId
}

const assignWriter = async () => {
  if (!assignForm.value.writer_id) {
    showErrorToast('Please select a writer')
    return
  }
  
  processing.value = true
  try {
    const data = {
      writer_id: assignForm.value.writer_id
    }
    
    if (assignForm.value.payment_amount) {
      data.payment_amount = assignForm.value.payment_amount
    } else if (assignForm.value.payment_percentage) {
      data.payment_percentage = assignForm.value.payment_percentage
    }
    
    if (assignForm.value.admin_notes) {
      data.admin_notes = assignForm.value.admin_notes
    }
    
    await specialOrdersAPI.assignWriter(order.value.id, data)
    showSuccessToast('Writer assigned successfully!')
    showAssignWriterModal.value = false
    assignForm.value = {
      writer_id: null,
      payment_amount: null,
      payment_percentage: null,
      admin_notes: ''
    }
    await loadOrder()
  } catch (err) {
    showErrorToast(err.response?.data?.error || err.response?.data?.detail || 'Failed to assign writer')
  } finally {
    processing.value = false
  }
}

const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'awaiting_approval': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'inquiry': 'Inquiry',
    'awaiting_approval': 'Awaiting Approval',
    'in_progress': 'In Progress',
    'completed': 'Completed',
  }
  return labels[status] || status
}

const getStatusTooltip = (status) => {
  const tooltips = {
    'inquiry': 'Initial inquiry submitted by client. Awaiting admin review and pricing.',
    'awaiting_approval': 'Order details reviewed. Waiting for admin approval before proceeding.',
    'in_progress': 'Order approved and assigned. Writer is actively working on this order.',
    'completed': 'Order has been completed and delivered to the client.',
  }
  return tooltips[status] || `Status: ${getStatusLabel(status)}`
}

const getStatusIcon = (status) => {
  const icons = {
    'inquiry': '📝',
    'awaiting_approval': '⏳',
    'in_progress': '🔄',
    'completed': '✅',
  }
  return icons[status] || '📌'
}

const formatCurrency = (value) => {
  return parseFloat(value || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const openAssignWriterModal = () => {
  showAssignWriterModal.value = true
  loadWriters()
}

onMounted(() => {
  loadOrder()
})
</script>
