<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <div v-if="USE_MOCK" class="mb-4 inline-block px-4 py-2 bg-yellow-100 border-2 border-yellow-400 rounded-lg">
          <p class="text-yellow-800 font-semibold text-sm flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            🎭 MOCK MODE - Using simulated data for testing
          </p>
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Place Your Order</h1>
        <p class="text-gray-600 text-lg">Complete your order as a guest - no account required</p>
      </div>

      <!-- Progress Steps -->
      <div class="mb-8 bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center flex-1">
            <div :class="[
              'w-12 h-12 rounded-full flex items-center justify-center font-semibold text-sm transition-all',
              currentStep >= 1 ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-600'
            ]">
              <span v-if="currentStep > 1">✓</span>
              <span v-else>1</span>
            </div>
            <span class="ml-3 font-medium text-gray-900">Order Details</span>
          </div>
          <div class="flex-1 h-1 mx-4" :class="currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-200'"></div>
          <div class="flex items-center flex-1">
            <div :class="[
              'w-12 h-12 rounded-full flex items-center justify-center font-semibold text-sm transition-all',
              currentStep >= 2 ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-600'
            ]">
              <span v-if="currentStep > 2">✓</span>
              <span v-else>2</span>
            </div>
            <span class="ml-3 font-medium text-gray-900">Email Verification</span>
          </div>
          <div class="flex-1 h-1 mx-4" :class="currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-200'"></div>
          <div class="flex items-center flex-1">
            <div :class="[
              'w-12 h-12 rounded-full flex items-center justify-center font-semibold text-sm transition-all',
              currentStep >= 3 ? 'bg-green-600 text-white shadow-lg' : 'bg-gray-200 text-gray-600'
            ]">
              <span v-if="currentStep >= 3">✓</span>
              <span v-else>3</span>
            </div>
            <span class="ml-3 font-medium text-gray-900">Complete</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Form -->
        <div class="lg:col-span-2">
          <!-- Step 1: Order Form -->
          <div v-if="currentStep === 1" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Order Information
            </h2>
            
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
                  class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
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
                  class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
              </div>

              <!-- Grid: Paper Type & Pages -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Paper Type <span class="text-red-500">*</span>
                  </label>
                  <select
                    v-model="orderForm.paper_type_id"
                    required
                    @change="calculatePrice"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white"
                  >
                    <option value="">Select paper type...</option>
                    <option v-for="type in paperTypes" :key="type.id" :value="type.id">
                      {{ type.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Number of Pages <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model.number="orderForm.number_of_pages"
                    type="number"
                    min="1"
                    required
                    @input="calculatePrice"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                  />
                </div>
              </div>

              <!-- Grid: Academic Level & Formatting Style -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Academic Level
                  </label>
                  <select
                    v-model="orderForm.academic_level_id"
                    @change="calculatePrice"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white"
                  >
                    <option value="">Select level...</option>
                    <option v-for="level in academicLevels" :key="level.id" :value="level.id">
                      {{ level.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Formatting Style
                  </label>
                  <select
                    v-model="orderForm.formatting_style_id"
                    @change="calculatePrice"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white"
                  >
                    <option value="">Select style...</option>
                    <option v-for="style in formattingStyles" :key="style.id" :value="style.id">
                      {{ style.name }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Grid: Type of Work & Subject -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Type of Work
                  </label>
                  <select
                    v-model="orderForm.type_of_work_id"
                    @change="calculatePrice"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white"
                  >
                    <option value="">Select type...</option>
                    <option v-for="type in typesOfWork" :key="type.id" :value="type.id">
                      {{ type.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <select
                    v-model="orderForm.subject_id"
                    @change="calculatePrice"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-white"
                  >
                    <option value="">Select subject...</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                      {{ subject.name }}
                    </option>
                  </select>
                </div>
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
                  @change="calculatePrice"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Minimum 12 hours from now</p>
              </div>

              <!-- Instructions -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Order Instructions <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="orderForm.order_instructions"
                  rows="5"
                  required
                  placeholder="Provide detailed instructions for your order..."
                  class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
                ></textarea>
              </div>

              <!-- Discount Code -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Discount Code (Optional)
                </label>
                <div class="flex gap-2">
                  <input
                    v-model="discountCode"
                    type="text"
                    placeholder="Enter discount code"
                    class="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                  />
                  <button
                    type="button"
                    @click="applyDiscount"
                    :disabled="!discountCode || quoteLoading"
                    class="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Apply
                  </button>
                </div>
                <p v-if="appliedDiscount" class="text-sm text-green-600 mt-2">
                  ✓ Discount applied: {{ appliedDiscount.code }} ({{ appliedDiscount.discount_percentage }}% off)
                </p>
              </div>

              <!-- Error Message -->
              <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p class="text-red-700 text-sm">{{ error }}</p>
                </div>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="loading || !canSubmit"
                class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3.5 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
                <span v-else>Continue to Email Verification</span>
              </button>
            </form>
          </div>

          <!-- Step 2: Email Verification -->
          <div v-if="currentStep === 2" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div class="mb-6">
              <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 class="text-2xl font-semibold text-gray-900 mb-2">Check Your Email</h2>
              <p class="text-gray-600 mb-4">
                We've sent a verification link to <strong class="text-gray-900">{{ orderForm.email }}</strong>
              </p>
              <p class="text-sm text-gray-500">
                Click the link in the email to verify your address and complete your order.
              </p>
            </div>

            <!-- Manual Verification -->
            <div class="border-t border-gray-200 pt-6 mt-6">
              <p class="text-sm text-gray-600 mb-4">Already verified? Enter your verification code:</p>
              
              <!-- Mock Mode: Show token for easy testing -->
              <div v-if="USE_MOCK && verificationToken" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p class="text-xs text-blue-800 font-medium mb-1">🎭 Mock Mode - Your verification token:</p>
                <div class="flex items-center gap-2">
                  <code class="flex-1 text-xs bg-white px-2 py-1 rounded border border-blue-300 text-blue-900 break-all">{{ verificationToken }}</code>
                  <button
                    @click="navigator.clipboard.writeText(verificationToken)"
                    class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    title="Copy token"
                  >
                    Copy
                  </button>
                </div>
              </div>
              
              <div class="flex gap-2 max-w-md mx-auto">
                <input
                  v-model="verificationToken"
                  type="text"
                  placeholder="Verification token"
                  class="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
                <button
                  @click="handleVerifyEmail"
                  :disabled="!verificationToken || loading"
                  class="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Verify
                </button>
              </div>
            </div>

            <!-- Resend Email -->
            <button
              @click="resendVerification"
              :disabled="resendCooldown > 0"
              class="mt-4 text-sm text-blue-600 hover:text-blue-700 disabled:text-gray-400 transition-colors"
            >
              <span v-if="resendCooldown > 0">Resend in {{ resendCooldown }}s</span>
              <span v-else>Resend verification email</span>
            </button>
          </div>

          <!-- Step 3: Success -->
          <div v-if="currentStep === 3" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div class="mb-6">
              <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 class="text-2xl font-semibold text-gray-900 mb-2">Order Created Successfully!</h2>
              <p class="text-gray-600 mb-4">
                Your order <strong class="text-gray-900">#{{ createdOrderId }}</strong> has been created.
              </p>
              <p class="text-sm text-gray-500">
                You'll receive order updates at <strong>{{ orderForm.email }}</strong>
              </p>
            </div>

            <div class="flex gap-4 justify-center">
              <button
                @click="$router.push(`/orders/${createdOrderId}`)"
                class="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                View Order
              </button>
              <button
                @click="resetForm"
                class="px-6 py-2.5 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                Place Another Order
              </button>
            </div>
          </div>
        </div>

        <!-- Price Summary Sidebar -->
        <div class="lg:col-span-1">
          <div v-if="currentStep === 1" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Price Estimate
            </h3>

            <div v-if="quoteLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p class="text-sm text-gray-500">Calculating...</p>
            </div>

            <div v-else-if="quote" class="space-y-3">
              <div class="space-y-2 text-sm">
                <div v-if="quote.breakdown" class="space-y-1.5">
                  <div class="flex justify-between text-gray-600">
                    <span>Base Price:</span>
                    <span>${{ formatPrice(quote.breakdown.base_price) }}</span>
                  </div>
                  <div v-if="quote.breakdown.extra_services > 0" class="flex justify-between text-gray-600">
                    <span>Extra Services:</span>
                    <span>${{ formatPrice(quote.breakdown.extra_services) }}</span>
                  </div>
                  <div v-if="quote.breakdown.deadline_multiplier > 1" class="flex justify-between text-gray-600">
                    <span>Urgency Fee:</span>
                    <span>{{ ((quote.breakdown.deadline_multiplier - 1) * 100).toFixed(0) }}%</span>
                  </div>
                  <div v-if="quote.breakdown.discount > 0" class="flex justify-between text-green-600">
                    <span>Discount:</span>
                    <span>-${{ formatPrice(quote.breakdown.discount) }}</span>
                  </div>
                  <div class="border-t border-gray-200 pt-2 mt-2"></div>
                </div>
                <div class="flex justify-between text-lg font-bold text-gray-900">
                  <span>Total:</span>
                  <span class="text-blue-600">${{ formatPrice(quote.total_price || quote.final_total || 0) }}</span>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8 text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p class="text-sm">Fill in order details to see price estimate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import ordersAPI from '@/api/orders'
import orderConfigsAPI from '@/api/orderConfigs'
import { mockGuestCheckoutAPI } from '@/api/mock/guestCheckout'
import { useToast } from '@/composables/useToast'

// Enable mock mode via query parameter or environment variable
const route = useRoute()
const USE_MOCK = ref(route.query.mock === 'true' || import.meta.env.VITE_USE_MOCK_API === 'true')

const { success: showSuccess, error: showError } = useToast()

// Show mock mode indicator
if (USE_MOCK.value) {
  console.log('🎭 Guest Checkout running in MOCK MODE')
}

const currentStep = ref(1)
const loading = ref(false)
const error = ref('')
const verificationToken = ref('')
const resendCooldown = ref(0)
const createdOrderId = ref(null)
const websiteId = ref(null)

// Order configs
const paperTypes = ref([])
const academicLevels = ref([])
const formattingStyles = ref([])
const typesOfWork = ref([])
const subjects = ref([])

// Price quote
const quote = ref(null)
const quoteLoading = ref(false)
const discountCode = ref('')
const appliedDiscount = ref(null)

const orderForm = ref({
  email: '',
  topic: '',
  paper_type_id: null,
  number_of_pages: 1,
  academic_level_id: null,
  formatting_style_id: null,
  type_of_work_id: null,
  subject_id: null,
  client_deadline: '',
  order_instructions: '',
  discount_code: ''
})

const minDeadline = computed(() => {
  const now = new Date()
  now.setHours(now.getHours() + 12) // Minimum 12 hours from now
  return now.toISOString().slice(0, 16)
})

const canSubmit = computed(() => {
  return orderForm.value.email &&
    orderForm.value.topic &&
    orderForm.value.paper_type_id &&
    orderForm.value.number_of_pages > 0 &&
    orderForm.value.client_deadline &&
    orderForm.value.order_instructions
})

const formatPrice = (price) => {
  return parseFloat(price || 0).toFixed(2)
}

const loadOrderConfigs = async () => {
  const params = { website_id: websiteId.value }
  
  try {
    if (USE_MOCK.value) {
      // Use mock API
      const [paperTypesRes, academicLevelsRes, formattingStylesRes, typesOfWorkRes, subjectsRes] = await Promise.all([
        mockGuestCheckoutAPI.getPaperTypes(params),
        mockGuestCheckoutAPI.getAcademicLevels(params),
        mockGuestCheckoutAPI.getFormattingStyles(params),
        mockGuestCheckoutAPI.getTypesOfWork(params),
        mockGuestCheckoutAPI.getSubjects(params)
      ])
      
      paperTypes.value = paperTypesRes.data?.results || paperTypesRes.data || []
      academicLevels.value = academicLevelsRes.data?.results || academicLevelsRes.data || []
      formattingStyles.value = formattingStylesRes.data?.results || formattingStylesRes.data || []
      typesOfWork.value = typesOfWorkRes.data?.results || typesOfWorkRes.data || []
      subjects.value = subjectsRes.data?.results || subjectsRes.data || []
    } else {
      // Use real API
      const [paperTypesRes, academicLevelsRes, formattingStylesRes, typesOfWorkRes, subjectsRes] = await Promise.all([
        orderConfigsAPI.getPaperTypes(params),
        orderConfigsAPI.getAcademicLevels(params),
        orderConfigsAPI.getFormattingStyles(params),
        orderConfigsAPI.getTypesOfWork(params),
        orderConfigsAPI.getSubjects(params)
      ])
      
      paperTypes.value = paperTypesRes.data?.results || paperTypesRes.data || []
      academicLevels.value = academicLevelsRes.data?.results || academicLevelsRes.data || []
      formattingStyles.value = formattingStylesRes.data?.results || formattingStylesRes.data || []
      typesOfWork.value = typesOfWorkRes.data?.results || typesOfWorkRes.data || []
      subjects.value = subjectsRes.data?.results || subjectsRes.data || []
    }
  } catch (e) {
    console.error('Failed to load order configs:', e)
    showError('Failed to load order options')
  }
}

const calculatePrice = async () => {
  if (!orderForm.value.paper_type_id || !orderForm.value.number_of_pages || !orderForm.value.client_deadline) {
    quote.value = null
    return
  }

  quoteLoading.value = true
  try {
    const quoteData = {
      topic: orderForm.value.topic,
      paper_type_id: orderForm.value.paper_type_id,
      academic_level_id: orderForm.value.academic_level_id,
      subject_id: orderForm.value.subject_id,
      type_of_work_id: orderForm.value.type_of_work_id,
      number_of_pages: orderForm.value.number_of_pages,
      client_deadline: new Date(orderForm.value.client_deadline).toISOString(),
      order_instructions: orderForm.value.order_instructions,
      discount_code: appliedDiscount.value?.code || discountCode.value || ''
    }
    
    const res = USE_MOCK.value 
      ? await mockGuestCheckoutAPI.quote(quoteData)
      : await ordersAPI.quote(quoteData)
    
    quote.value = res.data
  } catch (e) {
    console.error('Failed to calculate price:', e)
    quote.value = null
  } finally {
    quoteLoading.value = false
  }
}

const applyDiscount = async () => {
  if (!discountCode.value) return
  
  try {
    // Recalculate price with discount
    await calculatePrice()
    // If quote has discount info, mark as applied
    if (quote.value && quote.value.breakdown?.discount > 0) {
      appliedDiscount.value = { code: discountCode.value }
      orderForm.value.discount_code = discountCode.value
      showSuccess('Discount code applied' + (USE_MOCK.value ? ' (mock)' : ''))
    } else {
      showError('Invalid or expired discount code' + (USE_MOCK.value ? ' (Try: TEST10)' : ''))
    }
  } catch (e) {
    showError('Failed to apply discount code')
  }
}

const handleStartOrder = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const orderData = {
      topic: orderForm.value.topic,
      paper_type_id: orderForm.value.paper_type_id,
      number_of_pages: orderForm.value.number_of_pages,
      academic_level_id: orderForm.value.academic_level_id,
      formatting_style_id: orderForm.value.formatting_style_id,
      type_of_work_id: orderForm.value.type_of_work_id,
      subject_id: orderForm.value.subject_id,
      client_deadline: new Date(orderForm.value.client_deadline).toISOString(),
      order_instructions: orderForm.value.order_instructions,
      discount_code: appliedDiscount.value?.code || orderForm.value.discount_code || ''
    }

    const response = USE_MOCK.value
      ? await mockGuestCheckoutAPI.startGuestOrder({
          website_id: websiteId.value,
          email: orderForm.value.email,
          order_data: orderData
        })
      : await ordersAPI.startGuestOrder({
          website_id: websiteId.value,
          email: orderForm.value.email,
          order_data: orderData
        })

    if (response.data.verification_required) {
      verificationToken.value = response.data.verification_token || ''
      currentStep.value = 2
      startResendCooldown()
      showSuccess('Verification email sent! Please check your inbox.')
    } else {
      createdOrderId.value = response.data.order_id
      currentStep.value = 3
      showSuccess('Order created successfully!')
    }
  } catch (e) {
    const errorMsg = e.response?.data?.detail || 'Failed to start order. Please try again.'
    error.value = errorMsg
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const handleVerifyEmail = async () => {
  if (!verificationToken.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const orderData = {
      topic: orderForm.value.topic,
      paper_type_id: orderForm.value.paper_type_id,
      number_of_pages: orderForm.value.number_of_pages,
      academic_level_id: orderForm.value.academic_level_id,
      formatting_style_id: orderForm.value.formatting_style_id,
      type_of_work_id: orderForm.value.type_of_work_id,
      subject_id: orderForm.value.subject_id,
      client_deadline: new Date(orderForm.value.client_deadline).toISOString(),
      order_instructions: orderForm.value.order_instructions,
      discount_code: appliedDiscount.value?.code || orderForm.value.discount_code || ''
    }

    const response = USE_MOCK.value
      ? await mockGuestCheckoutAPI.verifyGuestEmail({
          verification_token: verificationToken.value,
          website_id: websiteId.value,
          order_data: orderData
        })
      : await ordersAPI.verifyGuestEmail({
          verification_token: verificationToken.value,
          website_id: websiteId.value,
          order_data: orderData
        })

    createdOrderId.value = response.data.order_id
    currentStep.value = 3
    showSuccess('Email verified! Order created successfully.')
  } catch (e) {
    const errorMsg = e.response?.data?.detail || 'Invalid verification token. Please check your email.'
    error.value = errorMsg
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const resendVerification = async () => {
  if (resendCooldown.value > 0) return
  
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
    academic_level_id: null,
    formatting_style_id: null,
    type_of_work_id: null,
    subject_id: null,
    client_deadline: '',
    order_instructions: '',
    discount_code: ''
  }
  verificationToken.value = ''
  createdOrderId.value = null
  error.value = ''
  quote.value = null
  discountCode.value = ''
  appliedDiscount.value = null
}

// Watch for form changes to recalculate price
watch([
  () => orderForm.value.paper_type_id,
  () => orderForm.value.number_of_pages,
  () => orderForm.value.academic_level_id,
  () => orderForm.value.formatting_style_id,
  () => orderForm.value.type_of_work_id,
  () => orderForm.value.subject_id,
  () => orderForm.value.client_deadline
], () => {
  if (orderForm.value.paper_type_id && orderForm.value.number_of_pages && orderForm.value.client_deadline) {
    calculatePrice()
  }
})

onMounted(() => {
  websiteId.value = parseInt(route.query.website_id) || 1
  loadOrderConfigs()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
