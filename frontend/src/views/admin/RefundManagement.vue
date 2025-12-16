<template>
  <div class="space-y-6 p-4 md:p-6" v-if="!componentError && !initialLoading">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Refund Management</h1>
        <p class="mt-2 text-sm md:text-base text-gray-600 dark:text-gray-400">Manage refund requests, approvals, and processing</p>
      </div>
      <button 
        @click="createNewRefund" 
        class="w-full sm:w-auto px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center justify-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Refund
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border border-yellow-200 dark:border-yellow-800">
        <p class="text-xs sm:text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending Refunds</p>
        <p class="text-2xl sm:text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-800">
        <p class="text-xs sm:text-sm font-medium text-green-700 dark:text-green-300 mb-1">Processed</p>
        <p class="text-2xl sm:text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.processed || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border border-red-200 dark:border-red-800">
        <p class="text-xs sm:text-sm font-medium text-red-700 dark:text-red-300 mb-1">Rejected</p>
        <p class="text-2xl sm:text-3xl font-bold text-red-900 dark:text-red-100">{{ stats.rejected || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-800">
        <p class="text-xs sm:text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Amount</p>
        <p class="text-2xl sm:text-3xl font-bold text-blue-900 dark:text-blue-100">${{ stats.total_amount.toFixed(2) }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
      <nav class="-mb-px flex space-x-4 sm:space-x-8 min-w-max">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm transition-colors',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Refunds Tab -->
    <div v-if="activeTab === 'refunds'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
            <select v-model="filters.status" @change="loadRefunds" class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processed">Processed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Refund Method</label>
            <select v-model="filters.refund_method" @change="loadRefunds" class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm">
              <option value="">All Methods</option>
              <option value="wallet">Wallet</option>
              <option value="external">External</option>
            </select>
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website</label>
            <select v-model="filters.website" @change="loadRefunds" class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm">
              <option value="">All Websites</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Client, order ID..."
              class="w-full border dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded px-3 py-2 text-sm"
            />
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium">Reset</button>
          </div>
        </div>
      </div>

      <!-- Refunds Table -->
      <div class="card overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">ID</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Client</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Order Payment</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Amount</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Method</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Processed</th>
                  <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="refund in refunds" :key="refund.id" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    #{{ refund.id }}
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {{ refund.client?.username || refund.client?.email || 'N/A' }}
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    Payment #{{ typeof refund.order_payment === 'object' ? refund.order_payment?.id : refund.order_payment || 'N/A' }}
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-semibold">
                    ${{ formatRefundAmount(refund) }}
                    <span v-if="refund.wallet_amount > 0 && refund.external_amount > 0" class="text-xs text-gray-500 dark:text-gray-400 block">
                      (${{ parseFloat(refund.wallet_amount || 0).toFixed(2) }} wallet + ${{ parseFloat(refund.external_amount || 0).toFixed(2) }} external)
                    </span>
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    <span class="capitalize">{{ refund.refund_method || 'wallet' }}</span>
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap">
                    <span :class="getStatusClass(refund.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ refund.status || 'pending' }}
                    </span>
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    <div v-if="refund.processed_at">
                      <div>{{ formatDate(refund.processed_at) }}</div>
                      <div class="text-xs text-gray-400 dark:text-gray-500" v-if="refund.processed_by">
                        by {{ typeof refund.processed_by === 'object' ? refund.processed_by?.username : 'Admin' }}
                      </div>
                    </div>
                    <span v-else class="text-gray-400 dark:text-gray-500">Not processed</span>
                  </td>
                  <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex flex-wrap gap-2">
                      <button @click="viewRefund(refund)" class="text-blue-600 dark:text-blue-400 hover:underline">View</button>
                      <button
                        v-if="refund.status === 'pending'"
                        @click="processRefund(refund)"
                        class="text-green-600 dark:text-green-400 hover:underline"
                      >
                        Process
                      </button>
                      <button
                        v-if="refund.status === 'pending'"
                        @click="cancelRefund(refund)"
                        class="text-red-600 dark:text-red-400 hover:underline"
                      >
                        Cancel
                      </button>
                      <button
                        v-if="refund.status === 'rejected'"
                        @click="retryRefund(refund)"
                        class="text-yellow-600 dark:text-yellow-400 hover:underline"
                      >
                        Retry
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="!refunds.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
            No refunds found.
          </div>
        </div>
      </div>
    </div>

    <!-- Logs Tab -->
    <div v-if="activeTab === 'logs'" class="space-y-4">
      <div class="card overflow-hidden">
        <div v-if="logsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Processed By</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="log in refundLogs" :key="log.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDateTime(log.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ log.client?.username || log.client?.email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  #{{ typeof log.order === 'object' ? log.order?.id : log.order || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                  ${{ parseFloat(log.amount || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                  {{ log.action || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusClass(log.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ log.status || 'N/A' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ typeof log.processed_by === 'object' ? log.processed_by?.username : log.processed_by || 'N/A' }}
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!refundLogs.length" class="text-center py-12 text-gray-500">
            No refund logs found.
          </div>
        </div>
      </div>
    </div>

    <!-- Receipts Tab -->
    <div v-if="activeTab === 'receipts'" class="space-y-4">
      <div class="card overflow-hidden">
        <div v-if="receiptsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference Code</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Generated</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="receipt in refundReceipts" :key="receipt.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ receipt.reference_code || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ receipt.client?.username || receipt.client?.email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                  ${{ parseFloat(receipt.amount || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDateTime(receipt.generated_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="viewReceipt(receipt)" class="text-blue-600 hover:underline">View</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!refundReceipts.length" class="text-center py-12 text-gray-500">
            No refund receipts found.
          </div>
        </div>
      </div>
    </div>

    <!-- Refund Detail Modal -->
    <div v-if="viewingRefund" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full my-auto p-4 md:p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Refund Details</h3>
          <button @click="viewingRefund = null" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-2xl">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-gray-600">Refund ID:</span>
              <p class="text-gray-900 font-medium">#{{ viewingRefund.id }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <span :class="getStatusClass(viewingRefund.status)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ viewingRefund.status || 'pending' }}
              </span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Client:</span>
              <p class="text-gray-900">{{ viewingRefund.client?.username || viewingRefund.client?.email || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Website:</span>
              <p class="text-gray-900">{{ typeof viewingRefund.website === 'object' ? viewingRefund.website?.name : 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Order Payment:</span>
              <p class="text-gray-900">#{{ typeof viewingRefund.order_payment === 'object' ? viewingRefund.order_payment?.id : viewingRefund.order_payment || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Refund Type:</span>
              <p class="text-gray-900 capitalize">{{ viewingRefund.type || 'manual' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Total Amount:</span>
              <p class="text-gray-900 font-semibold text-lg">
                ${{ formatRefundAmount(viewingRefund) }}
              </p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Refund Method:</span>
              <p class="text-gray-900 capitalize">{{ viewingRefund.refund_method || 'wallet' }}</p>
            </div>
            <div v-if="viewingRefund.wallet_amount > 0">
              <span class="text-sm font-medium text-gray-600">Wallet Amount:</span>
              <p class="text-gray-900">${{ parseFloat(viewingRefund.wallet_amount || 0).toFixed(2) }}</p>
            </div>
            <div v-if="viewingRefund.external_amount > 0">
              <span class="text-sm font-medium text-gray-600">External Amount:</span>
              <p class="text-gray-900">${{ parseFloat(viewingRefund.external_amount || 0).toFixed(2) }}</p>
            </div>
            <div v-if="viewingRefund.processed_at">
              <span class="text-sm font-medium text-gray-600">Processed At:</span>
              <p class="text-gray-900">{{ formatDateTime(viewingRefund.processed_at) }}</p>
            </div>
            <div v-if="viewingRefund.processed_by">
              <span class="text-sm font-medium text-gray-600">Processed By:</span>
              <p class="text-gray-900">{{ typeof viewingRefund.processed_by === 'object' ? viewingRefund.processed_by?.username : viewingRefund.processed_by || 'N/A' }}</p>
            </div>
          </div>

          <div v-if="viewingRefund.error_message" class="border-t pt-4">
            <span class="text-sm font-medium text-red-600">Error Message:</span>
            <p class="text-red-700 mt-1">{{ viewingRefund.error_message }}</p>
          </div>

          <div v-if="viewingRefund.metadata && Object.keys(viewingRefund.metadata).length > 0" class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Metadata:</span>
            <pre class="text-xs text-gray-700 mt-1 bg-gray-50 p-2 rounded overflow-auto">{{ JSON.stringify(viewingRefund.metadata, null, 2) }}</pre>
          </div>

          <!-- Actions -->
          <div class="border-t pt-4 flex gap-2">
            <button
              v-if="viewingRefund.status === 'pending'"
              @click="processRefund(viewingRefund)"
              class="btn btn-primary bg-green-600 hover:bg-green-700"
            >
              Process Refund
            </button>
            <button
              v-if="viewingRefund.status === 'pending'"
              @click="cancelRefund(viewingRefund)"
              class="btn btn-primary bg-red-600 hover:bg-red-700"
            >
              Cancel Refund
            </button>
            <button
              v-if="viewingRefund.status === 'rejected'"
              @click="retryRefund(viewingRefund)"
              class="btn btn-primary bg-yellow-600 hover:bg-yellow-700"
            >
              Retry Refund
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Receipt Detail Modal -->
    <div v-if="viewingReceipt" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full my-auto p-4 md:p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Refund Receipt Details</h3>
          <button @click="viewingReceipt = null" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-2xl">✕</button>
        </div>

        <div v-if="receiptLoading" class="flex items-center justify-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>

        <div v-else-if="receiptError" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ receiptError }}
        </div>

        <div v-else-if="viewingReceipt" class="space-y-6">
          <!-- Receipt Header -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white">Receipt #{{ viewingReceipt.reference_code || viewingReceipt.id }}</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Generated: {{ formatDateTime(viewingReceipt.generated_at) }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Amount</p>
                <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">${{ parseFloat(viewingReceipt.amount || 0).toFixed(2) }}</p>
              </div>
            </div>
          </div>

          <!-- Receipt Details -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Receipt ID</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">#{{ viewingReceipt.id }}</p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Reference Code</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">{{ viewingReceipt.reference_code || 'N/A' }}</p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Client</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">
                {{ viewingReceipt.client?.username || viewingReceipt.client?.email || viewingReceipt.client || 'N/A' }}
              </p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Order Payment ID</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">
                #{{ typeof viewingReceipt.order_payment === 'object' ? viewingReceipt.order_payment?.id : viewingReceipt.order_payment || 'N/A' }}
              </p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Refund ID</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">
                #{{ typeof viewingReceipt.refund === 'object' ? viewingReceipt.refund?.id : viewingReceipt.refund || 'N/A' }}
              </p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Processed By</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">
                {{ typeof viewingReceipt.processed_by === 'object' ? viewingReceipt.processed_by?.username || viewingReceipt.processed_by?.email : viewingReceipt.processed_by || 'N/A' }}
              </p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Website</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">
                {{ typeof viewingReceipt.website === 'object' ? viewingReceipt.website?.name : viewingReceipt.website || 'N/A' }}
              </p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Generated At</span>
              <p class="text-gray-900 dark:text-white font-medium mt-1">{{ formatDateTime(viewingReceipt.generated_at) }}</p>
            </div>
          </div>

          <!-- Reason -->
          <div v-if="viewingReceipt.reason" class="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <span class="text-sm font-medium text-yellow-800 dark:text-yellow-300">Refund Reason</span>
            <p class="text-yellow-900 dark:text-yellow-200 mt-2">{{ viewingReceipt.reason }}</p>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="downloadReceipt(viewingReceipt)"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              Download Receipt
            </button>
            <button
              @click="viewingReceipt = null"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Refund Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full my-auto p-4 md:p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Create Refund</h3>
          <button @click="closeCreateModal" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-2xl">✕</button>
        </div>
        <form @submit.prevent="saveRefund" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Order Payment ID *</label>
            <input v-model.number="refundForm.order_payment" type="number" required class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm" placeholder="Enter order payment ID" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Wallet Amount ($)</label>
              <input v-model.number="refundForm.wallet_amount" type="number" step="0.01" min="0" class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">External Amount ($)</label>
              <input v-model.number="refundForm.external_amount" type="number" step="0.01" min="0" class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Refund Method *</label>
            <select v-model="refundForm.refund_method" required class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm">
              <option value="wallet">Wallet</option>
              <option value="external">External</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Refund Type</label>
            <select v-model="refundForm.type" class="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded px-3 py-2 text-sm">
              <option value="manual">Manual</option>
              <option value="automated">Automated</option>
            </select>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeCreateModal" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium">Cancel</button>
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm font-medium">
              {{ saving ? 'Creating...' : 'Create Refund' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300' : 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300'">
      {{ message }}
    </div>

    <!-- Password Verification Modal -->
    <PasswordVerificationModal
      :show="showPasswordModal"
      @update:show="showPasswordModal = $event"
      :title="passwordModalTitle"
      :subtitle="passwordModalSubtitle"
      :warning-message="passwordModalWarning"
      :confirm-button-text="passwordModalConfirmText"
      :loading="passwordVerifying"
      :require-username="true"
      :saved-usernames="savedAdminIdentities"
      :default-username="savedAdminIdentities[0] || ''"
      @confirm="handlePasswordConfirm"
      @cancel="handlePasswordCancel"
      ref="passwordModalRef"
    />
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 dark:text-red-300 mb-2">Error Loading Page</h2>
      <p class="text-red-700 dark:text-red-300 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
  </div>

  <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show"
      :title="confirm.title"
      :message="confirm.message"
      :details="confirm.details"
      :variant="confirm.variant"
      :icon="confirm.icon"
      :confirm-text="confirm.confirmText"
      :cancel-text="confirm.cancelText"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { refundsAPI } from '@/api'
import adminRefundsAPI from '@/api/admin-refunds'
import apiClient from '@/api/client'
import PasswordVerificationModal from '@/components/common/PasswordVerificationModal.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import { useAuthStore } from '@/stores/auth'

const confirm = useConfirmDialog()
const authStore = useAuthStore()

const componentError = ref(null)
const initialLoading = ref(true)
const activeTab = ref('refunds')
const tabs = [
  { id: 'refunds', label: 'Refunds' },
  { id: 'logs', label: 'Refund Logs' },
  { id: 'receipts', label: 'Refund Receipts' },
]

const refunds = ref([])
const refundLogs = ref([])
const refundReceipts = ref([])
const websites = ref([])
const loading = ref(false)
const logsLoading = ref(false)
const receiptsLoading = ref(false)
const saving = ref(false)
const viewingRefund = ref(null)
const viewingReceipt = ref(null)
const receiptLoading = ref(false)
const receiptError = ref(null)
const showCreateModal = ref(false)
const showPasswordModal = ref(false)
const passwordVerifying = ref(false)
const passwordModalRef = ref(null)
const passwordModalTitle = ref('Confirm Refund Action')
const passwordModalSubtitle = ref('This action requires password verification')
const passwordModalWarning = ref(null)
const passwordModalConfirmText = ref('Confirm')
const pendingAction = ref(null) // Store the action to execute after password verification

const stats = ref({
  pending: 0,
  processed: 0,
  rejected: 0,
  total_amount: 0,
})

const filters = ref({
  status: '',
  refund_method: '',
  website: '',
  search: '',
})

const refundForm = ref({
  order_payment: null,
  wallet_amount: 0,
  external_amount: 0,
  refund_method: 'wallet',
  type: 'manual',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadRefunds()
  }, 500)
}

const loadRefunds = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) {
      params.status = filters.value.status
    }
    if (filters.value.refund_method) {
      params.refund_method = filters.value.refund_method
    }
    if (filters.value.website) {
      params.website = filters.value.website
    }
    if (filters.value.search) {
      params.search = filters.value.search
    }

    const res = await refundsAPI.list(params)
    refunds.value = res.data.results || res.data || []
    calculateStats()
  } catch (error) {
    showMessage('Failed to load refunds: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const loadRefundLogs = async () => {
  logsLoading.value = true
  try {
    const res = await refundsAPI.listLogs()
    refundLogs.value = res.data.results || res.data || []
  } catch (error) {
    showMessage('Failed to load refund logs: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    logsLoading.value = false
  }
}

const loadRefundReceipts = async () => {
  receiptsLoading.value = true
  try {
    const res = await refundsAPI.listReceipts()
    refundReceipts.value = res.data.results || res.data || []
  } catch (error) {
    showMessage('Failed to load refund receipts: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    receiptsLoading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const loadDashboard = async () => {
  try {
    const res = await adminRefundsAPI.getDashboard()
    const dashboard = res.data
    
    if (dashboard.summary) {
      stats.value = {
        pending: dashboard.summary.pending_refunds || 0,
        processed: dashboard.summary.processed_refunds || 0,
        rejected: dashboard.summary.rejected_refunds || 0,
        total_amount: parseFloat(dashboard.summary.total_amount || 0),
      }
    }
  } catch (error) {
    // Only log if it's not a 404 (endpoint doesn't exist)
    if (error?.response?.status !== 404) {
      console.error('Failed to load refund dashboard:', error)
    }
    // Fallback to calculating from refunds list
    calculateStats()
  }
}

const calculateStats = () => {
  stats.value = {
    pending: refunds.value.filter(r => r.status === 'pending').length,
    processed: refunds.value.filter(r => r.status === 'processed').length,
    rejected: refunds.value.filter(r => r.status === 'rejected').length,
    total_amount: refunds.value.reduce((sum, r) => {
      const amount = r.total_amount || (parseFloat(r.wallet_amount || 0) + parseFloat(r.external_amount || 0))
      return sum + parseFloat(amount)
    }, 0),
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    refund_method: '',
    website: '',
    search: '',
  }
  loadRefunds()
}

const viewRefund = async (refund) => {
  try {
    const res = await refundsAPI.get(refund.id)
    viewingRefund.value = res.data
  } catch (error) {
    viewingRefund.value = refund
    showMessage('Failed to load refund details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const processRefund = async (refund) => {
  const amount = parseFloat(refund.total_amount || (parseFloat(refund.wallet_amount || 0) + parseFloat(refund.external_amount || 0))).toFixed(2)
  passwordModalTitle.value = 'Process Refund'
  passwordModalSubtitle.value = `Processing refund of $${amount}`
  passwordModalWarning.value = `You are about to process a refund of $${amount}. This action will credit the client's wallet or initiate external refund. This action cannot be undone.`
  passwordModalConfirmText.value = 'Process Refund'
  pendingAction.value = { type: 'process', refund }
  showPasswordModal.value = true
}

const cancelRefund = async (refund) => {
  const amount = parseFloat(refund.total_amount || (parseFloat(refund.wallet_amount || 0) + parseFloat(refund.external_amount || 0))).toFixed(2)
  passwordModalTitle.value = 'Cancel Refund'
  passwordModalSubtitle.value = `Canceling refund of $${amount}`
  passwordModalWarning.value = `You are about to cancel this refund request. This action cannot be undone.`
  passwordModalConfirmText.value = 'Cancel Refund'
  pendingAction.value = { type: 'cancel', refund }
  showPasswordModal.value = true
}

const retryRefund = async (refund) => {
  const amount = parseFloat(refund.total_amount || (parseFloat(refund.wallet_amount || 0) + parseFloat(refund.external_amount || 0))).toFixed(2)
  const confirmed = await confirm.showDialog(
    `Are you sure you want to retry this refund?`,
    'Retry Refund',
    {
      details: `This will retry processing refund #${refund.id} for $${amount}. The refund will be processed again using the configured refund method.`,
      confirmText: 'Retry Refund',
      cancelText: 'Cancel',
      icon: '🔄'
    }
  )
  
  if (!confirmed) return
  
  saving.value = true
  try {
    await refundsAPI.retry(refund.id)
    showMessage('Refund retried successfully', true)
    await loadRefunds()
    if (viewingRefund.value?.id === refund.id) {
      viewingRefund.value = null
    }
  } catch (error) {
    showMessage('Failed to retry refund: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const createNewRefund = () => {
  refundForm.value = {
    order_payment: null,
    wallet_amount: 0,
    external_amount: 0,
    refund_method: 'wallet',
    type: 'manual',
  }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  refundForm.value = {
    order_payment: null,
    wallet_amount: 0,
    external_amount: 0,
    refund_method: 'wallet',
    type: 'manual',
  }
}

const saveRefund = async () => {
  saving.value = true
  try {
    const data = {
      order_payment: refundForm.value.order_payment,
      wallet_amount: parseFloat(refundForm.value.wallet_amount || 0),
      external_amount: parseFloat(refundForm.value.external_amount || 0),
      refund_method: refundForm.value.refund_method,
      type: refundForm.value.type,
    }
    
    await refundsAPI.create(data)
    showMessage('Refund created successfully', true)
    closeCreateModal()
    await loadRefunds()
  } catch (error) {
    showMessage('Failed to create refund: ' + (error.response?.data?.detail || error.message || 'Unknown error'), false)
  } finally {
    saving.value = false
  }
}

const viewReceipt = async (receipt) => {
  receiptLoading.value = true
  receiptError.value = null
  
  try {
    // If receipt is just an ID, fetch full details
    if (typeof receipt === 'number' || (typeof receipt === 'object' && !receipt.reference_code)) {
      const receiptId = typeof receipt === 'number' ? receipt : receipt.id
      const response = await refundsAPI.getReceipt(receiptId)
      viewingReceipt.value = response.data
    } else {
      // Use the receipt object directly
      viewingReceipt.value = receipt
    }
  } catch (error) {
    receiptError.value = error.response?.data?.detail || error.message || 'Failed to load receipt details'
    showMessage('Failed to load receipt details: ' + receiptError.value, false)
  } finally {
    receiptLoading.value = false
  }
}

const downloadReceipt = async (receipt) => {
  try {
    // Get full receipt details if needed
    let receiptData = receipt
    if (typeof receipt === 'number' || (receipt && !receipt.reference_code)) {
      const receiptId = typeof receipt === 'number' ? receipt : receipt.id
      const response = await refundsAPI.getReceipt(receiptId)
      receiptData = response.data
    }
    
    // Generate printable receipt HTML
    const receiptHTML = generateReceiptHTML(receiptData)
    
    // Open in new window for printing/downloading
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      showMessage('Please allow popups to download receipt', false)
      return
    }
    
    printWindow.document.write(receiptHTML)
    printWindow.document.close()
    
    // Wait for content to load, then trigger print dialog
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print()
        showMessage('Receipt ready for printing/download', true)
      }, 250)
    }
  } catch (error) {
    console.error('Failed to download receipt:', error)
    showMessage('Failed to download receipt: ' + (error.response?.data?.detail || error.message), false)
  }
}

const generateReceiptHTML = (receipt) => {
  const date = receipt.generated_at ? new Date(receipt.generated_at).toLocaleString() : new Date().toLocaleString()
  const referenceCode = receipt.reference_code || receipt.id || 'N/A'
  const amount = parseFloat(receipt.amount || 0).toFixed(2)
  const clientName = receipt.client?.username || receipt.client?.email || 'N/A'
  const websiteName = receipt.website?.name || 'N/A'
  const reason = receipt.reason || 'N/A'
  const processedBy = receipt.processed_by?.username || receipt.processed_by?.email || 'N/A'
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Refund Receipt - ${referenceCode}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          padding: 40px;
          color: #333;
          max-width: 800px;
          margin: 0 auto;
        }
        .header {
          text-align: center;
          border-bottom: 3px solid #3b82f6;
          padding-bottom: 20px;
          margin-bottom: 30px;
        }
        .header h1 {
          color: #1f2937;
          margin: 0;
          font-size: 28px;
        }
        .receipt-info {
          background: #f9fafb;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
        }
        .info-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #e5e7eb;
        }
        .info-row:last-child {
          border-bottom: none;
        }
        .info-label {
          font-weight: 600;
          color: #6b7280;
        }
        .info-value {
          color: #111827;
          font-weight: 500;
        }
        .amount {
          font-size: 24px;
          color: #059669;
          font-weight: bold;
        }
        .footer {
          margin-top: 40px;
          padding-top: 20px;
          border-top: 1px solid #e5e7eb;
          text-align: center;
          color: #6b7280;
          font-size: 12px;
        }
        @media print {
          body { padding: 20px; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Refund Receipt</h1>
        <p style="color: #6b7280; margin: 5px 0;">Reference: ${referenceCode}</p>
      </div>
      
      <div class="receipt-info">
        <div class="info-row">
          <span class="info-label">Amount Refunded:</span>
          <span class="info-value amount">$${amount}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Client:</span>
          <span class="info-value">${clientName}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Website:</span>
          <span class="info-value">${websiteName}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Date:</span>
          <span class="info-value">${date}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Processed By:</span>
          <span class="info-value">${processedBy}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Reason:</span>
          <span class="info-value">${reason}</span>
        </div>
        ${receipt.refund ? `
        <div class="info-row">
          <span class="info-label">Refund ID:</span>
          <span class="info-value">#${receipt.refund.id || receipt.refund}</span>
        </div>
        ` : ''}
      </div>
      
      <div class="footer">
        <p>This is an official refund receipt. Please keep this for your records.</p>
        <p>Generated on ${date}</p>
      </div>
    </body>
    </html>
  `
}

const handlePasswordConfirm = async (credentials) => {
  // Support both object (with username/password) and string (password only)
  const password = credentials?.password || credentials
  if (!pendingAction.value) return
  
  passwordVerifying.value = true
  if (passwordModalRef.value) {
    passwordModalRef.value.setError('')
  }
  
  try {
    const { type, refund } = pendingAction.value
    
    if (type === 'process') {
      await refundsAPI.process(refund.id, { 
        reason: 'Refund processed by admin',
        password: password
      })
      showMessage('Refund processed successfully', true)
      await loadRefunds()
      if (viewingRefund.value?.id === refund.id) {
        viewingRefund.value = null
      }
    } else if (type === 'cancel') {
      await refundsAPI.cancel(refund.id, { password: password })
      showMessage('Refund canceled successfully', true)
      await loadRefunds()
      if (viewingRefund.value?.id === refund.id) {
        viewingRefund.value = null
      }
    }
    
    // Close modal and reset
    showPasswordModal.value = false
    pendingAction.value = null
    if (passwordModalRef.value) {
      passwordModalRef.value.clearPassword()
    }
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.response?.data?.detail || error.message || 'Action failed'
    
    // If it's a password error, show it in the modal
    if (errorMessage.toLowerCase().includes('password') || error.response?.status === 400) {
      if (passwordModalRef.value) {
        passwordModalRef.value.setError(errorMessage)
      }
    } else {
      // For other errors, close modal and show message
      showPasswordModal.value = false
      showMessage(errorMessage, false)
      pendingAction.value = null
    }
  } finally {
    passwordVerifying.value = false
  }
}

const handlePasswordCancel = () => {
  pendingAction.value = null
  if (passwordModalRef.value) {
    passwordModalRef.value.clearPassword()
  }
}

const getStatusClass = (status) => {
  if (status === 'processed') return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
  if (status === 'rejected') return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
  return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'
}

const formatRefundAmount = (refund) => {
  if (!refund) return '0.00'
  const amount = refund.total_amount || (parseFloat(refund.wallet_amount || 0) + parseFloat(refund.external_amount || 0))
  return parseFloat(amount).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const message = ref('')
const messageSuccess = ref(false)

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

// Saved admin identities for quick-select in password modal
const savedAdminIdentities = computed(() => {
  const identities = []
  const user = authStore.user
  if (user?.username) identities.push(user.username)
  if (user?.email && !identities.includes(user.email)) identities.push(user.email)
  return identities
})

watch(activeTab, (newTab) => {
  if (newTab === 'refunds') {
    loadRefunds()
  } else if (newTab === 'logs') {
    loadRefundLogs()
  } else if (newTab === 'receipts') {
    loadRefundReceipts()
  }
})

onMounted(async () => {
  try {
    await Promise.all([
      loadWebsites(),
      loadDashboard(),
      loadRefunds()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing RefundManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid rgb(229 231 235);
}

.dark .card {
  background-color: rgb(31 41 55);
  border-color: rgb(55 65 81);
}
</style>

