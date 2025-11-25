import apiClient from './client'

export default {
  // Payment Reminder Configs
  getReminderConfigs: (params) => apiClient.get('/order-payments/payment-reminder-configs/', { params }),
  getReminderConfig: (id) => apiClient.get(`/order-payments/payment-reminder-configs/${id}/`),
  createReminderConfig: (data) => apiClient.post('/order-payments/payment-reminder-configs/', data),
  updateReminderConfig: (id, data) => apiClient.put(`/order-payments/payment-reminder-configs/${id}/`, data),
  patchReminderConfig: (id, data) => apiClient.patch(`/order-payments/payment-reminder-configs/${id}/`, data),
  deleteReminderConfig: (id) => apiClient.delete(`/order-payments/payment-reminder-configs/${id}/`),

  // Payment Deletion Messages
  getDeletionMessages: (params) => apiClient.get('/order-payments/payment-deletion-messages/', { params }),
  getDeletionMessage: (id) => apiClient.get(`/order-payments/payment-deletion-messages/${id}/`),
  createDeletionMessage: (data) => apiClient.post('/order-payments/payment-deletion-messages/', data),
  updateDeletionMessage: (id, data) => apiClient.put(`/order-payments/payment-deletion-messages/${id}/`, data),
  patchDeletionMessage: (id, data) => apiClient.patch(`/order-payments/payment-deletion-messages/${id}/`, data),
  deleteDeletionMessage: (id) => apiClient.delete(`/order-payments/payment-deletion-messages/${id}/`),

  // Sent Reminders (read-only history)
  getSentReminders: (params) => apiClient.get('/order-payments/payment-reminders-sent/', { params }),
  getSentReminder: (id) => apiClient.get(`/order-payments/payment-reminders-sent/${id}/`),
}

