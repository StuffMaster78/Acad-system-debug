<template>
  <div class="account-settings">
    <div class="settings-header">
      <h1>Account Settings</h1>
      <p class="subtitle">Manage your account preferences and security</p>
    </div>

    <div class="settings-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="handleTabClick(tab)"
        :class="['tab', { active: activeTab === tab.id }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Profile Tab -->
    <div v-if="activeTab === 'profile'" class="tab-content">
      <div class="settings-section">
        <h2>Profile Information</h2>
        <div v-if="loadingProfile" class="loading-state">
          <p>Loading profile...</p>
        </div>
        <form v-else @submit.prevent="updateProfile" class="settings-form">
          <!-- Avatar Display -->
          <div class="form-group avatar-group" v-if="profileData.avatar_url">
            <label>Profile Picture</label>
            <div class="avatar-preview">
              <img :src="profileData.avatar_url" alt="Avatar" class="avatar-image" />
            </div>
          </div>

          <div class="form-group">
            <label>Email</label>
            <input
              v-model="profileForm.email"
              type="email"
              disabled
              class="disabled-input"
            />
            <p class="help-text">Email cannot be changed</p>
          </div>

          <div class="form-group">
            <label>Username</label>
            <input
              v-model="profileForm.username"
              type="text"
              :disabled="loading"
              required
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>First Name</label>
              <input
                v-model="profileForm.first_name"
                type="text"
                :disabled="loading"
              />
            </div>

            <div class="form-group">
              <label>Last Name</label>
              <input
                v-model="profileForm.last_name"
                type="text"
                :disabled="loading"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="flex items-center gap-1">
              Phone Number
              <Tooltip text="We use your phone number to coordinate order completion and send SMS notifications about important updates regarding your orders." />
            </label>
            <input
              v-model="profileForm.phone_number"
              type="tel"
              :disabled="loading"
              placeholder="+1234567890"
            />
          </div>

          <div class="form-group">
            <RichTextEditor
              v-model="profileForm.bio"
              label="Bio"
              :disabled="loading"
              placeholder="Tell us about yourself..."
              :max-length="500"
              :show-char-count="true"
              toolbar="basic"
              height="150px"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="flex items-center gap-1">
                Country
                <Tooltip text="Your country helps us provide localized services and comply with regional regulations." />
              </label>
              <input
                v-model="profileForm.country"
                type="text"
                :disabled="loading"
                placeholder="Country"
              />
            </div>

            <div class="form-group">
              <label class="flex items-center gap-1">
                State/Province
                <Tooltip text="Your state or province helps us provide more accurate regional support and services." />
              </label>
              <input
                v-model="profileForm.state"
                type="text"
                :disabled="loading"
                placeholder="State or Province"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="flex items-center gap-1">
              Timezone
              <Tooltip text="We use your timezone to show deadlines, schedules, and notifications in your local time." />
            </label>
            <input
              v-model="profileForm.timezone"
              type="text"
              :disabled="loading"
              placeholder="e.g. America/New_York"
            />
            <p class="help-text">
              Detected: <strong>{{ detectedTimezone || 'Unknown' }}</strong>
            </p>
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>

          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary"
          >
            <span v-if="loading">Saving...</span>
            <span v-else>Save Changes</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Security Tab -->
    <div v-if="activeTab === 'security'" class="tab-content">
      <!-- Password Change -->
      <div class="settings-section">
        <h2>Change Password</h2>
        <p class="section-description">Update your password to keep your account secure.</p>
        <router-link to="/account/password-change" class="btn btn-primary">
          Change Password
        </router-link>
      </div>

      <!-- 2FA -->
      <div class="settings-section">
        <h2>Two-Factor Authentication</h2>
        <div v-if="!twoFAEnabled" class="two-fa-setup">
          <p class="section-description">
            Add an extra layer of security to your account by enabling two-factor authentication.
          </p>
          <button @click="show2FASetup = true" class="btn btn-primary">
            Enable 2FA
          </button>
        </div>
        <div v-else class="two-fa-enabled">
          <div class="status-badge enabled">✓ 2FA Enabled</div>
          <p class="section-description">Two-factor authentication is enabled for your account.</p>
          <button @click="disable2FA" class="btn btn-secondary">
            Disable 2FA
          </button>
        </div>
      </div>

      <!-- Active Sessions -->
      <div class="settings-section">
        <h2>Active Sessions</h2>
        <p class="section-description">Manage your active login sessions.</p>
        <div v-if="loadingSessions" class="loading">Loading sessions...</div>
        <div v-else-if="sessions.length === 0" class="no-sessions">
          <p>No active sessions</p>
        </div>
        <div v-else class="sessions-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="session-item"
          >
            <div class="session-info">
              <div class="session-device">
                <strong>{{ session.device_name || 'Unknown Device' }}</strong>
                <span v-if="session.is_current" class="current-badge">Current</span>
              </div>
              <div class="session-details">
                <p>IP: {{ session.ip_address }}</p>
                <p>Last active: {{ formatDate(session.last_activity) }}</p>
              </div>
            </div>
            <button
              v-if="!session.is_current"
              @click="revokeSession(session.id)"
              class="btn btn-danger btn-sm"
            >
              Revoke
            </button>
          </div>
        </div>
        <button @click="revokeAllSessions" class="btn btn-secondary" style="margin-top: 20px;">
          Logout All Devices
        </button>
      </div>

      <!-- Account Deletion (Only for clients, writers, support, editors) -->
      <div v-if="canRequestDeletion" class="settings-section danger-zone">
        <h2>Delete Account</h2>
        <p class="section-description">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <div v-if="deletionRequested" class="deletion-status">
          <div class="status-badge warning">⚠️ Deletion Requested</div>
          <p class="section-description">
            Your account deletion request is pending. Your account will be deleted in 3 months.
          </p>
        </div>
        <div v-else>
          <button @click="showDeletionModal = true" class="btn btn-danger">
            Request Account Deletion
          </button>
        </div>
      </div>
    </div>

    <!-- Sessions Tab -->
    <div v-if="activeTab === 'sessions'" class="tab-content">
      <SessionManagement />
    </div>

    <!-- Update Requests Tab -->
    <div v-if="activeTab === 'update-requests'" class="tab-content">
      <ProfileUpdateRequests />
    </div>

    <!-- Account Deletion Modal -->
    <div v-if="showDeletionModal" class="modal-overlay" @click="showDeletionModal = false">
      <div class="modal-content" @click.stop>
        <h2>Request Account Deletion</h2>
        <p class="section-description">
          Are you sure you want to delete your account? This action cannot be undone.
          Your account will be frozen immediately and permanently deleted after 3 months.
        </p>
        <div class="form-group">
          <label>Reason for deletion (optional)</label>
          <textarea
            v-model="deletionReason"
            rows="4"
            placeholder="Please let us know why you're leaving..."
            class="w-full border rounded px-3 py-2"
          ></textarea>
        </div>
        <div v-if="deletionError" class="error-message">{{ deletionError }}</div>
        <div class="modal-actions">
          <button @click="confirmDeletion" class="btn btn-danger" :disabled="deleting">
            <span v-if="deleting">Processing...</span>
            <span v-else>Yes, Delete My Account</span>
          </button>
          <button @click="showDeletionModal = false" class="btn btn-secondary" :disabled="deleting">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- 2FA Setup Modal -->
    <div v-if="show2FASetup" class="modal-overlay" @click="show2FASetup = false">
      <div class="modal-content" @click.stop>
        <h2>Setup Two-Factor Authentication</h2>
        <div v-if="!twoFASecret" class="two-fa-setup-step">
          <p>Scan this QR code with your authenticator app:</p>
          <div class="qr-code">
            <img :src="twoFAQrCode" alt="2FA QR Code" />
          </div>
          <p class="backup-codes-label">Backup Codes (save these):</p>
          <div class="backup-codes">
            <code v-for="code in twoFABackupCodes" :key="code">{{ code }}</code>
          </div>
          <p class="help-text">Enter the 6-digit code from your app to verify:</p>
          <input
            v-model="twoFACode"
            type="text"
            maxlength="6"
            pattern="[0-9]{6}"
            placeholder="000000"
            class="code-input"
          />
          <div class="modal-actions">
            <button @click="verify2FASetup" class="btn btn-primary">
              Verify & Enable
            </button>
            <button @click="show2FASetup = false" class="btn btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import usersAPI from '@/api/users'
