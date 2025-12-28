<template>
  <div class="class-bundle-purchase">
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="bundle" class="space-y-6">
      <!-- Bundle Header -->
      <div class="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white">
        <h2 class="text-2xl font-bold mb-2">{{ bundle.name }}</h2>
        <p v-if="bundle.description" class="text-primary-100">{{ bundle.description }}</p>
      </div>

      <!-- Bundle Details -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="card p-6">
          <h3 class="text-lg font-semibold mb-4">Bundle Information</h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Number of Classes:</span>
              <span class="font-medium">{{ bundle.number_of_classes || 'N/A' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Total Price:</span>
              <span class="font-bold text-lg">${{ formatCurrency(bundle.total_price) }}</span>
            </div>
            <div v-if="bundle.deposit_amount" class="flex justify-between">
              <span class="text-gray-600">Deposit Required:</span>
              <span class="font-medium">${{ formatCurrency(bundle.deposit_amount) }}</span>
            </div>
            <div v-if="bundle.installment_available" class="flex justify-between">
              <span class="text-gray-600">Installments:</span>
              <span class="font-medium text-green-600">Available</span>
            </div>
          </div>
        </div>

        <div class="card p-6">
          <h3 class="text-lg font-semibold mb-4">Payment Summary</h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Subtotal:</span>
              <span class="font-medium">${{ formatCurrency(bundle.total_price) }}</span>
            </div>
            <div v-if="discountAmount > 0" class="flex justify-between text-green-600">
              <span>Discount:</span>
              <span>- ${{ formatCurrency(discountAmount) }}</span>
            </div>
            <div class="flex justify-between pt-2 border-t border-gray-300">
              <span class="font-semibold">Total:</span>
              <span class="font-bold text-lg">${{ formatCurrency(finalTotal) }}</span>
            </div>
            <div v-if="bundle.deposit_amount" class="flex justify-between pt-2 border-t border-gray-300">
              <span class="font-semibold">Deposit:</span>
              <span class="font-bold text-lg">${{ formatCurrency(bundle.deposit_amount) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Discount Code -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold mb-4">Discount Code (Optional)</h3>
        <DiscountCodeInput
          v-model="discountCode"
          :order-total="bundle.total_price"
          @applied="handleDiscountApplied"
          @removed="handleDiscountRemoved"
        />
      </div>

      <!-- Installment Options -->
      <div v-if="bundle.installment_available" class="card p-6">
        <h3 class="text-lg font-semibold mb-4">Payment Options</h3>
        <div class="space-y-3">
          <label class="flex items-center">
            <input
              v-model="paymentOption"
              type="radio"
              value="full"
              class="mr-2"
            />
            <span>Pay in Full (${{ formatCurrency(finalTotal) }})</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="paymentOption"
              type="radio"
              value="deposit"
              class="mr-2"
            />
            <span>Pay Deposit Only (${{ formatCurrency(bundle.deposit_amount || 0) }})</span>
          </label>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-3">
        <button
          @click="proceedToPayment"
          :disabled="processing"
          class="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ processing ? 'Processing...' : `Proceed to Payment - $${formatCurrency(paymentAmount)}` }}
        </button>
        <button
          v-if="showCancel"
          @click="$emit('cancel')"
          class="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>

    <div v-else class="text-center py-12 text-gray-500">
      <p>Bundle not found</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import classManagementAPI from '@/api/class-management'
import DiscountCodeInput from '@/components/common/DiscountCodeInput.vue'

const props = defineProps({
  bundleId: {
    type: [Number, String],
    required: true
  },
  showCancel: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['proceed-payment', 'cancel'])

const bundle = ref(null)
const loading = ref(true)
const error = ref('')
const processing = ref(false)
const discountCode = ref('')
const discountAmount = ref(0)
const appliedDiscount = ref(null)
const paymentOption = ref('full')

const finalTotal = computed(() => {
  if (!bundle.value) return 0
  return Math.max(0, bundle.value.total_price - discountAmount.value)
})

const paymentAmount = computed(() => {
  if (paymentOption.value === 'deposit' && bundle.value?.deposit_amount) {
    return bundle.value.deposit_amount
  }
  return finalTotal.value
})

const loadBundle = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await classManagementAPI.getBundle(props.bundleId)
    bundle.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 
                  err.response?.data?.message || 
                  'Failed to load bundle details'
  } finally {
    loading.value = false
  }
}

const handleDiscountApplied = (discount, amount) => {
  appliedDiscount.value = discount
  discountAmount.value = amount
  discountCode.value = discount.code
}

const handleDiscountRemoved = () => {
  appliedDiscount.value = null
  discountAmount.value = 0
  discountCode.value = ''
}

const proceedToPayment = () => {
  emit('proceed-payment', {
    bundle: bundle.value,
    paymentAmount: paymentAmount.value,
    paymentOption: paymentOption.value,
    discount: appliedDiscount.value,
    discountAmount: discountAmount.value
  })
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

onMounted(() => {
  loadBundle()
})
</script>

<style scoped>
.class-bundle-purchase {
  width: 100%;
}
</style>

