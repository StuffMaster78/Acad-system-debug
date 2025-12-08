import apiClient from './client'

export default {
  list: (params) => apiClient.get('/order_payments_management/payments/', { params }),
  get: (id) => apiClient.get(`/order_payments_management/payments/${id}/`),
  getAllTransactions: (params) => apiClient.get('/order-payments/order-payments/all-transactions/', { params }),
  getClientPayments: (params) => apiClient.get('/order-payments/order-payments/client-payments/', { params }),
  getWriterPaymentsGrouped: (params) => apiClient.get('/writer-wallet/writer-payments/grouped/', { params }),
  getBatchBreakdown: (batchId) => apiClient.get(`/writer-wallet/payment-schedules/${batchId}/breakdown/`),
  getPaymentBreakdown: (paymentId) => apiClient.get(`/writer-wallet/scheduled-payments/${paymentId}/breakdown/`),
  
  // Payment Requests
  listPaymentRequests: (params) => apiClient.get('/writer-wallet/payment-requests/', { params }),
  getPaymentRequest: (id) => apiClient.get(`/writer-wallet/payment-requests/${id}/`),
  requestPayment: (data) => apiClient.post('/writer-wallet/payment-requests/request-payment/', data),
  approvePaymentRequest: (id, data = {}) => apiClient.post(`/writer-wallet/payment-requests/${id}/approve/`, data),
  rejectPaymentRequest: (id, data = {}) => apiClient.post(`/writer-wallet/payment-requests/${id}/reject/`, data),
  
  // Payment Actions
  initiate: (orderId, paymentData) => apiClient.post('/order_payments_management/order-payments/initiate/', {
    order_id: orderId,
    ...paymentData
  }),
  confirm: (paymentId, data = {}) => apiClient.post(`/order_payments_management/order-payments/${paymentId}/confirm/`, data),
  cancel: (paymentId) => apiClient.post(`/order_payments_management/order-payments/${paymentId}/cancel/`),
  refund: (paymentId, data = {}) => apiClient.post(`/order_payments_management/order-payments/${paymentId}/refund/`, data),
  
  // Payment Methods
  getPaymentMethods: () => apiClient.get('/order_payments_management/payment-methods/'),
  
  // Receipt Download
  downloadReceipt: (transactionId) => {
    return apiClient.get(`/order_payments_management/order-payments/receipt/${transactionId}/`, {
      responseType: 'blob'
    })
  },
}


