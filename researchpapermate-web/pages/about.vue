<script setup lang="ts">
const app = useAppUrl()

const heroStats = [
  { value: '14,700+', label: 'Papers delivered' },
  { value: '200+',    label: 'Expert writers' },
  { value: '4.8/5',   label: 'Average rating' },
  { value: '98%',     label: 'On-time delivery' },
]

const vettingSteps = [
  {
    step: '01',
    title: 'Academic credential check',
    desc: 'We verify every degree certificate against the issuing institution. Only Master\'s-level and above applicants advance.',
  },
  {
    step: '02',
    title: 'Subject knowledge test',
    desc: 'Writers sit a subject-specific written test in their field. This filters generalists and surfaces real specialists.',
  },
  {
    step: '03',
    title: 'Sample writing assessment',
    desc: 'An original sample paper is reviewed by our editorial team for structure, argument, and citation accuracy.',
  },
  {
    step: '04',
    title: 'Supervised trial period',
    desc: 'New writers complete their first 5 orders under editorial oversight. Only those who maintain our quality standard stay on.',
  },
]

const values = [
  {
    icon: 'trophy',
    color: 'bg-amber-100 text-amber-600',
    title: 'Quality over volume',
    desc: 'We accept only 2 in every 100 writer applicants. Every paper is reviewed before delivery.',
  },
  {
    icon: 'handshake',
    color: 'bg-brand-100 text-brand-600',
    title: 'Academic integrity',
    desc: 'We provide reference and model papers. We never encourage academic dishonesty and include a legal-use disclosure on every order.',
  },
  {
    icon: 'lock',
    color: 'bg-green-100 text-green-600',
    title: 'Privacy by design',
    desc: 'Your name, email, and order details are never sold, shared, or stored beyond what\'s needed to fulfil your order.',
  },
  {
    icon: 'message-square',
    color: 'bg-purple-100 text-purple-600',
    title: 'Real human support',
    desc: 'Every query reaches a real person. No chatbots, no scripted replies — just direct, knowledgeable support.',
  },
]

const milestones = [
  { year: '2019', label: 'Founded with 20 core writers across 12 subjects' },
  { year: '2021', label: 'Reached 1,000 completed orders with 4.7/5 average rating' },
  { year: '2023', label: 'Expanded to 100+ subject areas and 150+ active writers' },
  { year: '2024', label: '200+ writers, 10,000+ papers delivered, launched dissertation tier' },
  { year: '2025', label: 'AI-detection guarantee introduced; 14,700+ orders and counting' },
]

useSeoMeta({
  title: 'About ResearchPaperMate — Our Writers, Our Standards',
  description: 'ResearchPaperMate connects students with verified academic writing experts since 2019. Learn how we vet our writers and what we stand for.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/about' }] })
</script>

