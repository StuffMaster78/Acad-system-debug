<script setup lang="ts">
definePageMeta({ ssr: false })

const portal = usePortalStore()
const auth = useRpmAuthStore()
const app = useAppUrl()

type Tab = 'password' | 'magic'
const tab = ref<Tab>('password')

const form = reactive({ email: '', password: '' })
const magicEmail = ref('')
const magicState = ref<'idle' | 'sending' | 'sent'>('idle')
const magicError = ref('')

const canSubmit = computed(() => form.email.length > 3 && form.password.length > 0 && !auth.loading)
const canSendMagic = computed(() => magicEmail.value.includes('@') && magicState.value !== 'sending')

function buildAdoptUrl(access: string, refresh: string) {
  return `${app.dashboard}/auth/adopt#access=${encodeURIComponent(access)}&refresh=${encodeURIComponent(refresh)}`
}

async function submit() {
  auth.error = null
  try {
    const tokens = await auth.login(form.email, form.password)
    window.location.href = buildAdoptUrl(tokens.access, tokens.refresh)
  } catch {
    // error set by store
  }
}

async function sendMagicLink() {
  magicError.value = ''
  magicState.value = 'sending'
  try {
    await auth.requestMagicLink(magicEmail.value)
    magicState.value = 'sent'
  } catch {
    magicError.value = 'Could not send the link. Please check the email address and try again.'
    magicState.value = 'idle'
  }
}

useSeoMeta({
  title: 'Sign in',
  robots: 'noindex',
})
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md">
      <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">
        <!-- Header -->
        <div class="mb-6">
          <div class="mb-4 flex items-center gap-3">
            <img v-if="portal.logo" :src="portal.logo" :alt="portal.brandName" class="h-9 w-auto object-contain" />
            <span v-else class="flex h-9 items-center font-serif text-xl font-bold text-brand-700">
              {{ portal.brandName }}
            </span>
          </div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Sign in</h1>
          <p class="mt-1.5 text-sm text-slate-500">Use your account email and password to continue.</p>
        </div>

        <!-- Tab switcher -->
        <div class="mb-6 flex gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1">
          <button
            class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all"
            :class="tab === 'password' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            type="button"
            @click="tab = 'password'; auth.error = null"
          >
            Password
          </button>
          <button
            class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all"
            :class="tab === 'magic' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            type="button"
            @click="tab = 'magic'; magicState = 'idle'; magicError = ''"
          >
            Magic link
          </button>
        </div>

        <!-- Password tab -->
        <form v-if="tab === 'password'" class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700" for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="email"
              type="email"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label class="text-sm font-medium text-slate-700" for="password">Password</label>
              <NuxtLink to="/forgot-password" class="text-xs font-medium text-brand-600 hover:underline">
                Forgot password?
              </NuxtLink>
            </div>
            <input
              id="password"
              v-model="form.password"
              class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="current-password"
              type="password"
              placeholder="••••••••"
              required
            />
          </div>

          <div
            v-if="auth.error"
            class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800"
            role="alert"
          >
            {{ auth.error }}
          </div>

          <button
            class="relative inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-700 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="!canSubmit"
            type="submit"
          >
            <svg v-if="auth.loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
            </svg>
            {{ auth.loading ? 'Signing in…' : 'Sign in' }}
          </button>
        </form>

        <!-- Magic link tab -->
        <div v-else class="space-y-4">
          <template v-if="magicState !== 'sent'">
            <p class="text-sm text-slate-500">
              Enter your email and we'll send a one-click sign-in link. No password needed. Links expire in 15 minutes.
            </p>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700" for="magic-email">Email</label>
              <input
                id="magic-email"
                v-model="magicEmail"
                class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                autocomplete="email"
                type="email"
                placeholder="you@example.com"
                @keydown.enter.prevent="canSendMagic && sendMagicLink()"
              />
            </div>
            <div v-if="magicError" class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">
              {{ magicError }}
            </div>
            <button
              class="inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-700 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-800 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="!canSendMagic"
              type="button"
              @click="sendMagicLink"
            >
              <svg v-if="magicState === 'sending'" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
              </svg>
              {{ magicState === 'sending' ? 'Sending…' : 'Send magic link' }}
            </button>
          </template>

          <template v-else>
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center">
              <svg class="mx-auto h-8 w-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <p class="mt-3 font-semibold text-emerald-900">Check your inbox</p>
              <p class="mt-1 text-sm text-emerald-800">
                A sign-in link was sent to <strong>{{ magicEmail }}</strong>. Click it to sign in — it works once and expires in 15 minutes.
              </p>
            </div>
            <button
              class="w-full text-center text-xs text-slate-500 hover:text-slate-700 hover:underline"
              type="button"
              @click="magicState = 'idle'; magicError = ''"
            >
              Try a different email
            </button>
          </template>
        </div>
      </div>

      <p class="mt-4 text-center text-sm text-slate-500">
        New to {{ portal.brandName }}?
        <NuxtLink to="/register" class="ml-1 font-semibold text-brand-600 hover:underline">Create a free account</NuxtLink>
      </p>
    </section>
  </div>
</template>
