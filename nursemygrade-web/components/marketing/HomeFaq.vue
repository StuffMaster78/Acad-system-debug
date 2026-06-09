<script setup lang="ts">
const faqs = [
  {
    q: 'Is using NurseMyGrade legal?',
    a: 'Yes. We provide model nursing papers and academic assistance — similar to tutoring or using a writing centre. Thousands of nursing students use professional writing services every semester to manage academic demands alongside gruelling clinical hours. The work we deliver is a reference and study tool.',
  },
  {
    q: 'Are your writers actually nurses?',
    a: 'Every writer on our platform holds at minimum a BSN degree with active clinical experience. Many hold MSN or DNP credentials. We verify all credentials during our vetting process — when you see "DNP, FNP-BC" on a writer profile, that\'s real and confirmed.',
  },
  {
    q: 'Will my nursing paper be plagiarism-free?',
    a: 'Every paper is written from scratch for your specific brief and run through Turnitin before delivery. A free plagiarism report is included with every order. We also guarantee zero AI-generated content — every word is human-written by a qualified nurse.',
  },
  {
    q: 'How fast can you deliver a nursing paper?',
    a: 'We can deliver most nursing papers in as little as 3 hours for urgent orders. Standard turnaround is 24–72 hours. Capstone projects and dissertations require more lead time — contact us to discuss your deadline.',
  },
  {
    q: 'What citation style do you use for nursing papers?',
    a: 'Most nursing programmes use APA 7th edition, which all our writers know thoroughly. We also handle AMA, MLA, Chicago, and Harvard where required. Just specify your required style in the order form.',
  },
  {
    q: 'What if I\'m not happy with the delivered paper?',
    a: 'You\'re entitled to unlimited free revisions within the revision window (7 days for standard orders, 14 days for capstone/dissertations). If after revisions the paper still doesn\'t meet your original brief, we\'ll issue a full refund — no questions asked.',
  },
]

const open = ref<number | null>(null)

function toggle(i: number) {
  open.value = open.value === i ? null : i
}
</script>

<template>
  <section class="bg-slate-50">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">Frequently asked questions</h2>
        <p class="section-sub">Everything nursing students want to know before placing their first order.</p>
      </div>

      <dl class="mx-auto mt-10 max-w-3xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div v-for="(faq, i) in faqs" :key="faq.q" class="border-b border-slate-100 last:border-b-0">
          <dt>
            <button
              class="flex w-full items-center justify-between gap-4 px-6 py-5 text-left transition-colors hover:bg-slate-50"
              @click="toggle(i)"
            >
              <span class="font-semibold text-slate-900">{{ faq.q }}</span>
              <svg
                class="h-5 w-5 shrink-0 text-slate-400 transition-transform duration-200"
                :class="open === i ? 'rotate-180' : ''"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
          </dt>
          <dd v-show="open === i" class="border-t border-slate-100 bg-slate-50/60 px-6 pb-5 pt-4 text-sm text-slate-600 leading-relaxed">
            {{ faq.a }}
          </dd>
        </div>
      </dl>

      <p class="mt-8 text-center text-sm text-slate-500">
        Still have questions?
        <NuxtLink href="/contact" class="font-medium text-brand-600 hover:underline">Talk to our team →</NuxtLink>
      </p>
    </div>
  </section>
</template>