import SessionManagement from '@/components/settings/SessionManagement.vue'
import ProfileUpdateRequests from '@/components/profile/ProfileUpdateRequests.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import Tooltip from '@/components/common/Tooltip.vue'

export default {
  name: 'AccountSettings',
  components: {
    SessionManagement,
    ProfileUpdateRequests,
    RichTextEditor,
    Tooltip
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      activeTab: 'profile',
      tabs: [
        { id: 'profile', label: 'Profile' },
        { id: 'security', label: 'Security' },
        { id: 'privacy', label: 'Privacy', route: '/account/privacy' },
        { id: 'security-activity', label: 'Security Activity', route: '/account/security' },
        { id: 'sessions', label: 'Sessions' },
        { id: 'update-requests', label: 'Update Requests' }
      ],
      loading: false,
      loadingProfile: false,
      loadingSessions: false,
      error: null,
      success: null,
      profileData: {},
      profileForm: {
        email: '',
        username: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        bio: '',
        country: '',
        state: '',
        avatar: '',
        timezone: ''
      },
      detectedTimezone: null,
      twoFAEnabled: false,
      show2FASetup: false,
      twoFASecret: null,
      twoFAQrCode: null,
      twoFABackupCodes: [],
      twoFACode: '',
      sessions: [],
      showDeletionModal: false,
      deletionReason: '',
      deletionRequested: false,
      deleting: false,
      deletionError: null
    }
  },
  computed: {
    fullName() {
      if (this.profileForm.first_name && this.profileForm.last_name) {
        return `${this.profileForm.first_name} ${this.profileForm.last_name}`
      }
      return this.profileForm.first_name || this.profileForm.last_name || this.profileForm.username || ''
    },
    canRequestDeletion() {
      // Only clients, writers, support, and editors can request deletion
      const userRole = this.authStore.userRole
      return ['client', 'writer', 'support', 'editor'].includes(userRole)
    }
  },
  mounted() {
    this.loadProfile()
    this.loadSessions()
    this.check2FAStatus()
    this.checkDeletionStatus()
  },
  methods: {
    handleTabClick(tab) {
      if (tab.route) {
        // Navigate to separate page for Privacy and Security Activity
        this.$router.push(tab.route)
      } else {
        // Regular tab switch
        this.activeTab = tab.id
      }
    },
    async loadProfile() {
      this.loadingProfile = true
      this.error = null
      try {
        const response = await authApi.getCurrentUser()
        const data = response.data
        
        // Store full profile data for display
        this.profileData = data
        
        // Handle nested structure (for Client/Writer/Editor/Support profiles)
        // or flat structure (for Admin/Superadmin profiles)
        const userData = data.user || data
        
        // Populate form with available data
        this.profileForm = {
          email: userData.email || data.email || '',
          username: userData.username || data.username || '',
          first_name: userData.first_name || data.first_name || '',
          last_name: userData.last_name || data.last_name || '',
          phone_number: userData.phone_number || data.phone_number || '',
          bio: userData.bio || data.bio || '',
          country: userData.country || data.country || '',
          state: userData.state || data.state || '',
          avatar: userData.avatar || data.avatar || '',
          timezone: userData.timezone || data.timezone || ''
        }

        // Try to infer detected timezone from existing sources
        this.detectedTimezone =
          data.timezone ||
          userData.timezone ||
          localStorage.getItem('timezone') ||
          null
        
        // Update profileData with avatar_url if available
        const avatarUrl = userData.avatar_url || data.avatar_url
        if (avatarUrl) {
          // Ensure avatar URL is absolute if it's a relative path
          if (avatarUrl.startsWith('http') || avatarUrl.startsWith('//')) {
            this.profileData.avatar_url = avatarUrl
          } else {
            // Construct full URL for relative paths
            const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || 'http://localhost:8000'
            this.profileData.avatar_url = `${apiBaseUrl.replace('/api/v1', '')}${avatarUrl.startsWith('/') ? '' : '/'}${avatarUrl}`
          }
        }
      } catch (err) {
        console.error('Failed to load profile:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to load profile. Please try again.'
      } finally {
        this.loadingProfile = false
      }
    },

    async updateProfile() {
      this.loading = true
      this.error = null
      this.success = null

      try {
        // Prepare update data - only include fields that have values or are being cleared
        const updateData = {}
        
        if (this.profileForm.username) updateData.username = this.profileForm.username
        if (this.profileForm.first_name !== undefined) updateData.first_name = this.profileForm.first_name
        if (this.profileForm.last_name !== undefined) updateData.last_name = this.profileForm.last_name
        if (this.profileForm.phone_number !== undefined) updateData.phone_number = this.profileForm.phone_number || null
        if (this.profileForm.bio !== undefined) updateData.bio = this.profileForm.bio || null
        if (this.profileForm.country !== undefined) updateData.country = this.profileForm.country || null
        if (this.profileForm.state !== undefined) updateData.state = this.profileForm.state || null
        if (this.profileForm.timezone !== undefined) updateData.timezone = this.profileForm.timezone || null
        if (this.profileForm.avatar) updateData.avatar = this.profileForm.avatar
        
        const response = await authApi.updateProfile(updateData)
        
        // Check if response includes updated user data
        if (response.data && response.data.user) {
          this.profileData = response.data.user
        }
        
        this.success = response.data?.message || 'Profile updated successfully!'
        
        // Reload profile to get latest data from database
        await this.loadProfile()
        
        // Clear success message after 5 seconds
        setTimeout(() => {
          this.success = null
        }, 5000)
      } catch (err) {
        console.error('Profile update error:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    err.response?.data?.message ||
                    'Failed to update profile. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async loadSessions() {
      this.loadingSessions = true
      try {
        const response = await authApi.getActiveSessions()
        this.sessions = response.data.results || response.data || []
      } catch (err) {
        console.error('Failed to load sessions:', err)
      } finally {
        this.loadingSessions = false
      }
    },

    async revokeSession(sessionId) {
      try {
        // Implement session revocation endpoint call
        await this.loadSessions()
      } catch (err) {
        console.error('Failed to revoke session:', err)
      }
    },

    async revokeAllSessions() {
      if (!confirm('Are you sure you want to logout from all devices?')) {
        return
      }

      try {
        await authApi.logout(true)
        // Redirect to login
        this.$router.push('/login')
      } catch (err) {
        console.error('Failed to logout all devices:', err)
      }
    },

    async check2FAStatus() {
      // Check if 2FA is enabled (implement based on your API)
      // this.twoFAEnabled = ...
    },

    async setup2FA() {
      try {
        const response = await authApi.setup2FA()
        this.twoFASecret = response.data.secret
        this.twoFAQrCode = response.data.qr_code
        this.twoFABackupCodes = response.data.backup_codes || []
      } catch (err) {
        this.error = 'Failed to setup 2FA'
        console.error('2FA setup error:', err)
      }
    },

    async verify2FASetup() {
      try {
        await authApi.verify2FA(this.twoFACode)
        this.twoFAEnabled = true
        this.show2FASetup = false
        this.success = '2FA enabled successfully!'
      } catch (err) {
        this.error = 'Invalid code. Please try again.'
      }
    },

    async disable2FA() {
      if (!confirm('Are you sure you want to disable 2FA?')) {
        return
      }

      try {
        // Implement disable 2FA endpoint call
        this.twoFAEnabled = false
        this.success = '2FA disabled successfully!'
      } catch (err) {
        this.error = 'Failed to disable 2FA'
      }
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    async checkDeletionStatus() {
      // Check if user has a pending deletion request
      if (this.profileData && this.profileData.is_frozen) {
        this.deletionRequested = true
      }
    },

    async confirmDeletion() {
      if (!confirm('Are you absolutely sure? This action cannot be undone.')) {
        return
      }

      this.deleting = true
      this.deletionError = null

      try {
        const response = await usersAPI.requestAccountDeletion(this.deletionReason || 'No reason provided')
        this.success = response.data?.message || 'Account deletion requested successfully.'
        this.deletionRequested = true
        this.showDeletionModal = false
        this.deletionReason = ''
        
        // Reload profile to get updated status
        await this.loadProfile()
      } catch (err) {
        console.error('Deletion request error:', err)
        this.deletionError = err.response?.data?.error || 
                            err.response?.data?.detail || 
                            'Failed to request account deletion. Please try again.'
      } finally {
        this.deleting = false
      }
    }
  },
  watch: {
    show2FASetup(newVal) {
      if (newVal && !this.twoFASecret) {
        this.setup2FA()
      }
    }
  }
}
</script>

<style scoped>
.account-settings {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.settings-header {
  margin-bottom: 30px;
}

.settings-header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  color: #333;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.settings-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  transition: all 0.3s;
}

.tab.active {
  border-bottom-color: #667eea;
  color: #667eea;
  font-weight: 600;
}

.tab-content {
  padding: 20px 0;
}

.settings-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 20px;
}

.settings-section h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.section-description {
  color: #666;
  margin-bottom: 20px;
}

.settings-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.disabled-input {
  background: #f5f5f5;
  cursor: not-allowed;
}

.help-text {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.avatar-group {
  text-align: center;
}

.avatar-preview {
  margin: 10px 0;
}

.avatar-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #667eea;
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.loading-state p {
  margin: 0;
  font-size: 16px;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 10px;
}

.status-badge.enabled {
  background: #d4edda;
  color: #155724;
}

.sessions-list {
  margin-top: 20px;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 10px;
}

.session-device {
  display: flex;
  align-items: center;
  gap: 10px;
}

.current-badge {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
}

.session-details {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

.session-details p {
  margin: 2px 0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.qr-code {
  text-align: center;
  margin: 20px 0;
}

.qr-code img {
  max-width: 200px;
}

.backup-codes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 15px 0;
}

.backup-codes code {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  text-align: center;
}

.code-input {
  width: 100%;
  padding: 12px;
  text-align: center;
  font-size: 24px;
  letter-spacing: 8px;
  font-family: monospace;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin: 15px 0;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.modal-actions .btn {
  flex: 1;
}

.danger-zone {
  border-left: 4px solid #dc3545;
}

.danger-zone h2 {
  color: #dc3545;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.deletion-status {
  margin-top: 15px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .settings-form {
    max-width: 100%;
  }
}
</style>

