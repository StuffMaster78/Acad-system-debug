import apiClient from './client'

export default {
  // Pricing and discount endpoints
  getWriterLevels: (params) => apiClient.get('/pricing-configs/writer-level-options/', { params }),
  getAdditionalServices: (params) => apiClient.get('/pricing-configs/additional-services/', { params }),
  getPreferredWriterConfigs: (params) => apiClient.get('/pricing-configs/preferred-writer-configs/', { params }),
  // CRUD for Additional Services
  listAdditionalServices: (params) => apiClient.get('/pricing-configs/additional-services/', { params }),
  getAdditionalService: (id) => apiClient.get(`/pricing-configs/additional-services/${id}/`),
  createAdditionalService: (data) => apiClient.post('/pricing-configs/additional-services/', data),
  updateAdditionalService: (id, data) => apiClient.patch(`/pricing-configs/additional-services/${id}/`, data),
  deleteAdditionalService: (id) => apiClient.delete(`/pricing-configs/additional-services/${id}/`),
  // CRUD for Preferred Writer Configs
  listPreferredWriterConfigs: (params) => apiClient.get('/pricing-configs/preferred-writer-configs/', { params }),
  getPreferredWriterConfig: (id) => apiClient.get(`/pricing-configs/preferred-writer-configs/${id}/`),
  createPreferredWriterConfig: (data) => apiClient.post('/pricing-configs/preferred-writer-configs/', data),
  updatePreferredWriterConfig: (id, data) => apiClient.patch(`/pricing-configs/preferred-writer-configs/${id}/`, data),
  deletePreferredWriterConfig: (id) => apiClient.delete(`/pricing-configs/preferred-writer-configs/${id}/`),
  // CRUD for Writer Level Options (pricing)
  listWriterLevelOptions: (params) => apiClient.get('/pricing-configs/writer-level-options/', { params }),
  getWriterLevelOption: (id) => apiClient.get(`/pricing-configs/writer-level-options/${id}/`),
  createWriterLevelOption: (data) => apiClient.post('/pricing-configs/writer-level-options/', data),
  updateWriterLevelOption: (id, data) => apiClient.patch(`/pricing-configs/writer-level-options/${id}/`, data),
  deleteWriterLevelOption: (id) => apiClient.delete(`/pricing-configs/writer-level-options/${id}/`),
  // CRUD for Deadline Multipliers
  listDeadlineMultipliers: (params) => apiClient.get('/pricing-configs/deadline-multipliers/', { params }),
  getDeadlineMultiplier: (id) => apiClient.get(`/pricing-configs/deadline-multipliers/${id}/`),
  createDeadlineMultiplier: (data) => apiClient.post('/pricing-configs/deadline-multipliers/', data),
  updateDeadlineMultiplier: (id, data) => apiClient.patch(`/pricing-configs/deadline-multipliers/${id}/`, data),
  deleteDeadlineMultiplier: (id) => apiClient.delete(`/pricing-configs/deadline-multipliers/${id}/`),
  // Get preferred writers (writers the client has worked with before)
  getPreferredWriters: async () => {
    try {
      // Try to get from orders or writer management
      // For now, return empty - this would need a custom endpoint
      return { data: { results: [] } }
    } catch (e) {
      return { data: { results: [] } }
    }
  },
  validateDiscount: async (code, orderData) => {
    // Discount validation happens through the quote endpoint
    // For now, just return the code for use in quote
    return { data: { code, valid: true } }
  },
  estimatePrice: (data) => apiClient.post('/pricing-configs/estimate/', data),
}

