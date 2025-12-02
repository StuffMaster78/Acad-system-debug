import apiClient from './client'

export default {
  // List invoices with filters
  list: (params) => apiClient.get('/order-payments/invoices/', { params }),
  
  // Get single invoice
  get: (id) => apiClient.get(`/order-payments/invoices/${id}/`),
  
  // Create invoice
  create: (data) => apiClient.post('/order-payments/invoices/', data),
  
  // Update invoice
  update: (id, data) => apiClient.put(`/order-payments/invoices/${id}/`, data),
  
  // Partial update
  patch: (id, data) => apiClient.patch(`/order-payments/invoices/${id}/`, data),
  
  // Delete invoice
  delete: (id) => apiClient.delete(`/order-payments/invoices/${id}/`),
  
  // Send invoice email
  sendEmail: (id) => apiClient.post(`/order-payments/invoices/${id}/send_email/`),
  
  // Regenerate payment link
  regeneratePaymentLink: (id) => apiClient.post(`/order-payments/invoices/${id}/regenerate_payment_link/`),
  
  // Get invoice statistics
  getStatistics: () => apiClient.get('/order-payments/invoices/stats/'),
  
  // Public payment endpoints (no auth required)
  getPaymentPage: (token) => apiClient.get(`/order-payments/invoices/pay/${token}/`),
  processPayment: (token, data) => apiClient.post(`/order-payments/invoices/pay/${token}/`, data),
}

