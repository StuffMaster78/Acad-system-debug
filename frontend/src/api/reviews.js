import apiClient from './client'

export default {
  // Website Reviews
  listWebsiteReviews: (params) => apiClient.get('/reviews/website-reviews/', { params }),
  getWebsiteReview: (id) => apiClient.get(`/reviews/website-reviews/${id}/`),
  moderateWebsiteReview: (id, data) => apiClient.post(`/reviews/website-reviews/${id}/moderate/`, data),
  disputeWebsiteReview: (id, data) => apiClient.post(`/reviews/website-reviews/${id}/dispute/`, data),
  deleteWebsiteReview: (id) => apiClient.delete(`/reviews/website-reviews/${id}/`),
  
  // Writer Reviews
  listWriterReviews: (params) => apiClient.get('/reviews/writer-reviews/', { params }),
  getWriterReview: (id) => apiClient.get(`/reviews/writer-reviews/${id}/`),
  moderateWriterReview: (id, data) => apiClient.post(`/reviews/writer-reviews/${id}/moderate/`, data),
  disputeWriterReview: (id, data) => apiClient.post(`/reviews/writer-reviews/${id}/dispute/`, data),
  deleteWriterReview: (id) => apiClient.delete(`/reviews/writer-reviews/${id}/`),
  
  // Order Reviews
  listOrderReviews: (params) => apiClient.get('/reviews/order-reviews/', { params }),
  getOrderReview: (id) => apiClient.get(`/reviews/order-reviews/${id}/`),
  create: (data) => apiClient.post('/reviews/order-reviews/', data),
  moderateOrderReview: (id, data) => apiClient.post(`/reviews/order-reviews/${id}/moderate/`, data),
  disputeOrderReview: (id, data) => apiClient.post(`/reviews/order-reviews/${id}/dispute/`, data),
  deleteOrderReview: (id) => apiClient.delete(`/reviews/order-reviews/${id}/`),
}

