<script setup lang="ts">
definePageMeta({ ssr: false })

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

useSeoMeta({ title: 'Create an account | NurseMyGrade', robots: 'noindex', ogImageWidth: 1200, ogImageHeight: 630, twitterCard: 'summary_large_image' })
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center bg-slate-50 px-4 py-10">
    <section class="w-full max-w-4xl">

      <!-- Post-registration confirmation -->
      <template v-if="registered">
        <div class="mx-auto max-w-md rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center shadow-lg">
          <svg class="mx-auto h-12 w-12 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
          <h1 class="mt-4 text-2xl font-semibold text-emerald-900">Check your inbox</h1>
          <p class="mt-3 text-sm leading-relaxed text-emerald-800">
            We sent a confirmation link to <strong>{{ registeredEmail }}</strong>.<br/>
            Click it to activate your account and place your first nursing order.
          </p>
          <p class="mt-5 text-xs text-emerald-700">
            Didn't get it? Check your spam folder or
            <NuxtLink to="/login" class="font-semibold underline">sign in</NuxtLink>
            to request a new one.
          </p>
        </div>
      </template>

      <!-- Registration form + trust panel -->
      <template v-else>
        <div class="grid gap-0 overflow-hidden rounded-2xl border border-slate-200 shadow-lg shadow-slate-200/60 lg:grid-cols-[1fr_340px]">

          <!-- Left: form -->
          <div class="bg-white p-8">
            <!-- Logo -->
            <NuxtLink to="/" class="mb-6 flex items-center gap-2">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <defs>
                  <linearGradient id="lg-v-reg" x1="16" y1="2" x2="16" y2="30" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stop-color="#0d9488"/>
                    <stop offset="100%" stop-color="#115e59"/>
                  </linearGradient>
                  <linearGradient id="lg-h-reg" x1="2" y1="16" x2="30" y2="16" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stop-color="#2dd4bf"/>
                    <stop offset="100%" stop-color="#0d9488"/>
                  </linearGradient>
                </defs>
                <rect x="12" y="2" width="8" height="28" rx="4" fill="url(#lg-v-reg)"/>
                <rect x="2" y="12" width="28" height="8" rx="4" fill="url(#lg-h-reg)" opacity="0.9"/>
              </svg>
              <span class="text-[1.15rem] font-bold tracking-tight">
                <span class="text-slate-900">Nurse</span><span class="text-brand-600">MyGrade</span>
              </span>
            </NuxtLink>

            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Create your account</h1>
            <p class="mt-1 text-sm text-slate-500">
              Free to join. Your first nursing paper order takes minutes to place.
            </p>

            <form class="mt-6 space-y-4" @submit.prevent="submit">
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

              <div v-if="auth.error" class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">
                {{ auth.error }}
              </div>

              <button
                class="relative inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-700 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="!canSubmit"
                type="submit"
              >
                <svg v-if="auth.loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                </svg>
                {{ auth.loading ? 'Creating account…' : 'Create my account' }}
              </button>

              <p class="text-center text-xs leading-relaxed text-slate-400">
                By creating an account you agree to our
                <NuxtLink to="/terms" class="underline">Terms of Use</NuxtLink>
                and
                <NuxtLink to="/privacy" class="underline">Privacy Policy</NuxtLink>.
              </p>
            </form>

            <p class="mt-5 text-center text-sm text-slate-500">
              Already have an account?
              <NuxtLink to="/login" class="ml-1 font-semibold text-brand-600 hover:underline">Sign in</NuxtLink>
            </p>
          </div>

          <!-- Right: trust panel (hidden on mobile) -->
          <div class="hidden bg-gradient-to-br from-brand-800 to-brand-900 p-8 text-white lg:flex lg:flex-col lg:justify-between">
            <div>
              <p class="mb-6 text-xs font-semibold uppercase tracking-widest text-brand-300">
                Why nursing students choose us
              </p>
              <ul class="space-y-5">
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Real nurses write your papers</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">BSN minimum. MSN and DNP writers for graduate work. Every writer is licence-verified.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Grade or money back</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">If the work doesn't meet your stated requirements, we rewrite it free or refund you.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Zero AI — Turnitin clean</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Every paper written by a human nurse. Free Turnitin report included with every order.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">NANDA · SOAP · APA 7th — done right</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Writers use the same clinical frameworks your instructors grade against.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">As fast as 3 hours</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Urgent deadline? Most nursing papers up to 4 pages delivered in 3 hours.</p>
                  </div>
                </li>
              </ul>
            </div>

            <!-- Rating strip -->
            <div class="mt-8 rounded-xl border border-white/10 bg-white/5 p-4">
              <div class="flex items-center gap-1">
                <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="ml-1 text-sm font-bold text-white">4.98 / 5</span>
              </div>
              <p class="mt-1 text-xs text-brand-300">From 9,800+ nursing papers delivered</p>
            </div>
          </div>

        </div>
      </template>
    </section>
  </div>
</template>
