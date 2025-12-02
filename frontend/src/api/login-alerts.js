/**
 * Login Alerts API
 * Manages user preferences for login notifications
 */
import api from './client'

export const loginAlertsAPI = {
  /**
   * Get current user's login alert preferences
   */
  getPreferences() {
    return api.get('/users/login-alerts/')
  },

  /**
   * Create or update login alert preferences
   * @param {Object} data - Preferences data
   * @param {boolean} data.notify_new_login - Notify on new login
   * @param {boolean} data.notify_new_device - Notify on new device
   * @param {boolean} data.notify_new_location - Notify on new location
   * @param {boolean} data.email_enabled - Enable email notifications
   * @param {boolean} data.push_enabled - Enable push notifications
   */
  updatePreferences(data) {
    return api.patch('/users/login-alerts/', data)
  },

  /**
   * Create login alert preferences
   */
  createPreferences(data) {
    return api.post('/users/login-alerts/', data)
  }
}

