<script setup lang="ts">
import {
  Bot, ClipboardList, CreditCard, Download, Lock,
  MessageSquare, RefreshCw, Stethoscope, Trophy, Zap,
} from '@lucide/vue'

useSeoMeta({
  title: 'How It Works — Nursing Paper Writing Service | NurseMyGrade',
  description: 'How NurseMyGrade works: submit your nursing brief, get matched with a qualified nurse writer, track progress, and download your completed paper. Takes minutes to start.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/how-it-works' }],
})

const steps = [
  {
    number: '01',
    icon: ClipboardList,
    title: 'Submit your nursing brief',
    desc: 'Tell us your assignment type (care plan, SOAP note, essay, capstone…), your programme level, deadline, word count, and any rubric or clinical scenario details. The more specific your brief, the better matched your writer will be.',
    detail: [
      'Assignment type — care plan, SOAP note, essay, research paper, dissertation, simulation help, etc.',
      'Academic level — ADN, BSN, RN-to-BSN, MSN, DNP',
      'Deadline — as fast as 3 hours, or up to 14 days',
      'Word count or page count',
      'Rubric, marking criteria, or clinical scenario files',
      'Any special instructions — NANDA format, specific APA 7th requirements, instructor preferences',
    ],
  },
  {
    number: '02',
    icon: CreditCard,
    title: 'Pay securely — then we match you',
    desc: 'Payment is handled by our regulated third-party processor. Once confirmed, our matching system identifies nurse writers whose clinical speciality and credential level align with your assignment and assigns the best available match.',
    detail: [
      'BSN-qualified nurses for undergraduate ADN and BSN coursework',
      'MSN-qualified nurses for graduate-level papers and MSN capstones',
      'DNP or PhD nurses for doctoral projects, DNP capstones, and dissertations',
      'Specialty matching — Med-Surg, ICU, OB, Psych, Paeds, FNP, Community Health',
      'You receive an email notification when your writer accepts the order',
    ],
  },
  {
    number: '03',
    icon: MessageSquare,
    title: 'Communicate directly with your nurse writer',
    desc: 'From the moment a writer accepts, you have a direct message channel in your dashboard. Share additional files, clarify requirements, ask questions, or just check in on progress. Your writer knows nursing — you can speak the same clinical language.',
    detail: [
      'Direct messaging, no support ticket system in between',
      'Share rubrics, clinical scenario updates, or instructor feedback at any time',
      'Writer provides progress updates and can flag questions before they become problems',
      'All communication is stored — you can refer back to any message from the order history',
    ],
  },
  {
    number: '04',
    icon: Download,
    title: 'Download your completed paper',
    desc: 'Your nurse writer uploads the completed paper to your dashboard. You receive an email notification. Download in Word, PDF, or PowerPoint — your Turnitin originality report is included at no extra charge.',
    detail: [
      'Email notification when your paper is ready',
      'Download from the Files section of your dashboard at any time',
      'Free Turnitin originality report included with every order',
      'AI-detection report available free on request',
      'Free unlimited revisions within the revision window',
      'Grade guarantee — if you receive a lower grade than stated in your brief, contact us within 14 days',
    ],
  },
]

const guarantees = [
  { icon: Trophy,      title: 'Grade or money back',       desc: 'Receive a grade lower than stated in your brief? We rewrite it free or refund you — no questions asked.' },
  { icon: Stethoscope, title: 'Real nurses only',           desc: 'BSN minimum for every writer. MSN and DNP writers for graduate work. We verify every licence before a writer can accept orders.' },
  { icon: Bot,         title: 'Zero AI — verified',         desc: 'All papers are written by a real nurse. Free AI-detection report on request. Free Turnitin report with every order.' },
  { icon: Lock,        title: 'Your privacy protected',     desc: 'Your name, school, and order details are never shared. Your writer receives only the assignment brief.' },
  { icon: RefreshCw,   title: 'Unlimited free revisions',   desc: 'Request as many revisions as needed within the revision window. Always handled by your original nurse writer.' },
  { icon: Zap,         title: 'As fast as 3 hours',         desc: 'Urgent order? Most nursing papers up to 4 pages can be delivered in 3 hours. Available 24/7.' },
]

const services = [
  { label: 'Nursing Essays',         href: '/services/nursing-essays' },
  { label: 'Care Plans',             href: '/services/care-plans' },
  { label: 'SOAP Notes',             href: '/services/soap-notes' },
  { label: 'Capstone Projects',      href: '/services/capstone-projects' },
  { label: 'Nursing Research Papers',href: '/services/nursing-research-papers' },
  { label: 'Shadow Health Help',     href: '/services/shadow-health' },
  { label: 'iHuman Cases',           href: '/services/ihuman-patients' },
  { label: 'Online Class Help',      href: '/services/online-nursing-classes' },
  { label: 'Nursing Dissertations',  href: '/services/nursing-dissertations' },
]
</script>

