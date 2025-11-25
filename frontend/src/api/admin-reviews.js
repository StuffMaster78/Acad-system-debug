import apiClient from './client'

export default {
  // Review Moderation Dashboard
  getModerationQueue: (params) => apiClient.get('/admin-management/reviews/moderation-queue/', { params }),
  approveReview: (reviewType, reviewId, moderationNotes = '') => apiClient.post(`/admin-management/reviews/approve/`, { review_type: reviewType, review_id: reviewId, moderation_notes: moderationNotes }),
  rejectReview: (reviewType, reviewId, reason, moderationNotes = '') => apiClient.post(`/admin-management/reviews/reject/`, { review_type: reviewType, review_id: reviewId, reason, moderation_notes: moderationNotes }),
  flagReview: (reviewType, reviewId, reason, moderationNotes = '') => apiClient.post(`/admin-management/reviews/flag/`, { review_type: reviewType, review_id: reviewId, reason, moderation_notes: moderationNotes }),
  shadowReview: (reviewType, reviewId, reason = '', moderationNotes = '') => apiClient.post(`/admin-management/reviews/shadow/`, { review_type: reviewType, review_id: reviewId, reason, moderation_notes: moderationNotes }),
  getAnalytics: () => apiClient.get('/admin-management/reviews/analytics/'),
  getSpamDetection: () => apiClient.get('/admin-management/reviews/spam-detection/'),
}

