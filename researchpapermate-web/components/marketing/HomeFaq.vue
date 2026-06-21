<script setup lang="ts">
const faqs = [
  {
    q: 'Is it legal to use this service?',
    a: 'Yes. We provide model papers and reference material for educational purposes — similar to tutoring, sample essays, or study guides. At checkout, you acknowledge the intended academic use. How you incorporate the work into your own studies is your responsibility.',
  },
  {
    q: 'Will my paper pass Turnitin or plagiarism checks?',
    a: 'Every paper is written from scratch by a human expert and run through plagiarism detection before delivery. A free plagiarism report is included with every order. We guarantee zero AI-generated content — your paper is 100% human-written.',
  },
  {
    q: 'How fast can you deliver?',
    a: 'Our fastest turnaround is 2 hours for short assignments. Most orders are matched with an available expert within minutes of being placed. Select your deadline at checkout and we will confirm availability before you pay.',
  },
  {
    q: 'How do I know my writer is qualified?',
    a: 'We verify every writer\'s academic credentials before they join the platform. All writers hold at minimum a Master\'s degree in their subject area; PhD-level writers are available for doctoral work. You can see each writer\'s profile, subject specialisation, rating, and completed order count before and after assignment.',
  },
  {
    q: 'What if I\'m not happy with the paper?',
    a: 'Free unlimited revisions are included within the revision window — 7 days for standard orders, 14 days for dissertations. If after revisions the paper still falls short of your stated requirements, you are entitled to a full or partial refund under our grade-or-money-back guarantee.',
  },
  {
    q: 'How does the payment and escrow work?',
    a: 'You pay at checkout and your funds are held securely. The writer receives payment only after you approve the completed paper. This means there is no risk: if the work is not delivered or does not meet your requirements, your money is protected.',
  },
]

const open = ref<number | null>(null)

function toggle(i: number) {
  open.value = open.value === i ? null : i
}
</script>

<template>
  <section class="bg-parchment-100 border-y border-parchment-300">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">Frequently asked questions</h2>
        <p class="section-sub">Everything you want to know before placing your first order.</p>
      </div>

      <dl class="mx-auto mt-10 max-w-3xl overflow-hidden rounded-2xl border border-parchment-300 bg-white shadow-sm">
        <div v-for="(faq, i) in faqs" :key="faq.q" class="border-b border-parchment-200 last:border-b-0">
          <dt>
            <button
              class="flex w-full items-center justify-between gap-4 px-6 py-5 text-left transition-colors hover:bg-parchment-50"
              @click="toggle(i)"
            >
              <span class="font-semibold text-ink-DEFAULT">{{ faq.q }}</span>
              <svg
                class="h-5 w-5 shrink-0 text-ink-muted transition-transform duration-200"
                :class="open === i ? 'rotate-180' : ''"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
          </dt>
          <dd v-show="open === i" class="border-t border-parchment-200 bg-parchment-50/60 px-6 pb-5 pt-4 text-sm text-ink-secondary leading-relaxed">
            {{ faq.a }}
          </dd>
        </div>
      </dl>

      <p class="mt-8 text-center text-sm text-ink-muted">
        Still have questions?
        <NuxtLink href="/contact" class="font-medium text-amber-700 hover:underline">Talk to our team →</NuxtLink>
      </p>
    </div>
  </section>
</template>
