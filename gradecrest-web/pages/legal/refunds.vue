<script setup lang="ts">
import { ArrowRight, CheckCircle2 } from '@lucide/vue'

useSeoMeta({
  title: 'Refund Policy | GradeCrest',
  description: 'GradeCrest Refund Policy — full and partial refund conditions, how to request a refund, and our grade guarantee.',
})
useSeoBase('https://gradecrest.com/legal/refunds')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Refund Policy', url: 'https://gradecrest.com/legal/refunds' },
])

const fullRefunds = [
  'Your order is cancelled before any writing has begun',
  'We are unable to find a suitable writer for your order',
  'The completed work does not meet your requirements after a full revision cycle',
  'Your paper is delivered more than 24 hours after your stated deadline',
]

const partialRefunds = [
  'Cancellation after writing has started but before completion — the refund is proportional to the work remaining',
  'Late delivery of less than 24 hours — a proportional deduction based on the delay',
  'Part of a multi-part order is unsatisfactory after revision — a refund for the affected portion only',
]

const notEligible = [
  'Change of mind after the paper has been delivered and approved',
  'Requests based on a grade received at your institution (we guarantee the work meets your stated brief, not a specific institutional outcome)',
  'Requests submitted more than 30 days after delivery',
  'Orders where the brief was changed significantly after writing began',
]
</script>

<template>
  <div class="pt-16">

    <section class="bg-navy-900 py-14 relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">Legal</p>
        <h1 class="text-3xl font-bold text-white sm:text-4xl">Refund Policy</h1>
        <p class="mt-3 text-slate-400 text-sm">Effective date: 1 January 2024</p>
      </div>
    </section>

    <section class="bg-white py-14">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 space-y-10">

        <!-- Intro -->
        <div class="rounded-2xl border border-gc-200 bg-gc-50 p-6">
          <h2 class="text-base font-bold text-ink mb-2">Our commitment</h2>
          <p class="text-sm text-graphite leading-relaxed">
            Your payment is held in escrow and only released to your writer after you approve the work. If the work does not meet your stated requirements, we first offer a full revision cycle at no cost. If the work still does not meet your brief after revision, we issue a refund. We do not keep money for work that fails to deliver.
          </p>
        </div>

        <!-- Full refunds -->
        <div>
          <h2 class="text-base font-bold text-ink mb-4">Full refund conditions</h2>
          <p class="text-sm text-graphite mb-4">You are entitled to a full refund in any of the following circumstances:</p>
          <ul class="space-y-2.5">
            <li v-for="item in fullRefunds" :key="item" class="flex items-start gap-3 text-sm text-graphite">
              <CheckCircle2 class="size-4 text-emerald-500 shrink-0 mt-0.5" />
              {{ item }}
            </li>
          </ul>
        </div>

        <!-- Partial refunds -->
        <div>
          <h2 class="text-base font-bold text-ink mb-4">Partial refund conditions</h2>
          <p class="text-sm text-graphite mb-4">Partial refunds apply in the following situations:</p>
          <ul class="space-y-2.5">
            <li v-for="item in partialRefunds" :key="item" class="flex items-start gap-3 text-sm text-graphite">
              <CheckCircle2 class="size-4 text-amber-500 shrink-0 mt-0.5" />
              {{ item }}
            </li>
          </ul>
        </div>

        <!-- Not eligible -->
        <div>
          <h2 class="text-base font-bold text-ink mb-4">Not eligible for refund</h2>
          <ul class="space-y-2.5">
            <li v-for="item in notEligible" :key="item" class="flex items-start gap-3 text-sm text-graphite">
              <span class="mt-1.5 size-1.5 rounded-full bg-slate-400 shrink-0" />
              {{ item }}
            </li>
          </ul>
        </div>

        <!-- Process -->
        <div>
          <h2 class="text-base font-bold text-ink mb-4">How to request a refund</h2>
          <div class="space-y-4">
            <div v-for="(step, i) in [
              { title: 'Contact support',    desc: 'Reach our support team via live chat or email at support@gradecrest.com. Include your order number and the reason for your request.' },
              { title: 'Revision first',     desc: 'For quality issues, we will first arrange a full revision with your writer at no cost. This is usually the fastest route to a satisfactory outcome.' },
              { title: 'Refund decision',    desc: 'If the issue cannot be resolved through revision, our team will assess your request and issue a refund within 5–7 business days.' },
              { title: 'Payment returned',   desc: 'Refunds are returned to the original payment method. Processing time depends on your card issuer or PayPal — typically 3–10 business days.' },
            ]" :key="step.title" class="flex gap-4">
              <span class="flex size-7 shrink-0 items-center justify-center rounded-full border-2 border-gc-600 text-xs font-bold text-gc-600 mt-0.5">{{ i + 1 }}</span>
              <div>
                <p class="text-sm font-semibold text-ink">{{ step.title }}</p>
                <p class="mt-0.5 text-sm text-graphite leading-relaxed">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Contact CTA -->
        <div class="rounded-2xl border border-slate-200 bg-mist p-6 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p class="text-sm font-semibold text-ink">Questions about a refund?</p>
            <p class="text-sm text-graphite mt-0.5">Our support team is available 24/7 and responds within 5 minutes.</p>
          </div>
          <NuxtLink to="/contact" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors shrink-0">
            Contact support <ArrowRight class="size-4" />
          </NuxtLink>
        </div>

        <!-- Links -->
        <div class="flex flex-wrap gap-4 border-t border-slate-200 pt-8 text-sm text-graphite">
          <NuxtLink to="/legal/terms" class="hover:text-gc-600 transition-colors">Terms of Service</NuxtLink>
          <NuxtLink to="/legal/privacy" class="hover:text-gc-600 transition-colors">Privacy Policy</NuxtLink>
          <NuxtLink to="/contact" class="hover:text-gc-600 transition-colors">Contact Us</NuxtLink>
        </div>

      </div>
    </section>

  </div>
</template>
