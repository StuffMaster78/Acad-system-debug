<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Payment Requests</h1>
        <p class="mt-2 text-gray-600">Request manual payments outside of your scheduled payment dates</p>
      </div>
    </div>

    <!-- Wallet Balance Card -->
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm p-6 border border-blue-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-blue-700 mb-1">Available Balance</p>
          <p class="text-4xl font-bold text-blue-900">${{ formatCurrency(walletBalance) }}</p>
          <p class="text-sm text-blue-600 mt-2">
            Payment Schedule: <span class="font-medium">{{ paymentSchedule }}</span>
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm text-blue-600 mb-2">Next Scheduled Payment</p>
          <p class="text-lg font-semibold text-blue-900">{{ nextPaymentDate || 'Not scheduled' }}</p>
        </div>
      </div>
    </div>

    <!-- Request Payment Form -->
    <div v-if="manualRequestsEnabled" class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <h2 class="text-xl font-semibold mb-4">Request Payment</h2>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Requested Amount <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
            <input
              v-model="requestForm.amount"
              type="number"
              step="0.01"
              min="0.01"
              :max="walletBalance"
              class="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="0.00"
            />
          </div>
          <p class="text-xs text-gray-500 mt-1">
            Maximum: ${{ formatCurrency(walletBalance) }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason (Optional)
          </label>
          <textarea
            v-model="requestForm.reason"
            rows="3"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Enter reason for this payment request (optional)..."
          ></textarea>
        </div>

        <div class="flex items-center gap-4">
          <button
            @click="submitPaymentRequest"
            :disabled="!canSubmitRequest || submitting"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {{ submitting ? 'Submitting...' : 'Submit Request' }}
          </button>
          <button
            @click="requestForm = { amount: '', reason: '' }"
            class="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>
    </div>

    <!-- Manual Requests Disabled Message -->
    <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <div class="flex items-start">
        <div class="shrink-0">
          <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">Manual Payment Requests Disabled</h3>
          <p class="mt-2 text-sm text-yellow-700">
            Manual payment requests are not enabled for your account. You will receive payments automatically according to your payment schedule ({{ paymentSchedule }}).
          </p>
        </div>
      </div>
    </div>

    <!-- Payment Requests History -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold">Payment Request History</h2>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="paymentRequests.length === 0" class="p-12 text-center">
        <p class="text-gray-500">No payment requests yet</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Request ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Available Balance</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in paymentRequests" :key="request.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-mono">#{{ request.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">${{ formatCurrency(request.requested_amount) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${{ formatCurrency(request.available_balance) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(request.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ request.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ formatDate(request.created_at) }}</td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ request.reason || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button
                  v-if="request.status === 'pending'"
                  @click="cancelRequest(request.id)"
                  class="text-red-600 hover:underline"
                >
                  Cancel
                </button>
                <span v-else-if="request.status === 'approved'" class="text-green-600">Approved</span>
                <span v-else-if="request.status === 'rejected'" class="text-red-600">Rejected</span>
                <span v-else class="text-gray-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import paymentsAPI from '@/api/payments'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const submitting = ref(false)
const walletBalance = ref(0)
const paymentSchedule = ref('Not set')
const nextPaymentDate = ref(null)
const manualRequestsEnabled = ref(false)
const paymentRequests = ref([])

const requestForm = ref({
  amount: '',
  reason: ''
})

const canSubmitRequest = computed(() => {
  const amount = parseFloat(requestForm.value.amount)
  return amount > 0 && amount <= walletBalance.value && !submitting.value
})

const loadWalletInfo = async () => {
  try {
    const response = await apiClient.get('/writer-wallet/writer-wallets/')
    if (response.data && response.data.length > 0) {
      const wallet = response.data[0]
      walletBalance.value = parseFloat(wallet.balance || 0)
    }
  } catch (error) {
    console.error('Failed to load wallet info:', error)
  }
}

const loadWriterProfile = async () => {
  try {
    const response = await apiClient.get('/writer-management/writer-profiles/')
    if (response.data && response.data.length > 0) {
      const profile = response.data[0]
      paymentSchedule.value = profile.payment_schedule === 'bi-weekly' ? 'Bi-Weekly' : 
                              profile.payment_schedule === 'monthly' ? 'Monthly' : 'Not set'
      manualRequestsEnabled.value = profile.manual_payment_requests_enabled || false
    }
  } catch (error) {
    console.error('Failed to load writer profile:', error)
  }
}

const loadPaymentRequests = async () => {
  loading.value = true
  try {
    const response = await paymentsAPI.listPaymentRequests({})
    paymentRequests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load payment requests:', error)
    showError('Failed to load payment requests')
  } finally {
    loading.value = false
  }
}

const submitPaymentRequest = async () => {
  if (!canSubmitRequest.value) return

  submitting.value = true
  try {
    await paymentsAPI.requestPayment({
      amount: parseFloat(requestForm.value.amount),
      reason: requestForm.value.reason || ''
    })
    
    showSuccess('Payment request submitted successfully!')
    requestForm.value = { amount: '', reason: '' }
    await loadPaymentRequests()
    await loadWalletInfo()
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.message || 'Failed to submit payment request'
    showError(errorMsg)
  } finally {
    submitting.value = false
  }
}

const cancelRequest = async (requestId) => {
  const confirmed = await confirm.showDialog(
    'Are you sure you want to cancel this payment request?',
    'Cancel Payment Request',
    {
      variant: 'warning',
      icon: '⚠️',
      confirmText: 'Cancel Request',
      cancelText: 'Keep Request'
    }
  )
  
  if (!confirmed) {
    return
  }

  try {
    // Note: You may need to add a cancel endpoint
    await apiClient.delete(`/writer-wallet/payment-requests/${requestId}/`)
    showSuccess('Payment request cancelled')
    await loadPaymentRequests()
  } catch (error) {
    showError('Failed to cancel payment request')
  }
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getStatusClass = (status) => {
  const statusMap = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'approved': 'bg-green-100 text-green-800',
    'rejected': 'bg-red-100 text-red-800',
    'processed': 'bg-blue-100 text-blue-800',
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

onMounted(async () => {
  await Promise.all([
    loadWalletInfo(),
    loadWriterProfile(),
    loadPaymentRequests()
  ])
})
</script>

