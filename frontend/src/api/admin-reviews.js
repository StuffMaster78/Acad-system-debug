import apiClient from './client'

export default {
  // Review Moderation Dashboard
  getDashboard: () => apiClient.get('/admin-management/reviews/dashboard/dashboard/'),
  getAnalytics: (params) => apiClient.get('/admin-management/reviews/dashboard/analytics/', { params }),
  getPendingReviews: (params) => apiClient.get('/admin-management/reviews/dashboard/pending/', { params }),
  getModerationQueue: (params) => apiClient.get('/admin-management/reviews/moderation-queue/', { params }),
  approveReview: (reviewType, reviewId, moderationNotes = '') => apiClient.post(`/admin-management/reviews/approve/`, { review_type: reviewType, review_id: reviewId, moderation_notes: moderationNotes }),
  rejectReview: (reviewType, reviewId, reason, moderationNotes = '') => apiClient.post(`/admin-management/reviews/reject/`, { review_type: reviewType, review_id: reviewId, reason, moderation_notes: moderationNotes }),
  flagReview: (reviewType, reviewId, reason, moderationNotes = '') => apiClient.post(`/admin-management/reviews/flag/`, { review_type: reviewType, review_id: reviewId, reason, moderation_notes: moderationNotes }),
  shadowReview: (reviewType, reviewId, reason = '', moderationNotes = '') => apiClient.post(`/admin-management/reviews/shadow/`, { review_type: reviewType, review_id: reviewId, reason, moderation_notes: moderationNotes }),
  getSpamDetection: () => apiClient.get('/admin-management/reviews/spam-detection/'),
  bulkApprove: (reviewType, reviewIds, moderationNotes = '') => apiClient.post('/admin-management/reviews/bulk-approve/', { review_type: reviewType, review_ids: reviewIds, moderation_notes: moderationNotes }),
  bulkReject: (reviewType, reviewIds, reason, moderationNotes = '') => apiClient.post('/admin-management/reviews/bulk-reject/', { review_type: reviewType, review_ids: reviewIds, reason, moderation_notes: moderationNotes }),
  getModerationHistory: (reviewType, reviewId, days = 30) => apiClient.get('/admin-management/reviews/moderation-history/', { params: { review_type: reviewType, review_id: reviewId, days } }),
  list: (params) => apiClient.get('/admin-management/reviews/', { params }),
  get: (id) => apiClient.get(`/admin-management/reviews/${id}/`),
}

