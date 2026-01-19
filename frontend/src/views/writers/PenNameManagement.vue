<template>
  <div class="min-h-dvh bg-gray-50 page-shell space-y-6">
    <div>
      <h1 class="page-title text-gray-900">Pen Name Management</h1>
      <p class="mt-2 text-gray-600">Manage your pen name and request changes</p>
    </div>

    <!-- Current Pen Name Display -->
    <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Current Pen Name</h2>
      
      <div class="mb-6 p-4 bg-gray-50 rounded-lg">
        <label class="block text-sm font-medium text-gray-700 mb-1">Your Current Pen Name</label>
        <p class="text-lg font-semibold text-gray-900">
          {{ currentPenName || 'Not set (using registration ID)' }}
        </p>
        <p v-if="registrationId" class="text-xs text-gray-500 mt-1">
          Registration ID: <span class="font-mono">{{ registrationId }}</span>
        </p>
      </div>

      <!-- How Clients See You -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 class="text-sm font-semibold text-blue-900 mb-2">How Clients See You</h3>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm text-blue-800">Display Name:</span>
            <span class="font-mono font-semibold text-blue-900">{{ displayName }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-blue-800">Registration ID:</span>
            <span class="font-mono text-blue-900">{{ registrationId }}</span>
          </div>
        </div>
        <p class="text-xs text-blue-700 mt-3">
          <strong>Privacy Note:</strong> Clients will only see your pen name (or registration ID) and will not have access to your real name, email, or other personal information.
        </p>
      </div>
    </div>

    <!-- Pen Name Update / Change Request -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-2">Update Pen Name</h2>
      <p class="text-sm text-gray-600 mb-4">
        {{ requiresApproval
          ? 'Your current pen name is already set. Changes require admin approval.'
          : 'Set your pen name once. If you need to change it later, you will submit a request.' }}
      </p>
      
      <form @submit.prevent="handlePenNameSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Pen Name</label>
          <input
            v-model="penNameForm.pen_name"
            type="text"
            maxlength="100"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your pen name (e.g., 'Alex Writer', 'Professional Pen')"
          />
          <p class="text-xs text-gray-500 mt-1">
            Maximum 100 characters. If left empty, clients will see your registration ID.
          </p>
        </div>

        <div v-if="requiresApproval">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Reason for Change <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="changeRequestForm.reason"
            rows="4"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Please provide a valid reason for changing your pen name..."
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">A valid reason is required for admin review</p>
        </div>

        <div class="flex flex-wrap justify-end gap-3">
          <button
            type="button"
            @click="resetPenNameForm"
            class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full sm:w-auto"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!canSubmitPenName"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed w-full sm:w-auto"
          >
            <span v-if="requiresApproval">{{ submittingRequest ? 'Submitting...' : 'Submit Change Request' }}</span>
            <span v-else>{{ savingPenName ? 'Saving...' : 'Save Pen Name' }}</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Change Request History -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Change Request History</h2>
      
      <div v-if="loadingHistory" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="changeRequests.length === 0" class="text-center py-8 text-gray-500">
        <p>No previous change requests</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="request in changeRequests"
          :key="request.id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
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
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import writerAPI from '@/api/writers'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'

const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()

const currentPenName = ref('')
const registrationId = ref('')
const writerProfile = ref(null)
const loading = ref(false)
const savingPenName = ref(false)
const submittingRequest = ref(false)
const changeRequests = ref([])
const loadingHistory = ref(false)

const penNameForm = ref({
  pen_name: ''
})

const changeRequestForm = ref({
  requested_pen_name: '',
  reason: ''
})

const displayName = computed(() => {
  return currentPenName.value || registrationId.value || 'N/A'
})

const requiresApproval = computed(() => {
  return !!currentPenName.value
})

const hasPenNameChange = computed(() => {
  const nextValue = (penNameForm.value.pen_name || '').trim()
  const currentValue = (currentPenName.value || '').trim()
  return nextValue !== currentValue
})

const canSubmitPenName = computed(() => {
  if (!hasPenNameChange.value) return false
  if (requiresApproval.value) {
    return !!changeRequestForm.value.reason.trim() && !submittingRequest.value
  }
  return !savingPenName.value
})

const loadProfile = async () => {
  loading.value = true
  try {
    // Try to get writer profile
    const response = await writerAPI.getProfile()
    writerProfile.value = response.data
    currentPenName.value = response.data.pen_name || ''
    registrationId.value = response.data.registration_id || ''
    penNameForm.value.pen_name = response.data.pen_name || ''
  } catch (error) {
    console.error('Failed to load profile:', error)
    // Fallback: try alternative endpoint
    try {
      const profileResponse = await apiClient.get('/users/users/profile/')
      const profileData = profileResponse.data
      
      if (profileData.pen_name !== undefined) {
        currentPenName.value = profileData.pen_name || ''
        registrationId.value = profileData.registration_id || ''
        penNameForm.value.pen_name = profileData.pen_name || ''
      }
    } catch (fallbackError) {
      console.error('Failed to load profile with fallback:', fallbackError)
    }
  } finally {
    loading.value = false
  }
}

const savePenName = async () => {
  savingPenName.value = true
  try {
    // Get writer profile ID
    const profileResponse = await apiClient.get('/users/users/profile/')
    const profileData = profileResponse.data
    
    let writerProfileId = null
    if (profileData.id) {
      writerProfileId = profileData.id
    } else if (profileData.user && profileData.user.writer_profile) {
      writerProfileId = profileData.user.writer_profile
    }
    
    if (!writerProfileId) {
      // Try using the writer API endpoint
      const writerResponse = await writerAPI.getProfile()
      writerProfileId = writerResponse.data.id
    }
    
    if (!writerProfileId) {
      throw new Error('Writer profile not found')
    }
    
    // Update writer profile pen_name
    const response = await apiClient.patch(`/writer-management/writers/${writerProfileId}/`, {
      pen_name: penNameForm.value.pen_name || null
    })
    
    writerProfile.value = response.data
    currentPenName.value = response.data.pen_name || ''
    showSuccess('Pen name updated successfully')
  } catch (error) {
    console.error('Failed to update pen name:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to update pen name'
    showError(errorMsg)
  } finally {
    savingPenName.value = false
  }
}

const handlePenNameSubmit = async () => {
  if (!hasPenNameChange.value) return
  if (requiresApproval.value) {
    changeRequestForm.value.requested_pen_name = (penNameForm.value.pen_name || '').trim()
    await submitChangeRequest()
  } else {
    await savePenName()
  }
}

const resetPenNameForm = () => {
  penNameForm.value.pen_name = currentPenName.value || ''
  changeRequestForm.value.reason = ''
}

const loadChangeRequestHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await writerAPI.getPenNameChangeRequests()
    changeRequests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load change request history:', error)
    changeRequests.value = []
  } finally {
    loadingHistory.value = false
  }
}

const submitChangeRequest = async () => {
  if (!changeRequestForm.value.requested_pen_name.trim() || !changeRequestForm.value.reason.trim()) {
    showError('Please fill in all required fields')
    return
  }

  submittingRequest.value = true
  try {
    await writerAPI.createPenNameChangeRequest({
      requested_pen_name: changeRequestForm.value.requested_pen_name.trim(),
      reason: changeRequestForm.value.reason.trim()
    })
    
    // Reset form and reload
    resetChangeRequestForm()
    await loadChangeRequestHistory()
    await loadProfile()
    
    showSuccess('Change request submitted successfully! It will be reviewed by an admin.')
  } catch (error) {
    console.error('Failed to submit change request:', error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to submit change request. Please try again.'
    showError(errorMsg)
  } finally {
    submittingRequest.value = false
  }
}

const resetChangeRequestForm = () => {
  changeRequestForm.value = {
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
  await Promise.all([loadProfile(), loadChangeRequestHistory()])
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

