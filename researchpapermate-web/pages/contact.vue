<script setup lang="ts">
useSeoMeta({
  title: 'Contact',
  description: 'Get in touch with the ResearchPaperMate support team.',
})

const form = reactive({ name: '', email: '', subject: '', message: '' })
const sent = ref(false)
const error = ref('')
const submitting = ref(false)

const api = useApi()

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    await api('/api/support/contact/', { method: 'POST', body: form })
    sent.value = true
  } catch {
    error.value = 'Something went wrong — please email us directly.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="section max-w-2xl">
    <h1 class="section-heading">Contact us</h1>
    <p class="section-sub">We respond within 1 business hour during operating hours.</p>

    <div v-if="sent" class="mt-10 rounded-xl bg-green-50 p-8 text-center">
      <p class="text-lg font-semibold text-green-700">Message sent!</p>
      <p class="mt-2 text-sm text-green-600">We'll get back to you within 1 hour.</p>
    </div>

    <form v-else class="mt-10 space-y-5" @submit.prevent="submit">
      <div class="grid gap-5 sm:grid-cols-2">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-slate-700">Name</label>
          <input v-model="form.name" type="text" required
            class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-slate-700">Email</label>
          <input v-model="form.email" type="email" required
            class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
        </div>
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-slate-700">Subject</label>
        <input v-model="form.subject" type="text" required
          class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
      </div>
      <div>
        <label class="mb-1.5 block text-sm font-medium text-slate-700">Message</label>
        <textarea v-model="form.message" rows="6" required
          class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <button type="submit" class="btn-primary w-full py-3" :disabled="submitting">
        {{ submitting ? 'Sending…' : 'Send message' }}
      </button>
    </form>
  </div>
</template>
