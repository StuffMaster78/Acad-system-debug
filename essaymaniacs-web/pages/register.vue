<script setup lang="ts">
definePageMeta({ ssr: false })

const auth = useRpmAuthStore()

const form = reactive({ first_name: '', last_name: '', email: '', password: '' })
const registered = ref(false)
const registeredEmail = ref('')

const canSubmit = computed(
  () => form.first_name.trim().length > 0 && form.email.includes('@') && form.password.length >= 8 && !auth.loading,
)

async function submit() {
  auth.error = null
  try {
    await auth.register({ email: form.email, password: form.password, first_name: form.first_name, last_name: form.last_name })
    registeredEmail.value = form.email
    registered.value = true
  } catch { /* error set by store */ }
}

useSeoMeta({ title: 'Create an account | EssayManiacs', robots: 'noindex', ogImageWidth: 1200, ogImageHeight: 630, twitterCard: 'summary_large_image' })
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
            Click it to activate your account and place your first order.
          </p>
          <p class="mt-5 text-xs text-emerald-700">
            Didn't get it? Check your spam folder or
            <NuxtLink to="/login" class="font-semibold underline">sign in</NuxtLink> to request a new one.
          </p>
        </div>
      </template>

      <!-- Registration form + trust panel -->
      <template v-else>
        <div class="grid gap-0 overflow-hidden rounded-2xl border border-slate-200 shadow-lg shadow-slate-200/60 lg:grid-cols-[1fr_320px]">

          <!-- Left: form -->
          <div class="bg-white p-8">
            <!-- RPM logo -->
            <NuxtLink to="/" class="mb-6 flex items-center gap-2.5">
              <span class="font-serif text-xl font-bold text-brand-700">EssayManiacs</span>
            </NuxtLink>

            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Create your account</h1>
            <p class="mt-1 text-sm text-slate-500">Free to join. Place your first order in minutes.</p>

            <form class="mt-6 space-y-4" @submit.prevent="submit">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-slate-700" for="first-name">First name</label>
                  <input id="first-name" v-model="form.first_name" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" autocomplete="given-name" type="text" placeholder="Jane" required/>
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-slate-700" for="last-name">Last name</label>
                  <input id="last-name" v-model="form.last_name" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" autocomplete="family-name" type="text" placeholder="Smith"/>
                </div>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="reg-email">Email</label>
                <input id="reg-email" v-model="form.email" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" autocomplete="email" type="email" placeholder="you@example.com" required/>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="reg-password">Password</label>
                <input id="reg-password" v-model="form.password" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200" autocomplete="new-password" type="password" placeholder="At least 8 characters" required minlength="8"/>
              </div>
              <div v-if="auth.error" class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">{{ auth.error }}</div>
              <button class="relative inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-700 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60" :disabled="!canSubmit" type="submit">
                <svg v-if="auth.loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                </svg>
                {{ auth.loading ? 'Creating account…' : 'Create my account' }}
              </button>
              <p class="text-center text-xs leading-relaxed text-slate-400">
                By creating an account you agree to our
                <NuxtLink to="/terms" class="underline">Terms of Use</NuxtLink> and
                <NuxtLink to="/privacy" class="underline">Privacy Policy</NuxtLink>.
              </p>
            </form>

            <p class="mt-5 text-center text-sm text-slate-500">
              Already have an account?
              <NuxtLink to="/login" class="ml-1 font-semibold text-brand-600 hover:underline">Sign in</NuxtLink>
            </p>
          </div>

          <!-- Right: trust panel -->
          <div class="hidden bg-gradient-to-br from-brand-800 to-brand-900 p-8 text-white lg:flex lg:flex-col lg:justify-between">
            <div>
              <p class="mb-6 text-xs font-semibold uppercase tracking-widest text-brand-300">Why students choose us</p>
              <ul class="space-y-5">
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Expert writers — 100+ subjects</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Master's-level and PhD writers matched to your exact subject area.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Grade or money back</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">If the work doesn't meet your requirements, we rewrite it free or refund you.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Zero AI — plagiarism-free</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Every paper written by a human expert. Free Turnitin report included.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">As fast as 2 hours</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Urgent deadline? Most papers up to 4 pages delivered in 2 hours.</p>
                  </div>
                </li>
                <li class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">✓</span>
                  <div>
                    <p class="font-semibold text-white">Direct writer messaging</p>
                    <p class="mt-0.5 text-xs leading-relaxed text-brand-300">Communicate with your writer throughout — no support ticket middlemen.</p>
                  </div>
                </li>
              </ul>
            </div>
            <div class="mt-8 rounded-xl border border-white/10 bg-white/5 p-4">
              <div class="flex items-center gap-1">
                <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="ml-1 text-sm font-bold text-white">4.8 / 5</span>
              </div>
              <p class="mt-1 text-xs text-brand-300">From 14,700+ papers delivered</p>
            </div>
          </div>

        </div>
      </template>
    </section>
  </div>
</template>
