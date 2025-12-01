<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Refund Management</h1>
        <p class="mt-2 text-gray-600">Manage refund requests, approvals, and processing</p>
      </div>
      <button @click="createNewRefund" class="btn btn-primary">+ Create Refund</button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending Refunds</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Processed</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.processed || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Rejected</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.rejected || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Amount</p>
        <p class="text-3xl font-bold text-blue-900">${{ stats.total_amount.toFixed(2) }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="filters.status" @change="loadRefunds" class="w-full border rounded px-3 py-2">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processed">Processed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Refund Method</label>
            <select v-model="filters.refund_method" @change="loadRefunds" class="w-full border rounded px-3 py-2">
              <option value="">All Methods</option>
              <option value="wallet">Wallet</option>
              <option value="external">External</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Website</label>
            <select v-model="filters.website" @change="loadRefunds" class="w-full border rounded px-3 py-2">
              <option value="">All Websites</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Client, order ID..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Refunds Table -->
      <div class="card overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order Payment</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Processed</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="refund in refunds" :key="refund.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  #{{ refund.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ refund.client?.username || refund.client?.email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Payment #{{ typeof refund.order_payment === 'object' ? refund.order_payment?.id : refund.order_payment || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                  ${{ parseFloat(refund.total_amount || (parseFloat(refund.wallet_amount || 0) + parseFloat(refund.external_amount || 0))).toFixed(2) }}
                  <span v-if="refund.wallet_amount > 0 && refund.external_amount > 0" class="text-xs text-gray-500 block">
                    (${{ parseFloat(refund.wallet_amount || 0).toFixed(2) }} wallet + ${{ parseFloat(refund.external_amount || 0).toFixed(2) }} external)
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span class="capitalize">{{ refund.refund_method || 'wallet' }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusClass(refund.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ refund.status || 'pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div v-if="refund.processed_at">
                    <div>{{ formatDate(refund.processed_at) }}</div>
                    <div class="text-xs text-gray-400" v-if="refund.processed_by">
                      by {{ typeof refund.processed_by === 'object' ? refund.processed_by?.username : 'Admin' }}
                    </div>
                  </div>
                  <span v-else class="text-gray-400">Not processed</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="viewRefund(refund)" class="text-blue-600 hover:underline mr-2">View</button>
                  <button
                    v-if="refund.status === 'pending'"
                    @click="processRefund(refund)"
                    class="text-green-600 hover:underline mr-2"
                  >
                    Process
                  </button>
                  <button
                    v-if="refund.status === 'pending'"
                    @click="cancelRefund(refund)"
                    class="text-red-600 hover:underline mr-2"
                  >
                    Cancel
                  </button>
                  <button
                    v-if="refund.status === 'rejected'"
                    @click="retryRefund(refund)"
                    class="text-yellow-600 hover:underline"
                  >
                    Retry
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!refunds.length" class="text-center py-12 text-gray-500">
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
      <div class="bg-white rounded-lg max-w-3xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Refund Details</h3>
          <button @click="viewingRefund = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
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
                ${{ parseFloat(viewingRefund.total_amount || (parseFloat(viewingRefund.wallet_amount || 0) + parseFloat(viewingRefund.external_amount || 0))).toFixed(2) }}
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

    <!-- Create Refund Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Create Refund</h3>
          <button @click="closeCreateModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <form @submit.prevent="saveRefund" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Order Payment ID *</label>
            <input v-model.number="refundForm.order_payment" type="number" required class="w-full border rounded px-3 py-2" placeholder="Enter order payment ID" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Wallet Amount ($)</label>
              <input v-model.number="refundForm.wallet_amount" type="number" step="0.01" min="0" class="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">External Amount ($)</label>
              <input v-model.number="refundForm.external_amount" type="number" step="0.01" min="0" class="w-full border rounded px-3 py-2" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Refund Method *</label>
            <select v-model="refundForm.refund_method" required class="w-full border rounded px-3 py-2">
              <option value="wallet">Wallet</option>
              <option value="external">External</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Refund Type</label>
            <select v-model="refundForm.type" class="w-full border rounded px-3 py-2">
              <option value="manual">Manual</option>
              <option value="automated">Automated</option>
            </select>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeCreateModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Creating...' : 'Create Refund' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
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
      @confirm="handlePasswordConfirm"
      @cancel="handlePasswordCancel"
      ref="passwordModalRef"
    />
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { refundsAPI } from '@/api'
import adminRefundsAPI from '@/api/admin-refunds'
import apiClient from '@/api/client'
import PasswordVerificationModal from '@/components/common/PasswordVerificationModal.vue'

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
  if (!confirm('Are you sure you want to retry this refund?')) return
  
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

const viewReceipt = (receipt) => {
  // TODO: Implement receipt detail view
  showMessage('Receipt detail view coming soon', false)
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
  if (status === 'processed') return 'bg-green-100 text-green-800'
  if (status === 'rejected') return 'bg-red-100 text-red-800'
  return 'bg-yellow-100 text-yellow-800'
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

