<template>
  <div class="special-order-create">
    <div class="card p-6 space-y-6">
      <div class="flex items-start justify-between gap-4 mb-2">
        <div>
          <h2 class="text-2xl font-bold">Create Special Order</h2>
          <p class="mt-1 text-sm text-gray-600">
            Send a detailed request for work that doesn’t fit the normal order form (rush, complex scope, or custom arrangements).
          </p>
        </div>
        <button
          type="button"
          @click="showHelpModal = true"
          class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-full border border-primary-200 text-primary-700 bg-primary-50 hover:bg-primary-100"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16h6m2 4H7a2 2 0 01-2-2V6a2 2 0 012-2h5.586a2 2 0 011.414.586l4.414 4.414A2 2 0 0120 10.414V18a2 2 0 01-2 2z" />
          </svg>
          How special orders work
        </button>
      </div>

      <div class="p-4 rounded-lg bg-blue-50 border border-blue-200 text-sm text-blue-900 space-y-1">
        <p class="font-semibold">What happens after you submit?</p>
        <ol class="list-decimal list-inside space-y-0.5">
          <li>Your request is reviewed by our team (and priced if needed).</li>
          <li>We may reply with questions or a proposed price and schedule.</li>
          <li>Once you approve and pay, a writer is assigned and work begins.</li>
        </ol>
        <p class="text-xs text-blue-700 mt-1">
          Tip: Attach any syllabus, rubric, or examples to help us scope the work accurately.
        </p>
      </div>

      <form @submit.prevent="submitOrder" class="space-y-6">
        <!-- Order Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Order Type <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.order_type"
            required
            class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select Order Type</option>
            <option value="rush">Rush Order</option>
            <option value="revision">Revision</option>
            <option value="custom">Custom Order</option>
          </select>
        </div>

        <!-- Topic/Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Topic/Title <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.topic"
            type="text"
            required
            placeholder="Enter order topic or title"
            class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Description -->
        <RichTextEditor
          v-model="form.description"
          label="Description"
          :required="true"
          placeholder="Provide detailed description of the order requirements"
          toolbar="full"
          height="250px"
          :error="error && error.includes('description') ? error : ''"
        />

        <!-- Academic Level -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Academic Level
          </label>
          <select
            v-model="form.academic_level_id"
            class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            :disabled="loadingLevels"
          >
            <option :value="null">Select Level</option>
            <option v-for="level in academicLevels" :key="level.id" :value="level.id">
              {{ level.name }}
            </option>
          </select>
          <p v-if="loadingLevels" class="text-xs text-gray-500 mt-1">Loading levels...</p>
        </div>

        <!-- Deadline -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Deadline <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.deadline"
            type="datetime-local"
            required
            class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Pages/Word Count -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Number of Pages
            </label>
            <input
              v-model.number="form.number_of_pages"
              type="number"
              min="1"
              placeholder="e.g., 5"
              class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Word Count
            </label>
            <input
              v-model.number="form.word_count"
              type="number"
              min="1"
              placeholder="e.g., 1500"
              class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <!-- Budget -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Budget ($)
          </label>
          <input
            v-model.number="form.budget"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p class="text-xs text-gray-500 mt-1">Your budget for negotiation purposes (optional)</p>
        </div>

        <!-- Price -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Price ($)
          </label>
          <input
            v-model.number="form.price"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <p class="text-xs text-gray-500 mt-1">Leave empty for automatic calculation</p>
        </div>

        <!-- Special Instructions -->
        <RichTextEditor
          v-model="form.special_instructions"
          label="Special Instructions"
          placeholder="Any additional instructions or requirements"
          toolbar="basic"
          height="150px"
        />

        <!-- Attachments -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Attachments
          </label>
          <FileUpload
            v-model="form.attachments"
            :multiple="true"
            accept=".pdf,.doc,.docx,.txt"
            upload-label="Upload Files"
          />
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {{ error }}
        </div>

        <!-- Submit Button -->
        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ submitting ? 'Creating...' : 'Create Special Order' }}
          </button>
          <button
            type="button"
            @click="$emit('cancel')"
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
  
  <!-- How It Works Modal -->
  <div
    v-if="showHelpModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    @click.self="showHelpModal = false"
  >
    <div class="bg-white rounded-xl shadow-2xl max-w-xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-bold text-gray-900">How Special Orders Work</h3>
        <button
          type="button"
          class="text-gray-400 hover:text-gray-600"
          @click="showHelpModal = false"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="p-6 space-y-4 text-sm text-gray-700">
        <p>
          Special orders are designed for work that doesn’t fit our standard order form
          (for example: rush situations, multi‑part projects, or very custom scopes).
        </p>
        <div class="space-y-2">
          <h4 class="font-semibold text-gray-900">Typical flow</h4>
          <ol class="list-decimal list-inside space-y-1">
            <li><strong>Submit request:</strong> Share your topic, deadline, scope, and any files (syllabus, rubric, examples).</li>
            <li><strong>Review & pricing:</strong> Our team reviews the details, asks clarifying questions if needed, and proposes a price and plan.</li>
            <li><strong>Negotiation:</strong> You can adjust your budget or scope; we’ll work with you to find a realistic plan.</li>
            <li><strong>Approval & payment:</strong> Once you approve, you’ll receive a payment link or invoice to confirm the order.</li>
            <li><strong>Writer assignment:</strong> An experienced writer is assigned and you can communicate with them via the order messages.</li>
          </ol>
        </div>
        <div class="space-y-2">
          <h4 class="font-semibold text-gray-900">About budget & price</h4>
          <p>
            The <strong>Budget</strong> field is optional and used as a starting point for negotiation.
            If you leave <strong>Price</strong> empty, our team will estimate a fair price based on your scope
            and share it with you for approval.
          </p>
        </div>
        <div class="space-y-2">
          <h4 class="font-semibold text-gray-900">Best practices</h4>
          <ul class="list-disc list-inside space-y-1">
            <li>Upload all relevant files (instructions, grading rubric, sample work, syllabus).</li>
            <li>Be specific about timelines, milestones, and what success looks like.</li>
            <li>Mention if this is connected to ongoing classes, exams, or long‑term projects.</li>
          </ul>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end">
        <button
          type="button"
          class="px-5 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium"
          @click="showHelpModal = false"
        >
          Got it, continue
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FileUpload from '@/components/common/FileUpload.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import ordersAPI from '@/api/orders'
import orderConfigsAPI from '@/api/orderConfigs'

