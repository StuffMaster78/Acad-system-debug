import apiClient from './client'

const reviewAggregationAPI = {
  // Website Reviews
  listWebsiteReviews(params = {}) {
    return apiClient.get('/reviews/website-reviews/', { params })
  },
  
  getWebsiteReview(id) {
    return apiClient.get(`/reviews/website-reviews/${id}/`)
  },
  
  moderateWebsiteReview(id, data) {
    return apiClient.post(`/reviews/website-reviews/${id}/moderate/`, data)
  },
  
  // Writer Reviews
  listWriterReviews(params = {}) {
    return apiClient.get('/reviews/writer-reviews/', { params })
  },
  
  getWriterReview(id) {
    return apiClient.get(`/reviews/writer-reviews/${id}/`)
  },
  
  moderateWriterReview(id, data) {
    return apiClient.post(`/reviews/writer-reviews/${id}/moderate/`, data)
  },
  
  // Order Reviews
  listOrderReviews(params = {}) {
    return apiClient.get('/reviews/order-reviews/', { params })
  },
  
  getOrderReview(id) {
    return apiClient.get(`/reviews/order-reviews/${id}/`)
  },
  
  moderateOrderReview(id, data) {
    return apiClient.post(`/reviews/order-reviews/${id}/moderate/`, data)
  },
  
  // Aggregation endpoints
  getAggregatedStats(type = 'all') {
    return apiClient.get(`/reviews/aggregation/stats/`, { params: { type } })
  },
  
  getReviewQueue(status = 'pending', type = 'all') {
    return apiClient.get(`/reviews/aggregation/queue/`, { params: { status, type } })
  },
}

export default reviewAggregationAPI

