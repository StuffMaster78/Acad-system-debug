<script setup lang="ts">
useSeoMeta({
  title: 'Contact Us — EssayManiacs Support',
  description: 'Get in touch with our support team. We respond within 1 hour, 7 days a week.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/contact' }] })

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
    error.value = 'Something went wrong — please email us directly at support@essaymaniacs.com'
  } finally {
    submitting.value = false
  }
}

const faq = [
  {
    q: 'How quickly will I get a response?',
    a: 'Our support team responds within 1 hour during operating hours (Mon–Sun, 08:00–23:00). For urgent orders, use the WhatsApp button for the fastest reply.',
  },
  {
    q: 'Can I make changes to my order after placing it?',
    a: 'Yes. Contact us as soon as possible and we\'ll update your requirements. Changes are free before a writer has been assigned.',
  },
  {
    q: 'What if I\'m not happy with the delivered paper?',
    a: 'You\'re entitled to unlimited free revisions within the revision window. If the paper still doesn\'t meet your original requirements, we\'ll issue a full refund.',
  },
  {
    q: 'How do I check my order status?',
    a: 'Log in to your dashboard at app.essaymaniacs.com. You\'ll see real-time progress, messages from your writer, and all deliverables.',
  },
]

const openFaq = ref<number | null>(null)
function toggleFaq(i: number) {
  openFaq.value = openFaq.value === i ? null : i
}

const waNumber = '254700000000'
const waMessage = encodeURIComponent('Hi, I need help with my order.')
const waUrl = `https://wa.me/${waNumber}?text=${waMessage}`
</script>

<template>
  <div>
    <!-- ── Hero ──────────────────────────────────────────────────── -->
    <div class="bg-gradient-to-br from-brand-900 to-brand-700 py-16 text-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
        <h1 class="font-serif text-4xl font-bold sm:text-5xl">We're here when you need us</h1>
        <p class="mt-4 text-lg text-brand-200">
          Questions, order updates, revisions — our team responds within <strong class="text-white">1 hour</strong>, 7 days a week.
        </p>

        <!-- Quick-contact channel cards -->
        <div class="mt-10 grid gap-4 sm:grid-cols-3 max-w-3xl mx-auto">
          <!-- Live chat -->
          <div class="rounded-2xl bg-white/10 ring-1 ring-white/20 p-5 text-left">
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500">
              <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-4 4v-4z"/>
              </svg>
            </div>
            <p class="font-semibold text-white">Live Chat</p>
            <p class="mt-1 text-sm text-brand-300">Available in your dashboard — fastest response for active orders.</p>
          </div>

          <!-- WhatsApp -->
          <a :href="waUrl" target="_blank" rel="noopener noreferrer"
            class="rounded-2xl bg-white/10 ring-1 ring-white/20 p-5 text-left transition-colors hover:bg-white/20">
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[#25D366]">
              <svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
            </div>
            <p class="font-semibold text-white">WhatsApp</p>
            <p class="mt-1 text-sm text-brand-300">Tap to open a chat — reply usually within minutes.</p>
          </a>

          <!-- Email -->
          <div class="rounded-2xl bg-white/10 ring-1 ring-white/20 p-5 text-left">
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500">
              <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <p class="font-semibold text-white">Email</p>
            <p class="mt-1 text-xs text-brand-300 break-all">
              <a href="mailto:support@essaymaniacs.com" class="text-white hover:underline">
                support@essaymaniacs.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Form + Info ─────────────────────────────────────────────── -->
    <div class="section">
      <div class="grid gap-12 lg:grid-cols-[1fr_380px]">

        <!-- Left: form -->
        <div>
          <h2 class="font-serif text-2xl font-bold text-slate-900">Send us a message</h2>
          <p class="mt-2 text-slate-500">Fill in the form and we'll get back to you within 1 hour.</p>

          <!-- Success state -->
          <div v-if="sent" class="mt-8 rounded-2xl bg-green-50 border border-green-100 p-8 text-center">
            <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <svg class="h-7 w-7 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <p class="text-lg font-semibold text-green-800">Message received!</p>
            <p class="mt-2 text-sm text-green-700">We'll reply to your email within 1 hour. Check your inbox (and spam folder just in case).</p>
          </div>

          <form v-else class="mt-8 space-y-5" @submit.prevent="submit">
            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700">Your name</label>
                <input v-model="form.name" type="text" required placeholder="Jane Smith"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700">Email address</label>
                <input v-model="form.email" type="email" required placeholder="jane@example.com"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20" />
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Subject</label>
              <input v-model="form.subject" type="text" required placeholder="e.g. Question about my order #12345"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20" />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Message</label>
              <textarea v-model="form.message" rows="6" required placeholder="Tell us how we can help…"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 resize-none" />
            </div>

            <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>

            <button type="submit" class="btn-primary w-full py-3.5 text-base" :disabled="submitting">
              {{ submitting ? 'Sending…' : 'Send message' }}
            </button>

            <p class="text-center text-xs text-slate-400">
              We respond within 1 hour · Mon–Sun 08:00 – 23:00
            </p>
          </form>
        </div>

        <!-- Right: info panel -->
        <div class="space-y-6">
          <!-- Operating hours card -->
          <div class="rounded-2xl border border-slate-100 bg-slate-50 p-6">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">Support hours</p>
            <div class="space-y-2.5 text-sm">
              <div class="flex justify-between">
                <span class="text-slate-600">Monday – Friday</span>
                <span class="font-semibold text-slate-900">08:00 – 23:00</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-600">Saturday – Sunday</span>
                <span class="font-semibold text-slate-900">09:00 – 21:00</span>
              </div>
              <div class="mt-3 flex items-center gap-2 rounded-lg bg-green-50 px-3 py-2">
                <span class="h-2 w-2 rounded-full bg-green-500 shrink-0" />
                <span class="text-xs font-medium text-green-700">Typical reply time: under 30 minutes</span>
              </div>
            </div>
          </div>

          <!-- Trust signals -->
          <div class="rounded-2xl border border-slate-100 bg-white p-6">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">Our guarantees</p>
            <ul class="space-y-3 text-sm">
              <li class="flex items-start gap-3">
                <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 text-[10px] font-bold">✓</span>
                <span class="text-slate-700"><strong class="text-slate-900">Grade guarantee</strong> — meet your requirements or get a full refund</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 text-[10px] font-bold">✓</span>
                <span class="text-slate-700"><strong class="text-slate-900">Free revisions</strong> — unlimited within your revision window</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 text-[10px] font-bold">✓</span>
                <span class="text-slate-700"><strong class="text-slate-900">100% confidential</strong> — your identity and order details are never shared</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 text-[10px] font-bold">✓</span>
                <span class="text-slate-700"><strong class="text-slate-900">Zero AI content</strong> — every paper is human-written and plagiarism-free</span>
              </li>
            </ul>
          </div>

          <!-- FAQ -->
          <div class="rounded-2xl border border-slate-100 bg-white p-6">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">Common questions</p>
            <div class="divide-y divide-slate-100">
              <div v-for="(item, i) in faq" :key="i">
                <button
                  class="flex w-full items-center justify-between py-3.5 text-left text-sm font-medium text-slate-900 hover:text-brand-700 transition-colors"
                  @click="toggleFaq(i)"
                >
                  {{ item.q }}
                  <svg
                    class="ml-3 h-4 w-4 shrink-0 text-slate-400 transition-transform"
                    :class="openFaq === i ? 'rotate-180' : ''"
                    fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                  </svg>
                </button>
                <p v-if="openFaq === i" class="pb-4 text-sm leading-relaxed text-slate-600">{{ item.a }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
