<script setup lang="ts">
useSeoMeta({
  title: 'Contact | Writers Creek',
  description: 'Get in touch with the Writers Creek team. Questions about applying, earnings, or the platform.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const config = useRuntimeConfig()

const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: '',
})

const submitting = ref(false)
const submitted = ref(false)
const error = ref<string | null>(null)

async function submit() {
  submitting.value = true
  error.value = null
  try {
    const apiBase = String(config.public.apiBase || '').replace(/\/+$/, '')
    await $fetch(`${apiBase}/api/v1/contact/`, {
      method: 'POST',
      credentials: 'include',
      body: {
        ...form,
        website: 'writerscreek',
      },
    })
    submitted.value = true
  } catch {
    error.value = 'Something went wrong. Please try again or email us directly at writers@writerscreek.com.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-white">

    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'Contact' }]" />
        <h1 class="mt-4 text-3xl font-bold text-slate-900 sm:text-4xl">Get in touch</h1>
        <p class="mt-2 text-slate-600">Questions about applying, your application status, or the platform. We respond within one business day.</p>
      </div>
    </div>

    <!-- Body -->
    <div class="mx-auto max-w-3xl px-4 py-14 sm:px-6 lg:px-8">

      <!-- Success -->
      <div v-if="submitted" class="rounded-2xl border border-green-200 bg-green-50 p-8 text-center">
        <div class="mb-4 flex justify-center">
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
            <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </div>
        <h2 class="text-lg font-bold text-green-900">Message sent</h2>
        <p class="mt-2 text-sm text-green-800">We have received your message and will respond within one business day.</p>
      </div>

      <form v-else class="space-y-6" @submit.prevent="submit">
        <div class="grid gap-5 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="name">Your name</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
              placeholder="Jane Smith"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="email">Email address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
              placeholder="jane@example.com"
            />
          </div>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="subject">Subject</label>
          <input
            id="subject"
            v-model="form.subject"
            type="text"
            required
            class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            placeholder="e.g. Question about my application"
          />
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-800" for="message">Message</label>
          <textarea
            id="message"
            v-model="form.message"
            rows="6"
            required
            class="block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            placeholder="Tell us what you need…"
          />
        </div>

        <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="submitting"
          class="w-full rounded-xl bg-brand-600 py-4 text-base font-bold text-white transition-colors hover:bg-brand-700 disabled:opacity-60"
        >
          {{ submitting ? 'Sending…' : 'Send message' }}
        </button>
      </form>

      <div class="mt-10 border-t border-slate-100 pt-8 text-sm text-slate-500">
        <p>Prefer email? Write directly to <a href="mailto:writers@writerscreek.com" class="font-medium text-brand-600 hover:underline">writers@writerscreek.com</a>.</p>
        <p class="mt-1">We respond within one business day.</p>
      </div>
    </div>

  </div>
</template>
