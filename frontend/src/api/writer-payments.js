import apiClient from './client'

export default {
  // Get grouped payments (bi-weekly/monthly)
  getGroupedPayments: (params) => apiClient.get('/writer-wallet/writer-payments/grouped/', { params }),
  
  // Get payment breakdown (for ScheduledWriterPayment)
  getPaymentBreakdown: (paymentId) => apiClient.get(`/writer-wallet/scheduled-payments/${paymentId}/breakdown/`),

  // Payment management endpoints
  moveToNextPeriod: (paymentId, data) => apiClient.post(`/writer-payments/payment-management/${paymentId}/move-to-next-period/`, data),
  
  adjustForOrderStatus: (paymentId, data) => apiClient.post(`/writer-payments/payment-management/${paymentId}/adjust-for-order-status/`, data),
  
  clearPayments: (data) => apiClient.post('/writer-payments/payment-management/clear-payments/', data),
  
  getPayoutRequests: (params) => apiClient.get('/writer-payments/payment-management/payout-requests/', { params }),
  
  approvePayout: (payoutId) => apiClient.post(`/writer-payments/payment-management/${payoutId}/approve-payout/`),
  
  getAdjustments: (params) => apiClient.get('/writer-payments/payment-management/adjustments/', { params }),
}
