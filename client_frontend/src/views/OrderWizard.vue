<template>
  <Layout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="container-custom max-w-4xl">
        <div class="bg-white rounded-lg shadow-lg p-8">
          <h1 class="text-3xl font-bold mb-8">Place Your Order</h1>

          <!-- Step Indicator -->
          <div class="mb-8">
            <div class="flex items-center justify-between">
              <div 
                v-for="(step, index) in steps" 
                :key="index"
                class="flex items-center flex-1"
              >
                <div class="flex flex-col items-center flex-1">
                  <div 
                    class="w-10 h-10 rounded-full flex items-center justify-center font-semibold transition"
                    :class="currentStep >= index 
                      ? 'bg-primary-600 text-white' 
                      : 'bg-gray-200 text-gray-600'"
                  >
                    {{ index + 1 }}
                  </div>
                  <span class="mt-2 text-sm text-gray-600">{{ step }}</span>
                </div>
                <div 
                  v-if="index < steps.length - 1"
                  class="h-1 flex-1 mx-2"
                  :class="currentStep > index ? 'bg-primary-600' : 'bg-gray-200'"
                ></div>
              </div>
            </div>
          </div>

          <!-- Step 1: Order Details -->
          <div v-if="currentStep === 0" class="space-y-6">
            <h2 class="text-2xl font-semibold mb-4">Order Details</h2>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Paper Type *
              </label>
              <select 
                v-model="orderData.paper_type" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                required
              >
                <option value="">Select paper type</option>
                <option value="essay">Essay</option>
                <option value="research_paper">Research Paper</option>
                <option value="dissertation">Dissertation</option>
                <option value="thesis">Thesis</option>
                <option value="case_study">Case Study</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Academic Level *
              </label>
              <select 
                v-model="orderData.academic_level" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Select level</option>
                <option value="high_school">High School</option>
                <option value="undergraduate">Undergraduate</option>
                <option value="masters">Masters</option>
                <option value="phd">PhD</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Number of Pages *
              </label>
              <input 
                v-model.number="orderData.pages" 
                type="number" 
                min="1"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Deadline *
              </label>
              <input 
                v-model="orderData.deadline" 
                type="datetime-local" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Subject/Topic
              </label>
              <input 
                v-model="orderData.subject" 
                type="text" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="Enter your subject or topic"
              />
            </div>
          </div>

          <!-- Step 2: Instructions -->
          <div v-if="currentStep === 1" class="space-y-6">
            <h2 class="text-2xl font-semibold mb-4">Instructions</h2>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Instructions *
              </label>
              <textarea 
                v-model="orderData.instructions" 
                rows="8"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="Provide detailed instructions for your order..."
                required
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Additional Files (Optional)
              </label>
              <input 
                type="file" 
                multiple
                @change="handleFileUpload"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <!-- Step 3: Price & Review -->
          <div v-if="currentStep === 2" class="space-y-6">
            <h2 class="text-2xl font-semibold mb-4">Review & Price</h2>
            
            <div v-if="priceLoading" class="text-center py-8">
              <p class="text-gray-600">Calculating price...</p>
            </div>

            <div v-else-if="priceQuote" class="bg-gray-50 p-6 rounded-lg">
              <div class="space-y-4">
                <div class="flex justify-between">
                  <span class="text-gray-600">Paper Type:</span>
                  <span class="font-semibold">{{ orderData.paper_type }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Pages:</span>
                  <span class="font-semibold">{{ orderData.pages }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Deadline:</span>
                  <span class="font-semibold">{{ formatDate(orderData.deadline) }}</span>
                </div>
                <div class="border-t pt-4 flex justify-between text-lg">
                  <span class="font-semibold">Total:</span>
                  <span class="font-bold text-primary-600 text-xl">
                    ${{ priceQuote.total_price?.toFixed(2) || '0.00' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p class="text-sm text-yellow-800">
                <strong>Note:</strong> You can proceed as a guest or create an account to track your order.
              </p>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex justify-between mt-8">
            <button 
              v-if="currentStep > 0"
              @click="currentStep--"
              class="btn btn-secondary"
            >
              Previous
            </button>
            <div v-else></div>
            
            <button 
              v-if="currentStep < steps.length - 1"
              @click="nextStep"
              class="btn btn-primary"
            >
              Next
            </button>
            <button 
              v-else
              @click="submitOrder"
              :disabled="submitting"
              class="btn btn-primary"
            >
              {{ submitting ? 'Submitting...' : 'Place Order' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'
import servicesAPI from '@/api/services'
import { useAuthStore } from '@/stores/auth'
import { useWebsiteStore } from '@/stores/website'

const router = useRouter()
const authStore = useAuthStore()
const websiteStore = useWebsiteStore()

const steps = ['Order Details', 'Instructions', 'Review & Price']
const currentStep = ref(0)
const submitting = ref(false)
const priceLoading = ref(false)
const priceQuote = ref(null)

const orderData = ref({
  paper_type: '',
  academic_level: '',
  pages: 1,
  deadline: '',
  subject: '',
  instructions: '',
  files: []
})

// Calculate price when step 2 is reached
watch(currentStep, async (newStep) => {
  if (newStep === 2 && !priceQuote.value) {
    await calculatePrice()
  }
})

const calculatePrice = async () => {
  if (!orderData.value.paper_type || !orderData.value.pages) return
  
  priceLoading.value = true
  try {
    const response = await servicesAPI.getQuote({
      paper_type: orderData.value.paper_type,
      academic_level: orderData.value.academic_level,
      pages: orderData.value.pages,
      deadline: orderData.value.deadline,
    })
    priceQuote.value = response.data
  } catch (error) {
    console.error('Price calculation error:', error)
    alert('Failed to calculate price. Please check your inputs.')
  } finally {
    priceLoading.value = false
  }
}

const nextStep = async () => {
  // Validate current step
  if (currentStep.value === 0) {
    if (!orderData.value.paper_type || !orderData.value.academic_level || 
        !orderData.value.pages || !orderData.value.deadline) {
      alert('Please fill in all required fields')
      return
    }
  }
  
  if (currentStep.value === 1) {
    if (!orderData.value.instructions) {
      alert('Please provide instructions')
      return
    }
  }
  
  currentStep.value++
}

const handleFileUpload = (event) => {
  orderData.value.files = Array.from(event.target.files)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

const submitOrder = async () => {
  submitting.value = true
  try {
    const response = await servicesAPI.createOrder({
      ...orderData.value,
      website: websiteStore.website?.id,
    })
    
    // Redirect based on auth status
    if (authStore.isAuthenticated) {
      router.push({ name: 'Dashboard' })
    } else {
      router.push({ name: 'Login', query: { orderId: response.data.id } })
    }
  } catch (error) {
    console.error('Order submission error:', error)
    alert(error.response?.data?.detail || 'Failed to submit order. Please try again.')
  } finally {
    submitting.value = false
  }
}
</script>

