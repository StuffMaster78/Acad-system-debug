<script setup lang="ts">
useSeoMeta({
  title: 'FAQ | Writers Creek',
  description: 'Frequently asked questions about writing for Writers Creek — qualification requirements, earnings, payouts, assignment process, and more.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const faqs = [
  {
    category: 'Eligibility',
    items: [
      {
        q: 'How do I qualify to write?',
        a: "You need a postgraduate degree (Master's or PhD) or active professional credentials in your subject area. We verify qualifications before activating any writer account.",
      },
      {
        q: 'Can I write in multiple subjects?',
        a: 'Yes. You can list multiple subject areas at application. Assignments will be matched to your verified credentials — you will not be assigned work outside your stated specialisms.',
      },
      {
        q: 'I have a Bachelor\'s degree. Can I still apply?',
        a: "Currently we require postgraduate credentials or equivalent professional credentials (e.g. RN, CPA, licensed engineer). Bachelor's-only applicants are not accepted at this time.",
      },
      {
        q: 'Is there an age requirement?',
        a: 'You must be at least 18 years old to create a writer account and receive payment.',
      },
    ],
  },
  {
    category: 'Earnings and payouts',
    items: [
      {
        q: 'How much can I earn?',
        a: 'Entry writers earn $18–$22 per page. Standard writers earn $24–$28. Senior writers earn $30–$36. Expert writers earn $38–$45. Rates increase as you complete assignments and maintain high ratings.',
      },
      {
        q: 'When do I get paid?',
        a: 'Bi-weekly, without fail. Payments are released every two weeks once clients have approved the relevant work. You choose between direct bank transfer and PayPal at sign-up.',
      },
      {
        q: 'Is there a minimum payout amount?',
        a: 'Yes — $20 minimum to avoid excessive processing fees. Earnings below this threshold roll over to the next bi-weekly cycle.',
      },
      {
        q: 'Does the platform take a commission?',
        a: 'The per-page rate you see is what you receive. We do not take a further commission from your listed rate — what you see is what lands in your account.',
      },
    ],
  },
  {
    category: 'Assignments and workflow',
    items: [
      {
        q: 'How many assignments can I take?',
        a: "There is no minimum or maximum. Take as many or as few as you want. The platform does not penalise writers for low volume — quality is what matters, not output count.",
      },
      {
        q: 'Can I reject an assignment after accepting it?',
        a: 'You can withdraw from an assignment before you start writing. Once you have submitted work, withdrawal is not available. Repeated pre-start withdrawals may affect your assignment access.',
      },
      {
        q: 'What happens if a client requests revisions?',
        a: 'Revisions within the stated brief are part of the job. If a client requests something outside the original scope — a new section, a different argument, a substantially expanded word count — that is flagged and handled separately. You will not be asked to do unlimited unpaid rework.',
      },
      {
        q: 'What subjects are available?',
        a: 'We have demand across over 100 subjects including nursing, business, psychology, law, history, literature, finance, statistics, biology, chemistry, sociology, philosophy, engineering, education, public health, political science, economics, and marketing.',
      },
    ],
  },
  {
    category: 'Privacy and identity',
    items: [
      {
        q: 'Is my personal information kept private?',
        a: 'Yes. Your full name, credentials, and contact details are never shared with clients. You interact through the platform under your writer profile name only.',
      },
      {
        q: 'Will clients know my real name?',
        a: 'No. Clients see your writer profile name. Your real name and personal details remain confidential throughout the engagement.',
      },
      {
        q: 'How are my credentials stored?',
        a: 'Credential documents submitted during vetting are stored securely and used only for verification purposes. They are not shared with clients or third parties.',
      },
    ],
  },
]
</script>

<template>
  <div class="bg-white">

    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-900 px-4 py-14 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'FAQ' }]" />
        <h1 class="mt-5 text-4xl font-bold text-white sm:text-5xl">Frequently asked questions</h1>
        <p class="mt-4 text-lg text-slate-300">Everything a prospective Writers Creek writer needs to know.</p>
      </div>
    </div>

    <!-- FAQ sections -->
    <div class="mx-auto max-w-3xl px-4 py-14 sm:px-6 lg:px-8">
      <div class="space-y-14">
        <div v-for="section in faqs" :key="section.category">
          <h2 class="mb-6 text-xl font-bold text-slate-900">{{ section.category }}</h2>
          <div class="divide-y divide-slate-100">
            <details
              v-for="faq in section.items"
              :key="faq.q"
              class="group py-5"
            >
              <summary class="flex cursor-pointer items-center justify-between gap-4 text-base font-semibold text-slate-900 marker:hidden [&::-webkit-details-marker]:hidden">
                {{ faq.q }}
                <svg class="h-5 w-5 shrink-0 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </summary>
              <p class="mt-3 text-sm leading-relaxed text-slate-600">{{ faq.a }}</p>
            </details>
          </div>
        </div>
      </div>

      <!-- Contact CTA -->
      <div class="mt-14 rounded-2xl border border-slate-100 bg-slate-50 p-8 text-center">
        <p class="font-semibold text-slate-900">Still have questions?</p>
        <p class="mt-1 text-sm text-slate-600">Our team responds within one business day.</p>
        <NuxtLink to="/contact" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-700">
          Contact us
        </NuxtLink>
      </div>
    </div>

  </div>
</template>
