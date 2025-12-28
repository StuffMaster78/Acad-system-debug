<template>
  <div class="space-y-4">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Topic
          </label>
          <input
            v-model="form.topic"
            type="text"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <select
            v-model="form.status"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option v-for="status in orderStatuses" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Total Price ($)
          </label>
          <input
            v-model.number="form.total_price"
            type="number"
            step="0.01"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Writer Compensation ($)
          </label>
          <input
            v-model.number="form.writer_compensation"
            type="number"
            step="0.01"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Client Deadline
          </label>
          <input
            v-model="form.client_deadline"
            type="datetime-local"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Writer Deadline
          </label>
          <input
            v-model="form.writer_deadline"
            type="datetime-local"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Instructions
        </label>
        <textarea
          v-model="form.order_instructions"
          rows="5"
          class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
        ></textarea>
      </div>
      <div class="flex gap-3 pt-4 border-t">
        <button
          type="button"
          @click="handleCancel"
          class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="saving"
          class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ordersAPI } from '@/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  order: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['success', 'error'])

const { success: showSuccessToast, error: showErrorToast } = useToast()

const form = ref({
  topic: '',
  total_price: 0,
  writer_compensation: 0,
  status: '',
  client_deadline: '',
  writer_deadline: '',
  order_instructions: ''
})

const saving = ref(false)

const orderStatuses = [
  { value: 'created', label: 'Created' },
  { value: 'pending', label: 'Pending' },
  { value: 'unpaid', label: 'Unpaid' },
  { value: 'available', label: 'Available' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'under_editing', label: 'Under Editing' },
  { value: 'completed', label: 'Completed' },
  { value: 'disputed', label: 'Disputed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'archived', label: 'Archived' }
]

const initializeForm = () => {
  if (props.order) {
    form.value = {
      topic: props.order.topic || '',
      total_price: props.order.total_price || 0,
      writer_compensation: props.order.writer_compensation || 0,
      status: props.order.status || '',
      client_deadline: props.order.client_deadline ? new Date(props.order.client_deadline).toISOString().slice(0, 16) : '',
      writer_deadline: props.order.writer_deadline ? new Date(props.order.writer_deadline).toISOString().slice(0, 16) : '',
      order_instructions: props.order.order_instructions || props.order.instructions || ''
    }
  }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    await ordersAPI.update(props.order.id, form.value)
    showSuccessToast('Order updated successfully!')
    emit('success', { action: 'edit', data: form.value })
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to update order'
    showErrorToast(errorMsg)
    emit('error', error)
  } finally {
    saving.value = false
  }
}

const handleCancel = () => {
  initializeForm()
  emit('error', { cancelled: true })
}

onMounted(() => {
  initializeForm()
})
</script>

