import apiClient from './client'

export default {
  // Class Bundles
  listBundles: (params) => apiClient.get('/class-management/class-bundles/', { params }),
  getBundle: (id) => apiClient.get(`/class-management/class-bundles/${id}/`),
  createBundle: (data) => apiClient.post('/class-management/class-bundles/', data),
  updateBundle: (id, data) => apiClient.patch(`/class-management/class-bundles/${id}/`, data),
  deleteBundle: (id) => apiClient.delete(`/class-management/class-bundles/${id}/`),
  
  // Admin Manual Bundle Creation
  createManualBundle: (data) => apiClient.post('/class-management/class-bundles/create_manual/', data),
  
  // Bundle Actions
  payDeposit: (id, data) => apiClient.post(`/class-management/class-bundles/${id}/pay_deposit/`, data),
  configureInstallments: (id, data) => apiClient.post(`/class-management/class-bundles/${id}/configure_installments/`, data),
  assignWriter: (id, data) => apiClient.post(`/class-management/class-bundles/${id}/assign_writer/`, data),
  createThread: (id, data) => apiClient.post(`/class-management/class-bundles/${id}/create_thread/`, data),
  getThreads: (id) => apiClient.get(`/class-management/class-bundles/${id}/threads/`),
  createTicket: (id, data) => apiClient.post(`/class-management/class-bundles/${id}/create_ticket/`, data),
  
  // Class Purchases
  listPurchases: (params) => apiClient.get('/class-management/class-purchases/', { params }),
  getPurchase: (id) => apiClient.get(`/class-management/class-purchases/${id}/`),
  
  // Class Installments
  listInstallments: (params) => apiClient.get('/class-management/class-installments/', { params }),
  getInstallment: (id) => apiClient.get(`/class-management/class-installments/${id}/`),
  payInstallment: (id, data) => apiClient.post(`/class-management/class-installments/${id}/pay/`, data),
  
  // Bundle Configs
  listConfigs: (params) => apiClient.get('/class-management/class-bundle-configs/', { params }),
  getConfig: (id) => apiClient.get(`/class-management/class-bundle-configs/${id}/`),
  createConfig: (data) => apiClient.post('/class-management/class-bundle-configs/', data),
  updateConfig: (id, data) => apiClient.patch(`/class-management/class-bundle-configs/${id}/`, data),
  deleteConfig: (id) => apiClient.delete(`/class-management/class-bundle-configs/${id}/`),
}

