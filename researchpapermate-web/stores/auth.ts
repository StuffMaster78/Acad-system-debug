import { defineStore } from 'pinia'

interface LoginResponse {
  success: boolean
  mfa_required: boolean
  access_token?: string
  refresh_token?: string
}

interface RegisterResponse {
  success: boolean
  user_id: number
  message: string
}

interface MagicConfirmResponse {
  success: boolean
  mfa_required: boolean
  access_token?: string
  refresh_token?: string
}

export const useRpmAuthStore = defineStore('rpm-auth', {
  state: () => ({
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async login(email: string, password: string): Promise<{ access: string; refresh: string }> {
      this.loading = true
      this.error = null
      const api = useApi()
      try {
        const data = await api<LoginResponse>('/api/v1/auth/login/', {
          method: 'POST',
          body: { email, password },
        })
        if (data.mfa_required) throw new Error('mfa_required')
        if (!data.access_token) throw new Error('no_token')
        return { access: data.access_token, refresh: data.refresh_token ?? '' }
      } catch (err: any) {
        if (err.message === 'mfa_required') {
          this.error = 'Two-factor authentication is required. Please use your authenticator app.'
        } else {
          this.error = err.data?.detail || 'We could not sign you in with those details.'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async requestMagicLink(email: string): Promise<void> {
      const api = useApi()
      await api('/api/v1/auth/magic-link/request/', {
        method: 'POST',
        body: { email },
      })
    },

    async confirmMagicLink(token: string): Promise<{ access: string; refresh: string }> {
      this.loading = true
      this.error = null
      const api = useApi()
      try {
        const data = await api<MagicConfirmResponse>('/api/v1/auth/magic-link/confirm/', {
          method: 'POST',
          body: { token },
        })
        if (!data.access_token) throw new Error('no_token')
        return { access: data.access_token, refresh: data.refresh_token ?? '' }
      } catch (err: any) {
        this.error = 'This link is invalid or has already been used. Links expire after 15 minutes.'
        throw err
      } finally {
        this.loading = false
      }
    },

    async register(payload: {
      email: string
      password: string
      first_name: string
      last_name: string
    }): Promise<RegisterResponse> {
      this.loading = true
      this.error = null
      const api = useApi()
      try {
        return await api<RegisterResponse>('/api/v1/auth/register/', {
          method: 'POST',
          body: {
            email: payload.email,
            password: payload.password,
            username: payload.email,
            first_name: payload.first_name,
            last_name: payload.last_name,
          },
        })
      } catch (err: any) {
        const d = err.data || {}
        this.error =
          d.email?.[0] ||
          d.password?.[0] ||
          d.username?.[0] ||
          d.non_field_errors?.[0] ||
          d.detail ||
          'Registration failed. Please try again.'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
