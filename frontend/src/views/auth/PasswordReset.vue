<template>
  <div class="password-reset-container">
    <div class="password-reset-card">
      <!-- Step 1: Request Reset -->
      <div v-if="step === 'request'" class="reset-step">
        <h1>Forgot Password?</h1>
        <p class="subtitle">Enter your email address and we'll send you a link to reset your password.</p>

        <form @submit.prevent="handleRequestReset" class="reset-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="requestForm.email"
              type="email"
              required
              placeholder="your@email.com"
              :disabled="loading"
            />
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <div v-if="success" class="success-message">
            {{ success }}
          </div>

          <button
            type="submit"
            :disabled="loading || !requestForm.email"
            class="btn btn-primary btn-block"
          >
            <span v-if="loading">Sending...</span>
            <span v-else>Send Reset Link</span>
          </button>
        </form>

        <div class="back-to-login">
          <router-link to="/login">← Back to login</router-link>
        </div>
      </div>

      <!-- Step 2: Reset Confirmation -->
      <div v-if="step === 'confirm'" class="reset-step">
        <h1>Reset Password</h1>
        <p class="subtitle">Enter your new password below.</p>

        <form @submit.prevent="handleConfirmReset" class="reset-form">
          <div class="form-group">
            <label for="new-password">New Password</label>
            <div class="password-input">
              <input
                id="new-password"
                v-model="resetForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Enter your new password"
                :disabled="loading"
                @input="checkPasswordStrength"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="password-toggle"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
            <div v-if="resetForm.password" class="password-strength">
              <div class="strength-bar">
                <div
                  :class="['strength-fill', passwordStrength.level]"
                  :style="{ width: passwordStrength.percentage + '%' }"
                ></div>
              </div>
              <p class="strength-text">{{ passwordStrength.text }}</p>
            </div>
          </div>

          <div class="form-group">
            <label for="confirm-password">Confirm New Password</label>
            <div class="password-input">
              <input
                id="confirm-password"
                v-model="resetForm.confirmPassword"
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
            <div v-if="resetForm.confirmPassword && resetForm.password" class="password-match">
              <span v-if="resetForm.password === resetForm.confirmPassword" class="match-success">
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

          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="btn btn-primary btn-block"
          >
            <span v-if="loading">Resetting password...</span>
            <span v-else>Reset Password</span>
          </button>
        </form>
      </div>

      <!-- Step 3: Success -->
      <div v-if="step === 'success'" class="reset-step success-step">
        <div class="success-icon">✓</div>
        <h1>Password Reset Successful!</h1>
        <p>Your password has been successfully reset. You can now log in with your new password.</p>
        <router-link to="/login" class="btn btn-primary btn-block">
          Go to Login
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api/auth' // Adjust import path
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'PasswordReset',
  setup() {
    const router = useRouter()
    const route = useRoute()
    return { router, route }
  },
  data() {
    return {
      step: 'request', // 'request', 'confirm', 'success'
      loading: false,
      error: null,
      success: null,
      showPassword: false,
      showConfirmPassword: false,
      requestForm: {
        email: ''
      },
      resetForm: {
        token: '',
        password: '',
        confirmPassword: ''
      },
      passwordStrength: {
        level: 'weak',
        percentage: 0,
        text: ''
      }
    }
  },
  computed: {
    isFormValid() {
      return (
        this.resetForm.password &&
        this.resetForm.confirmPassword &&
        this.resetForm.password === this.resetForm.confirmPassword &&
        this.passwordStrength.percentage >= 40
      )
    }
  },
  mounted() {
    // Check if token is in URL (from email link)
    const token = this.route.query.token
    if (token) {
      this.resetForm.token = token
      this.step = 'confirm'
    }
  },
  methods: {
    checkPasswordStrength() {
      const password = this.resetForm.password
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
        text
      }
    },

    async handleRequestReset() {
      this.loading = true
      this.error = null
      this.success = null

      try {
        await authApi.requestPasswordReset(this.requestForm.email)
        
        // Always show success message (security best practice)
        this.success = 'If that email exists, a password reset link has been sent. Please check your email.'
        
        // Clear form
        this.requestForm.email = ''
      } catch (err) {
        // Even on error, show generic success message
        this.success = 'If that email exists, a password reset link has been sent. Please check your email.'
      } finally {
        this.loading = false
      }
    },

    async handleConfirmReset() {
      this.loading = true
      this.error = null

      try {
        await authApi.confirmPasswordReset(
          this.resetForm.token,
          this.resetForm.password
        )

        this.step = 'success'
      } catch (err) {
        const errorData = err.response?.data
        
        if (errorData?.details && Array.isArray(errorData.details)) {
          this.error = errorData.details
        } else {
          this.error = errorData?.error || 
                      errorData?.detail || 
                      'Failed to reset password. The link may have expired. Please request a new one.'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.password-reset-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.password-reset-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
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

.reset-form {
  margin-bottom: 20px;
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
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.password-input {
  position: relative;
}

.password-input input {
  padding-right: 45px;
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
  margin: 0;
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

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
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

.btn-block {
  width: 100%;
}

.back-to-login {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.back-to-login a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.back-to-login a:hover {
  text-decoration: underline;
}

.success-step {
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: #28a745;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin: 0 auto 20px;
}

.success-step h1 {
  color: #28a745;
  margin-bottom: 15px;
}

.success-step p {
  color: #666;
  margin-bottom: 30px;
}
</style>

