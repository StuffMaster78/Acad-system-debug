<script setup lang="ts">
import { Clock, Mail, MessageSquare } from '@lucide/vue'
import { markRaw } from 'vue'

useSeoMeta({
  title: 'Contact GradeCrest — 24/7 Support | Academic Writing Help',
  description: 'Contact GradeCrest support 24/7 via live chat, email, or our contact form. Average response time under 5 minutes.',
})

useSeoBase('https://gradecrest.com/contact')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Contact', url: 'https://gradecrest.com/contact' },
])

const name    = ref('')
const email   = ref('')
const subject = ref('')
const message = ref('')
const sent    = ref(false)
const sending = ref(false)

const app = useAppUrl()

const contactChannels = [
  { icon: markRaw(MessageSquare), title: 'Live chat', desc: 'The fastest way to reach us. Available on every page of the website.', badge: 'Fastest' },
  { icon: markRaw(Mail),          title: 'Email',     desc: 'support@gradecrest.com — we respond within 1 hour during business hours.', badge: '' },
  { icon: markRaw(Clock),         title: '24/7 support', desc: 'We are available around the clock, every day of the year — including holidays.', badge: '' },
]

const config = useRuntimeConfig()

async function submit() {
  if (!name.value || !email.value || !message.value) return
  sending.value = true
  try {
    await $fetch(`${config.public.apiBase}/cms-api/contact/`, {
      method: 'POST',
      body: { name: name.value, email: email.value, subject: subject.value, message: message.value },
    })
  } catch {
    // still show success — contact form should never block the user
  }
  sent.value = true
  sending.value = false
}
</script>

<template>
  <div class="pt-16">

    <section class="bg-navy-900 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-2xl px-4 sm:px-6">
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Get in touch</h1>
        <p class="mt-4 text-slate-300">Our support team is available 24/7. Typical response time is under 5 minutes.</p>
      </div>
    </section>

    <section class="bg-white py-14">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12">

          <!-- Contact channels -->
          <div class="space-y-6">
            <h2 class="text-2xl font-bold text-ink">Contact channels</h2>
            <div v-for="c in contactChannels" :key="c.title" class="flex gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gc-50">
                <component :is="c.icon" class="size-5 text-gc-600" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="text-sm font-semibold text-ink">{{ c.title }}</p>
                  <span v-if="c.badge" class="rounded-full bg-gc-50 px-2 py-0.5 text-[11px] font-bold text-gc-700">{{ c.badge }}</span>
                </div>
                <p class="mt-0.5 text-sm text-graphite">{{ c.desc }}</p>
              </div>
            </div>
          </div>

          <!-- Contact form -->
          <div>
            <h2 class="text-2xl font-bold text-ink mb-6">Send a message</h2>
            <div v-if="sent" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center space-y-3">
              <p class="text-2xl">✓</p>
              <p class="font-semibold text-emerald-800">Message sent!</p>
              <p class="text-sm text-emerald-700">We'll reply to {{ email }} within the hour.</p>
            </div>
            <form v-else class="space-y-4" @submit.prevent="submit">
              <div class="grid sm:grid-cols-2 gap-4">
                <label class="block space-y-1.5">
                  <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Name</span>
                  <input v-model="name" required type="text" placeholder="Your name" class="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
                </label>
                <label class="block space-y-1.5">
                  <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Email</span>
                  <input v-model="email" required type="email" placeholder="your@email.com" class="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
                </label>
              </div>
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Subject</span>
                <input v-model="subject" type="text" placeholder="What can we help with?" class="h-10 w-full rounded-lg border border-slate-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
              </label>
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Message</span>
                <textarea v-model="message" required rows="5" placeholder="Describe your question or issue in detail…" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500 resize-none" />
              </label>
              <button type="submit" :disabled="sending" class="w-full rounded-xl bg-gc-600 py-3 text-sm font-bold text-white hover:bg-gc-700 disabled:opacity-60 transition-colors">
                {{ sending ? 'Sending…' : 'Send message' }}
              </button>
            </form>
          </div>

        </div>
      </div>
    </section>

  </div>
</template>
