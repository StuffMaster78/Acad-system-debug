<script setup lang="ts">
useSeoMeta({
  title: 'Frequently Asked Questions | EssayManiacs',
  description: 'Answers to the most common questions about EssayManiacs — writers, quality, pricing, revisions, privacy, and delivery.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/faq' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        { '@type': 'Question', name: 'Is EssayManiacs legit?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. EssayManiacs is a legitimate academic assistance service. Every writer holds at minimum a Master\'s degree verified against the issuing institution. We have delivered 14,700+ papers with a 4.8/5 average rating.' } },
        { '@type': 'Question', name: 'Who writes my paper?', acceptedAnswer: { '@type': 'Answer', text: 'A subject-specialist writer matched to your exact assignment. Undergraduate papers are handled by Master\'s-level writers. Dissertations and doctoral work go to PhD-qualified writers.' } },
        { '@type': 'Question', name: 'How fast can you deliver?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 2 hours for most standard papers up to 4 pages. Longer papers and dissertations have minimum lead times — use our price calculator for an exact estimate.' } },
        { '@type': 'Question', name: 'What is your grade guarantee?', acceptedAnswer: { '@type': 'Answer', text: 'If you receive a grade lower than stated in your brief, contact us within 14 days with your graded paper and instructor feedback. We rewrite free or issue a full refund.' } },
        { '@type': 'Question', name: 'Is my personal information private?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. Your name, email, school, and order details are never shared, never sold, and never disclosed to your writer beyond what is needed to complete the assignment.' } },
      ],
    }),
  }],
})

const sections = [
  {
    heading: 'About the Service',
    items: [
      { q: 'Is EssayManiacs legit?', a: 'Yes. EssayManiacs is a legitimate academic assistance platform. Every writer holds at minimum a Master\'s degree that we verify before they can accept orders. We have delivered 14,700+ papers with a 4.8/5 average rating.' },
      { q: 'What exactly do you provide?', a: 'Custom academic papers written from scratch by subject-specialist writers — research papers, essays, dissertations, case studies, coursework, lab reports, presentations, and more. Papers are model documents for study and reference, provided in the same spirit as a writing centre or tutoring service.' },
      { q: 'Is using an academic writing service legal?', a: 'Yes. Commissioning a model paper for reference and study is legal. Every order includes an academic-use acknowledgement. Submitting it as your own original work where prohibited by your institution is a violation of their academic integrity policy, not of law.' },
      { q: 'Do you work with international students?', a: 'Yes. We serve students across the US, UK, Canada, Australia, and internationally. Our writers are familiar with APA, MLA, Harvard, Chicago, and all major citation styles.' },
    ],
  },
  {
    heading: 'Writers & Quality',
    items: [
      { q: 'Who writes my paper?', a: 'A subject-specialist writer matched to your assignment type and academic level. Undergraduate papers go to Master\'s-level writers. Dissertations and doctoral work go to PhD-qualified specialists. We match based on subject area, not just general academic level.' },
      { q: 'How do you vet your writers?', a: 'Four stages: (1) degree verification against the issuing institution, (2) subject knowledge assessment in their field, (3) sample paper review by our editorial team, (4) supervised trial period on the first five orders. We reject over 95% of applicants.' },
      { q: 'Will my paper be original — not AI-generated?', a: 'Yes. Every paper is written from scratch by a real human writer. We do not use AI writing tools. A free AI-detection report is available on any order — just request it.' },
      { q: 'Will my paper pass Turnitin?', a: 'Yes. A free Turnitin originality report is included with every order. Papers are written to your specific brief with no template reuse.' },
    ],
  },
  {
    heading: 'Ordering & Communication',
    items: [
      { q: 'How do I place an order?', a: 'Click "Order Now" and fill in your brief: assignment type, academic level, deadline, word count, and any rubric or source requirements. Pay securely — your order is then matched with a qualified writer.' },
      { q: 'Can I communicate with my writer?', a: 'Yes. From the moment a writer accepts your order, you have a direct message channel in your dashboard. Share additional instructions, rubric files, or feedback at any time.' },
      { q: 'What if I need to change requirements after ordering?', a: 'Contact support as soon as possible — changes are free before the writer has started. Changes mid-order are assessed case-by-case and may affect delivery time.' },
      { q: 'How do I receive my completed paper?', a: 'Your writer uploads the completed paper to your dashboard. You receive an email notification and can download the file (Word, PDF, or other formats) from the Files section of your account.' },
    ],
  },
  {
    heading: 'Delivery & Deadlines',
    items: [
      { q: 'How fast can you deliver?', a: 'As fast as 2 hours for most standard papers up to 4 pages. Longer papers, dissertations, and complex projects have minimum lead times. Use the price calculator for an exact estimate for your specific order.' },
      { q: 'What happens if my paper is late?', a: 'If we deliver later than the agreed deadline, you are entitled to a partial or full refund proportional to the delay. See our Refund Policy for the full schedule.' },
      { q: 'Can you handle urgent orders?', a: 'Yes. Orders with 2–12 hour deadlines carry a rush surcharge but are always available. For genuine emergencies, WhatsApp or live chat gives the fastest response.' },
    ],
  },
  {
    heading: 'Revisions & Refunds',
    items: [
      { q: 'How many revisions do I get?', a: 'Unlimited free revisions within the revision window (equal to the original delivery time, minimum 24 hours, maximum 30 days). All revisions handled by your original writer.' },
      { q: 'What is your grade guarantee?', a: 'If you receive a grade lower than stated in your brief, contact us within 14 days with the graded paper and instructor feedback. We rewrite the relevant sections at no charge or issue a partial or full refund.' },
      { q: 'What if I am not satisfied with my paper?', a: 'Request a revision first — most quality concerns are resolved in one revision round. If after revision you are still dissatisfied within the terms of our grade guarantee, email support@essaymaniacs.com with your order number and details.' },
    ],
  },
  {
    heading: 'Privacy & Payment',
    items: [
      { q: 'Is my personal information kept private?', a: 'Yes. Your name, email, school, and order details are never sold, shared, or disclosed to third parties. Your writer receives only the assignment brief — not your name or contact information.' },
      { q: 'How do I pay?', a: 'We accept credit and debit cards, bank transfers, and M-Pesa. All payments are processed securely through our regulated payment processor. We never store your card details.' },
      { q: 'What does my statement show?', a: 'Your bank statement will show the payment processor name, not EssayManiacs — for your privacy.' },
    ],
  },
]

