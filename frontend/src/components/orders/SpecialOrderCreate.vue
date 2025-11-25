<template>
  <div class="special-order-create">
    <div class="card p-6">
      <h2 class="text-2xl font-bold mb-6">Create Special Order</h2>

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
  price: null,
  special_instructions: '',
  attachments: []
})

const submitting = ref(false)
const error = ref('')
const academicLevels = ref([])
const loadingLevels = ref(false)

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

