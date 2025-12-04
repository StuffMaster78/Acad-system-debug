import apiClient from './client'

export default {
  trackEvent(payload) {
    return apiClient.post('/analytics/content-events/', payload)
  },
}


