import apiClient from './client'

export default {
  // Get progress reports for an order
  getOrderProgress: (orderId) => {
    return apiClient.get(`/orders/progress/order/${orderId}/history/`)
  },
  
  // Get latest progress for an order
  getLatestProgress: (orderId) => {
    return apiClient.get(`/orders/progress/order/${orderId}/latest/`)
  },
  
  // Create a progress report
  createProgress: (data) => {
    return apiClient.post('/orders/progress/', data)
  },
  
  // List all progress reports (filtered by order_id query param)
  list: (params = {}) => {
    return apiClient.get('/orders/progress/', { params })
  },
  
  // Get a specific progress report
  get: (id) => {
    return apiClient.get(`/orders/progress/${id}/`)
  },
  
  // Withdraw a progress report (admin only)
  withdraw: (id, reason) => {
    return apiClient.post(`/orders/progress/${id}/withdraw/`, { reason })
  },
}

