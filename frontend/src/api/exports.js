import apiClient from './client'

export default {
  // Export orders
  exportOrders: (params = {}) => {
    return apiClient.get('/admin-management/exports/orders/', {
      params,
      responseType: 'blob'
    })
  },
  
  // Export payments
  exportPayments: (params = {}) => {
    return apiClient.get('/admin-management/exports/payments/', {
      params,
      responseType: 'blob'
    })
  },
  
  // Export users
  exportUsers: (params = {}) => {
    return apiClient.get('/admin-management/exports/users/', {
      params,
      responseType: 'blob'
    })
  },
  
  // Export financial report
  exportFinancialReport: (params = {}) => {
    return apiClient.get('/admin-management/exports/financial-report/', {
      params,
      responseType: 'blob'
    })
  },
}

