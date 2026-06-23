<script setup lang="ts">
import { markRaw } from 'vue'
import { MessageSquare, Smartphone, Mail } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Contact ResearchPaperMate — 24/7 Support',
  description: 'Get in touch with our support team. We respond within 1 hour, 7 days a week. Contact us via form, email, or WhatsApp.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/contact' }] })

const form = reactive({ name: '', email: '', subject: '', message: '' })
const sent = ref(false)
const err  = ref('')
const busy = ref(false)
const api  = useApi()

async function submit() {
  busy.value = true
  err.value  = ''
  try {
    await api('/cms-api/contact/', { method: 'POST', body: form })
    sent.value = true
  } catch {
    err.value = 'Something went wrong — email us directly at support@researchpapermate.com'
  } finally {
    busy.value = false
  }
}

const channels = [
  {
    icon: markRaw(MessageSquare),
    title: 'Live chat',
    desc: 'The fastest way to reach us. Available on every page — look for the chat button.',
    badge: 'Fastest',
    badgeColor: 'bg-green-100 text-green-700',
    link: null,
  },
  {
    icon: markRaw(Smartphone),
    title: 'WhatsApp',
    desc: 'Message us on WhatsApp for urgent orders or quick questions. Typical reply: under 5 minutes.',
    badge: 'Recommended',
    badgeColor: 'bg-amber-50 text-claret-700',
    link: 'https://wa.me/1234567890',
  },
  {
    icon: markRaw(Mail),
    title: 'Email',
    desc: 'support@researchpapermate.com — we reply within 1 hour during operating hours.',
    badge: null,
    badgeColor: '',
    link: 'mailto:support@researchpapermate.com',
  },
]

const faqs = [
  { q: 'How quickly will I get a response?', a: 'Our support team responds within 1 hour during operating hours (Mon–Sun, 08:00–23:00 GMT). For urgent orders, use the WhatsApp button for the fastest reply.' },
  { q: 'Can I make changes to my order after placing it?', a: "Yes. Contact us as soon as possible and we'll update your requirements. Changes are free before a writer has been assigned." },
  { q: 'What if I\'m not happy with the delivered paper?', a: "You're entitled to unlimited free revisions within the revision window. If the paper still doesn't meet your original brief, we'll issue a full refund." },
  { q: 'How do I check my order status?', a: 'Log in to your dashboard at app.researchpapermate.com. You\'ll see real-time progress, messages from your writer, and all deliverables.' },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-claret-950 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="relative mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-amber-400">We're here</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Get in touch</h1>
        <p class="mt-4 text-lg text-claret-200">Real people, real responses. No chatbots, no scripted replies — just direct, knowledgeable support.</p>
      </div>
    </section>

    <!-- ── Main content ───────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-16 lg:grid-cols-2">

          <!-- Left: channels + FAQ -->
          <div class="space-y-10">
            <div>
              <h2 class="text-xl font-bold text-slate-900">Contact channels</h2>
              <div class="mt-5 space-y-4">
                <div v-for="c in channels" :key="c.title" class="flex gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-slate-100">
                    <component :is="c.icon" class="h-5 w-5 text-slate-600" />
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <p class="font-semibold text-slate-900">{{ c.title }}</p>
                      <span v-if="c.badge" class="rounded-full px-2 py-0.5 text-[11px] font-bold" :class="c.badgeColor">{{ c.badge }}</span>
                    </div>
                    <p class="mt-0.5 text-sm text-slate-500">{{ c.desc }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h2 class="mb-4 text-xl font-bold text-slate-900">Common questions</h2>
              <div class="space-y-3">
                <details v-for="faq in faqs" :key="faq.q" class="group rounded-xl border border-slate-200 bg-parchment-100">
                  <summary class="flex cursor-pointer list-none items-center justify-between gap-3 px-5 py-3.5 text-sm font-semibold text-slate-800">
                    {{ faq.q }}
                    <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-white text-slate-400 shadow-sm transition-transform group-open:rotate-45">+</span>
                  </summary>
                  <p class="px-5 pb-4 text-sm leading-relaxed text-slate-500">{{ faq.a }}</p>
                </details>
              </div>
            </div>
          </div>

          <!-- Right: contact form -->
          <div>
            <h2 class="mb-6 text-xl font-bold text-slate-900">Send us a message</h2>
            <div v-if="sent" class="rounded-2xl border border-green-200 bg-green-50 p-10 text-center space-y-3">
              <div class="text-4xl">✓</div>
              <p class="font-bold text-green-800">Message received!</p>
              <p class="text-sm text-green-700">We'll reply to {{ form.email }} within the hour.</p>
              <a :href="app.dashboard" class="mt-2 inline-block text-sm font-semibold text-amber-700 hover:underline">Go to your dashboard →</a>
            </div>
            <form v-else class="space-y-4" @submit.prevent="submit">
              <div class="grid sm:grid-cols-2 gap-4">
                <label class="block space-y-1.5">
                  <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Your name</span>
                  <input v-model="form.name" required type="text" placeholder="Jane Smith" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm focus:border-claret-400 focus:outline-none focus:ring-2 focus:ring-claret-100" />
                </label>
                <label class="block space-y-1.5">
                  <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Email</span>
                  <input v-model="form.email" required type="email" placeholder="jane@university.edu" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm focus:border-claret-400 focus:outline-none focus:ring-2 focus:ring-claret-100" />
                </label>
              </div>
              <label class="block space-y-1.5">
                <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Subject</span>
                <input v-model="form.subject" type="text" placeholder="e.g. Question about my order" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm focus:border-claret-400 focus:outline-none focus:ring-2 focus:ring-claret-100" />
              </label>
              <label class="block space-y-1.5">
                <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Message</span>
                <textarea v-model="form.message" required rows="5" placeholder="Tell us how we can help…" class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-claret-400 focus:outline-none focus:ring-2 focus:ring-claret-100 resize-none" />
              </label>
              <p v-if="err" class="text-xs text-red-500">{{ err }}</p>
              <button type="submit" :disabled="busy" class="h-12 w-full rounded-xl bg-claret-900 text-sm font-bold text-white shadow transition-colors hover:bg-claret-900 disabled:opacity-50">
                {{ busy ? 'Sending…' : 'Send message' }}
              </button>
              <p class="text-center text-xs text-slate-400">Typical reply time: under 1 hour · Mon–Sun 08:00–23:00</p>
            </form>
          </div>

        </div>
      </div>
    </section>

  </div>
</template>
