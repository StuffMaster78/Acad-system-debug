import apiClient from './client'

export default {
  // Client Email Blacklist Management
  listBlacklistedEmails: (params) => apiClient.get('/client-management/blacklist/', { params }),
  addBlacklistedEmail: (email, reason) => apiClient.post('/client-management/blacklist/add/', { email, reason }),
  removeBlacklistedEmail: (email) => apiClient.delete('/client-management/blacklist/remove/', { data: { email } }),
  checkEmailBlacklisted: (email) => apiClient.get('/client-management/blacklist/', { params: { email } }),
}

