<script setup lang="ts">
useSeoMeta({
  title: 'How It Works — Academic Writing Service | ResearchPaperMate',
  description: 'How ResearchPaperMate works: submit your brief, get matched with a subject expert, track progress, and download your paper. Takes minutes to start.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/how-it-works' }] })

const steps = [
  {
    number: '01', icon: '📋', title: 'Submit your brief',
    desc: 'Tell us your assignment type, academic level, deadline, word count, and any rubric or source requirements. The more specific your brief, the better matched your writer will be.',
    detail: ['Assignment type — research paper, essay, dissertation, case study, coursework, lab report, etc.', 'Academic level — high school through PhD', 'Deadline — as fast as 2 hours, up to 14 days', 'Word count or page count', 'Rubric, marking criteria, or reading list files', 'Citation style — APA, MLA, Harvard, Chicago, Vancouver, etc.'],
  },
  {
    number: '02', icon: '💳', title: 'Pay securely — then we match you',
    desc: 'Payment is handled by our regulated third-party processor. Once confirmed, we match your order to a subject-specialist writer whose academic background and credential level align with your requirements.',
    detail: ["Master's-level writers for undergraduate work", 'PhD-qualified writers for dissertations and doctoral papers', 'Subject matching — not just level matching', 'You receive an email notification when your writer accepts the order'],
  },
  {
    number: '03', icon: '💬', title: 'Communicate directly with your writer',
    desc: "From the moment a writer accepts, you have a direct message channel in your dashboard. Share additional files, clarify requirements, or check progress — all in real time.",
    detail: ['Direct messaging — no support ticket middlemen', 'Share rubrics, reading lists, or instructor feedback at any time', 'Writer provides progress updates and can flag questions proactively', 'All messages stored for the full order lifecycle'],
  },
  {
    number: '04', icon: '📥', title: 'Download your completed paper',
    desc: 'Your writer uploads the completed paper to your dashboard. Download in Word, PDF, or PowerPoint — your free Turnitin originality report is included.',
    detail: ['Email notification when your paper is ready', 'Download from the Files section of your dashboard', 'Free Turnitin originality report included with every order', 'AI-detection report available free on request', 'Free unlimited revisions within the revision window', 'Grade guarantee — if you receive a lower grade than stated in your brief, contact us within 14 days'],
  },
]

const guarantees = [
  { icon: '🏆', title: 'Grade or money back', desc: 'Receive a lower grade than stated in your brief? We rewrite free or refund you — no questions asked.' },
  { icon: '🎓', title: 'Subject experts matched to your brief', desc: "Master's and PhD writers matched by subject area — not just assigned randomly." },
  { icon: '🤖', title: 'Zero AI — plagiarism-free', desc: 'All papers written by a real human. Free Turnitin and AI-detection reports included.' },
  { icon: '🔒', title: 'Your privacy protected', desc: 'Your name, school, and order details are never shared with third parties.' },
  { icon: '🔄', title: 'Unlimited free revisions', desc: 'Request as many revisions as needed within your revision window at zero extra cost.' },
  { icon: '⚡', title: 'As fast as 2 hours', desc: 'Most papers up to 4 pages can be delivered in 2 hours for urgent orders, 24/7.' },
]
</script>

<template>
  <div class="bg-white">
    <div class="bg-gradient-to-br from-brand-900 to-brand-700 px-4 py-16 text-white sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-300">Simple. Fast. Expert-written.</p>
        <h1 class="font-serif text-4xl font-bold sm:text-5xl">How ResearchPaperMate Works</h1>
        <p class="mx-auto mt-4 max-w-xl text-lg leading-relaxed text-brand-200">
          From submitting your brief to downloading a polished, properly cited paper — the entire process takes minutes to start and is backed by a grade guarantee.
        </p>
        <NuxtLink to="/order" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-10 py-4 text-base font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
          Get started now
          <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
        </NuxtLink>
        <p class="mt-3 text-sm text-brand-300">From $15/page · 100+ subjects · Grade or money back</p>
      </div>
    </div>

    <div class="mx-auto max-w-4xl space-y-12 px-4 py-16 sm:px-6 lg:px-8">
      <div v-for="(step, i) in steps" :key="step.number" class="grid gap-8 md:grid-cols-[72px_1fr]">
        <div class="flex flex-col items-center">
          <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-700 text-xl font-bold text-white shadow-md">{{ step.number }}</div>
          <div v-if="i < steps.length - 1" class="mt-4 h-full w-0.5 bg-brand-100" />
        </div>
        <div class="pb-4">
          <div class="mb-1 text-2xl">{{ step.icon }}</div>
          <h2 class="font-serif text-2xl font-bold text-slate-900">{{ step.title }}</h2>
          <p class="mt-2 text-base leading-relaxed text-slate-600">{{ step.desc }}</p>
          <ul class="mt-4 space-y-2">
            <li v-for="d in step.detail" :key="d" class="flex items-start gap-2.5 text-sm text-slate-600">
              <span class="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-brand-100 text-[9px] font-bold text-brand-700">✓</span>
              {{ d }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="bg-slate-50 px-4 py-16 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-5xl">
        <div class="mb-10 text-center">
          <h2 class="font-serif text-3xl font-bold text-slate-900">Every order, every time</h2>
          <p class="mt-3 text-slate-500">These guarantees apply to every single order — no exceptions.</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="g in guarantees" :key="g.title" class="card">
            <span class="text-3xl">{{ g.icon }}</span>
            <h3 class="mt-3 font-semibold text-slate-900">{{ g.title }}</h3>
            <p class="mt-1 text-sm leading-relaxed text-slate-500">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-brand-700 px-4 py-16 text-center sm:px-6 lg:px-8">
      <h2 class="font-serif text-3xl font-bold text-white">Ready to get started?</h2>
      <p class="mt-3 text-brand-200">Submit your brief in under 5 minutes. A subject expert is ready.</p>
      <div class="mt-8 flex flex-wrap justify-center gap-4">
        <NuxtLink to="/order" class="btn-primary bg-white px-10 py-4 text-base text-brand-700 hover:bg-brand-50 shadow-lg">Place my order — from $15/page</NuxtLink>
        <NuxtLink to="/faq" class="btn-outline border-white/60 px-8 py-4 text-base text-white hover:bg-white/10">Read the FAQ first</NuxtLink>
      </div>
    </div>
  </div>
</template>
