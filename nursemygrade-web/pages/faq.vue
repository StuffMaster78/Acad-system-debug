<script setup lang="ts">
useSeoMeta({
  title: 'Frequently Asked Questions | NurseMyGrade',
  description: 'Answers to the most common questions about NurseMyGrade nursing paper services — quality, privacy, writers, revisions, pricing, and delivery.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/faq' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Is NurseMyGrade legit?',
          acceptedAnswer: { '@type': 'Answer', text: 'Yes. NurseMyGrade is a legitimate nursing academic assistance service staffed entirely by credentialed BSN, MSN, and DNP nurses. Every writer holds an active nursing qualification that we verify before they can accept orders.' },
        },
        {
          '@type': 'Question',
          name: 'Who writes my nursing paper?',
          acceptedAnswer: { '@type': 'Answer', text: 'A qualified nurse matched to your subject and academic level. BSN writers handle undergraduate work; MSN writers handle graduate-level papers; DNP writers handle doctoral projects and capstones. All writers are vetted through a 4-stage process.' },
        },
        {
          '@type': 'Question',
          name: 'How fast can you deliver a nursing paper?',
          acceptedAnswer: { '@type': 'Answer', text: 'As fast as 3 hours for most standard nursing papers (1–4 pages). Longer papers, dissertations, and simulation help (Shadow Health, iHuman) have minimum lead times — use the calculator on our pricing page for an exact estimate.' },
        },
        {
          '@type': 'Question',
          name: 'What is your grade guarantee?',
          acceptedAnswer: { '@type': 'Answer', text: 'If your paper is delivered and you receive a grade lower than stated in your order brief, contact us within 14 days with the graded paper and instructor feedback. We will rewrite at no charge or issue a full refund.' },
        },
        {
          '@type': 'Question',
          name: 'Is my personal information kept private?',
          acceptedAnswer: { '@type': 'Answer', text: 'Yes. Your name, email, school, and order details are never shared with third parties, never resold, and never disclosed to your writer beyond what is needed to complete the assignment. Payments are processed by a regulated third-party processor.' },
        },
      ],
    }),
  }],
})

const sections = [
  {
    heading: 'About the Service',
    items: [
      {
        q: 'Is NurseMyGrade legit?',
        a: 'Yes. NurseMyGrade is a legitimate nursing academic assistance platform. Every writer holds a current nursing qualification — BSN at minimum. We verify degrees, licences, and clinical credentials before any writer accepts an order. We have delivered 9,800+ nursing papers with a 4.98/5 average rating.',
      },
      {
        q: 'What exactly do you provide?',
        a: 'We provide custom nursing papers written from scratch by credentialed nurse writers — essays, care plans, SOAP notes, capstone projects, dissertations, research papers, concept maps, and more. Papers are model documents for study and reference, provided in the same spirit as a writing centre or tutoring service.',
      },
      {
        q: 'Is using a nursing writing service legal?',
        a: 'Yes. Commissioning a model paper for reference and study purposes is legal. Every order includes an academic-use acknowledgement. How you choose to use the material is your responsibility — submitting it as your own original work where prohibited by your institution is a violation of their academic integrity policy, not of law.',
      },
      {
        q: 'Do you work with students outside the US?',
        a: 'Yes. We work with nursing students across the US, UK, Canada, Australia, and internationally. Our writers are familiar with the nursing curricula, clinical frameworks, and citation standards used in all major markets.',
      },
    ],
  },
  {
    heading: 'Writers & Quality',
    items: [
      {
        q: 'Who writes my nursing paper?',
        a: 'A nurse matched to your subject area and academic level. BSN-qualified nurses handle undergraduate work; MSN nurses handle graduate-level papers; DNP and PhD nurses handle doctoral capstone projects and dissertations. Writers are matched based on speciality (Med-Surg, ICU, OB, Psych, FNP, etc.) as well as credential level.',
      },
      {
        q: 'How do you vet your nurse writers?',
        a: 'Four stages: (1) nursing licence and degree verification against the issuing institution, (2) clinical knowledge assessment covering NANDA-I, ADPIE, pharmacology, and documentation, (3) sample nursing paper review by our senior editors, (4) supervised trial period on the first five orders. We reject over 95% of applicants.',
      },
      {
        q: 'Will my paper be original — not AI-generated?',
        a: 'Yes. Every paper is written from scratch by a real nurse. We do not use AI writing tools. An AI-detection report is available free of charge on any order — just request it when you place the order or via dashboard message.',
      },
      {
        q: 'Will my paper pass Turnitin?',
        a: 'Yes. A free Turnitin originality report is included with every order. Papers are written from scratch to your specific brief, which means there is no template reuse and no recycled content. Each paper is unique to your assignment.',
      },
      {
        q: 'Can I see a sample before I order?',
        a: 'Yes. Sample nursing papers (care plans, SOAP notes, essays) are available on our blog and on individual service pages. You can also request a sample from our support team before placing your order.',
      },
    ],
  },
  {
    heading: 'Ordering & Communication',
    items: [
      {
        q: 'How do I place an order?',
        a: 'Click "Order Now" and fill in your nursing brief: assignment type, academic level, deadline, word count, and any rubric or clinical scenario details. Pay securely — your order is then matched with a qualified nurse writer. You receive a notification when a writer accepts.',
      },
      {
        q: 'Can I talk directly with my nurse writer?',
        a: 'Yes. From the moment a writer accepts your order, you can message them directly through the dashboard. Share your rubric, clinical scenario details, instructor feedback, or any additional materials. Direct, ongoing communication is included at no extra cost.',
      },
      {
        q: 'What if I need to change my requirements after placing the order?',
        a: 'Contact support as soon as possible — changes are free before the writer has started. Changes mid-order are assessed on a case-by-case basis and may affect the delivery time. Changes that substantially expand the scope of the order (new rubric sections, significant word count increases) may be treated as a new order.',
      },
      {
        q: 'How do I receive my completed paper?',
        a: 'Your nurse writer uploads the completed paper to your dashboard. You receive an email notification and can download the file directly (Word, PDF, or PowerPoint depending on the assignment type). All files are accessible from the Files section of your account.',
      },
    ],
  },
  {
    heading: 'Delivery & Deadlines',
    items: [
      {
        q: 'How fast can you deliver a nursing paper?',
        a: 'As fast as 3 hours for most standard nursing papers (essays, SOAP notes, care plans up to 4 pages). Longer papers, dissertations, and simulation help (Shadow Health DCEs, iHuman cases) have minimum lead times. Use the price calculator for an exact delivery estimate for your specific order.',
      },
      {
        q: 'What happens if my paper is delivered late?',
        a: 'If we deliver later than the agreed deadline, you are entitled to a partial or full refund proportional to the delay — see our Refund Policy for the full schedule. Delays caused by late submission of your rubric or clinical scenario details do not qualify for this guarantee.',
      },
      {
        q: 'Can you handle urgent nursing orders?',
        a: 'Yes. Urgent orders (3–12 hour deadlines) carry a rush surcharge but are always available. For genuine emergencies, WhatsApp us directly — fastest response for urgent turnarounds.',
      },
    ],
  },
  {
    heading: 'Revisions & Refunds',
    items: [
      {
        q: 'How many revisions do I get?',
        a: 'Unlimited free revisions within the revision window (equal to the original delivery time, minimum 24 hours, maximum 30 days). Revision requests must fall within the original scope of the brief. All revisions are handled by your original nurse writer.',
      },
      {
        q: 'What is your grade guarantee?',
        a: 'If you receive a grade lower than stated in your order brief and the shortfall is attributable to our work, contact us within 14 days with the graded paper and instructor feedback. We will rewrite the relevant sections at no charge or issue a partial or full refund.',
      },
      {
        q: 'What if I am not satisfied with the paper?',
        a: 'Request a revision first — most quality concerns are resolved through revision. If after revision you are still dissatisfied and the issue falls within the scope of our grade guarantee, email support@nursemygrade.com with your order number and details. We resolve all cases within 3 business days.',
      },
    ],
  },
  {
    heading: 'Privacy & Payment',
    items: [
      {
        q: 'Is my personal information kept private?',
        a: 'Yes. Your name, email, school, and order details are never sold, shared, or disclosed to third parties. Your nurse writer receives only the assignment brief — not your name or contact information. Payment is handled by a regulated third-party processor; we never see or store your card details.',
      },
      {
        q: 'How do I pay?',
        a: 'We accept credit and debit cards, and bank transfers. All payments are processed securely through our regulated payment processor. Your statement will show the processor name. We also accept M-Pesa for users in Kenya and East Africa.',
      },
      {
        q: 'For online class help — are my login details safe?',
        a: 'Class coordinators sign NDAs and access your portal through a VPN to protect your location and identity. Coordinator access is limited strictly to the course tasks specified in your order. We never store login credentials beyond the active order period.',
      },
    ],
  },
]

