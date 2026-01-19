<template>
  <div class="min-h-dvh bg-gray-50 page-shell space-y-6">
    <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6">
      <h1 class="page-title text-gray-900 mb-2">Pen Name Change Request</h1>
      <p class="text-gray-600 mb-6">
        You can request to change your pen name. Once set, pen names cannot be deleted, only changed with admin approval.
      </p>

      <!-- Current Pen Name -->
      <div class="mb-6 p-4 bg-gray-50 rounded-lg">
        <label class="block text-sm font-medium text-gray-700 mb-1">Current Pen Name</label>
        <p class="text-lg font-semibold text-gray-900">
          {{ currentPenName || 'Not set (using registration ID)' }}
        </p>
      </div>

      <!-- Request Form -->
      <form @submit.prevent="submitRequest" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            New Pen Name <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.requested_pen_name"
            type="text"
            maxlength="100"
            required
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your new pen name"
          />
          <p class="text-xs text-gray-500 mt-1">Maximum 100 characters</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Reason for Change <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.reason"
            rows="4"
            required
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Please provide a valid reason for changing your pen name..."
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">A valid reason is required for admin review</p>
        </div>

        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="submitting">Submitting...</span>
            <span v-else>Submit Request</span>
          </button>
          <button
            type="button"
            @click="resetForm"
            class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Reset
          </button>
        </div>
      </form>
    </div>

    <!-- Request History -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Request History</h2>
      
      <div v-if="loadingHistory" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="requests.length === 0" class="text-center py-8 text-gray-500">
        <p>No previous requests</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="request in requests"
          :key="request.id"
          class="border border-gray-200 rounded-lg p-4"
        >
          <div class="flex items-start justify-between mb-3">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold text-gray-900">{{ request.requested_pen_name }}</span>
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    request.status === 'approved' ? 'bg-green-100 text-green-700' :
                    request.status === 'rejected' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  ]"
                >
                  {{ request.status.charAt(0).toUpperCase() + request.status.slice(1) }}
                </span>
              </div>
              <p class="text-sm text-gray-600">
                From: <span class="font-medium">{{ request.current_pen_name || 'Not set' }}</span>
              </p>
            </div>
            <span class="text-xs text-gray-500">
              {{ formatDate(request.requested_at) }}
            </span>
          </div>
          
          <div class="mb-2">
            <p class="text-sm font-medium text-gray-700 mb-1">Reason:</p>
            <p class="text-sm text-gray-600">{{ request.reason }}</p>
          </div>

          <div v-if="request.admin_notes" class="mt-3 pt-3 border-t border-gray-200">
            <p class="text-sm font-medium text-gray-700 mb-1">Admin Notes:</p>
            <p class="text-sm text-gray-600">{{ request.admin_notes }}</p>
          </div>

          <div v-if="request.reviewed_by" class="mt-2 text-xs text-gray-500">
            Reviewed by: {{ request.reviewer_username }} on {{ formatDate(request.reviewed_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import writerAPI from '@/api/writers'

const authStore = useAuthStore()

const currentPenName = ref('')
const form = ref({
  requested_pen_name: '',
  reason: ''
})
const submitting = ref(false)
const requests = ref([])
const loadingHistory = ref(false)

const loadCurrentPenName = async () => {
  try {
    // Load writer profile to get current pen name
    const response = await writerAPI.getProfile()
    currentPenName.value = response.data.pen_name || ''
  } catch (error) {
    console.error('Failed to load pen name:', error)
  }
}

const loadRequestHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await writerAPI.getPenNameChangeRequests()
    requests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load request history:', error)
    requests.value = []
  } finally {
    loadingHistory.value = false
  }
}

const submitRequest = async () => {
  if (!form.value.requested_pen_name.trim() || !form.value.reason.trim()) {
    return
  }

  submitting.value = true
  try {
    await writerAPI.createPenNameChangeRequest({
      requested_pen_name: form.value.requested_pen_name.trim(),
      reason: form.value.reason.trim()
    })
    
    // Reset form and reload
    resetForm()
    await loadRequestHistory()
    await loadCurrentPenName()
    
    alert('Request submitted successfully! It will be reviewed by an admin.')
  } catch (error) {
    console.error('Failed to submit request:', error)
    alert(error.response?.data?.error || 'Failed to submit request. Please try again.')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  form.value = {
    requested_pen_name: '',
    reason: ''
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  await Promise.all([loadCurrentPenName(), loadRequestHistory()])
})
</script>

