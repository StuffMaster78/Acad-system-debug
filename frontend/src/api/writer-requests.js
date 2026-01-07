import apiClient from './client'

const writerRequestsAPI = {
  // Get all writer requests for an order
  getRequests(orderId) {
    return apiClient.get(`/orders/writer-request/?order=${orderId}`)
  },

  // Create a new writer request
  createRequest(data) {
    return apiClient.post('/orders/writer-request/create/', data)
  },

  // Client responds to a request (accept, decline, counteroffer)
  clientRespond(requestId, data) {
    return apiClient.post(`/orders/writer-request/${requestId}/client-respond/`, data)
  },

  // Get pricing preview for a request
  getPricingPreview(params) {
    return apiClient.get('/orders/writer-request/pricing-preview/', { params })
  }
}

export default writerRequestsAPI