const openItems = ref<Record<string, boolean>>({})
function toggle(key: string) {
  openItems.value[key] = !openItems.value[key]
}
</script>

<template>
  <div class="bg-white">

    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <Breadcrumbs :items="[{ label: 'FAQ' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
          Frequently Asked Questions
        </h1>
        <p class="mx-auto mt-3 max-w-xl text-base text-slate-500">
          Everything you need to know about NurseMyGrade nursing paper services.
          Can't find your answer? <NuxtLink to="/contact" class="font-semibold text-brand-600 hover:underline">Message us</NuxtLink> — we reply within 1 hour.
        </p>
      </div>
    </div>

    <!-- FAQ sections -->
    <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8 space-y-10">
      <div v-for="section in sections" :key="section.heading">

        <!-- Section heading -->
        <h2 class="font-serif text-xl font-bold text-slate-900 border-b border-slate-100 pb-3 mb-1">
          {{ section.heading }}
        </h2>

        <!-- Accordion items -->
        <dl class="divide-y divide-slate-100">
          <div v-for="(item, i) in section.items" :key="i">
            <button
              class="flex w-full items-start justify-between py-4 text-left"
              @click="toggle(`${section.heading}-${i}`)"
            >
              <span class="pr-6 font-semibold text-slate-900 leading-snug">{{ item.q }}</span>
              <span
                class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 transition-transform"
                :class="openItems[`${section.heading}-${i}`] ? 'rotate-45' : ''"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
              </span>
            </button>
            <Transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-1"
            >
              <dd v-if="openItems[`${section.heading}-${i}`]" class="pb-5 text-sm leading-7 text-slate-600">
                {{ item.a }}
              </dd>
            </Transition>
          </div>
        </dl>
      </div>
    </div>

    <!-- Bottom CTA -->
    <div class="border-t border-slate-100 bg-slate-50 px-4 py-12 text-center sm:px-6 lg:px-8">
      <h2 class="font-serif text-2xl font-bold text-slate-900">Still have a question?</h2>
      <p class="mt-2 text-slate-500">Our support team responds within 1 hour, 7 days a week.</p>
      <div class="mt-6 flex flex-wrap justify-center gap-4">
        <NuxtLink to="/contact" class="btn-primary px-8 py-3">
          Contact support
        </NuxtLink>
        <NuxtLink to="/order" class="btn-outline px-8 py-3">
          Place an order
        </NuxtLink>
      </div>
    </div>

  </div>
</template>