<template>
  <div class="bg-white">

    <!-- Hero -->
    <div class="bg-gradient-to-br from-brand-900 to-brand-700 px-4 py-16 text-white sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-300">Simple. Fast. Nurse-written.</p>
        <h1 class="font-serif text-4xl font-bold sm:text-5xl">How NurseMyGrade Works</h1>
        <p class="mx-auto mt-4 max-w-xl text-lg leading-relaxed text-brand-200">
          From submitting your nursing brief to downloading a clinically accurate, APA-formatted paper — the entire process takes minutes to start and is backed by a grade guarantee.
        </p>
        <NuxtLink
          to="/order"
          class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-10 py-4 text-base font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Get started now
          <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </NuxtLink>
        <p class="mt-3 text-sm text-brand-300">From $24/page · As fast as 3 hours · Grade or money back</p>
      </div>
    </div>

    <!-- Steps -->
    <div class="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="space-y-12">
        <div
          v-for="(step, i) in steps"
          :key="step.number"
          class="grid gap-8 md:grid-cols-[72px_1fr]"
        >
          <!-- Step number -->
          <div class="flex flex-col items-center">
            <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-600 text-xl font-bold text-white shadow-md">
              {{ step.number }}
            </div>
            <div v-if="i < steps.length - 1" class="mt-4 h-full w-0.5 bg-brand-100" />
          </div>

          <!-- Step content -->
          <div class="pb-4">
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-100">
              <component :is="step.icon" class="h-5 w-5 text-brand-700" />
            </div>
            <h2 class="font-serif text-2xl font-bold text-slate-900">{{ step.title }}</h2>
            <p class="mt-2 text-base leading-relaxed text-slate-600">{{ step.desc }}</p>
            <ul class="mt-4 space-y-2">
              <li
                v-for="d in step.detail"
                :key="d"
                class="flex items-start gap-2.5 text-sm text-slate-600"
              >
                <span class="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-brand-100 text-[9px] font-bold text-brand-700">✓</span>
                {{ d }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Guarantees -->
    <div class="bg-slate-50 px-4 py-16 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-5xl">
        <div class="mb-10 text-center">
          <h2 class="font-serif text-3xl font-bold text-slate-900">Every order, every time</h2>
          <p class="mt-3 text-slate-500">These guarantees apply to every single order — not just selected ones.</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="g in guarantees" :key="g.title" class="card">
            <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100">
              <component :is="g.icon" class="h-5 w-5 text-brand-700" />
            </div>
            <h3 class="mt-3 font-semibold text-slate-900">{{ g.title }}</h3>
            <p class="mt-1 text-sm leading-relaxed text-slate-600">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Services overview -->
    <div class="px-4 py-16 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-4xl">
        <div class="mb-8 text-center">
          <h2 class="font-serif text-3xl font-bold text-slate-900">What we write</h2>
          <p class="mt-2 text-slate-500">22 nursing-specific services — every assignment type in your programme.</p>
        </div>
        <div class="grid gap-3 sm:grid-cols-3">
          <NuxtLink
            v-for="s in services"
            :key="s.href"
            :to="s.href"
            class="flex items-center gap-2 rounded-xl border border-slate-100 bg-white px-4 py-3 text-sm font-medium text-slate-700 transition-all hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700"
          >
            <span class="text-brand-400">→</span>
            {{ s.label }}
          </NuxtLink>
        </div>
        <div class="mt-6 text-center">
          <NuxtLink to="/services" class="text-sm font-semibold text-brand-600 hover:underline">
            View all 22 services →
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="bg-brand-700 px-4 py-16 text-center sm:px-6 lg:px-8">
      <h2 class="font-serif text-3xl font-bold text-white">Ready to get started?</h2>
      <p class="mt-3 text-brand-200">Submit your brief in under 5 minutes. A qualified nurse writer is ready.</p>
      <div class="mt-8 flex flex-wrap justify-center gap-4">
        <NuxtLink to="/order" class="btn-primary bg-white px-10 py-4 text-base text-brand-700 hover:bg-brand-50 shadow-lg">
          Place my order — from $24/page
        </NuxtLink>
        <NuxtLink to="/faq" class="btn-outline border-white/60 px-8 py-4 text-base text-white hover:bg-white/10">
          Read the FAQ first
        </NuxtLink>
      </div>
    </div>

  </div>
</template>