<template>
  <div>
    <!-- Hero with stat overlay -->
    <section class="relative bg-gradient-to-br from-brand-900 to-brand-700 pb-0 pt-20">
      <div class="section py-0 text-center">
        <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-300">About us</p>
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">
          Expert academic writing,<br class="hidden sm:block" /> built on trust
        </h1>
        <p class="mx-auto mt-5 max-w-2xl text-lg text-brand-100 leading-relaxed">
          Since 2019, we've connected students with verified, degree-holding experts who write
          original papers from scratch — not AI, not templates.
        </p>
      </div>

      <!-- Stats bar — floats at bottom of hero -->
      <div class="mt-16 border-t border-white/10">
        <div class="section py-0">
          <div class="grid grid-cols-2 gap-0 md:grid-cols-4">
            <div v-for="(stat, i) in heroStats" :key="stat.label"
              class="border-r border-white/10 py-6 text-center last:border-r-0"
              :class="i % 2 === 0 ? 'border-r border-white/10' : ''"
            >
              <div class="text-3xl font-bold text-white">{{ stat.value }}</div>
              <div class="mt-1 text-sm text-brand-200">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mission -->
    <section class="bg-white">
      <div class="section">
        <div class="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-600">Our mission</p>
            <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
              Every student deserves expert academic support
            </h2>
            <p class="mt-5 text-slate-600 leading-relaxed text-lg">
              ResearchPaperMate was founded on a simple belief: access to expert academic help shouldn't
              depend on your first language, time zone, or budget. We built a platform where students connect
              directly with writers who hold advanced degrees in their exact subject area — not generalists,
              not AI, but specialists.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              Every paper is written from scratch to your specific brief. Every writer is vetted through
              a four-stage process. And every order is backed by our grade-or-money-back guarantee.
            </p>
            <NuxtLink to="/order" class="btn-primary mt-8 inline-flex">
              Place your first order
            </NuxtLink>
          </div>

          <!-- Visual trust card -->
          <div class="grid gap-4 sm:grid-cols-2">
            <div v-for="v in values" :key="v.title" class="card">
              <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl" :class="v.color.split(' ')[0]">
                <Icon :name="v.icon" class="h-5 w-5" :class="v.color.split(' ')[1]" />
              </div>
              <h3 class="font-semibold text-slate-900">{{ v.title }}</h3>
              <p class="mt-2 text-sm text-slate-500 leading-relaxed">{{ v.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How we vet writers -->
    <section class="bg-slate-50">
      <div class="section">
        <div class="mx-auto max-w-3xl text-center">
          <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-600">Writer quality</p>
          <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
            Only 2 in 100 applicants make it through
          </h2>
          <p class="section-sub">
            Our vetting process is designed to find subject-matter experts, not just capable writers.
          </p>
        </div>
        <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="step in vettingSteps" :key="step.step" class="card relative">
            <div class="mb-4 font-mono text-4xl font-bold text-brand-100">{{ step.step }}</div>
            <h3 class="font-semibold text-slate-900">{{ step.title }}</h3>
            <p class="mt-2 text-sm text-slate-500 leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Milestones timeline -->
    <section class="bg-white">
      <div class="section">
        <div class="mx-auto max-w-3xl">
          <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-600 text-center">Our story</p>
          <h2 class="font-serif text-3xl font-bold text-slate-900 text-center sm:text-4xl">
            Growing with every order
          </h2>
          <div class="mt-12 space-y-0">
            <div
              v-for="(m, i) in milestones"
              :key="m.year"
              class="relative flex gap-6 pb-10 last:pb-0"
            >
              <!-- Line -->
              <div class="flex flex-col items-center">
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white shadow-md">
                  {{ m.year.slice(2) }}'
                </div>
                <div v-if="i < milestones.length - 1" class="mt-2 h-full w-0.5 bg-brand-100"></div>
              </div>
              <!-- Content -->
              <div class="pt-1.5 pb-2">
                <p class="text-sm font-bold text-brand-700">{{ m.year }}</p>
                <p class="mt-1 text-slate-700 leading-relaxed">{{ m.label }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Commitments -->
    <section class="bg-brand-50 border-y border-brand-100">
      <div class="section">
        <div class="grid gap-6 sm:grid-cols-3 text-center">
          <div>
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-green-100">
              <Icon name="check-circle" class="h-6 w-6 text-green-600" />
            </div>
            <h3 class="font-semibold text-slate-900">100% original</h3>
            <p class="mt-1 text-sm text-slate-500">Every paper written from scratch, checked for plagiarism before delivery.</p>
          </div>
          <div>
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100">
              <Icon name="bot" class="h-6 w-6 text-blue-600" />
            </div>
            <h3 class="font-semibold text-slate-900">Zero AI content</h3>
            <p class="mt-1 text-sm text-slate-500">All work is 100% human-written. AI-detection report available on request.</p>
          </div>
          <div>
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-100">
              <Icon name="lock" class="h-6 w-6 text-brand-600" />
            </div>
            <h3 class="font-semibold text-slate-900">Private by default</h3>
            <p class="mt-1 text-sm text-slate-500">Your data is never sold or shared. Payment handled by a regulated third party.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-700 py-20 text-center">
      <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">Ready to get started?</h2>
      <p class="mt-4 text-brand-200 text-lg">
        Join 14,700+ students who've trusted us with their academic work.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <NuxtLink
          to="/order"
          class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base shadow-lg"
        >
          Place your first order — from $15/page
        </NuxtLink>
        <NuxtLink
          href="/contact"
          class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-4 text-base"
        >
          Talk to us first
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
