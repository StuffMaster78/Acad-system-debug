<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Place New Order</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Fill in the details below to create your order</p>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300">
      {{ message }}
    </div>
    <div v-if="error" class="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <!-- Order Form -->
    <form @submit.prevent="submitOrder" class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 space-y-6">
      <!-- Topic -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Topic/Title <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.topic"
          type="text"
          required
          placeholder="Enter your paper topic or title"
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        />
        <p class="mt-1 text-xs text-gray-500">Be specific about what you need help with</p>
      </div>

      <!-- Paper Type and Pages -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Paper Type <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.paper_type_id"
            required
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="">Select paper type</option>
            <option v-for="pt in paperTypes" :key="pt.id" :value="pt.id">
              {{ pt.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Number of Pages <span class="text-red-500">*</span>
          </label>
          <input
            v-model.number="form.number_of_pages"
            type="number"
            min="1"
            required
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>

      <!-- Academic Level and Subject -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Academic Level
          </label>
          <select
            v-model="form.academic_level_id"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="">Select academic level</option>
            <option v-for="level in academicLevels" :key="level.id" :value="level.id">
              {{ level.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Subject
          </label>
          <select
            v-model="form.subject_id"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="">Select subject</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Deadline -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Deadline <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.client_deadline"
          type="datetime-local"
          required
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        />
        <p class="mt-1 text-xs text-gray-500">Please provide a realistic deadline</p>
      </div>

      <!-- Instructions -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Instructions <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="form.order_instructions"
          required
          rows="6"
          placeholder="Provide detailed instructions for your order..."
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        ></textarea>
        <p class="mt-1 text-xs text-gray-500">Include specific requirements, formatting guidelines, and any other important details</p>
      </div>

      <!-- Discount Code -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Discount Code (Optional)
        </label>
        <input
          v-model="form.discount_code"
          type="text"
          placeholder="Enter discount code"
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        />
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <router-link
          to="/client/orders"
          class="px-6 py-3 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          Cancel
        </router-link>
        <button
          type="submit"
          :disabled="loading || !canSubmit"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {{ loading ? 'Creating Order...' : 'Create Order' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ordersAPI from '@/api/orders'
import dropdownOptionsAPI from '@/api/dropdown-options'

const router = useRouter()

const loading = ref(false)
const error = ref('')
const message = ref('')

const form = ref({
  topic: '',
  paper_type_id: null,
  number_of_pages: 1,
  academic_level_id: null,
  subject_id: null,
  client_deadline: '',
  order_instructions: '',
  discount_code: ''
})

const paperTypes = ref([])
const academicLevels = ref([])
const subjects = ref([])

const canSubmit = computed(() => {
  return form.value.topic &&
    form.value.paper_type_id &&
    form.value.number_of_pages > 0 &&
    form.value.client_deadline &&
    form.value.order_instructions
})

const loadDropdownOptions = async () => {
  try {
    const [paperTypesRes, academicLevelsRes, subjectsRes] = await Promise.all([
      dropdownOptionsAPI.getPaperTypes().catch(() => ({ data: [] })),
      dropdownOptionsAPI.getAcademicLevels().catch(() => ({ data: [] })),
      dropdownOptionsAPI.getSubjects().catch(() => ({ data: [] }))
    ])

    paperTypes.value = Array.isArray(paperTypesRes.data) ? paperTypesRes.data : []
    academicLevels.value = Array.isArray(academicLevelsRes.data) ? academicLevelsRes.data : []
    subjects.value = Array.isArray(subjectsRes.data) ? subjectsRes.data : []
  } catch (err) {
    if (import.meta.env.DEV) {
      console.error('Failed to load dropdown options:', err)
    }
  }
}

const submitOrder = async () => {
  if (!canSubmit.value) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = ''
  message.value = ''

  try {
    const payload = {
      topic: form.value.topic,
      paper_type_id: form.value.paper_type_id,
      number_of_pages: form.value.number_of_pages,
      client_deadline: form.value.client_deadline,
      order_instructions: form.value.order_instructions
    }

    if (form.value.academic_level_id) {
      payload.academic_level_id = form.value.academic_level_id
    }
    if (form.value.subject_id) {
      payload.subject_id = form.value.subject_id
    }
    if (form.value.discount_code) {
      payload.discount_code = form.value.discount_code
    }

    const response = await ordersAPI.create(payload)
    message.value = 'Order created successfully!'
    
    // Redirect to order detail page
    setTimeout(() => {
      router.push(`/client/orders/${response.data.id}`)
    }, 1500)
  } catch (err) {
    if (import.meta.env.DEV) {
      console.error('Failed to create order:', err)
    }
    error.value = err.response?.data?.detail || err.response?.data?.error || 'Failed to create order. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDropdownOptions()
})
</script>

