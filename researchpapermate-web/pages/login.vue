<script setup lang="ts">
definePageMeta({ ssr: false })

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
  } catch { /* error set by store */ }
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

useSeoMeta({ title: 'Sign in | ResearchPaperMate', robots: 'noindex' })
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center bg-parchment-100 px-4 py-10">
    <section class="w-full max-w-md">
      <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">

        <!-- RPM wordmark logo -->
        <div class="mb-7">
          <NuxtLink to="/" class="mb-5 flex items-center gap-2.5">
            <span class="font-serif text-xl font-bold text-claret-800 font-bold">ResearchPaperMate</span>
          </NuxtLink>

          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Welcome back</h1>
          <p class="mt-1 text-sm text-slate-500">
            Sign in to track your orders, message your writer, and download papers.
          </p>
        </div>

        <!-- Tab switcher -->
        <div class="mb-6 flex gap-1 rounded-xl border border-slate-200 bg-parchment-100 p-1">
          <button
            class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all"
            :class="tab === 'password' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            type="button"
            @click="tab = 'password'; auth.error = null"
          >Password</button>
          <button
            class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all"
            :class="tab === 'magic' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            type="button"
            @click="tab = 'magic'; magicState = 'idle'; magicError = ''"
          >Magic link</button>
        </div>

        <!-- Password form -->
        <form v-if="tab === 'password'" class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700" for="email">Email</label>
            <input id="email" v-model="form.email" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-claret-500 focus:outline-none focus:ring-2 focus:ring-claret-200" autocomplete="email" type="email" placeholder="you@example.com" required/>
          </div>
          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label class="text-sm font-medium text-slate-700" for="password">Password</label>
              <a :href="`${app.dashboard}/auth/reset-password`" class="text-xs font-medium text-amber-700 hover:underline">Forgot password?</a>
            </div>
            <input id="password" v-model="form.password" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-claret-500 focus:outline-none focus:ring-2 focus:ring-claret-200" autocomplete="current-password" type="password" placeholder="••••••••" required/>
          </div>
          <div v-if="auth.error" class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">{{ auth.error }}</div>
          <button class="relative inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-claret-900 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-claret-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60" :disabled="!canSubmit" type="submit">
            <svg v-if="auth.loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
            </svg>
            {{ auth.loading ? 'Signing in…' : 'Sign in to my dashboard' }}
          </button>
        </form>

        <!-- Magic link tab -->
        <div v-else class="space-y-4">
          <template v-if="magicState !== 'sent'">
            <p class="text-sm text-slate-500">Enter your email and we'll send a one-click sign-in link. No password needed. Links expire in 15 minutes.</p>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700" for="magic-email">Email</label>
              <input id="magic-email" v-model="magicEmail" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-claret-500 focus:outline-none focus:ring-2 focus:ring-claret-200" autocomplete="email" type="email" placeholder="you@example.com" @keydown.enter.prevent="canSendMagic && sendMagicLink()"/>
            </div>
            <div v-if="magicError" class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">{{ magicError }}</div>
            <button class="inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-claret-900 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-claret-800 disabled:cursor-not-allowed disabled:opacity-60" :disabled="!canSendMagic" type="button" @click="sendMagicLink">
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <p class="mt-3 font-semibold text-emerald-900">Check your inbox</p>
              <p class="mt-1 text-sm text-emerald-800">A sign-in link was sent to <strong>{{ magicEmail }}</strong>. Click it to sign in — it works once and expires in 15 minutes.</p>
            </div>
            <button class="w-full text-center text-xs text-slate-500 hover:text-slate-700 hover:underline" type="button" @click="magicState = 'idle'; magicError = ''">Try a different email</button>
          </template>
        </div>

        <!-- Trust strip -->
        <div class="mt-6 flex items-center justify-center gap-4 border-t border-slate-100 pt-5 text-xs text-slate-400">
          <span class="flex items-center gap-1">
            <svg class="h-3.5 w-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            4.8/5 rating
          </span>
          <span class="text-slate-200">|</span>
          <span>14,700+ papers</span>
          <span class="text-slate-200">|</span>
          <span>Grade guarantee</span>
        </div>
      </div>

      <p class="mt-4 text-center text-sm text-slate-500">
        New to ResearchPaperMate?
        <NuxtLink to="/register" class="ml-1 font-semibold text-amber-700 hover:underline">Create a free account</NuxtLink>
      </p>
    </section>
  </div>
</template>
