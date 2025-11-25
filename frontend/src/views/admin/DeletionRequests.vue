<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Account Deletion Requests</h1>
        <p class="mt-2 text-gray-600">Review and manage account deletion requests from users</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending Requests</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending || 0 }}</p>
        <p class="text-xs text-yellow-600 mt-1">Awaiting review</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Confirmed</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.confirmed || 0 }}</p>
        <p class="text-xs text-green-600 mt-1">Accounts frozen</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Rejected</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.rejected || 0 }}</p>
        <p class="text-xs text-red-600 mt-1">Requests denied</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Filter by Status</label>
          <select v-model="statusFilter" @change="loadDeletionRequests" class="border rounded px-3 py-2">
            <option value="">All Requests</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div class="flex-1"></div>
        <button @click="loadDeletionRequests" class="btn btn-secondary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card p-8 text-center">
      <p class="text-gray-600">Loading deletion requests...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card p-4 bg-red-50 border border-red-200">
      <p class="text-red-700">{{ error }}</p>
      <button @click="loadDeletionRequests" class="mt-2 btn btn-secondary btn-sm">Try Again</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="deletionRequests.length === 0" class="card p-8 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-600 text-lg">No deletion requests found</p>
      <p class="text-gray-500 text-sm mt-2">All deletion requests have been processed</p>
    </div>

    <!-- Deletion Requests Table -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requested</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in deletionRequests" :key="request.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ request.user_full_name || request.user_username }}</div>
                  <div class="text-sm text-gray-500">{{ request.user_email }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                      :class="getRoleBadgeClass(request.user_role)">
                  {{ request.user_role }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 max-w-xs truncate" :title="request.reason">
                  {{ request.reason || 'No reason provided' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                      :class="getStatusBadgeClass(request.status)">
                  {{ request.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(request.request_time) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    v-if="request.status === 'pending'"
                    @click="approveRequest(request)"
                    :disabled="processing"
                    class="text-green-600 hover:text-green-900 disabled:opacity-50"
                    title="Approve deletion"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  <button
                    v-if="request.status === 'pending'"
                    @click="showRejectModal(request)"
                    :disabled="processing"
                    class="text-red-600 hover:text-red-900 disabled:opacity-50"
                    title="Reject deletion"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <button
                    v-if="request.status === 'confirmed'"
                    @click="reinstateAccount(request)"
                    :disabled="processing"
                    class="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                    title="Reinstate account"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModalFlag" class="modal-overlay" @click="showRejectModalFlag = false">
      <div class="modal-content" @click.stop>
        <h2 class="text-xl font-bold mb-4">Reject Deletion Request</h2>
        <p class="text-gray-600 mb-4">
          Are you sure you want to reject the deletion request for <strong>{{ selectedRequest?.user_email }}</strong>?
        </p>
        <div class="form-group">
          <label class="block text-sm font-medium mb-1">Rejection Reason (optional)</label>
          <textarea
            v-model="rejectionReason"
            rows="3"
            placeholder="Enter reason for rejection..."
            class="w-full border rounded px-3 py-2"
          ></textarea>
        </div>
        <div v-if="error" class="error-message mt-2">{{ error }}</div>
        <div class="modal-actions mt-4">
          <button @click="confirmReject" class="btn btn-danger" :disabled="processing">
            <span v-if="processing">Processing...</span>
            <span v-else>Reject Request</span>
          </button>
          <button @click="showRejectModalFlag = false" class="btn btn-secondary" :disabled="processing">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="card p-4 bg-green-50 border border-green-200">
      <p class="text-green-700">{{ successMessage }}</p>
    </div>
  </div>
</template>

<script>
import usersAPI from '@/api/users'

export default {
  name: 'DeletionRequests',
  data() {
    return {
      deletionRequests: [],
      loading: false,
      error: null,
      successMessage: null,
      statusFilter: '',
      processing: false,
      showRejectModalFlag: false,
      selectedRequest: null,
      rejectionReason: '',
      stats: {
        pending: 0,
        confirmed: 0,
        rejected: 0
      }
    }
  },
  mounted() {
    this.loadDeletionRequests()
  },
  methods: {
    async loadDeletionRequests() {
      this.loading = true
      this.error = null
      this.successMessage = null

      try {
        const response = await usersAPI.getDeletionRequests(this.statusFilter || null)
        this.deletionRequests = response.data.requests || []
        this.calculateStats()
      } catch (err) {
        console.error('Failed to load deletion requests:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to load deletion requests. Please try again.'
      } finally {
        this.loading = false
      }
    },

    calculateStats() {
      this.stats = {
        pending: this.deletionRequests.filter(r => r.status === 'pending').length,
        confirmed: this.deletionRequests.filter(r => r.status === 'confirmed').length,
        rejected: this.deletionRequests.filter(r => r.status === 'rejected').length
      }
    },

    async approveRequest(request) {
      if (!confirm(`Are you sure you want to approve the deletion request for ${request.user_email}? The account will be frozen immediately.`)) {
        return
      }

      this.processing = true
      this.error = null
      this.successMessage = null

      try {
        await usersAPI.approveDeletionRequest(request.id)
        this.successMessage = `Deletion request approved. Account for ${request.user_email} has been frozen.`
        await this.loadDeletionRequests()
      } catch (err) {
        console.error('Failed to approve deletion request:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to approve deletion request. Please try again.'
      } finally {
        this.processing = false
      }
    },

    showRejectModal(request) {
      this.selectedRequest = request
      this.rejectionReason = ''
      this.showRejectModalFlag = true
      this.error = null
    },

    async confirmReject() {
      if (!this.selectedRequest) return

      this.processing = true
      this.error = null
      this.successMessage = null

      try {
        await usersAPI.rejectDeletionRequest(
          this.selectedRequest.id,
          this.rejectionReason || 'No reason provided'
        )
        this.successMessage = `Deletion request rejected for ${this.selectedRequest.user_email}.`
        this.showRejectModalFlag = false
        this.selectedRequest = null
        this.rejectionReason = ''
        await this.loadDeletionRequests()
      } catch (err) {
        console.error('Failed to reject deletion request:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to reject deletion request. Please try again.'
      } finally {
        this.processing = false
      }
    },

    async reinstateAccount(request) {
      if (!confirm(`Are you sure you want to reinstate the account for ${request.user_email}? This will unfreeze the account and cancel the deletion.`)) {
        return
      }

      this.processing = true
      this.error = null
      this.successMessage = null

      try {
        await usersAPI.reinstateAccount(request.id)
        this.successMessage = `Account for ${request.user_email} has been reinstated.`
        await this.loadDeletionRequests()
      } catch (err) {
        console.error('Failed to reinstate account:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to reinstate account. Please try again.'
      } finally {
        this.processing = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    getStatusBadgeClass(status) {
      const classes = {
        pending: 'bg-yellow-100 text-yellow-800',
        confirmed: 'bg-green-100 text-green-800',
        rejected: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    },

    getRoleBadgeClass(role) {
      const classes = {
        client: 'bg-purple-100 text-purple-800',
        writer: 'bg-indigo-100 text-indigo-800',
        editor: 'bg-blue-100 text-blue-800',
        support: 'bg-teal-100 text-teal-800',
        admin: 'bg-orange-100 text-orange-800',
        superadmin: 'bg-red-100 text-red-800'
      }
      return classes[role] || 'bg-gray-100 text-gray-800'
    }
  }
}
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1rem;
  border: 1px solid #e5e7eb;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #4b5563;
  color: white;
}

.btn-secondary:hover {
  background-color: #374151;
}

.btn-danger {
  background-color: #dc2626;
  color: white;
}

.btn-danger:hover {
  background-color: #b91c1c;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 1.5rem;
  max-width: 28rem;
  width: 100%;
  margin: 0 1rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.form-group textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  padding: 0.5rem 0.75rem;
}

.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
</style>

