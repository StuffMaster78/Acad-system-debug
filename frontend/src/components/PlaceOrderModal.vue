<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-2xl font-bold leading-6 text-gray-900 mb-4">
                Place New Order
              </DialogTitle>

              <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- Order Type Selection -->
                <div class="border-b border-gray-200 pb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Order Type
                  </label>
                  <div class="flex gap-4">
                    <label class="flex items-center">
                      <input
                        type="radio"
                        v-model="orderType"
                        value="attributed"
                        class="mr-2"
                      />
                      <span>Attributed to Client</span>
                    </label>
                    <label class="flex items-center">
                      <input
                        type="radio"
                        v-model="orderType"
                        value="unattributed"
                        class="mr-2"
                      />
                      <span>External/Unattributed</span>
                    </label>
                  </div>
                </div>

                <!-- Client Selection (for attributed orders) -->
                <div v-if="orderType === 'attributed'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Client *
                    </label>
                    <select
                      v-model="formData.client_id"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    >
                      <option value="">Select a client...</option>
                      <option v-for="client in clients" :key="client.id" :value="client.id">
                        {{ formatClientName(client) }}
                      </option>
                    </select>
                  </div>
                </div>

                <!-- External Contact (for unattributed orders) -->
                <div v-if="orderType === 'unattributed'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Contact Name *
                    </label>
                    <input
                      v-model="formData.external_contact_name"
                      type="text"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Email *
                    </label>
                    <input
                      v-model="formData.external_contact_email"
                      type="email"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Phone
                    </label>
                    <input
                      v-model="formData.external_contact_phone"
                      type="tel"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    />
                  </div>
                </div>

                <!-- Order Details -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Topic/Title *
                    </label>
                    <input
                      v-model="formData.topic"
                      type="text"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Paper Type *
                    </label>
                    <select
                      v-model="formData.paper_type_id"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    >
                      <option value="">Select paper type...</option>
                      <option v-for="type in paperTypes" :key="type.id" :value="type.id">
                        {{ type.name }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Number of Pages *
                    </label>
                    <input
                      v-model.number="formData.number_of_pages"
                      type="number"
                      min="1"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Deadline *
                    </label>
                    <input
                      v-model="formData.client_deadline"
                      type="datetime-local"
                      class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      required
                    />
                  </div>
                </div>

                <!-- Instructions -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Order Instructions *
                  </label>
                  <textarea
                    v-model="formData.order_instructions"
                    rows="4"
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    required
                  ></textarea>
                </div>

                <!-- Optional Fields -->
                <details class="border border-gray-200 rounded-md p-4">
                  <summary class="cursor-pointer text-sm font-medium text-gray-700">
                    Additional Options (Optional)
                  </summary>
                  <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Academic Level
                      </label>
                      <select
                        v-model="formData.academic_level_id"
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      >
                        <option value="">Select...</option>
                        <option v-for="level in academicLevels" :key="level.id" :value="level.id">
                          {{ level.name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Formatting Style
                      </label>
                      <select
                        v-model="formData.formatting_style_id"
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      >
                        <option value="">Select...</option>
                        <option v-for="style in formattingStyles" :key="style.id" :value="style.id">
                          {{ style.name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Subject
                      </label>
                      <select
                        v-model="formData.subject_id"
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      >
                        <option value="">Select...</option>
                        <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                          {{ subject.name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Discount Code
                      </label>
                      <input
                        v-model="formData.discount_code"
                        type="text"
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      />
                    </div>
                  </div>
                </details>

                <!-- Unpaid Access Override -->
                <div class="flex items-center">
                  <input
                    v-model="formData.allow_unpaid_access"
                    type="checkbox"
                    class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label class="ml-2 block text-sm text-gray-700">
                    Allow access even if unpaid
                  </label>
                </div>

                <!-- Error Message -->
                <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {{ error }}
                </div>

                <!-- Actions -->
                <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    @click="closeModal"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="loading"
                    class="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 disabled:opacity-50"
                  >
                    {{ loading ? 'Creating...' : 'Create Order' }}
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import dashboardAPI from '@/api/dashboard'
import orderConfigsAPI from '@/api/orderConfigs'
import usersAPI from '@/api/users'
import { formatClientName } from '@/utils/formatDisplay'

const props = defineProps({
  isOpen: Boolean,
})

const emit = defineEmits(['close', 'success'])

const orderType = ref('attributed')
const loading = ref(false)
const error = ref(null)
const loadingConfigs = ref(false)

const formData = ref({
  topic: '',
  paper_type_id: '',
  number_of_pages: 1,
  client_deadline: '',
  order_instructions: '',
  client_id: null,
  external_contact_name: '',
  external_contact_email: '',
  external_contact_phone: '',
  academic_level_id: null,
  formatting_style_id: null,
  subject_id: null,
  discount_code: '',
  allow_unpaid_access: false,
})

// Data fetched from database
const clients = ref([])
const paperTypes = ref([])
const academicLevels = ref([])
const formattingStyles = ref([])
const subjects = ref([])

watch(orderType, () => {
  // Reset form fields when order type changes
  if (orderType.value === 'attributed') {
    formData.value.external_contact_name = ''
    formData.value.external_contact_email = ''
    formData.value.external_contact_phone = ''
  } else {
    formData.value.client_id = null
  }
})

const closeModal = () => {
  error.value = null
  emit('close')
}

const handleSubmit = async () => {
  error.value = null
  loading.value = true

  try {
    // Prepare data based on order type
    const submitData = {
      topic: formData.value.topic,
      paper_type_id: formData.value.paper_type_id,
      number_of_pages: formData.value.number_of_pages,
      client_deadline: formData.value.client_deadline,
      order_instructions: formData.value.order_instructions,
      allow_unpaid_access: formData.value.allow_unpaid_access,
    }

    if (orderType.value === 'attributed') {
      submitData.client_id = formData.value.client_id
    } else {
      submitData.external_contact_name = formData.value.external_contact_name
      submitData.external_contact_email = formData.value.external_contact_email
      if (formData.value.external_contact_phone) {
        submitData.external_contact_phone = formData.value.external_contact_phone
      }
    }

    // Add optional fields
    if (formData.value.academic_level_id) {
      submitData.academic_level_id = formData.value.academic_level_id
    }
    if (formData.value.formatting_style_id) {
      submitData.formatting_style_id = formData.value.formatting_style_id
    }
    if (formData.value.subject_id) {
      submitData.subject_id = formData.value.subject_id
    }
    if (formData.value.discount_code) {
      submitData.discount_code = formData.value.discount_code
    }

    const response = await dashboardAPI.placeOrder(submitData)
    
    emit('success', response.data)
    closeModal()
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Failed to create order'
    console.error('Place order error:', err)
  } finally {
    loading.value = false
  }
}

// Fetch dropdown options from database
const loadConfigData = async () => {
  if (loadingConfigs.value) return
  loadingConfigs.value = true
  try {
    const [paperTypesRes, academicLevelsRes, formattingStylesRes, subjectsRes, clientsRes] = await Promise.all([
      orderConfigsAPI.getPaperTypes(),
      orderConfigsAPI.getAcademicLevels(),
      orderConfigsAPI.getFormattingStyles(),
      orderConfigsAPI.getSubjects(),
      usersAPI.list({ role: 'client' }).catch(() => ({ data: { results: [] } }))
    ])
    
    paperTypes.value = paperTypesRes.data?.results || paperTypesRes.data || []
    academicLevels.value = academicLevelsRes.data?.results || academicLevelsRes.data || []
    formattingStyles.value = formattingStylesRes.data?.results || formattingStylesRes.data || []
    subjects.value = subjectsRes.data?.results || subjectsRes.data || []
    clients.value = clientsRes.data?.results || clientsRes.data || []
  } catch (e) {
    console.error('Failed to load config data:', e)
    error.value = 'Failed to load order configuration. Please refresh the page.'
  } finally {
    loadingConfigs.value = false
  }
}

// Load data when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && paperTypes.value.length === 0) {
    loadConfigData()
  }
})

// Also load on mount
onMounted(() => {
  if (props.isOpen) {
    loadConfigData()
  }
})
</script>

