<script setup lang="ts">
useSeoMeta({
  title: 'Sign in | Writers Creek',
  description: 'Sign in to Writers Creek. Writers and staff are routed to their portal automatically.',
  robots: 'noindex',
})

const config  = useRuntimeConfig()
const apiBase = computed(() => String(config.public.apiBase || '').replace(/\/+$/, ''))

const WRITER_PORTAL = computed(() =>
  String(config.public.appUrl  || 'https://app.writerscreek.com').replace(/\/+$/, '')
)
const STAFF_PORTAL  = computed(() =>
  String(config.public.staffUrl || 'https://admin.writerscreek.com').replace(/\/+$/, '')
)

const STAFF_ROLES = new Set(['admin', 'superadmin', 'editor', 'support'])

// ── step machine ─────────────────────────────────────────────────────────────
type Step = 'form' | 'mfa_wall' | 'redirecting' | 'error'
const step = ref<Step>('form')

const form     = reactive({ email: '', password: '' })
const error    = ref('')
const loading  = ref(false)

// ── submit password ───────────────────────────────────────────────────────────
async function submit() {
  error.value   = ''
  loading.value = true
  try {
    const res = await $fetch<{
      success: boolean
      mfa_required: boolean
      user_id?: number
      access_token?: string
      refresh_token?: string
    }>(`${apiBase.value}/api/v1/auth/login/`, {
      method: 'POST',
      credentials: 'include',
      body: { email: form.email, password: form.password },
    })

    if (res.mfa_required) {
      step.value = 'mfa_wall'
      return
    }

    if (!res.access_token || !res.refresh_token) {
      error.value = 'Unexpected response from the server. Please try again.'
      return
    }

    await routeToPortal(res.access_token, res.refresh_token)
  } catch (e: any) {
    const msg = e?.data?.detail || e?.data?.message
    error.value = typeof msg === 'string'
      ? msg
      : 'Invalid email or password.'
  } finally {
    loading.value = false
  }
}

// ── determine portal and redirect ─────────────────────────────────────────────
async function routeToPortal(access: string, refresh: string) {
  const me = await $fetch<{ role: string }>(`${apiBase.value}/api/v1/users/users/me/`, {
    headers: { Authorization: `Bearer ${access}` },
  })

  const base = STAFF_ROLES.has(me.role) ? STAFF_PORTAL.value : WRITER_PORTAL.value
  const dest  = `${base}/auth/adopt`

  step.value = 'redirecting'
  // Tokens go in the URL fragment — never sent to any server, cleared on arrival
  window.location.href = `${dest}#access=${encodeURIComponent(access)}&refresh=${encodeURIComponent(refresh)}`
}
</script>

<template>
  <div class="flex min-h-[calc(100vh-9rem)] items-center justify-center bg-slate-50 px-4 py-16">
    <div class="w-full max-w-md">

      <!-- ── Logo mark ──────────────────────────────────────────────────── -->
      <div class="mb-8 text-center">
        <NuxtLink href="/" class="inline-flex items-center gap-2.5">
          <svg width="32" height="32" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="28" height="28" rx="7" fill="#0f172a"/>
            <path d="M7 8l3.5 12L14 12l3.5 8L21 8" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-lg font-bold leading-none tracking-tight">
            <span class="text-slate-900">Writers</span><span class="text-brand-500">Creek</span>
          </span>
        </NuxtLink>
      </div>

      <!-- ── Card ───────────────────────────────────────────────────────── -->
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

        <!-- ── Password form ─────────────────────────────────────────────── -->
        <template v-if="step === 'form'">
          <div class="px-8 pb-8 pt-7">
            <h1 class="text-xl font-bold text-slate-900">Sign in</h1>
            <p class="mt-1 text-sm text-slate-500">Writers and staff are routed to their portal automatically.</p>

            <form class="mt-7 space-y-5" @submit.prevent="submit">
              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700" for="email">Email</label>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  required
                  autocomplete="email"
                  placeholder="you@example.com"
                  class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
                />
              </div>

              <div>
                <div class="mb-1.5 flex items-center justify-between">
                  <label class="text-sm font-semibold text-slate-700" for="password">Password</label>
                  <a
                    :href="`${WRITER_PORTAL}/auth/forgot-password`"
                    class="text-xs text-brand-600 hover:underline"
                  >Forgot password?</a>
                </div>
                <input
                  id="password"
                  v-model="form.password"
                  type="password"
                  required
                  autocomplete="current-password"
                  placeholder="••••••••"
                  class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
                />
              </div>

              <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {{ error }}
              </div>

              <button
                type="submit"
                :disabled="loading || !form.email || !form.password"
                class="w-full rounded-xl bg-brand-600 py-3.5 text-sm font-bold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Signing in…
                </span>
                <span v-else>Sign in →</span>
              </button>
            </form>
          </div>

          <div class="border-t border-slate-100 bg-slate-50 px-8 py-4 text-center">
            <p class="text-sm text-slate-500">
              Not a writer yet?
              <NuxtLink to="/apply" class="font-semibold text-brand-600 hover:underline">Apply to join →</NuxtLink>
            </p>
          </div>
        </template>

        <!-- ── MFA wall ───────────────────────────────────────────────────── -->
        <template v-else-if="step === 'mfa_wall'">
          <div class="px-8 pb-8 pt-7">
            <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
              <svg class="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h2 class="text-lg font-bold text-slate-900">Two-factor authentication required</h2>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">
              Your account has two-factor authentication enabled. Complete the sign-in from your portal, where the full verification flow is available.
            </p>
            <div class="mt-6 space-y-3">
              <a
                :href="`${WRITER_PORTAL}/auth/login`"
                class="flex w-full items-center justify-between rounded-xl border border-brand-200 bg-brand-50 px-5 py-3.5 text-sm font-semibold text-brand-700 transition-colors hover:bg-brand-100"
              >
                <span>Writer portal</span>
                <span class="text-xs font-normal text-brand-500">app.writerscreek.com →</span>
              </a>
              <a
                :href="`${STAFF_PORTAL}/auth/login`"
                class="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-5 py-3.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
              >
                <span>Staff portal</span>
                <span class="text-xs font-normal text-slate-400">admin.writerscreek.com →</span>
              </a>
            </div>
            <button
              class="mt-5 text-xs text-slate-400 hover:text-slate-600 hover:underline"
              @click="step = 'form'"
            >← Back</button>
          </div>
        </template>

        <!-- ── Redirecting ────────────────────────────────────────────────── -->
        <template v-else-if="step === 'redirecting'">
          <div class="px-8 py-16 text-center">
            <svg class="mx-auto h-10 w-10 animate-spin text-brand-400" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            <p class="mt-5 text-base font-semibold text-slate-900">Signing you in…</p>
            <p class="mt-1 text-sm text-slate-500">You'll be at your dashboard in a moment.</p>
          </div>
        </template>

      </div>

    </div>
  </div>
</template>
