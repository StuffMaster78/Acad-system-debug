<template>
  <div class="installment-payment">
    <div class="space-y-6">
      <!-- Installment Summary -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 class="font-semibold text-gray-900 mb-3">Installment Details</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Installment Amount:</span>
            <span class="font-medium">${{ formatCurrency(installment.amount) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Due Date:</span>
            <span class="font-medium">{{ formatDate(installment.due_date) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Installment #:</span>
            <span class="font-medium">{{ installment.installment_number }}/{{ installment.total_installments }}</span>
          </div>
          <div v-if="installment.is_overdue" class="flex justify-between text-red-600">
            <span class="font-medium">Status:</span>
            <span class="font-bold">Overdue</span>
          </div>
        </div>
      </div>

      <!-- Payment Method Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Payment Method
        </label>
        <select
          v-model="selectedPaymentMethod"
          class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          :disabled="processing"
        >
          <option value="">Select payment method...</option>
          <option value="wallet">Wallet Balance</option>
          <option value="stripe">Credit/Debit Card (Stripe)</option>
          <option value="paypal">PayPal</option>
          <option value="bank_transfer">Bank Transfer</option>
        </select>
      </div>

      <!-- Wallet Payment -->
      <div v-if="selectedPaymentMethod === 'wallet'" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-blue-900">Wallet Balance:</span>
          <span class="text-lg font-bold text-blue-900">${{ formatCurrency(walletBalance) }}</span>
        </div>
        <div v-if="walletBalance < installment.amount" class="text-sm text-red-600 mt-2">
          ⚠️ Insufficient balance. You need ${{ formatCurrency(installment.amount - walletBalance) }} more.
        </div>
        <div v-else class="text-sm text-green-600 mt-2">
          ✓ Sufficient balance available
        </div>
      </div>

      <!-- Card Payment Form -->
      <div v-if="selectedPaymentMethod === 'stripe'" class="space-y-4">
        <div class="border rounded-lg p-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Card Number
            </label>
            <input
              v-model="cardForm.number"
              type="text"
              placeholder="1234 5678 9012 3456"
              maxlength="19"
              class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              :disabled="processing"
              @input="formatCardNumber"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Expiry Date
              </label>
              <input
                v-model="cardForm.expiry"
                type="text"
                placeholder="MM/YY"
                maxlength="5"
                class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                :disabled="processing"
                @input="formatExpiry"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                CVV
              </label>
              <input
                v-model="cardForm.cvv"
                type="text"
                placeholder="123"
                maxlength="4"
                class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                :disabled="processing"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Cardholder Name
            </label>
            <input
              v-model="cardForm.name"
              type="text"
              placeholder="John Doe"
              class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              :disabled="processing"
            />
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-3">
        <button
          v-if="showCancel"
          @click="$emit('cancel')"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          :disabled="processing"
        >
          Cancel
        </button>
        <button
          @click="processPayment"
          :disabled="!canProcess || processing"
          class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="processing">
            <span class="inline-block animate-spin mr-2">⏳</span>
            Processing...
          </span>
          <span v-else>
            Pay ${{ formatCurrency(installment.amount) }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import classManagementAPI from '@/api/class-management'
import walletAPI from '@/api/wallet'

const props = defineProps({
  installment: {
    type: Object,
    required: true
  },
  walletBalance: {
    type: Number,
    default: 0
  },
  showCancel: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['success', 'error', 'cancel'])

const selectedPaymentMethod = ref('')
const processing = ref(false)
const error = ref('')

const cardForm = ref({
  number: '',
  expiry: '',
  cvv: '',
  name: ''
})

const canProcess = computed(() => {
  if (!selectedPaymentMethod.value) return false
  if (selectedPaymentMethod.value === 'wallet') {
    return props.walletBalance >= props.installment.amount
  }
  if (selectedPaymentMethod.value === 'stripe') {
    return cardForm.value.number && cardForm.value.expiry && cardForm.value.cvv && cardForm.value.name
  }
  return true
})

const formatCardNumber = (event) => {
  let value = event.target.value.replace(/\s/g, '')
  value = value.replace(/\D/g, '')
  value = value.match(/.{1,4}/g)?.join(' ') || value
  cardForm.value.number = value
}

const formatExpiry = (event) => {
  let value = event.target.value.replace(/\D/g, '')
  if (value.length >= 2) {
    value = value.substring(0, 2) + '/' + value.substring(2, 4)
  }
  cardForm.value.expiry = value
}

const processPayment = async () => {
  if (!canProcess.value) return
  
  processing.value = true
  error.value = ''
  
  try {
    let paymentData = {
      amount: props.installment.amount,
      payment_method: selectedPaymentMethod.value
    }
    
    // Handle wallet payment
    if (selectedPaymentMethod.value === 'wallet') {
      // Use wallet API to pay
      const response = await walletAPI.topUp(0, `Installment payment for installment #${props.installment.installment_number}`)
      // Then mark installment as paid
      await classManagementAPI.payInstallment(props.installment.id)
      emit('success', response.data)
      return
    }
    
    // Handle card payment
    if (selectedPaymentMethod.value === 'stripe') {
      paymentData.card = {
        number: cardForm.value.number.replace(/\s/g, ''),
        expiry: cardForm.value.expiry,
        cvv: cardForm.value.cvv,
        name: cardForm.value.name
      }
    }
    
    // Pay installment
    await classManagementAPI.payInstallment(props.installment.id, paymentData)
    
    emit('success', { message: 'Installment paid successfully' })
  } catch (err) {
    error.value = err.response?.data?.message || 
                  err.response?.data?.detail || 
                  'Payment processing failed. Please try again.'
    emit('error', err)
  } finally {
    processing.value = false
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.installment-payment {
  width: 100%;
}
</style>

