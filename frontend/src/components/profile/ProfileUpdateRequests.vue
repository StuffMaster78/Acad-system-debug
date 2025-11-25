<template>
  <div class="profile-update-requests">
    <div class="card p-6">
      <h2 class="text-2xl font-bold mb-4">Profile Update Requests</h2>
      <p class="text-gray-600 mb-6">
        Track the status of your profile update requests that require admin approval.
      </p>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="requests.length === 0" class="text-center py-12">
        <p class="text-gray-500">No pending profile update requests.</p>
        <p class="text-sm text-gray-400 mt-2">All profile updates that require approval will appear here.</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="request in requests"
          :key="request.id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900">
                Update Request #{{ request.id }}
              </h3>
              <p class="text-sm text-gray-600 mt-1">
                Submitted: {{ formatDate(request.created_at) }}
              </p>
            </div>
            <StatusBadge :status="request.status" />
          </div>

          <!-- Requested Changes -->
          <div v-if="request.requested_fields && Object.keys(request.requested_fields).length > 0" class="mt-4">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Requested Changes:</h4>
            <div class="bg-gray-50 rounded-lg p-3 space-y-2">
              <div
                v-for="(value, field) in request.requested_fields"
                :key="field"
                class="text-sm"
              >
                <span class="font-medium text-gray-700">{{ formatFieldName(field) }}:</span>
                <span class="text-gray-600 ml-2">{{ formatFieldValue(field, value) }}</span>
              </div>
            </div>
          </div>

          <!-- Admin Response -->
          <div v-if="request.admin_response" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 class="text-sm font-medium text-blue-900 mb-1">Admin Response:</h4>
            <p class="text-sm text-blue-800">{{ request.admin_response }}</p>
          </div>

          <!-- Rejection Reason -->
          <div v-if="request.status === 'rejected' && request.rejection_reason" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <h4 class="text-sm font-medium text-red-900 mb-1">Rejection Reason:</h4>
            <p class="text-sm text-red-800">{{ request.rejection_reason }}</p>
          </div>

          <!-- Timestamps -->
          <div class="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500 space-y-1">
            <div v-if="request.reviewed_at">
              Reviewed: {{ formatDate(request.reviewed_at) }}
            </div>
            <div v-if="request.reviewed_by">
              Reviewed by: {{ request.reviewed_by }}
            </div>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mt-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import usersAPI from '@/api/users'
import StatusBadge from '@/components/common/StatusBadge.vue'

const requests = ref([])
const loading = ref(true)
const error = ref('')

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFieldName = (field) => {
  return field
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const formatFieldValue = (field, value) => {
  if (value === null || value === undefined || value === '') {
    return '(empty)'
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  if (field.includes('date') || field.includes('time')) {
    return formatDate(value)
  }
  return String(value)
}

const loadRequests = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await usersAPI.getUpdateRequests()
    requests.value = Array.isArray(response.data) ? response.data : (response.data?.results || [])
  } catch (err) {
    console.error('Failed to load profile update requests:', err)
    error.value = err?.response?.data?.error || err?.response?.data?.message || 'Failed to load update requests. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRequests()
})
</script>

<style scoped>
.profile-update-requests {
  width: 100%;
}
</style>

