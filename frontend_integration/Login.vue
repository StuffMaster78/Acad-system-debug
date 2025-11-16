<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Welcome Back</h1>
      <p class="subtitle">Sign in to your account</p>

      <!-- Tabs for Login Methods -->
      <div class="login-tabs">
        <button
          @click="loginMethod = 'password'"
          :class="['tab', { active: loginMethod === 'password' }]"
        >
          Email & Password
        </button>
        <button
          @click="loginMethod = 'magic'"
          :class="['tab', { active: loginMethod === 'magic' }]"
        >
          Magic Link
        </button>
      </div>

      <!-- Email/Password Login -->
      <div v-if="loginMethod === 'password'" class="login-form">
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="loginForm.email"
              type="email"
              required
              placeholder="your@email.com"
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="password-input">
              <input
                id="password"
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Enter your password"
                :disabled="loading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="password-toggle"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
          </div>

          <div class="form-options">
            <label class="checkbox-label">
              <input
                v-model="loginForm.rememberMe"
                type="checkbox"
                :disabled="loading"
              />
              <span>Remember me</span>
            </label>
            <router-link to="/forgot-password" class="forgot-link">
              Forgot password?
            </router-link>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="btn btn-primary btn-block"
          >
            <span v-if="loading">Signing in...</span>
            <span v-else>Sign In</span>
          </button>
        </form>
      </div>

      <!-- Magic Link Login -->
      <div v-if="loginMethod === 'magic'" class="login-form">
        <div v-if="!magicLinkSent" class="magic-link-form">
          <form @submit.prevent="handleMagicLinkRequest">
            <div class="form-group">
              <label for="magic-email">Email</label>
              <input
                id="magic-email"
                v-model="magicForm.email"
                type="email"
                required
                placeholder="your@email.com"
                :disabled="loading"
              />
            </div>

            <div v-if="error" class="error-message">
              {{ error }}
            </div>

            <button
              type="submit"
              :disabled="loading || !magicForm.email"
              class="btn btn-primary btn-block"
            >
              <span v-if="loading">Sending...</span>
              <span v-else>Send Magic Link</span>
            </button>
          </form>
        </div>

        <div v-else class="magic-link-sent">
          <div class="success-icon">✉️</div>
          <h2>Check your email</h2>
          <p>We've sent a magic link to <strong>{{ magicForm.email }}</strong></p>
          <p class="help-text">Click the link in the email to sign in. The link will expire in 15 minutes.</p>
          <button
            @click="magicLinkSent = false"
            class="btn btn-secondary"
          >
            Use different email
          </button>
        </div>
      </div>

      <!-- 2FA Verification (if required) -->
      <div v-if="requires2FA" class="two-fa-form">
        <h2>Two-Factor Authentication</h2>
        <p>Enter the code from your authenticator app</p>
        <form @submit.prevent="handle2FAVerification">
          <div class="form-group">
            <label for="totp-code">6-digit code</label>
            <input
              id="totp-code"
              v-model="twoFAForm.code"
              type="text"
              maxlength="6"
              pattern="[0-9]{6}"
              required
              placeholder="000000"
              :disabled="loading"
              class="code-input"
            />
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading || twoFAForm.code.length !== 6"
            class="btn btn-primary btn-block"
          >
            <span v-if="loading">Verifying...</span>
            <span v-else>Verify</span>
          </button>

          <button
            type="button"
            @click="requires2FA = false"
            class="btn btn-link"
          >
            Back to login
          </button>
        </form>
      </div>

      <!-- Sign Up Link -->
      <div class="signup-link">
        <p>Don't have an account? <router-link to="/register">Sign up</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api/auth' // Adjust import path
import { useAuthStore } from '@/stores/auth' // Adjust import path
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    return {
      router,
      authStore
    }
  },
  data() {
    return {
      loginMethod: 'password', // 'password' or 'magic'
      loading: false,
      error: null,
      showPassword: false,
      requires2FA: false,
      magicLinkSent: false,
      sessionId: null,
      loginForm: {
        email: '',
        password: '',
        rememberMe: false
      },
      magicForm: {
        email: ''
      },
      twoFAForm: {
        code: ''
      }
    }
  },
  computed: {
    isFormValid() {
      return this.loginForm.email && this.loginForm.password
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.login(
          this.loginForm.email,
          this.loginForm.password,
          this.loginForm.rememberMe
        )

        // Check if 2FA is required
        if (response.data.requires_2fa) {
          this.requires2FA = true
          this.sessionId = response.data.session_id
          return
        }

        // Store tokens and user data
        await this.authStore.setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token
        })
        await this.authStore.setUser(response.data.user)

        // Redirect to dashboard or intended page
        const redirectTo = this.$route.query.redirect || '/dashboard'
        this.router.push(redirectTo)
      } catch (err) {
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Login failed. Please check your credentials.'
        
        // Handle account locked
        if (err.response?.status === 403) {
          this.error = 'Your account is locked. Please request an unlock.'
        }
      } finally {
        this.loading = false
      }
    },

    async handleMagicLinkRequest() {
      this.loading = true
      this.error = null

      try {
        await authApi.requestMagicLink(this.magicForm.email)
        this.magicLinkSent = true
      } catch (err) {
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to send magic link. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async handle2FAVerification() {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.verify2FA(this.twoFAForm.code)

        // Store tokens and user data
        await this.authStore.setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token
        })
        await this.authStore.setUser(response.data.user)

        // Redirect to dashboard
        const redirectTo = this.$route.query.redirect || '/dashboard'
        this.router.push(redirectTo)
      } catch (err) {
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Invalid code. Please try again.'
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    // Check if user is already logged in
    if (this.authStore.isAuthenticated) {
      this.router.push('/dashboard')
    }

    // Check for magic link token in URL (if redirected from email)
    const urlParams = new URLSearchParams(window.location.search)
    const magicToken = urlParams.get('token')
    if (magicToken) {
      this.verifyMagicLink(magicToken)
    }
  },
  methods: {
    // ... existing methods ...

    async verifyMagicLink(token) {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.verifyMagicLink(token)

        // Store tokens and user data
        await this.authStore.setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token
        })
        await this.authStore.setUser(response.data.user)

        // Redirect to dashboard
        this.router.push('/dashboard')
      } catch (err) {
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Invalid or expired magic link. Please request a new one.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
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

.login-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.3s;
}

.tab.active {
  border-bottom-color: #667eea;
  color: #667eea;
  font-weight: 600;
}

.login-form {
  margin-top: 20px;
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.forgot-link {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.forgot-link:hover {
  text-decoration: underline;
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

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-block {
  width: 100%;
}

.btn-link {
  background: none;
  color: #667eea;
  text-decoration: underline;
  padding: 8px;
  margin-top: 10px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.magic-link-sent {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.magic-link-sent h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.magic-link-sent p {
  color: #666;
  margin-bottom: 10px;
}

.help-text {
  font-size: 12px;
  color: #999;
}

.two-fa-form {
  margin-top: 20px;
}

.two-fa-form h2 {
  margin-bottom: 10px;
  color: #333;
}

.two-fa-form p {
  color: #666;
  margin-bottom: 20px;
}

.code-input {
  text-align: center;
  font-size: 24px;
  letter-spacing: 8px;
  font-family: monospace;
}

.signup-link {
  margin-top: 30px;
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.signup-link p {
  color: #666;
  font-size: 14px;
}

.signup-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>

