import apiClient from './client'

export default {
  // Discounts
  list: (params) => apiClient.get('/discounts/discounts/', { params }),
  get: (id) => apiClient.get(`/discounts/discounts/${id}/`),
  create: (data) => apiClient.post('/discounts/discounts/', data),
  update: (id, data) => apiClient.patch(`/discounts/discounts/${id}/`, data),
  delete: (id) => apiClient.delete(`/discounts/discounts/${id}/`),
  
  // Discount Usage
  listUsage: (params) => apiClient.get('/discounts/discount-usage/', { params }),
  getUsage: (id) => apiClient.get(`/discounts/discount-usage/${id}/`),
  
  // Discount Stacking Rules
  listStackingRules: (params) => apiClient.get('/discounts/discount-stacking-rules/', { params }),
  getStackingRule: (id) => apiClient.get(`/discounts/discount-stacking-rules/${id}/`),
  createStackingRule: (data) => apiClient.post('/discounts/discount-stacking-rules/', data),
  updateStackingRule: (id, data) => apiClient.patch(`/discounts/discount-stacking-rules/${id}/`, data),
  deleteStackingRule: (id) => apiClient.delete(`/discounts/discount-stacking-rules/${id}/`),
  
  // Promotional Campaigns
  listCampaigns: (params) => apiClient.get('/discounts/promotional-campaigns/', { params }),
  getCampaign: (id) => apiClient.get(`/discounts/promotional-campaigns/${id}/`),
  createCampaign: (data) => apiClient.post('/discounts/promotional-campaigns/', data),
  updateCampaign: (id, data) => apiClient.patch(`/discounts/promotional-campaigns/${id}/`, data),
  deleteCampaign: (id) => apiClient.delete(`/discounts/promotional-campaigns/${id}/`),
  
  // Seasonal Events
  listEvents: (params) => apiClient.get('/discounts/seasonal-events/', { params }),
  getEvent: (id) => apiClient.get(`/discounts/seasonal-events/${id}/`),
  createEvent: (data) => apiClient.post('/discounts/seasonal-events/', data),
  updateEvent: (id, data) => apiClient.patch(`/discounts/seasonal-events/${id}/`, data),
  deleteEvent: (id) => apiClient.delete(`/discounts/seasonal-events/${id}/`),
  
  // Discount Actions
  validate: (code, params = {}) => apiClient.post('/discounts/discounts/validate/', { code, ...params }),
  apply: (orderId, code) => apiClient.post(`/discounts/discounts/apply/`, { order_id: orderId, code }),
  remove: (orderId) => apiClient.post(`/discounts/discounts/remove/`, { order_id: orderId }),
  preview: (orderId, code) => apiClient.get(`/discounts/discounts/preview/`, { params: { order_id: orderId, code } }),
  
  // Analytics
  getAnalytics: (type) => apiClient.get(`/discounts/discounts/analytics/`, { params: { type } }),
  getOverallStats: () => apiClient.get(`/discounts/discounts/analytics/`, { params: { type: 'stats' } }),
  getTopUsed: () => apiClient.get(`/discounts/discounts/analytics/`, { params: { type: 'top-used' } }),
  getEventsBreakdown: () => apiClient.get(`/discounts/discounts/analytics/`, { params: { type: 'events-breakdown' } }),
}
