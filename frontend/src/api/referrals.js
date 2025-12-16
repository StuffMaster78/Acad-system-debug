import apiClient from './client'

export default {
  // Referral Bonus Configs
  listConfigs: (params) => apiClient.get('/referrals/referral-bonus-configs/', { params }),
  getConfig: (id) => apiClient.get(`/referrals/referral-bonus-configs/${id}/`),
  createConfig: (data) => apiClient.post('/referrals/referral-bonus-configs/', data),
  updateConfig: (id, data) => apiClient.patch(`/referrals/referral-bonus-configs/${id}/`, data),
  deleteConfig: (id) => apiClient.delete(`/referrals/referral-bonus-configs/${id}/`),
  // Referrals
  list: (params) => apiClient.get('/referrals/referrals/', { params }),
  get: (id) => apiClient.get(`/referrals/referrals/${id}/`),
  // Referral Codes
  listCodes: (params) => apiClient.get('/referrals/referral-codes/', { params }),
  getMyCode: () => apiClient.get('/referrals/referral-codes/my-code/'),
  generateCode: (websiteId) => apiClient.post('/referrals/referrals/generate-code/', { website: websiteId }),
  // Referral Stats
  getStats: (websiteId) => apiClient.get('/referrals/referrals/stats/', { params: { website: websiteId } }),
  // Manual referral by email
  referByEmail: (email, websiteId) => apiClient.post('/referrals/referrals/refer-by-email/', { email, website: websiteId }),
  // Admin endpoints
  getTopReferrers: (params) => apiClient.get('/referrals/referral-admin/top-referrers/', { params }),
  getTopEarners: (params) => apiClient.get('/referrals/referral-admin/top-earners/', { params }),
  getCompletedOrders: (params) => apiClient.get('/referrals/referral-admin/completed-orders/', { params }),
  creditBonus: (referralId) => apiClient.post('/referrals/referral-admin/credit-bonus/', { referral_id: referralId }),
  // Referral Bonus Decays
  listBonusDecays: (params) => apiClient.get('/referrals/referral-bonus-decays/', { params }),
}
