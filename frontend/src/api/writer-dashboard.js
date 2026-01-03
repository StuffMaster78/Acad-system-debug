import apiClient from './client'

export default {
  getMyProfile: () => apiClient.get('/writer-management/writers/my_profile/'),
  getOrders: (params) => apiClient.get('/orders/orders/', { params }),
  getPerformance: () => apiClient.get('/writer-management/writers/my_performance/'),
  getBadges: () => apiClient.get('/writer-management/badge-achievements/'),
  
  // Dashboard endpoints
  getEarnings: (days = 30) => apiClient.get('/writer-management/dashboard/earnings/', { params: { days } }),
  getPerformanceAnalytics: (days = 30) => apiClient.get('/writer-management/dashboard/performance/', { params: { days } }),
  getOrderQueue: () => apiClient.get('/writer-management/dashboard/queue/'),
  getAvailability: () => apiClient.get('/writer-management/dashboard/availability/'),
  updateAvailability: (data) => apiClient.post('/writer-management/dashboard/availability/', data),
  getBadgesAndAchievements: () => apiClient.get('/writer-management/dashboard/badges/'),
  getLevelAndRanking: () => apiClient.get('/writer-management/dashboard/level/'),
  getEstimatedEarnings: (params) => apiClient.get('/writer-management/dashboard/estimated-earnings/', { params }),
  getPayments: () => apiClient.get('/writer-management/dashboard/payments/'),
  getPaymentStatus: () => apiClient.get('/writer-management/dashboard/payment-status/'),
      getCalendar: (params) => apiClient.get('/writer-management/dashboard/calendar/', { params }),
      exportCalendarICS: async (params) => {
        try {
          const response = await apiClient.get('/writer-management/dashboard/calendar/export/', {
            params,
            responseType: 'blob'
          })
          
          // Create blob from response
          const blob = new Blob([response.data], { type: 'text/calendar;charset=utf-8' })
          const url = window.URL.createObjectURL(blob)
          
          // Create download link
          const link = document.createElement('a')
          link.href = url
          link.download = `writer_calendar_${new Date().toISOString().split('T')[0]}.ics`
          document.body.appendChild(link)
          link.click()
          
          // Cleanup
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        } catch (error) {
          console.error('Failed to export calendar:', error)
          throw error
        }
      },
      getWorkload: () => apiClient.get('/writer-management/dashboard/workload-capacity/'),
      getOrderRequests: () => 
        apiClient.get('/writer-management/dashboard/order-requests/'),
      getDashboardSummary: () => 
        apiClient.get('/writer-management/dashboard/summary/'),
      getCommunications: () => 
        apiClient.get('/writer-management/dashboard/communications/'),
      getPaymentInfo: () => 
        apiClient.get('/writer-management/dashboard/payment-info/'),
      getPaymentStatus: () =>
        apiClient.get('/writer-management/dashboard/payment-status/'),
      getEarningsBreakdown: (params) => 
        apiClient.get(
          '/writer-management/dashboard/earnings-breakdown/',
          { params }
        ),
      getOrderPriority: (orderId) =>
        apiClient.get(
          `/writer-management/dashboard/order-priority/${orderId}/`
        ),
      setOrderPriority: (orderId, data) =>
        apiClient.post(
          `/writer-management/dashboard/order-priority/${orderId}/`,
          data
        ),
      updateOrderPriority: (orderId, data) =>
        apiClient.patch(
          `/writer-management/dashboard/order-priority/${orderId}/`,
          data
        ),
      getOrderPriorities: () =>
        apiClient.get(
          '/writer-management/dashboard/order-priorities/'
        ),
      exportEarnings: async (params) => {
        try {
          const response = await apiClient.get(
            '/writer-management/dashboard/earnings-export/',
            { params, responseType: 'blob' }
          )
          
          // Create blob from response
          const blob = new Blob([response.data], { 
            type: 'text/csv;charset=utf-8' 
          })
          const url = window.URL.createObjectURL(blob)
          
          // Create download link
          const link = document.createElement('a')
          link.href = url
          const dateStr = new Date().toISOString().split('T')[0]
          link.download = `earnings_export_${dateStr}.csv`
          document.body.appendChild(link)
          link.click()
          
          // Cleanup
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
          
          return response
        } catch (error) {
          console.error('Failed to export earnings:', error)
          throw error
        }
      },
  
  getEarningsBreakdown: (params) => 
    apiClient.get('/writer-management/dashboard/earnings-breakdown/', { params }),
  
  exportEarnings: (params) => 
    apiClient.get('/writer-management/dashboard/earnings-export/', { 
      params,
      responseType: 'blob' 
    }),
  
  getOrderRequests: () => 
    apiClient.get('/writer-management/dashboard/order-requests/'),
}

