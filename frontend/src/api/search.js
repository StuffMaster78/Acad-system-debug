import apiClient from './client'

export default {
  // Unified search across all entity types
  search: (query, params = {}) => {
    const searchParams = {
      q: query,
      ...params
    }
    return apiClient.get('/admin-management/unified-search/search/', { params: searchParams })
  },
  
  // Search specific entity types
  searchOrders: (query, limit = 10) => {
    return apiClient.get('/admin-management/unified-search/search/', {
      params: { q: query, types: 'orders', limit }
    })
  },
  
  searchUsers: (query, limit = 10) => {
    return apiClient.get('/admin-management/unified-search/search/', {
      params: { q: query, types: 'users', limit }
    })
  },
  
  searchPayments: (query, limit = 10) => {
    return apiClient.get('/admin-management/unified-search/search/', {
      params: { q: query, types: 'payments', limit }
    })
  },
  
  searchMessages: (query, limit = 10) => {
    return apiClient.get('/admin-management/unified-search/search/', {
      params: { q: query, types: 'messages', limit }
    })
  },
}

