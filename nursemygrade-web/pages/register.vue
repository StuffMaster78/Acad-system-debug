<script setup lang="ts">
definePageMeta({ ssr: false })

const portal = usePortalStore()
const auth = useRpmAuthStore()

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
})

const registered = ref(false)
const registeredEmail = ref('')

const canSubmit = computed(
  () =>
    form.first_name.trim().length > 0 &&
    form.email.includes('@') &&
    form.password.length >= 8 &&
    !auth.loading,
)

async function submit() {
  auth.error = null
  try {
    await auth.register({
      email: form.email,
      password: form.password,
      first_name: form.first_name,
      last_name: form.last_name,
    })
    registeredEmail.value = form.email
    registered.value = true
  } catch {
    // error set by store
  }
}

useSeoMeta({
  title: 'Create an account',
  robots: 'noindex',
})
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md">

      <!-- Post-registration state -->
      <template v-if="registered">
        <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center shadow-lg">
          <svg class="mx-auto h-12 w-12 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h1 class="mt-4 text-2xl font-semibold text-emerald-900">Check your inbox</h1>
          <p class="mt-3 text-sm text-emerald-800 leading-relaxed">
            We sent a confirmation link to <strong>{{ registeredEmail }}</strong>.<br />
            Click it to activate your account and place your first order.
          </p>
          <p class="mt-5 text-xs text-emerald-700">
            Didn't get it? Check your spam folder or
            <NuxtLink to="/login" class="font-semibold underline">sign in</NuxtLink>
            to request a new one.
          </p>
        </div>
      </template>

      <!-- Registration form -->
      <template v-else>
        <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">
          <div class="mb-6">
            <div class="mb-4 flex items-center gap-3">
              <img v-if="portal.logo" :src="portal.logo" :alt="portal.brandName" class="h-9 w-auto object-contain" />
              <span v-else class="font-serif text-xl font-bold text-brand-700">{{ portal.brandName }}</span>
            </div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Create your account</h1>
            <p class="mt-1.5 text-sm text-slate-500">Free to join. Place your first order in minutes.</p>
          </div>

          <form class="space-y-4" @submit.prevent="submit">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="first-name">First name</label>
                <input
                  id="first-name"
                  v-model="form.first_name"
                  class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                  autocomplete="given-name"
                  type="text"
                  placeholder="Jane"
                  required
                />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="last-name">Last name</label>
                <input
                  id="last-name"
                  v-model="form.last_name"
                  class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                  autocomplete="family-name"
                  type="text"
                  placeholder="Smith"
                />
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700" for="reg-email">Email</label>
              <input
                id="reg-email"
                v-model="form.email"
                class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                autocomplete="email"
                type="email"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700" for="reg-password">Password</label>
              <input
                id="reg-password"
                v-model="form.password"
                class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                autocomplete="new-password"
                type="password"
                placeholder="At least 8 characters"
                required
                minlength="8"
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
              {{ auth.loading ? 'Creating account…' : 'Create account' }}
            </button>

            <p class="text-center text-xs text-slate-400 leading-relaxed">
              By creating an account you agree to our
              <NuxtLink to="/terms" class="underline">Terms</NuxtLink>
              and
              <NuxtLink to="/privacy" class="underline">Privacy Policy</NuxtLink>.
            </p>
          </form>
        </div>

        <p class="mt-4 text-center text-sm text-slate-500">
          Already have an account?
          <NuxtLink to="/login" class="ml-1 font-semibold text-brand-600 hover:underline">Sign in</NuxtLink>
        </p>
      </template>
    </section>
  </div>
</template>
