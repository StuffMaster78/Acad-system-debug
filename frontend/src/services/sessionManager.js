/**
 * Session Manager Service
 * Handles session timeout detection, warnings, and auto-logout
 */
import apiClient from '@/api/client'

class SessionManager {
  constructor() {
    this.checkInterval = null
    this.warningInterval = null
    this.idleTimer = null
    this.lastActivity = Date.now()
    this.warningCallback = null
    this.logoutCallback = null
    this.checkIntervalMs = 5 * 60 * 1000 // Check every 5 minutes (reduced frequency for JWT-based auth)
    this.idleTimeoutMs = 8 * 60 * 60 * 1000 // 8 hours (increased for JWT tokens which last 1 day)
    this.warningTimeMs = 30 * 60 * 1000 // 30 minutes before timeout
    this.isWarningShown = false
    this.extendCooldownMs = 2 * 60 * 1000 // Limit extend calls to once every 2 minutes
    this.lastExtendAt = 0
    this.extendTimeout = null
    this.extendInFlight = null
    this.removeActivityListeners = () => {}
  }

  /**
   * Start session monitoring
   */
  start(warningCallback, logoutCallback) {
    this.warningCallback = warningCallback
    this.logoutCallback = logoutCallback

    // Track user activity
    this.setupActivityTracking()

    // Check session status periodically
    this.checkInterval = setInterval(() => {
      this.checkSessionStatus()
    }, this.checkIntervalMs)

    // Initial check after a short delay (don't check immediately on mount)
    setTimeout(() => {
      this.checkSessionStatus()
    }, 10000) // Wait 10 seconds before first check
  }

  /**
   * Stop session monitoring
   */
  stop() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
    if (this.warningInterval) {
      clearInterval(this.warningInterval)
      this.warningInterval = null
    }
    if (this.idleTimer) {
      clearTimeout(this.idleTimer)
      this.idleTimer = null
    }
    if (this.extendTimeout) {
      clearTimeout(this.extendTimeout)
      this.extendTimeout = null
    }
    this.extendInFlight = null
    this.removeActivityListeners()
  }

  /**
   * Setup activity tracking (mouse, keyboard, scroll, touch)
   */
  setupActivityTracking() {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    const updateActivity = () => {
      this.lastActivity = Date.now()
      this.scheduleExtend()
    }

    events.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true })
    })

    this.removeActivityListeners = () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity)
      })
    }
  }

  scheduleExtend() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      return
    }
    const now = Date.now()
    const elapsed = now - this.lastExtendAt

    if (elapsed >= this.extendCooldownMs) {
      this.extendSession()
      return
    }

    if (this.extendTimeout) {
      return
    }

    const delay = Math.max(500, this.extendCooldownMs - elapsed)
    this.extendTimeout = setTimeout(() => {
      this.extendTimeout = null
      this.extendSession()
    }, delay)
  }

  /**
   * Check session status from backend
   * Note: For JWT-based auth, this is less critical since tokens handle expiration
   */
  async checkSessionStatus() {
    if (!localStorage.getItem('access_token')) {
      return
    }
    try {
      const response = await apiClient.get('/auth/session-management/status/')
      const data = response.data

      // Only enforce session timeout if explicitly marked as inactive
      // JWT tokens have their own expiration (1 day), so we're more lenient here
      if (data.is_active === false) {
        // Only logout if explicitly inactive AND no remaining time
        // This prevents false logouts from session management
        if (data.remaining_seconds <= 0) {
          this.handleLogout()
        }
        return
      }

      const remainingMs = data.remaining_seconds * 1000

      // Show warning if needed (only if very close to expiration)
      // For JWT tokens, we rely on token refresh, so warnings are less critical
      if (data.should_warn && !this.isWarningShown && remainingMs < 5 * 60 * 1000) {
        // Only warn if less than 5 minutes remaining
        this.showWarning(data.remaining_seconds)
      }

      // Auto logout only if time is actually expired (not just low)
      if (remainingMs <= 0) {
        this.handleLogout()
      }
    } catch (error) {
      // If 401, try token refresh first before logging out
      if (error.response?.status === 401) {
        // Don't immediately logout on 401 - let the token refresh interceptor handle it
        // Only logout if token refresh also fails
        console.debug('Session status check returned 401, token refresh will handle')
      } else {
        // Only log non-401 errors
        console.error('Session status check failed:', error)
      }
    }
  }

  /**
   * Show warning dialog
   */
  showWarning(remainingSeconds) {
    this.isWarningShown = true
    if (this.warningCallback) {
      this.warningCallback(remainingSeconds)
    }
  }

  /**
   * Extend session
   */
  async extendSession(force = false) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      return
    }

    if (this.extendTimeout) {
      clearTimeout(this.extendTimeout)
      this.extendTimeout = null
    }

    const now = Date.now()
    if (!force && this.extendInFlight) {
      return this.extendInFlight
    }

    if (!force && now - this.lastExtendAt < this.extendCooldownMs) {
      return
    }

    this.extendInFlight = apiClient.post('/auth/session-management/extend/', {})
      .then(() => {
        this.lastExtendAt = Date.now()
      this.isWarningShown = false
      })
      .catch((error) => {
        if (error.response?.status === 401) {
          this.handleLogout()
        } else if (error.response?.status === 400) {
          console.warn('Session extend rejected:', error.response?.data || error.message)
        } else {
      console.error('Failed to extend session:', error)
    }
      })
      .finally(() => {
        this.extendInFlight = null
      })

    return this.extendInFlight
  }

  /**
   * Handle logout
   */
  handleLogout() {
    this.stop()
    if (this.logoutCallback) {
      this.logoutCallback()
    }
  }

  /**
   * User clicked "Stay Logged In"
   */
  async stayLoggedIn() {
    await this.extendSession(true)
    this.isWarningShown = false
  }

  /**
   * User clicked "Logout Now"
   */
  async logoutNow() {
    try {
      await apiClient.post('/auth/session-management/logout/')
    } catch (error) {
      console.error('Logout failed:', error)
    }
    this.handleLogout()
  }
}

// Export singleton instance
export default new SessionManager()

