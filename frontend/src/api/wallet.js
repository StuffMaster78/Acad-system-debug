import apiClient from './client'

export default {
  // Client wallet endpoints
  getWallet: () => apiClient.get('/wallet/api/client-wallet/my_wallet/'),
  getBalance: () => apiClient.get('/wallet/api/client-wallet/my_wallet/'),
  getTransactions: async (params = {}) => {
    // First get wallet to get wallet ID, then get transactions
    try {
      const walletRes = await apiClient.get('/wallet/api/client-wallet/my_wallet/')
      const walletId = walletRes.data.wallet?.id || walletRes.data.id
      if (walletId) {
        return apiClient.get(`/wallet/api/client-wallet/${walletId}/transactions/`, { params })
      }
      // Fallback: return transactions from my_wallet if available
      return { data: { results: walletRes.data.transactions || [], count: walletRes.data.transactions?.length || 0 } }
    } catch (e) {
      console.error('Failed to get transactions:', e)
      return { data: { results: [], count: 0 } }
    }
  },
  topUp: (amount, description) => apiClient.post('/wallet/api/client-wallet/top_up/', { amount, description }),
  convertLoyaltyPoints: () => apiClient.post('/wallet/api/client-wallet/convert_my_loyalty_points/'),
  
  // Admin wallet management endpoints
  admin: {
    listWallets: (params) => apiClient.get('/wallet/api/admin/wallets/', { params }),
    getWallet: (id) => apiClient.get(`/wallet/api/admin/wallets/${id}/`),
    adjustWallet: (id, data) => apiClient.post(`/wallet/api/admin/wallets/${id}/adjust/`, data),
    // Writer wallet endpoints
    listWriterWallets: (params) => apiClient.get('/writer-wallet/writer-wallets/', { params }),
    getWriterWallet: (id) => apiClient.get(`/writer-wallet/writer-wallets/${id}/`),
    adjustWriterWallet: (id, data) => apiClient.post(`/writer-wallet/writer-wallets/${id}/adjust/`, data),
    getWriterTransactions: (id) => apiClient.get(`/writer-wallet/writer-wallets/${id}/transactions/`),
  },
}

