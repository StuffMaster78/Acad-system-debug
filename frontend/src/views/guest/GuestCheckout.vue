<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Place Your Order</h1>
        <p class="text-gray-600">Complete your order as a guest - no account required</p>
      </div>

      <!-- Progress Steps -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center font-semibold',
              currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            ]">
              1
            </div>
            <span class="ml-3 font-medium text-gray-900">Order Details</span>
          </div>
          <div class="flex-1 h-1 mx-4" :class="currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-200'"></div>
          <div class="flex items-center">
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center font-semibold',
              currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            ]">
              2
            </div>
            <span class="ml-3 font-medium text-gray-900">Email Verification</span>
          </div>
          <div class="flex-1 h-1 mx-4" :class="currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-200'"></div>
          <div class="flex items-center">
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center font-semibold',
              currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            ]">
              3
            </div>
            <span class="ml-3 font-medium text-gray-900">Complete</span>
          </div>
        </div>
      </div>

      <!-- Step 1: Order Form -->
      <div v-if="currentStep === 1" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Order Information</h2>
        
        <form @submit.prevent="handleStartOrder" class="space-y-6">
          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email Address <span class="text-red-500">*</span>
            </label>
            <input
              v-model="orderForm.email"
              type="email"
              required
              placeholder="your@email.com"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">We'll send order updates to this email</p>
          </div>

          <!-- Topic -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Topic/Title <span class="text-red-500">*</span>
            </label>
            <input
              v-model="orderForm.topic"
              type="text"
              required
              placeholder="Enter your order topic"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Paper Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Paper Type <span class="text-red-500">*</span>
            </label>
            <select
              v-model="orderForm.paper_type_id"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select paper type...</option>
              <option v-for="type in paperTypes" :key="type.id" :value="type.id">
                {{ type.name }}
              </option>
            </select>
          </div>

          <!-- Number of Pages -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Number of Pages <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="orderForm.number_of_pages"
              type="number"
              min="1"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Deadline -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Deadline <span class="text-red-500">*</span>
            </label>
            <input
              v-model="orderForm.client_deadline"
              type="datetime-local"
              required
              :min="minDeadline"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Instructions -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Order Instructions <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="orderForm.order_instructions"
              rows="4"
              required
              placeholder="Provide detailed instructions for your order..."
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-700 text-sm">{{ error }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Processing...</span>
            <span v-else>Continue to Email Verification</span>
          </button>
        </form>
      </div>

      <!-- Step 2: Email Verification -->
      <div v-if="currentStep === 2" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
        <div class="mb-6">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">Check Your Email</h2>
          <p class="text-gray-600 mb-4">
            We've sent a verification link to <strong>{{ orderForm.email }}</strong>
          </p>
          <p class="text-sm text-gray-500">
            Click the link in the email to verify your address and complete your order.
          </p>
        </div>

        <!-- Manual Verification -->
        <div class="border-t border-gray-200 pt-6 mt-6">
          <p class="text-sm text-gray-600 mb-4">Already verified? Enter your verification code:</p>
          <div class="flex gap-2 max-w-md mx-auto">
            <input
              v-model="verificationToken"
              type="text"
              placeholder="Verification token"
              class="flex-1 border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              @click="handleVerifyEmail"
              :disabled="!verificationToken || loading"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              Verify
            </button>
          </div>
        </div>

        <!-- Resend Email -->
        <button
          @click="resendVerification"
          :disabled="resendCooldown > 0"
          class="mt-4 text-sm text-blue-600 hover:text-blue-700 disabled:text-gray-400"
        >
          <span v-if="resendCooldown > 0">Resend in {{ resendCooldown }}s</span>
          <span v-else>Resend verification email</span>
        </button>
      </div>

      <!-- Step 3: Success -->
      <div v-if="currentStep === 3" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
        <div class="mb-6">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">Order Created Successfully!</h2>
          <p class="text-gray-600 mb-4">
            Your order #{{ createdOrderId }} has been created.
          </p>
          <p class="text-sm text-gray-500">
            You'll receive order updates at <strong>{{ orderForm.email }}</strong>
          </p>
        </div>

        <div class="flex gap-4 justify-center">
          <button
            @click="$router.push(`/orders/${createdOrderId}`)"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
          >
            View Order
          </button>
          <button
            @click="resetForm"
            class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300"
          >
            Place Another Order
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ordersAPI from '@/api/orders'
import orderConfigsAPI from '@/api/orderConfigs'

const route = useRoute()
const currentStep = ref(1)
const loading = ref(false)
const error = ref('')
const verificationToken = ref('')
const resendCooldown = ref(0)
const createdOrderId = ref(null)
const paperTypes = ref([])
const websiteId = ref(null)

const orderForm = ref({
  email: '',
  topic: '',
  paper_type_id: null,
  number_of_pages: 1,
  client_deadline: '',
  order_instructions: ''
})

const minDeadline = computed(() => {
  const now = new Date()
  now.setHours(now.getHours() + 12) // Minimum 12 hours from now
  return now.toISOString().slice(0, 16)
})

const loadPaperTypes = async () => {
  try {
    const response = await orderConfigsAPI.getPaperTypes({ website_id: websiteId.value })
    paperTypes.value = response.data?.results || response.data || []
  } catch (e) {
    console.error('Failed to load paper types:', e)
  }
}

const handleStartOrder = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await ordersAPI.startGuestOrder({
      website_id: websiteId.value,
      email: orderForm.value.email,
      order_data: {
        topic: orderForm.value.topic,
        paper_type_id: orderForm.value.paper_type_id,
        number_of_pages: orderForm.value.number_of_pages,
        client_deadline: new Date(orderForm.value.client_deadline).toISOString(),
        order_instructions: orderForm.value.order_instructions
      }
    })

    if (response.data.verification_required) {
      // Store order data for verification step
      verificationToken.value = response.data.verification_token || ''
      currentStep.value = 2
      startResendCooldown()
    } else {
      // Order created immediately
      createdOrderId.value = response.data.order_id
      currentStep.value = 3
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to start order. Please try again.'
    console.error('Failed to start guest order:', e)
  } finally {
    loading.value = false
  }
}

const handleVerifyEmail = async () => {
  if (!verificationToken.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await ordersAPI.verifyGuestEmail({
      verification_token: verificationToken.value,
      website_id: websiteId.value,
      order_data: {
        topic: orderForm.value.topic,
        paper_type_id: orderForm.value.paper_type_id,
        number_of_pages: orderForm.value.number_of_pages,
        client_deadline: new Date(orderForm.value.client_deadline).toISOString(),
        order_instructions: orderForm.value.order_instructions
      }
    })

    createdOrderId.value = response.data.order_id
    currentStep.value = 3
  } catch (e) {
    error.value = e.response?.data?.detail || 'Invalid verification token. Please check your email.'
    console.error('Failed to verify email:', e)
  } finally {
    loading.value = false
  }
}

const resendVerification = async () => {
  if (resendCooldown.value > 0) return
  
  // Resend by starting order again
  await handleStartOrder()
  startResendCooldown()
}

const startResendCooldown = () => {
  resendCooldown.value = 60
  const interval = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(interval)
    }
  }, 1000)
}

const resetForm = () => {
  currentStep.value = 1
  orderForm.value = {
    email: '',
    topic: '',
    paper_type_id: null,
    number_of_pages: 1,
    client_deadline: '',
    order_instructions: ''
  }
  verificationToken.value = ''
  createdOrderId.value = null
  error.value = ''
}

onMounted(() => {
  // Get website ID from route query or use default
  websiteId.value = parseInt(route.query.website_id) || 1
  loadPaperTypes()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

