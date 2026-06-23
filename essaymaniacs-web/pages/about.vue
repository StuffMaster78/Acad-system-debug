<script setup lang="ts">
import { markRaw } from 'vue'
import { Target, Heart, Handshake, Lock } from '@lucide/vue'

const app = useAppUrl()
useSeoMeta({
  title: 'About EssayManiacs — Our Writers, Our Standards',
  description: 'EssayManiacs connects students with subject-obsessed essay specialists since 2018. Only writers who genuinely know your subject.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/about' }] })

const stats = [
  { value: '20,000+', label: 'Essays delivered',    sub: 'Across 100+ subjects' },
  { value: '2/100',   label: 'Writer acceptance',   sub: 'We turn away 98%' },
  { value: '4.8/5',   label: 'Average rating',      sub: 'Based on 9,400+ reviews' },
  { value: '2018',    label: 'Founded',             sub: 'Still human-only' },
]

const values = [
  { icon: markRaw(Target),    title: 'Subject matching is non-negotiable', desc: "Your history essay doesn't go to a business writer. We match strictly by subject and degree level." },
  { icon: markRaw(Heart),     title: 'Writers who love the subject',      desc: "We hire writers who are enthusiastic about their discipline — it comes through in the quality of their arguments." },
  { icon: markRaw(Handshake), title: 'Academic integrity',                desc: "We provide model papers for reference and study. We include an academic-use disclosure on every order and never encourage misrepresentation." },
  { icon: markRaw(Lock),      title: 'Privacy first',                     desc: "Your name, school, and order details are never shared. Your writer receives only the brief — not your personal information." },
]

const vettingSteps = [
  { n: '01', title: 'Subject declaration and credential check', desc: "Applicants declare their subjects and submit degree certificates. We verify directly with the issuing institution before reviewing anything else." },
  { n: '02', title: 'Subject knowledge assessment',             desc: "A written test in the declared subject area. Reveals whether applicants genuinely know their field — not just how to structure an essay." },
  { n: '03', title: 'Sample essay review',                      desc: "Our editorial team reviews an original sample against our quality rubric: argument, sourcing, academic register, and citation accuracy." },
  { n: '04', title: 'Supervised first orders',                  desc: "New writers complete their first five orders under editorial oversight. Quality must hold before full marketplace access is granted." },
]

const milestones = [
  { year: '2018', event: 'Founded with 30 core essay writers across 8 subjects.' },
  { year: '2020', event: 'Expanded to 60+ subject areas; 5,000+ essays delivered.' },
  { year: '2021', event: 'Dissertations and admission essays added as specialist tiers.' },
  { year: '2022', event: 'Proofreading service launched; 10,000+ orders milestone.' },
  { year: '2023', event: '200+ active writers; AI-detection guarantee introduced.' },
  { year: '2025', event: '500+ subject specialists; 20,000+ essays and still growing.' },
]
</script>

<template>
  <div>
    <section class="relative overflow-hidden bg-brand-900 py-24">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-96 w-96 rounded-full bg-brand-500 opacity-20 blur-[120px]" />
      <div class="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">Our story</p>
        <h1 class="text-4xl font-bold leading-tight text-white sm:text-5xl">We believe the best essays are written<br class="hidden sm:block" /> by people who love the subject.</h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-brand-200">Since 2018, EssayManiacs has connected students with subject-specialist writers who are genuinely enthusiastic about their disciplines — and it shows in the quality of their arguments.</p>
      </div>
    </section>

    <section class="border-b border-slate-100 bg-white">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 divide-x divide-y divide-slate-100 md:grid-cols-4 md:divide-y-0">
          <div v-for="stat in stats" :key="stat.label" class="flex flex-col items-center py-10 text-center">
            <span class="text-3xl font-extrabold tabular-nums text-brand-700">{{ stat.value }}</span>
            <span class="mt-1 text-sm font-semibold text-slate-800">{{ stat.label }}</span>
            <span class="mt-0.5 text-xs text-slate-400">{{ stat.sub }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-white py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-16 lg:grid-cols-2">
          <div>
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-600">What we believe</p>
            <h2 class="text-3xl font-bold leading-snug text-slate-900 sm:text-4xl">Subject knowledge isn't a bonus. It's the whole point.</h2>
            <p class="mt-5 text-base leading-relaxed text-slate-500">A psychology essay written by a psychology specialist reads differently from one written by a generic writer. The literature cited is more relevant. The argument structure matches disciplinary conventions. The terminology is used correctly. The marker notices.</p>
            <p class="mt-4 text-base leading-relaxed text-slate-500">That's why we hire writers for their subject knowledge first, and their writing ability second. Both have to be excellent. But subject expertise is what creates the difference between a competent essay and an outstanding one.</p>
          </div>
          <div class="grid gap-4 sm:grid-cols-2">
            <div v-for="v in values" :key="v.title" class="rounded-2xl border border-brand-100 bg-brand-50 p-6">
              <div class="mb-3">
                <component :is="v.icon" class="h-8 w-8" />
              </div>
              <h3 class="font-bold text-slate-900">{{ v.title }}</h3>
              <p class="mt-2 text-sm leading-relaxed text-slate-500">{{ v.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-slate-50 py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-16 lg:grid-cols-2">
          <div>
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-600">How we hire</p>
            <h2 class="text-3xl font-bold text-slate-900">98 out of 100 applicants don't make it.</h2>
            <p class="mt-5 text-base leading-relaxed text-slate-500">We're building a team of genuine subject enthusiasts who happen to be excellent writers — not a pool of thousands of generalists. That means saying no, a lot.</p>
          </div>
          <div class="space-y-5">
            <div v-for="step in vettingSteps" :key="step.n" class="flex gap-5">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-xl border-2 border-brand-200 bg-white text-sm font-extrabold text-brand-700">{{ step.n }}</div>
              <div>
                <h3 class="font-bold text-slate-900">{{ step.title }}</h3>
                <p class="mt-1 text-sm leading-relaxed text-slate-500">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-white py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="mb-12 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Our journey</p>
          <h2 class="text-3xl font-bold text-slate-900">Seven years and 20,000 essays later.</h2>
        </div>
        <div class="relative space-y-0">
          <div class="absolute left-[39px] top-4 bottom-4 w-px bg-brand-100" />
          <div v-for="m in milestones" :key="m.year" class="relative flex gap-6 pb-8 last:pb-0">
            <div class="flex size-[42px] shrink-0 items-center justify-center rounded-full border-2 border-brand-200 bg-white text-xs font-extrabold text-brand-700 shadow-sm z-10">{{ m.year.slice(2) }}'</div>
            <div class="pt-2">
              <p class="text-xs font-bold text-brand-600">{{ m.year }}</p>
              <p class="mt-0.5 text-sm leading-relaxed text-slate-600">{{ m.event }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-brand-900 py-20 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-3xl font-bold text-white">Work with a writer who loves your subject.</h2>
        <p class="mt-4 text-lg text-brand-200">Tell us your subject, level, and deadline. We'll find your match in minutes.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">Start my order — from $10/page</a>
          <a href="/how-it-works" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10">How it works →</a>
        </div>
      </div>
    </section>
  </div>
</template>
