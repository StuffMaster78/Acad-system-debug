import apiClient from './client'

export default {
  // Referral Tracking
  listReferrals: (params) => apiClient.get('/admin-management/referrals/tracking/', { params }),
  getReferral: (id) => apiClient.get(`/admin-management/referrals/tracking/${id}/`),
  getReferralStatistics: () => apiClient.get('/admin-management/referrals/tracking/statistics/'),
  voidReferral: (id, data) => apiClient.post(`/admin-management/referrals/tracking/${id}/void-referral/`, data),
  
  // Abuse Flags
  listAbuseFlags: (params) => apiClient.get('/admin-management/referrals/abuse-flags/', { params }),
  getAbuseFlag: (id) => apiClient.get(`/admin-management/referrals/abuse-flags/${id}/`),
  getAbuseStatistics: () => apiClient.get('/admin-management/referrals/abuse-flags/statistics/'),
  reviewAbuseFlag: (id, data) => apiClient.post(`/admin-management/referrals/abuse-flags/${id}/review/`, data),
  markFalsePositive: (id) => apiClient.post(`/admin-management/referrals/abuse-flags/${id}/mark-false-positive/`),
  
  // Referral Codes
  listReferralCodes: (params) => apiClient.get('/admin-management/referrals/codes/', { params }),
  getReferralCodeStatistics: () => apiClient.get('/admin-management/referrals/codes/statistics/'),
}

