/**
 * Subscription Management API
 * Handles client subscriptions to newsletters, blog posts, coupons, etc.
 */
import apiClient from './client'

export default {
  // List all subscriptions with status
  listAll: () => 
    apiClient.get('/users/subscriptions/list-all/'),
  
  // Subscribe to a subscription type
  subscribe: (subscriptionType, frequency = 'immediate', preferredChannels = []) => 
    apiClient.post('/users/subscriptions/subscribe/', {
      subscription_type: subscriptionType,
      frequency,
      preferred_channels: preferredChannels
    }),
  
  // Unsubscribe from a subscription type
  unsubscribe: (subscriptionType) => 
    apiClient.post('/users/subscriptions/unsubscribe/', {
      subscription_type: subscriptionType
    }),
  
  // Update subscription frequency
  updateFrequency: (subscriptionType, frequency) => 
    apiClient.put('/users/subscriptions/update-frequency/', {
      subscription_type: subscriptionType,
      frequency
    }),
  
  // Update preferred channels
  updateChannels: (subscriptionType, preferredChannels) => 
    apiClient.put('/users/subscriptions/update-channels/', {
      subscription_type: subscriptionType,
      preferred_channels: preferredChannels
    }),
  
  // Get subscription preferences
  getPreferences: () => 
    apiClient.get('/users/subscriptions/preferences/'),
  
  // Update subscription preferences
  updatePreferences: (data) => 
    apiClient.put('/users/subscriptions/update-preferences/', data),
  
  // Get phone reminder info
  getPhoneReminder: () => 
    apiClient.get('/users/account/phone-reminder/'),
}

