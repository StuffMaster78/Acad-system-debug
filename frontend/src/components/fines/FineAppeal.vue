<template>
  <div class="fine-appeal">
    <div class="space-y-6">
      <!-- Fine Information -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 class="font-semibold text-gray-900 mb-3">Fine Details</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Fine Type:</span>
            <span class="font-medium">{{ fine.fine_type_name || fine.fine_type || 'N/A' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Amount:</span>
            <span class="font-bold text-lg text-red-600">${{ formatCurrency(fine.amount) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Issued Date:</span>
            <span class="font-medium">{{ formatDate(fine.issued_at || fine.created_at) }}</span>
          </div>
          <div v-if="fine.reason" class="flex justify-between">
            <span class="text-gray-600">Reason:</span>
            <span class="font-medium">{{ fine.reason }}</span>
          </div>
          <div v-if="fine.order" class="flex justify-between">
            <span class="text-gray-600">Related Order:</span>
            <span class="font-medium">#{{ fine.order }}</span>
          </div>
        </div>
      </div>

      <!-- Appeal Form -->
      <div>
        <h3 class="text-lg font-semibold mb-4">Appeal Information</h3>
        <form @submit.prevent="submitAppeal" class="space-y-4">
          <!-- Appeal Reason -->
          <RichTextEditor
            v-model="appealForm.reason"
            label="Appeal Reason"
            :required="true"
            placeholder="Please explain why you believe this fine should be waived or reduced..."
            toolbar="basic"
            height="200px"
            :max-length="1000"
            :show-char-count="true"
            :error="error && error.includes('reason') ? error : ''"
          />

          <!-- Supporting Evidence -->
          <RichTextEditor
            v-model="appealForm.supporting_evidence"
            label="Supporting Evidence (Optional)"
            placeholder="Any additional information, links, or evidence that supports your appeal..."
            toolbar="basic"
            height="150px"
          />

          <!-- File Attachments -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Attachments (Optional)
            </label>
            <FileUpload
              v-model="attachments"
              :multiple="true"
              :max-size="10 * 1024 * 1024"
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              label="Upload supporting documents"
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>

          <!-- Submit Button -->
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="!appealForm.reason.trim() || submitting"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ submitting ? 'Submitting Appeal...' : 'Submit Appeal' }}
            </button>
            <button
              v-if="showCancel"
              type="button"
              @click="$emit('cancel')"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      <!-- Existing Appeals -->
      <div v-if="existingAppeals.length > 0" class="border-t pt-6">
        <h3 class="text-lg font-semibold mb-4">Previous Appeals</h3>
        <div class="space-y-3">
          <div
            v-for="appeal in existingAppeals"
            :key="appeal.id"
            class="border rounded-lg p-4"
            :class="{
              'bg-green-50 border-green-200': appeal.status === 'approved',
              'bg-red-50 border-red-200': appeal.status === 'rejected',
              'bg-yellow-50 border-yellow-200': appeal.status === 'pending' || appeal.status === 'under_review',
            }"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium">Appeal #{{ appeal.id }}</span>
              <StatusBadge :status="appeal.status" />
            </div>
            <p class="text-sm text-gray-700 mb-2">{{ appeal.reason }}</p>
            <div class="text-xs text-gray-500">
              Submitted: {{ formatDate(appeal.created_at) }}
              <span v-if="appeal.reviewed_at">
                • Reviewed: {{ formatDate(appeal.reviewed_at) }}
              </span>
            </div>
            <div v-if="appeal.admin_response" class="mt-2 p-2 bg-white rounded text-xs">
              <strong>Admin Response:</strong> {{ appeal.admin_response }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import finesAPI from '@/api/fines'
import FileUpload from '@/components/common/FileUpload.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const props = defineProps({
  fineId: {
    type: [Number, String],
    required: true
  },
  fine: {
    type: Object,
    default: () => ({})
  },
  showCancel: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['success', 'cancel'])

const appealForm = ref({
  reason: '',
  supporting_evidence: '',
  fine: props.fineId
})

const attachments = ref([])
const submitting = ref(false)
const error = ref('')
const existingAppeals = ref([])

const loadExistingAppeals = async () => {
  try {
    const response = await finesAPI.listAppeals({ fine: props.fineId })
    existingAppeals.value = Array.isArray(response.data?.results) 
      ? response.data.results 
      : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    console.error('Failed to load existing appeals:', err)
  }
}

const submitAppeal = async () => {
  if (!appealForm.value.reason.trim()) {
    error.value = 'Please provide a reason for your appeal'
    return
  }

  if (appealForm.value.reason.length > 1000) {
    error.value = 'Appeal reason must be 1000 characters or less'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    const appealData = {
      fine: props.fineId,
      reason: appealForm.value.reason,
      supporting_evidence: appealForm.value.supporting_evidence || undefined
    }

    const response = await finesAPI.createAppeal(appealData)
    
    emit('success', response.data)
    
    // Reset form
    appealForm.value = {
      reason: '',
      supporting_evidence: '',
      fine: props.fineId
    }
    attachments.value = []
    
    // Reload appeals
    await loadExistingAppeals()
  } catch (err) {
    error.value = err.response?.data?.detail || 
                  err.response?.data?.message || 
                  'Failed to submit appeal. Please try again.'
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadExistingAppeals()
})
</script>

<style scoped>
.fine-appeal {
  width: 100%;
}
</style>

