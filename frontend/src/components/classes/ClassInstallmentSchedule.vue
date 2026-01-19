<template>
  <div class="class-installment-schedule">
    <!-- Progress Summary -->
    <div class="mb-6">
      <div class="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1">Payment Progress</h3>
            <p class="text-sm text-gray-600">Track your installment payments</p>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold text-primary-600">${{ formatCurrency(totalPaid) }}</p>
            <p class="text-sm text-gray-600">of ${{ formatCurrency(totalAmount) }}</p>
          </div>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
          <div
            class="bg-primary-600 h-3 rounded-full transition-all duration-300"
            :style="{ width: `${paymentProgress}%` }"
          ></div>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600">{{ paymentProgress.toFixed(1) }}% Complete</span>
          <span class="font-medium text-gray-900">${{ formatCurrency(remainingBalance) }} Remaining</span>
        </div>
      </div>
    </div>

    <!-- Installment Timeline -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Installment Schedule</h3>
      
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="installments.length === 0" class="text-center py-12 text-gray-500">
        <p>No installments found</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="(installment, index) in sortedInstallments"
          :key="installment.id"
          class="relative"
        >
          <!-- Timeline Connector -->
          <div
            v-if="index < sortedInstallments.length - 1"
            class="absolute left-6 top-16 bottom-0 w-0.5 bg-gray-300"
          ></div>

          <!-- Installment Card -->
          <div
            :class="[
              'relative bg-white border-2 rounded-lg p-6 shadow-sm transition-all hover:shadow-md',
              getInstallmentCardClass(installment)
            ]"
          >
            <div class="flex items-start gap-4">
              <!-- Status Icon -->
              <div
                :class="[
                  'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
                  getStatusIconClass(installment)
                ]"
              >
                <svg
                  v-if="installment.is_paid"
                  class="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <svg
                  v-else-if="installment.is_overdue"
                  class="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <span v-else class="text-white font-bold text-lg">{{ installment.installment_number }}</span>
              </div>

              <!-- Installment Details -->
              <div class="flex-1">
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <h4 class="text-lg font-semibold text-gray-900">
                      Installment #{{ installment.installment_number }}
                    </h4>
                    <p v-if="installment.due_date" class="text-sm text-gray-600 mt-1">
                      Due: {{ formatDate(installment.due_date) }}
                    </p>
                    <p v-else class="text-sm text-gray-500 italic">No due date set</p>
                  </div>
                  <div class="text-right">
                    <p class="text-2xl font-bold text-gray-900">
                      ${{ formatCurrency(installment.amount) }}
                    </p>
                    <span
                      :class="[
                        'inline-block px-3 py-1 rounded-full text-xs font-medium mt-2',
                        getStatusBadgeClass(installment)
                      ]"
                    >
                      {{ getStatusLabel(installment) }}
                    </span>
                  </div>
                </div>

                <!-- Payment Info (if paid) -->
                <div v-if="installment.is_paid && installment.paid_at" class="mt-3 pt-3 border-t border-gray-200">
                  <div class="flex items-center gap-2 text-sm text-gray-600">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span>Paid on {{ formatDateTime(installment.paid_at) }}</span>
                    <span v-if="installment.paid_by" class="text-gray-500">
                      • by {{ installment.paid_by?.username || 'N/A' }}
                    </span>
                  </div>
                </div>

                <!-- Overdue Warning -->
                <div v-if="installment.is_overdue && !installment.is_paid" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div class="flex items-center gap-2 text-sm text-red-700">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                    <span class="font-medium">This installment is overdue. Please pay immediately.</span>
                  </div>
                </div>

                <!-- Action Button -->
                <div v-if="!installment.is_paid" class="mt-4">
                  <button
                    @click="payInstallment(installment)"
                    :disabled="processingPayment === installment.id"
                    :class="[
                      'px-6 py-2 rounded-lg font-medium transition-colors',
                      installment.is_overdue
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-primary-600 text-white hover:bg-primary-700',
                      processingPayment === installment.id ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    <span v-if="processingPayment === installment.id" class="flex items-center gap-2">
                      <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                    <span v-else class="flex items-center gap-2">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                        />
                      </svg>
                      {{ installment.is_overdue ? 'Pay Now (Overdue)' : 'Pay Now' }}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div
      v-if="showPaymentModal && selectedInstallment"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closePaymentModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-gray-900">Pay Installment</h3>
            <button @click="closePaymentModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-600 mb-1">Installment #{{ selectedInstallment.installment_number }}</p>
              <p class="text-2xl font-bold text-gray-900">${{ formatCurrency(selectedInstallment.amount) }}</p>
              <p v-if="selectedInstallment.due_date" class="text-sm text-gray-500 mt-1">
                Due: {{ formatDate(selectedInstallment.due_date) }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
              <select
                v-model="paymentMethod"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="wallet">Wallet Balance</option>
                <option value="stripe">Credit/Debit Card (Stripe)</option>
                <option value="paypal">PayPal</option>
                <option value="bank_transfer">Bank Transfer</option>
              </select>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                @click="closePaymentModal"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                @click="confirmPayment"
                :disabled="processingPayment === selectedInstallment.id"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ processingPayment === selectedInstallment.id ? 'Processing...' : 'Confirm Payment' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import classManagementAPI from '@/api/class-management'

const props = defineProps({
  bundleId: {
    type: [Number, String],
    required: true
  }
})

const { showToast } = useToast()

const installments = ref([])
const loading = ref(true)
const processingPayment = ref(null)
const showPaymentModal = ref(false)
const selectedInstallment = ref(null)
const paymentMethod = ref('wallet')

const sortedInstallments = computed(() => {
  return [...installments.value].sort((a, b) => {
    // Sort by installment number, then by due date
    if (a.installment_number !== b.installment_number) {
      return (a.installment_number || 0) - (b.installment_number || 0)
    }
    if (a.due_date && b.due_date) {
      return new Date(a.due_date) - new Date(b.due_date)
    }
    return 0
  })
})

const totalAmount = computed(() => {
  return installments.value.reduce((sum, inst) => sum + parseFloat(inst.amount || 0), 0)
})

const totalPaid = computed(() => {
  return installments.value
    .filter(inst => inst.is_paid)
    .reduce((sum, inst) => sum + parseFloat(inst.amount || 0), 0)
})

const remainingBalance = computed(() => {
  return totalAmount.value - totalPaid.value
})

const paymentProgress = computed(() => {
  if (totalAmount.value === 0) return 0
  return (totalPaid.value / totalAmount.value) * 100
})

const loadInstallments = async () => {
  loading.value = true
  try {
    const response = await classManagementAPI.listInstallments({ class_bundle: props.bundleId })
    installments.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (error) {
    showToast('Failed to load installments: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error loading installments:', error)
  } finally {
    loading.value = false
  }
}

const payInstallment = (installment) => {
  selectedInstallment.value = installment
  paymentMethod.value = 'wallet'
  showPaymentModal.value = true
}

const closePaymentModal = () => {
  showPaymentModal.value = false
  selectedInstallment.value = null
}

const confirmPayment = async () => {
  if (!selectedInstallment.value) return

  processingPayment.value = selectedInstallment.value.id
  try {
    const response = await classManagementAPI.payInstallment(selectedInstallment.value.id, {
      payment_method: paymentMethod.value
    })
    
    showToast('Installment paid successfully!', 'success')
    closePaymentModal()
    await loadInstallments()
    
    // Emit event for parent component
    emit('installment-paid', response.data)
  } catch (error) {
    showToast('Failed to process payment: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error paying installment:', error)
  } finally {
    processingPayment.value = null
  }
}

const getStatusLabel = (installment) => {
  if (installment.is_paid) return 'Paid'
  if (installment.is_overdue) return 'Overdue'
  return 'Upcoming'
}

const getStatusBadgeClass = (installment) => {
  if (installment.is_paid) {
    return 'bg-green-100 text-green-800'
  }
  if (installment.is_overdue) {
    return 'bg-red-100 text-red-800'
  }
  return 'bg-yellow-100 text-yellow-800'
}

const getStatusIconClass = (installment) => {
  if (installment.is_paid) {
    return 'bg-green-500'
  }
  if (installment.is_overdue) {
    return 'bg-red-500'
  }
  return 'bg-primary-500'
}

const getInstallmentCardClass = (installment) => {
  if (installment.is_paid) {
    return 'border-green-200 bg-green-50'
  }
  if (installment.is_overdue) {
    return 'border-red-300 bg-red-50'
  }
  return 'border-gray-200'
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const emit = defineEmits(['installment-paid'])

onMounted(() => {
  loadInstallments()
})
</script>

<style scoped>
.class-installment-schedule {
  width: 100%;
}
</style>
