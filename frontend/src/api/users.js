import apiClient from './client'

export default {
  list: (params) => apiClient.get('/users/users/', { params }),
  get: (id) => apiClient.get(`/users/${id}/`),
  getProfile: () => apiClient.get('/users/users/profile/'),
  updateProfile: (data) => apiClient.patch('/users/users/update_profile/', data),
  requestDeletion: (userId, reason) => apiClient.post(`/users/${userId}/request_deletion/`, { reason }),
  // Account deletion request (for current user)
  requestAccountDeletion: (reason) => apiClient.post('/users/account-deletion/request_deletion/', { reason }),
  // Admin/Superadmin: Get all deletion requests
  getDeletionRequests: (status = null) => {
    const params = status ? { status } : {}
    return apiClient.get('/users/account-deletion/list/', { params })
  },
  // Admin/Superadmin: Approve deletion request
  approveDeletionRequest: (requestId) => apiClient.post(`/users/account-deletion/${requestId}/approve_deletion/`),
  // Admin/Superadmin: Reject deletion request
  rejectDeletionRequest: (requestId, reason) => apiClient.post(`/users/account-deletion/${requestId}/reject_deletion/`, { reason }),
  // Admin/Superadmin: Reinstate account
  reinstateAccount: (requestId) => apiClient.post(`/users/account-deletion/${requestId}/reinstate_account/`),
  getUpdateRequests: () => apiClient.get('/users/account/profile-update-requests/'),
  update: (id, data) => apiClient.put(`/users/${id}/`, data),
  // Location info endpoint
  getLocationInfo: () => apiClient.get('/users/location-info/'),
  // Timezone update – called after login / on settings change
  updateTimezone: (timezone) =>
    apiClient.post('/users/users/update-timezone/', { timezone }),
  // Impersonation - generate token for user
  // Uses the new token-based impersonation endpoint
  generateImpersonationToken: (userId) => apiClient.post('/auth/impersonate/create_token/', { target_user: userId }),

  // User Edit Requests
  createEditRequest: (data) => apiClient.post('/users/edit-requests/request/', data),
  getMyEditRequests: (params) => apiClient.get('/users/edit-requests/my-requests/', { params }),
  cancelEditRequest: (requestId) => apiClient.post(`/users/edit-requests/${requestId}/cancel/`),
  getEditRequestDetail: (requestId) => apiClient.get(`/users/edit-requests/${requestId}/detail/`),
  
  // Admin: Edit Requests Management
  getPendingEditRequests: (params) => apiClient.get('/users/edit-requests/admin/pending/', { params }),
  getAllEditRequests: (params) => apiClient.get('/users/edit-requests/admin/all/', { params }),
  approveEditRequest: (requestId, notes) => apiClient.post(`/users/edit-requests/${requestId}/admin/approve/`, { notes }),
  rejectEditRequest: (requestId, reason) => apiClient.post(`/users/edit-requests/${requestId}/admin/reject/`, { reason }),
}