const openItems = ref<Record<string, boolean>>({})
function toggle(key: string) { openItems.value[key] = !openItems.value[key] }
</script>

<template>
  <div class="bg-white">
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <Breadcrumbs :items="[{ label: 'FAQ' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Frequently Asked Questions</h1>
        <p class="mx-auto mt-3 max-w-xl text-base text-slate-500">
          Everything you need to know about EssayManiacs.
          Can't find your answer?
          <NuxtLink to="/contact" class="font-semibold text-brand-600 hover:underline">Message us</NuxtLink> — we reply within 1 hour.
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-3xl space-y-10 px-4 py-12 sm:px-6 lg:px-8">
      <div v-for="section in sections" :key="section.heading">
        <h2 class="mb-1 border-b border-slate-100 pb-3 font-serif text-xl font-bold text-slate-900">{{ section.heading }}</h2>
        <dl class="divide-y divide-slate-100">
          <div v-for="(item, i) in section.items" :key="i">
            <button class="flex w-full items-start justify-between py-4 text-left" @click="toggle(`${section.heading}-${i}`)">
              <span class="pr-6 font-semibold leading-snug text-slate-900">{{ item.q }}</span>
              <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 transition-transform" :class="openItems[`${section.heading}-${i}`] ? 'rotate-45' : ''">
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
              </span>
            </button>
            <Transition enter-active-class="transition-all duration-200 ease-out" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-150 ease-in" leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-1">
              <dd v-if="openItems[`${section.heading}-${i}`]" class="pb-5 text-sm leading-7 text-slate-600">{{ item.a }}</dd>
            </Transition>
          </div>
        </dl>
      </div>
    </div>

    <div class="border-t border-slate-100 bg-slate-50 px-4 py-12 text-center sm:px-6 lg:px-8">
      <h2 class="font-serif text-2xl font-bold text-slate-900">Still have a question?</h2>
      <p class="mt-2 text-slate-500">Our support team responds within 1 hour, 7 days a week.</p>
      <div class="mt-6 flex flex-wrap justify-center gap-4">
        <NuxtLink to="/contact" class="btn-primary px-8 py-3">Contact support</NuxtLink>
        <NuxtLink to="/order" class="btn-outline px-8 py-3">Place an order</NuxtLink>
      </div>
    </div>
  </div>
</template>
