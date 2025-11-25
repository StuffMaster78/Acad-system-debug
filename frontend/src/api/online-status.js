import apiClient from './client'

export default {
  // Update current user's online status
  updateStatus: () => apiClient.post('/users/users/update_online_status/'),
  
  // Get online statuses for multiple users
  getStatuses: (userIds) => apiClient.get('/users/users/get_online_statuses/', {
    params: { user_ids: userIds.join(',') }
  }),
  
  // Get detailed online status for a specific user (includes timezone info)
  getUserStatus: (userId) => apiClient.get(`/users/users/${userId}/get_user_online_status/`),
}

