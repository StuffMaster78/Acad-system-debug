<template>
  <div class="payment-checkout">
    <div class="space-y-6">
      <!-- Order Summary -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 class="font-semibold text-gray-900 mb-3">Order Summary</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Subtotal:</span>
            <span class="font-medium">${{ formatCurrency(orderTotal) }}</span>
          </div>
          <div v-if="discountAmount > 0" class="flex justify-between text-green-600">
            <span>Discount:</span>
            <span>- ${{ formatCurrency(discountAmount) }}</span>
          </div>
          <div class="flex justify-between pt-2 border-t border-gray-300">
            <span class="font-semibold text-gray-900">Total:</span>
            <span class="font-bold text-lg">${{ formatCurrency(finalTotal) }}</span>
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
      <div v-if="selectedPaymentMethod === 'wallet'" class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-blue-900">Wallet Balance:</span>
            <span class="text-lg font-bold text-blue-900">${{ formatCurrency(walletBalance) }}</span>
          </div>
          <div v-if="walletBalance < finalTotal" class="text-sm text-red-600 mt-2">
            ⚠️ Insufficient balance. You need ${{ formatCurrency(finalTotal - walletBalance) }} more.
          </div>
          <div v-else class="text-sm text-green-600 mt-2">
            ✓ Sufficient balance available
          </div>
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
        <p class="text-xs text-gray-500">
          🔒 Your payment information is secure and encrypted
        </p>
      </div>

      <!-- PayPal Payment -->
      <div v-if="selectedPaymentMethod === 'paypal'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p class="text-sm text-gray-700">
          You will be redirected to PayPal to complete your payment.
        </p>
      </div>

      <!-- Bank Transfer -->
      <div v-if="selectedPaymentMethod === 'bank_transfer'" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p class="text-sm text-gray-700 mb-2">
          Please transfer the amount to the following account:
        </p>
        <div class="text-sm space-y-1 font-mono">
          <div><strong>Account Name:</strong> Writing System Inc.</div>
          <div><strong>Account Number:</strong> 1234567890</div>
          <div><strong>Routing Number:</strong> 987654321</div>
          <div><strong>Bank:</strong> Example Bank</div>
        </div>
        <p class="text-xs text-gray-500 mt-3">
          Please include your order ID (#{{ orderId }}) in the transfer reference.
        </p>
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
            Pay ${{ formatCurrency(finalTotal) }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import paymentsAPI from '@/api/payments'
import ordersAPI from '@/api/orders'

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  orderTotal: {
    type: Number,
    required: true
  },
  discountAmount: {
    type: Number,
    default: 0
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

const finalTotal = computed(() => {
  return Math.max(0, props.orderTotal - props.discountAmount)
})

const canProcess = computed(() => {
  if (!selectedPaymentMethod.value) return false
  if (selectedPaymentMethod.value === 'wallet') {
    return props.walletBalance >= finalTotal.value
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
      amount: finalTotal.value,
      payment_method: selectedPaymentMethod.value
    }
    
    // Handle wallet payment
    if (selectedPaymentMethod.value === 'wallet') {
      const response = await ordersAPI.payWithWallet(props.orderId)
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
    
    // Initiate payment
    const response = await paymentsAPI.initiate(props.orderId, paymentData)
    
    // Handle redirects (PayPal, etc.)
    if (response.data.redirect_url) {
      window.location.href = response.data.redirect_url
      return
    }
    
    // Confirm payment if needed
    if (response.data.payment_id && selectedPaymentMethod.value === 'stripe') {
      await paymentsAPI.confirm(response.data.payment_id)
    }
    
    emit('success', response.data)
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
  }).format(amount)
}
</script>

<style scoped>
.payment-checkout {
  width: 100%;
}
</style>

