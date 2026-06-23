<script setup lang="ts">
import { ArrowRight, CheckCircle2 } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'About GradeCrest — Academic Writing Service | Our Mission & Values',
  description: 'Learn about GradeCrest — our mission, our writers, and the values behind every paper we deliver. Human-written academic work, grade guaranteed.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

useSeoBase('https://gradecrest.com/about')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'About', url: 'https://gradecrest.com/about' },
])

const values = [
  { title: 'Human expertise only',     desc: 'We will never use AI to write your paper. Every order is handled by a verified human expert with subject-specific credentials.' },
  { title: 'Radical transparency',     desc: 'Our pricing is public, our policies are clear, and our writers are vetted. No hidden fees, no bait-and-switch.' },
  { title: 'Academic integrity',       desc: 'We provide model papers for reference and learning. We are explicit about our purpose and responsible in how we operate.' },
  { title: 'Writer respect',           desc: 'Our writers are fairly compensated, professionally supported, and given the time they need to produce excellent work.' },
]

const stats = [
  { value: '2016',     label: 'Year founded' },
  { value: '600+',     label: 'Expert writers' },
  { value: '50,000+',  label: 'Papers delivered' },
  { value: '100+',     label: 'Subjects covered' },
]
</script>

<template>
  <div class="pt-16">

    <section class="bg-forest-950 py-16 relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6 text-center">
        <h1 class="text-4xl font-bold text-white sm:text-5xl">About GradeCrest</h1>
        <p class="mt-4 text-lg text-slate-300 leading-relaxed">
          GradeCrest exists because students deserve access to the same quality of academic support that has always been available to those who can afford private tutors, coaches, and consultants.
        </p>
      </div>
    </section>

    <!-- Mission -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 grid sm:grid-cols-2 gap-10 items-center">
        <div class="space-y-4">
          <h2 class="text-2xl font-bold text-ink">Our mission</h2>
          <p class="text-graphite leading-relaxed">
            We believe every student deserves access to expert academic guidance. GradeCrest provides custom model papers written by subject specialists — giving students the tools to understand complex material, improve their own writing, and meet the demands of their programmes.
          </p>
          <p class="text-graphite leading-relaxed">
            Since 2016 we have delivered over 50,000 papers to students across the UK, US, Canada, Australia, and beyond. Every paper is human-written, original, and backed by a grade guarantee.
          </p>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="s in stats" :key="s.label" class="rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-card">
            <p class="text-2xl font-bold text-ink">{{ s.value }}</p>
            <p class="mt-1 text-xs text-graphite">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Values -->
    <section class="bg-mist py-14">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-ink text-center mb-8">What we stand for</h2>
        <div class="grid gap-5 sm:grid-cols-2">
          <div v-for="v in values" :key="v.title" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
            <CheckCircle2 class="size-6 text-gc-600 mb-3" />
            <h3 class="text-sm font-semibold text-ink">{{ v.title }}</h3>
            <p class="mt-1.5 text-sm text-graphite leading-relaxed">{{ v.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Writers -->
    <section class="bg-white py-14 text-center">
      <div class="mx-auto max-w-2xl px-4 sm:px-6 space-y-5">
        <h2 class="text-2xl font-bold text-ink">Our writers</h2>
        <p class="text-graphite leading-relaxed">
          Every GradeCrest writer holds a postgraduate degree and passes a multi-stage verification process — degree certificates, writing assessment, subject knowledge test, and supervised trial orders — before they handle their first customer paper.
        </p>
        <NuxtLink to="/writers" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
          Meet the team <ArrowRight class="size-4" />
        </NuxtLink>
      </div>
    </section>

  </div>
</template>