const emit = defineEmits(['success', 'cancel'])

const form = ref({
  order_type: '',
  topic: '',
  description: '',
  academic_level_id: null,
  deadline: '',
  number_of_pages: null,
  word_count: null,
  budget: null,
  price: null,
  special_instructions: '',
  attachments: []
})

const submitting = ref(false)
const error = ref('')
const academicLevels = ref([])
const loadingLevels = ref(false)
const showHelpModal = ref(false)

const submitOrder = async () => {
  submitting.value = true
  error.value = ''

  try {
    // Prepare form data
    const formData = new FormData()
    
    Object.keys(form.value).forEach(key => {
      const value = form.value[key]
      if (value !== null && value !== undefined && value !== '') {
        if (key === 'attachments' && Array.isArray(value)) {
          value.forEach((file, index) => {
            if (file instanceof File) {
              formData.append(`attachments`, file)
            }
          })
        } else {
          formData.append(key, value)
        }
      }
    })

    const response = await ordersAPI.create(formData)
    
    emit('success', response.data)
    
    // Reset form
    form.value = {
      order_type: '',
      topic: '',
      description: '',
      academic_level_id: null,
      deadline: '',
      number_of_pages: null,
      word_count: null,
      budget: null,
      price: null,
      special_instructions: '',
      attachments: []
    }
  } catch (err) {
    console.error('Failed to create special order:', err)
    error.value = err?.response?.data?.error || err?.response?.data?.message || 'Failed to create order. Please try again.'
  } finally {
    submitting.value = false
  }
}

// Load academic levels from database
const loadAcademicLevels = async () => {
  loadingLevels.value = true
  try {
    const response = await orderConfigsAPI.getAcademicLevels()
    academicLevels.value = response.data?.results || response.data || []
  } catch (err) {
    console.error('Failed to load academic levels:', err)
    academicLevels.value = []
  } finally {
    loadingLevels.value = false
  }
}

onMounted(() => {
  loadAcademicLevels()
})
</script>

<style scoped>
.special-order-create {
  width: 100%;
}
</style>

