<script setup lang="ts">
import { ArrowRight } from '@lucide/vue'

const app = useAppUrl()

const categories = [
  {
    title: 'Ordering & Pricing',
    faqs: [
      { q: 'How is the price calculated?', a: 'Price depends on three factors: your academic level, your deadline, and the number of pages (1 page = 275 words, double-spaced). Use our calculator for an instant quote — what you see is what you pay.' },
      { q: 'Are there any hidden fees?', a: 'None. Title page, reference list, plagiarism report, and standard formatting are all included free. The calculator shows your total before you pay.' },
      { q: 'Can I get a discount?', a: 'Yes. New customers receive an introductory discount code. Returning customers earn loyalty points on every order that convert to future discounts.' },
      { q: 'What payment methods do you accept?', a: 'Visa, Mastercard, American Express, Discover, and PayPal. All transactions are secured with 256-bit SSL encryption.' },
      { q: 'Is my payment safe?', a: 'Yes. Your payment is held in escrow and only released to your writer after you approve the completed work. You are never charged for undelivered work.' },
      { q: 'Can I cancel my order?', a: 'Yes, before writing begins you can cancel for a full refund. Partial refunds apply depending on how much work has been completed.' },
    ],
  },
  {
    title: 'Quality & Originality',
    faqs: [
      { q: 'Is the work plagiarism-free?', a: 'Yes. Every paper is written from scratch and checked against plagiarism databases before delivery. Your plagiarism report is included free of charge.' },
      { q: 'Do your writers use AI?', a: 'No. Every paper is written by a verified human expert. We provide a free AI-detection certificate on every order upon request.' },
      { q: 'Will my paper meet my grade requirements?', a: 'Our writers are matched to your subject and academic level. If the work does not meet your stated grade requirements, we rewrite it free or refund in full.' },
      { q: 'Who writes my paper?', a: 'A verified expert with a postgraduate degree in your subject. Credentials are checked before a writer handles their first order on the platform.' },
      { q: 'Can I request a specific writer?', a: 'Yes. If you have worked with a writer before and want them again, include their name in your order instructions.' },
      { q: 'What citation styles do you support?', a: 'APA, MLA, Chicago, Harvard, Vancouver, OSCOLA, Turabian, and any other style. Specify your requirements and it will be formatted correctly.' },
    ],
  },
  {
    title: 'Revisions & Guarantees',
    faqs: [
      { q: 'How many revisions can I request?', a: 'Unlimited free revisions within the revision window (14 days for standard papers, 30 days for dissertations). We revise until you are satisfied.' },
      { q: 'What is the grade guarantee?', a: 'If the completed work does not meet your stated grade target, we rewrite it free of charge. If still unsatisfied after revision, you receive a full refund.' },
      { q: 'What if my paper is delivered late?', a: 'Late delivery entitles you to a partial or full refund depending on the delay. We take deadline commitments extremely seriously.' },
      { q: 'Can I ask for a refund?', a: 'Yes. Refunds are issued when the work cannot be completed, does not meet stated requirements after revision, or is delivered late. See our refund policy for full details.' },
    ],
  },
  {
    title: 'Privacy & Security',
    faqs: [
      { q: 'Is my identity kept private?', a: 'Completely. We never share your name, email, order details, or any personal information with third parties under any circumstances.' },
      { q: 'Will my university know I used this service?', a: 'No. We operate with complete confidentiality. Our model papers are for reference and learning — how you use them is entirely between you and your institution.' },
      { q: 'Is my data stored securely?', a: 'Yes. We use industry-standard encryption to protect all personal and payment data. Our data practices comply with applicable privacy laws.' },
      { q: 'Can I delete my account?', a: 'Yes. Contact our support team and we will remove your account and associated data in accordance with our privacy policy.' },
    ],
  },
  {
    title: 'Communication & Support',
    faqs: [
      { q: 'Can I communicate with my writer?', a: 'Yes. Direct messaging with your writer is included at no extra cost. Share files, ask questions, and check progress at any time.' },
      { q: 'Is customer support available 24/7?', a: 'Yes. Our support team is available around the clock via live chat and email. Response time is typically under 5 minutes during peak hours.' },
      { q: 'What if I need to add more instructions after ordering?', a: 'Message your writer directly through the platform at any time. If the scope changes significantly, a price adjustment may apply.' },
    ],
  },
]

useSeoMeta({
  title: 'Frequently Asked Questions | GradeCrest Academic Writing',
  description: 'Answers to the most common questions about GradeCrest — pricing, quality, plagiarism, revisions, privacy, and more.',
})

useSeoBase('https://gradecrest.com/faq')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'FAQ', url: 'https://gradecrest.com/faq' },
])
useFaqLd(categories.flatMap(c => c.faqs))
</script>

<template>
  <div class="pt-16">

    <section class="bg-forest-950 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Frequently Asked Questions</h1>
        <p class="mt-4 text-lg text-slate-300 max-w-xl mx-auto">Everything you need to know about GradeCrest, answered clearly.</p>
      </div>
    </section>

    <section class="bg-white py-14">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 space-y-12">
        <div v-for="cat in categories" :key="cat.title">
          <h2 class="text-lg font-bold text-ink mb-4 pb-2 border-b border-slate-200">{{ cat.title }}</h2>
          <div class="space-y-2.5">
            <details v-for="faq in cat.faqs" :key="faq.q" class="group rounded-2xl border border-slate-200 bg-white shadow-card">
              <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
                {{ faq.q }}
                <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 transition-transform group-open:rotate-45">+</span>
              </summary>
              <p class="px-6 pb-5 text-sm text-graphite leading-relaxed">{{ faq.a }}</p>
            </details>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-mist py-12 text-center">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="text-xl font-bold text-ink">Still have a question?</h2>
        <p class="text-sm text-graphite">Our support team is available 24/7 via live chat.</p>
        <NuxtLink to="/contact" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Contact support <ArrowRight class="size-4" />
        </NuxtLink>
      </div>
    </section>

  </div>
</template>
