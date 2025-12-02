<template>
  <div class="login-alerts">
    <div class="header">
      <h1>Login Alert Preferences</h1>
      <p class="subtitle">Manage how you receive notifications about account login activity</p>
    </div>

    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading preferences...
    </div>

    <div v-else class="preferences-form">
      <div class="section">
        <h2>Email Notifications</h2>
        <div class="preference-item">
          <div class="preference-info">
            <label>Email on New Login</label>
            <p class="description">Receive an email notification when a new device or location logs into your account</p>
          </div>
          <div class="preference-control">
            <label class="toggle">
              <input
                type="checkbox"
                v-model="preferences.email_on_new_login"
                @change="savePreferences"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="preference-item">
          <div class="preference-info">
            <label>Email on Unusual Activity</label>
            <p class="description">Get notified when suspicious login activity is detected (e.g., new location, unusual time)</p>
          </div>
          <div class="preference-control">
            <label class="toggle">
              <input
                type="checkbox"
                v-model="preferences.email_on_unusual_activity"
                @change="savePreferences"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>SMS Notifications</h2>
        <div class="preference-item">
          <div class="preference-info">
            <label>SMS on New Login</label>
            <p class="description">Receive an SMS notification when a new device or location logs into your account</p>
          </div>
          <div class="preference-control">
            <label class="toggle">
              <input
                type="checkbox"
                v-model="preferences.sms_on_new_login"
                @change="savePreferences"
                :disabled="!preferences.phone_number"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div v-if="!preferences.phone_number" class="warning">
            <i class="fas fa-exclamation-triangle"></i>
            Phone number required for SMS notifications
          </div>
        </div>

        <div class="preference-item">
          <div class="preference-info">
            <label>SMS on Unusual Activity</label>
            <p class="description">Get notified via SMS when suspicious login activity is detected</p>
          </div>
          <div class="preference-control">
            <label class="toggle">
              <input
                type="checkbox"
                v-model="preferences.sms_on_unusual_activity"
                @change="savePreferences"
                :disabled="!preferences.phone_number"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>In-App Notifications</h2>
        <div class="preference-item">
          <div class="preference-info">
            <label>In-App Notification on New Login</label>
            <p class="description">Show a notification in the app when a new login occurs</p>
          </div>
          <div class="preference-control">
            <label class="toggle">
              <input
                type="checkbox"
                v-model="preferences.in_app_on_new_login"
                @change="savePreferences"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>Activity Thresholds</h2>
        <div class="preference-item">
          <div class="preference-info">
            <label>Unusual Activity Sensitivity</label>
            <p class="description">How sensitive the system should be when detecting unusual login activity</p>
          </div>
          <div class="preference-control">
            <select
              v-model="preferences.unusual_activity_sensitivity"
              @change="savePreferences"
              class="select-input"
            >
              <option value="low">Low - Only very suspicious activity</option>
              <option value="medium">Medium - Moderate suspicious activity</option>
              <option value="high">High - Any unusual activity</option>
            </select>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>Recent Login Activity</h2>
        <div v-if="recentLogins.length === 0" class="empty-state">
          <p>No recent login activity</p>
        </div>
        <div v-else class="login-history">
          <div
            v-for="login in recentLogins"
            :key="login.id"
            class="login-item"
            :class="{ 'unusual': login.is_unusual }"
          >
            <div class="login-icon">
              <i :class="getDeviceIcon(login.device_type)"></i>
            </div>
            <div class="login-details">
              <div class="login-header">
                <span class="device-name">{{ login.device_name || 'Unknown Device' }}</span>
                <span v-if="login.is_unusual" class="unusual-badge">
                  <i class="fas fa-exclamation-triangle"></i> Unusual
                </span>
              </div>
              <div class="login-meta">
                <span>{{ login.location || 'Unknown Location' }}</span>
                <span>{{ formatDate(login.login_time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { loginAlertsAPI } from '@/api'

const { showToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const preferences = ref({
  email_on_new_login: false,
  email_on_unusual_activity: false,
  sms_on_new_login: false,
  sms_on_unusual_activity: false,
  in_app_on_new_login: true,
  unusual_activity_sensitivity: 'medium',
  phone_number: null
})

const recentLogins = ref([])

const loadPreferences = async () => {
  loading.value = true
  try {
    const response = await loginAlertsAPI.getPreferences()
    if (response.data) {
      preferences.value = { ...preferences.value, ...response.data }
    }
  } catch (error) {
    // If no preferences exist, create default
    if (error.response?.status === 404) {
      await createDefaultPreferences()
    } else {
      showToast('Failed to load preferences', 'error')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const createDefaultPreferences = async () => {
  try {
    const response = await loginAlertsAPI.createPreferences(preferences.value)
    preferences.value = { ...preferences.value, ...response.data }
  } catch (error) {
    showToast('Failed to create preferences', 'error')
    console.error(error)
  }
}

const savePreferences = async () => {
  saving.value = true
  try {
    await loginAlertsAPI.updatePreferences(preferences.value)
    showToast('Preferences saved successfully', 'success')
  } catch (error) {
    showToast('Failed to save preferences', 'error')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const loadRecentLogins = async () => {
  try {
    // This would come from a separate API endpoint for login history
    // For now, we'll leave it empty
    recentLogins.value = []
  } catch (error) {
    console.error('Failed to load recent logins', error)
  }
}

const getDeviceIcon = (deviceType) => {
  const icons = {
    'desktop': 'fas fa-desktop',
    'mobile': 'fas fa-mobile-alt',
    'tablet': 'fas fa-tablet-alt',
    'unknown': 'fas fa-question-circle'
  }
  return icons[deviceType] || icons.unknown
}

const formatDate = (date) => {
  if (!date) return 'Unknown'
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadPreferences()
  loadRecentLogins()
})
</script>

<style scoped>
.login-alerts {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.subtitle {
  color: #6b7280;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.preferences-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.section h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.preference-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.preference-item:last-child {
  border-bottom: none;
}

.preference-info {
  flex: 1;
  margin-right: 1rem;
}

.preference-info label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #111827;
}

.description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.preference-control {
  display: flex;
  align-items: center;
}

.toggle {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #d1d5db;
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle input:checked + .toggle-slider {
  background-color: #3b82f6;
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.toggle input:disabled + .toggle-slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.warning {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  min-width: 250px;
}

.login-history {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.login-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.login-item.unusual {
  border-color: #fbbf24;
  background: #fffbeb;
}

.login-icon {
  font-size: 1.5rem;
  color: #6b7280;
  display: flex;
  align-items: center;
}

.login-details {
  flex: 1;
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.device-name {
  font-weight: 500;
  color: #111827;
}

.unusual-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: #fbbf24;
  color: #92400e;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.login-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}
</style>

