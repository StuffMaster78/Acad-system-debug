<template>
  <div class="discount-code-input">
    <div class="flex gap-2">
      <div class="flex-1">
        <input
          v-model="code"
          type="text"
          :placeholder="placeholder"
          class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          :class="{
            'border-red-300': error,
            'border-green-300': isValid && code,
            'border-gray-300': !error && !isValid
          }"
          :disabled="loading || disabled"
          @input="handleInput"
          @keyup.enter="applyDiscount"
        />
        <div v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</div>
        <div v-if="discountInfo && !error" class="mt-1 text-sm text-green-600">
          ✓ {{ discountInfo.description || `Discount: ${discountInfo.discount_percentage || discountInfo.discount_amount}%` }}
        </div>
      </div>
      <button
        @click="applyDiscount"
        :disabled="!code.trim() || loading || disabled"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="loading">...</span>
        <span v-else>{{ applied ? 'Remove' : 'Apply' }}</span>
      </button>
    </div>
    
    <!-- Applied Discount Info -->
    <div v-if="applied && discountInfo" class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-start justify-between">
        <div>
          <div class="font-medium text-green-900">{{ discountInfo.code }}</div>
          <div class="text-sm text-green-700">
            {{ discountInfo.description || 'Discount applied' }}
          </div>
          <div v-if="discountAmount" class="text-sm font-semibold text-green-900 mt-1">
            Savings: {{ formatCurrency(discountAmount) }}
          </div>
        </div>
        <button
          v-if="!disabled"
          @click="removeDiscount"
          class="text-green-700 hover:text-green-900"
        >
          ✕
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import discountsAPI from '@/api/discounts'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  orderId: {
    type: [Number, String],
    default: null
  },
  orderTotal: {
    type: Number,
    default: 0
  },
  placeholder: {
    type: String,
    default: 'Enter discount code'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'applied', 'removed', 'error'])

const code = ref(props.modelValue || '')
const loading = ref(false)
const error = ref('')
const isValid = ref(false)
const applied = ref(false)
const discountInfo = ref(null)
const discountAmount = ref(0)

watch(() => props.modelValue, (newVal) => {
  if (newVal !== code.value) {
    code.value = newVal || ''
  }
})

const handleInput = () => {
  error.value = ''
  isValid.value = false
  emit('update:modelValue', code.value)
}

const validateDiscount = async () => {
  if (!code.value.trim()) {
    error.value = ''
    isValid.value = false
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // Validate discount code
    const response = await discountsAPI.validate(code.value.trim(), {
      order_id: props.orderId,
      order_total: props.orderTotal
    })
    
    if (response.data.valid) {
      isValid.value = true
      discountInfo.value = response.data.discount
      calculateDiscountAmount(response.data.discount)
    } else {
      error.value = response.data.message || 'Invalid discount code'
      isValid.value = false
      discountInfo.value = null
    }
  } catch (err) {
    error.value = err.response?.data?.message || err.response?.data?.detail || 'Failed to validate discount code'
    isValid.value = false
    discountInfo.value = null
  } finally {
    loading.value = false
  }
}

const applyDiscount = async () => {
  if (applied.value) {
    removeDiscount()
    return
  }
  
  if (!code.value.trim()) {
    error.value = 'Please enter a discount code'
    return
  }
  
  // Validate first
  await validateDiscount()
  
  if (!isValid.value || !discountInfo.value) {
    return
  }
  
  // Apply discount if order ID is provided
  if (props.orderId) {
    loading.value = true
    try {
      const response = await discountsAPI.apply(props.orderId, code.value.trim())
      applied.value = true
      discountInfo.value = response.data.discount || discountInfo.value
      calculateDiscountAmount(discountInfo.value)
      emit('applied', discountInfo.value, discountAmount.value)
    } catch (err) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Failed to apply discount'
      emit('error', err)
    } finally {
      loading.value = false
    }
  } else {
    // Just emit the discount info for parent to handle
    applied.value = true
    emit('applied', discountInfo.value, discountAmount.value)
  }
}

const removeDiscount = () => {
  if (props.orderId) {
    // Remove discount from order via API
    discountsAPI.remove(props.orderId).catch(err => {
      console.error('Failed to remove discount:', err)
    })
  }
  
  applied.value = false
  discountInfo.value = null
  discountAmount.value = 0
  code.value = ''
  error.value = ''
  isValid.value = false
  emit('removed')
  emit('update:modelValue', '')
}

const calculateDiscountAmount = (discount) => {
  if (!discount || !props.orderTotal) {
    discountAmount.value = 0
    return
  }
  
  if (discount.discount_percentage) {
    discountAmount.value = (props.orderTotal * discount.discount_percentage) / 100
  } else if (discount.discount_amount) {
    discountAmount.value = discount.discount_amount
  } else {
    discountAmount.value = 0
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

// Debounced validation
let validationTimeout = null
watch(code, () => {
  if (validationTimeout) {
    clearTimeout(validationTimeout)
  }
  validationTimeout = setTimeout(() => {
    if (code.value.trim() && !applied.value) {
      validateDiscount()
    }
  }, 500)
})
</script>

<style scoped>
.discount-code-input {
  width: 100%;
}
</style>

