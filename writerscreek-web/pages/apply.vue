<script setup lang="ts">
useSeoMeta({
  title: 'Apply to Write | Writers Creek',
  description: 'Apply to join the Writers Creek network. We accept writers with postgraduate credentials in any academic discipline.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const config = useRuntimeConfig()

interface FormData {
  full_name: string
  email: string
  qualification: string
  subject_specialisms: string
  years_experience: string
  bio: string
  portfolio_link: string
}

const form = reactive<FormData>({
  full_name: '',
  email: '',
  qualification: '',
  subject_specialisms: '',
  years_experience: '',
  bio: '',
  portfolio_link: '',
})

const submitting = ref(false)
const submitted = ref(false)
const error = ref<string | null>(null)

async function submit() {
  submitting.value = true
  error.value = null
  try {
    const apiBase = String(config.public.apiBase || '').replace(/\/+$/, '')
    await $fetch(`${apiBase}/writer-management/applications/submit/`, {
      method: 'POST',
      credentials: 'include',
      body: form,
    })
    submitted.value = true
  } catch (e: any) {
    error.value = e?.data?.detail || e?.data?.message || 'Something went wrong. Please try again or email us directly.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-white">

    <!-- Page header -->
    <div class="border-b border-slate-100 bg-slate-900 px-4 py-14 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-brand-400/30 bg-brand-400/10 px-4 py-1.5 text-sm font-medium text-brand-300">
          <span class="inline-block h-1.5 w-1.5 rounded-full bg-brand-400 animate-pulse"></span>
          Applications open
        </div>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Apply to write</h1>
        <p class="mt-4 text-lg text-slate-300">Share your background. We review every application personally.</p>
        <div class="mt-5 flex flex-wrap justify-center gap-4 text-sm text-slate-400">
          <span>Postgrad credentials required</span>
          <span>·</span>
          <span>Decision within 48 hours</span>
          <span>·</span>
          <span>Takes ~10 minutes</span>
        </div>
      </div>
    </div>

    <!-- Success state -->
    <div v-if="submitted" class="mx-auto max-w-2xl px-4 py-20 text-center sm:px-6 lg:px-8">
      <div class="mb-6 flex justify-center">
        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
      </div>
      <h2 class="text-2xl font-bold text-slate-900">Application received</h2>
      <p class="mt-3 text-slate-600">Thank you for applying to Writers Creek. Our team reviews every application and you will hear from us within 48 hours.</p>
      <p class="mt-2 text-sm text-slate-500">Check your inbox at <strong>{{ form.email }}</strong> for confirmation.</p>
      <NuxtLink to="/" class="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-brand-600 hover:underline">
        ← Back to home
      </NuxtLink>
    </div>

    <!-- Application form -->
    <div v-else class="mx-auto max-w-2xl px-4 py-14 sm:px-6 lg:px-8">
      <form class="space-y-7" @submit.prevent="submit">

        <!-- Name + email -->
        <div class="grid gap-5 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="full_name">Full name</label>
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              required
              class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
              placeholder="Dr. Jane Smith"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="email">Email address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
              placeholder="jane@example.com"
            />
          </div>
        </div>

        <!-- Qualification + years -->
        <div class="grid gap-5 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="qualification">Highest qualification</label>
            <select
              id="qualification"
              v-model="form.qualification"
              required
              class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            >
              <option value="" disabled>Select qualification</option>
              <option>Bachelor's degree</option>
              <option>Master's degree</option>
              <option>PhD / Doctorate</option>
              <option>Professional credential (RN, RD, CPA, etc.)</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="years_experience">Academic writing experience</label>
            <select
              id="years_experience"
              v-model="form.years_experience"
              required
              class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            >
              <option value="" disabled>Select years</option>
              <option>Less than 1 year</option>
              <option>1–2 years</option>
              <option>3–5 years</option>
              <option>6–10 years</option>
              <option>More than 10 years</option>
            </select>
          </div>
        </div>

        <!-- Subject specialisms -->
        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="subject_specialisms">Subject specialisms</label>
          <input
            id="subject_specialisms"
            v-model="form.subject_specialisms"
            type="text"
            required
            class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            placeholder="e.g. Nursing, Public Health, Clinical Psychology"
          />
          <p class="mt-1.5 text-xs text-slate-500">List your primary academic disciplines, comma-separated.</p>
        </div>

        <!-- Bio -->
        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="bio">Brief professional bio</label>
          <textarea
            id="bio"
            v-model="form.bio"
            rows="5"
            required
            class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            placeholder="Tell us about your academic background, current work, and why you want to write for Writers Creek."
          />
          <p class="mt-1.5 text-xs text-slate-500">3–5 sentences is sufficient. Mention your highest degree, institution, and relevant experience.</p>
        </div>

        <!-- Portfolio link -->
        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="portfolio_link">Portfolio or writing sample URL <span class="font-normal text-slate-400">(optional)</span></label>
          <input
            id="portfolio_link"
            v-model="form.portfolio_link"
            type="url"
            class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            placeholder="https://your-portfolio.com or Google Drive link"
          />
          <p class="mt-1.5 text-xs text-slate-500">A link to published work, a portfolio, or a Google Drive document. If you have none, leave blank.</p>
        </div>

        <!-- Error -->
        <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="submitting"
          class="w-full rounded-xl bg-brand-600 py-4 text-base font-bold text-white shadow-sm transition-colors hover:bg-brand-700 disabled:opacity-60"
        >
          {{ submitting ? 'Submitting…' : 'Submit application' }}
        </button>

        <p class="text-center text-xs text-slate-400">
          By applying you agree to our
          <NuxtLink to="/legal/terms" class="underline hover:text-slate-600">Terms of Service</NuxtLink>
          and
          <NuxtLink to="/legal/privacy" class="underline hover:text-slate-600">Privacy Policy</NuxtLink>.
        </p>
      </form>
    </div>

  </div>
</template>
