<template>
  <div class="password-change-container">
    <div class="password-change-card">
      <h1>Change Password</h1>
      <p class="subtitle">Update your account password</p>

      <form @submit.prevent="handlePasswordChange" class="password-form">
        <div class="form-group">
          <label for="current-password">Current Password</label>
          <div class="password-input">
            <input
              id="current-password"
              v-model="form.currentPassword"
              :type="showCurrentPassword ? 'text' : 'password'"
              required
              placeholder="Enter your current password"
              :disabled="loading"
            />
            <button
              type="button"
              @click="showCurrentPassword = !showCurrentPassword"
              class="password-toggle"
            >
              {{ showCurrentPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="new-password">New Password</label>
          <div class="password-input">
            <input
              id="new-password"
              v-model="form.newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              required
              placeholder="Enter your new password"
              :disabled="loading"
              @input="checkPasswordStrength"
            />
            <button
              type="button"
              @click="showNewPassword = !showNewPassword"
              class="password-toggle"
            >
              {{ showNewPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="form.newPassword" class="password-strength">
            <div class="strength-bar">
              <div
                :class="['strength-fill', passwordStrength.level]"
                :style="{ width: passwordStrength.percentage + '%' }"
              ></div>
            </div>
            <p class="strength-text">{{ passwordStrength.text }}</p>
            <ul class="password-requirements">
              <li :class="{ met: passwordStrength.checks.length >= 8 }">
                At least 8 characters
              </li>
              <li :class="{ met: passwordStrength.checks.hasUppercase }">
                Contains uppercase letter
              </li>
              <li :class="{ met: passwordStrength.checks.hasLowercase }">
                Contains lowercase letter
              </li>
              <li :class="{ met: passwordStrength.checks.hasNumber }">
                Contains number
              </li>
              <li :class="{ met: passwordStrength.checks.hasSpecial }">
                Contains special character
              </li>
            </ul>
          </div>
        </div>

        <div class="form-group">
          <label for="confirm-password">Confirm New Password</label>
          <div class="password-input">
            <input
              id="confirm-password"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              placeholder="Confirm your new password"
              :disabled="loading"
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="password-toggle"
            >
              {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="form.confirmPassword && form.newPassword" class="password-match">
            <span v-if="form.newPassword === form.confirmPassword" class="match-success">
              ✓ Passwords match
            </span>
            <span v-else class="match-error">
              ✗ Passwords do not match
            </span>
          </div>
        </div>

        <div v-if="error" class="error-message">
          <ul v-if="Array.isArray(error)">
            <li v-for="(msg, index) in error" :key="index">{{ msg }}</li>
          </ul>
          <span v-else>{{ error }}</span>
        </div>

        <div v-if="success" class="success-message">
          {{ success }}
        </div>

        <div class="form-actions">
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="btn btn-primary"
          >
            <span v-if="loading">Changing password...</span>
            <span v-else>Change Password</span>
          </button>
          <button
            type="button"
            @click="$router.back()"
            class="btn btn-secondary"
            :disabled="loading"
          >
            Cancel
          </button>
        </div>
      </form>

      <div class="security-tips">
        <h3>Security Tips</h3>
        <ul>
          <li>Use a unique password that you don't use elsewhere</li>
          <li>Make it at least 12 characters long for better security</li>
          <li>Consider using a password manager</li>
          <li>Change your password regularly</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'PasswordChange',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    return { router, authStore }
  },
  data() {
    return {
      loading: false,
      error: null,
      success: null,
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false,
      form: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      passwordStrength: {
        level: 'weak',
        percentage: 0,
        text: '',
        checks: {
          length: false,
          hasUppercase: false,
          hasLowercase: false,
          hasNumber: false,
          hasSpecial: false
        }
      }
    }
  },
  computed: {
    isFormValid() {
      return (
        this.form.currentPassword &&
        this.form.newPassword &&
        this.form.confirmPassword &&
        this.form.newPassword === this.form.confirmPassword &&
        this.passwordStrength.percentage >= 40 // At least medium strength
      )
    }
  },
  methods: {
    checkPasswordStrength() {
      const password = this.form.newPassword
      const checks = {
        length: password.length >= 8,
        hasUppercase: /[A-Z]/.test(password),
        hasLowercase: /[a-z]/.test(password),
        hasNumber: /[0-9]/.test(password),
        hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password)
      }

      const metCount = Object.values(checks).filter(Boolean).length
      const percentage = (metCount / 5) * 100

      let level = 'weak'
      let text = 'Weak password'

      if (percentage >= 80) {
        level = 'strong'
        text = 'Strong password'
      } else if (percentage >= 60) {
        level = 'medium'
        text = 'Medium strength'
      } else if (percentage >= 40) {
        level = 'weak'
        text = 'Weak password'
      }

      this.passwordStrength = {
        level,
        percentage,
        text,
        checks
      }
    },

    async handlePasswordChange() {
      this.loading = true
      this.error = null
      this.success = null

      try {
        const result = await this.authStore.changePassword(
          this.form.currentPassword,
          this.form.newPassword,
          this.form.confirmPassword
        )

        if (result.success) {
          this.success = result.message || 'Password changed successfully!'
          
          // Clear form
          this.form = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          }

          // Redirect after 2 seconds
          setTimeout(() => {
            this.router.push('/account/settings')
          }, 2000)
        } else {
          if (result.details && Array.isArray(result.details)) {
            this.error = result.details
          } else {
            this.error = result.error || 'Failed to change password. Please try again.'
          }
        }
      } catch (err) {
        this.error = err.message || 'Failed to change password. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.password-change-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  padding: 20px;
}

.password-change-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #333;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
}

.password-form {
  margin-bottom: 30px;
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

.password-input {
  position: relative;
}

.password-input input {
  width: 100%;
  padding: 12px;
  padding-right: 45px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.password-input input:focus {
  outline: none;
  border-color: #667eea;
}

.password-input input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
}

.password-strength {
  margin-top: 10px;
}

.strength-bar {
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s;
}

.strength-fill.weak {
  background: #dc3545;
}

.strength-fill.medium {
  background: #ffc107;
}

.strength-fill.strong {
  background: #28a745;
}

.strength-text {
  font-size: 12px;
  color: #666;
  margin: 0 0 8px 0;
}

.password-requirements {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 12px;
}

.password-requirements li {
  padding: 4px 0;
  color: #999;
  transition: color 0.3s;
}

.password-requirements li.met {
  color: #28a745;
}

.password-requirements li.met::before {
  content: '✓ ';
  color: #28a745;
}

.password-match {
  margin-top: 8px;
  font-size: 12px;
}

.match-success {
  color: #28a745;
}

.match-error {
  color: #dc3545;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.error-message ul {
  margin: 0;
  padding-left: 20px;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  flex: 1;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.security-tips {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #e0e0e0;
}

.security-tips h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.security-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.security-tips li {
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
  color: #666;
  font-size: 14px;
}

.security-tips li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #667eea;
}
</style>

