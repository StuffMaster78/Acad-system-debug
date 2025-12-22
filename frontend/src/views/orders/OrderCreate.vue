<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Place a New Order</h1>

    <div v-if="message" class="mb-4 p-3 rounded bg-green-50 text-green-700">{{ message }}</div>
    <div v-if="error" class="mb-4 p-3 rounded bg-red-50 text-red-700">{{ error }}</div>

    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Topic *</label>
        <input v-model="form.topic" type="text" required class="w-full border rounded px-3 py-2" />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Paper Type *</label>
          <select
            v-model="form.paper_type_id"
            required
            class="w-full border rounded px-3 py-2"
          >
            <option value="">Select paper type</option>
            <option v-for="pt in paperTypes" :key="pt.id" :value="pt.id">
              {{ pt.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Number of Pages *</label>
          <input v-model.number="form.number_of_pages" type="number" min="1" required class="w-full border rounded px-3 py-2" />
        </div>
      </div>

      <!-- Academic Level and Subject -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Academic Level</label>
          <select
            v-model="form.academic_level_id"
            class="w-full border rounded px-3 py-2"
          >
            <option value="">Select academic level</option>
            <option v-for="level in academicLevels" :key="level.id" :value="level.id">
              {{ level.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Subject</label>
          <select
            v-model="form.subject_id"
            class="w-full border rounded px-3 py-2"
          >
            <option value="">Select subject</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1 flex items-center gap-1">
          Deadline *
          <Tooltip text="Your deadline helps us assign the right writer and ensure your order is completed on time. Please provide a realistic deadline to ensure quality work." />
        </label>
        <input v-model="form.client_deadline" type="datetime-local" required class="w-full border rounded px-3 py-2" />
      </div>

      <div>
        <div class="flex items-center gap-1 mb-1">
          <label class="block text-sm font-medium">Instructions *</label>
          <Tooltip text="Detailed instructions help our writers understand exactly what you need. Include specific requirements, formatting guidelines, sources to use, and any other important details." />
        </div>
        <RichTextEditor
          v-model="form.order_instructions"
          :required="true"
          placeholder="Provide detailed instructions for your order..."
          toolbar="full"
          height="250px"
        />
      </div>

      <!-- Discount Code -->
      <div>
        <label class="block text-sm font-medium mb-1">Discount Code (Optional)</label>
        <DiscountCodeInput
          v-model="discountCode"
          :order-total="estimatedTotal"
          @applied="handleDiscountApplied"
          @removed="handleDiscountRemoved"
        />
      </div>

      <div class="flex gap-3">
        <button :disabled="loading" class="px-4 py-2 bg-primary-600 text-white rounded disabled:opacity-50">
          {{ loading ? 'Creating...' : 'Create Order' }}
        </button>
        <router-link to="/orders" class="px-4 py-2 bg-gray-100 rounded">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ordersAPI from '@/api/orders'
import { useRouter } from 'vue-router'
import dropdownOptionsAPI from '@/api/dropdown-options'
import DiscountCodeInput from '@/components/common/DiscountCodeInput.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import Tooltip from '@/components/common/Tooltip.vue'

const router = useRouter()

const form = ref({
  topic: '',
  paper_type_id: null,
  number_of_pages: 1,
  academic_level_id: null,
  subject_id: null,
  client_deadline: '',
  order_instructions: '',
  discount_code: '',
})

const loading = ref(false)
const error = ref('')
const message = ref('')
const discountCode = ref('')
const discountAmount = ref(0)
const appliedDiscount = ref(null)

const paperTypes = ref([])
const academicLevels = ref([])
const subjects = ref([])

const estimatedTotal = computed(() => {
  // This would be calculated based on paper type and pages
  // For now, return a placeholder
  return 100
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

const handleDiscountApplied = (discount, amount) => {
  appliedDiscount.value = discount
  discountAmount.value = amount
  form.value.discount_code = discount.code
}

const handleDiscountRemoved = () => {
  appliedDiscount.value = null
  discountAmount.value = 0
  form.value.discount_code = ''
}

const submit = async () => {
  error.value = ''
  message.value = ''
  loading.value = true
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
    if (form.value.discount_code || appliedDiscount.value?.code) {
      payload.discount_code = form.value.discount_code || appliedDiscount.value?.code
    }

    const res = await ordersAPI.createClient(payload)
    message.value = `Order #${res.data.id} created successfully.`
    setTimeout(() => router.push(`/orders/${res.data.id}`), 800)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to create order'
    if (import.meta.env.DEV) {
      console.error('Failed to create order:', e)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDropdownOptions()
})
</script>
