<script setup lang="ts">
import {
  ArrowRight, BadgeCheck, BookOpen, Bot, CheckCircle2,
  Clock, FileText, GraduationCap, Lock, RefreshCw,
  Shield, Star, Trophy, Users, Zap,
} from '@lucide/vue'
import { markRaw } from 'vue'
import PricingCalculator from '~/components/ui/PricingCalculator.vue'

const app = useAppUrl()
const siteSettings = await fetchSiteSettings()
const ogImage = siteSettings?.og_image_url ?? '/og-default.svg'

// ── Structured data ───────────────────────────────────────────────────────────
useSeoMeta({
  title: 'GradeCrest — Academic Writing Service | Essays, Research Papers & More',
  description: 'Get essays, research papers, dissertations, and assignments written by human experts. From $13/page. Grade or money back. Zero AI content. 50,000+ papers delivered.',
  ogTitle: 'GradeCrest — Academic Writing Service',
  ogDescription: 'Human-written papers across every subject. Grade or money back guarantee. 50,000+ papers delivered. 4.9/5 rated.',
  ogImage,
  twitterCard: 'summary_large_image',
})

useSeoBase('https://gradecrest.com/')

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ProfessionalService',
      '@id': 'https://gradecrest.com/#service',
      name: 'GradeCrest Academic Writing',
      url: 'https://gradecrest.com',
      description: 'Custom academic writing service providing essays, research papers, dissertations, and assignments written by human experts.',
      priceRange: '$13 – $35 per page',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.9', reviewCount: '12400', bestRating: '5' },
      hasOfferCatalog: {
        '@type': 'OfferCatalog',
        name: 'Academic Writing Services',
        itemListElement: [
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Essay Writing' }, price: '13.00', priceCurrency: 'USD' },
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Research Paper Writing' }, price: '15.00', priceCurrency: 'USD' },
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Dissertation Writing' }, price: '22.00', priceCurrency: 'USD' },
        ],
      },
    }),
  }],
})

useFaqLd([
  { q: 'Is GradeCrest legit?', a: 'Yes. GradeCrest provides 100% original, human-written academic papers. Every order includes a plagiarism report and AI-detection certificate.' },
  { q: 'How much does it cost?', a: 'Prices start from $13/page for high school level with a 14-day deadline. Cost depends on academic level, deadline, and number of pages.' },
  { q: 'Do you use AI to write papers?', a: 'No. Every paper is written by a verified human expert. We provide a free AI-detection report on every completed order.' },
  { q: 'What is the grade guarantee?', a: 'If your paper does not meet the stated grade requirement, we rewrite it for free or issue a full refund.' },
  { q: 'How fast can you deliver?', a: 'We can deliver in as little as 6 hours for urgent orders. Standard turnaround is 14 days.' },
])

// ── Page data ─────────────────────────────────────────────────────────────────

const stats = [
  { value: '50,000+', label: 'Papers delivered' },
  { value: '600+',    label: 'Expert writers'   },
  { value: '4.9/5',   label: 'Average rating'   },
  { value: '98%',     label: 'On-time delivery' },
]

const services = [
  { icon: markRaw(FileText),      title: 'Essays',              href: '/services/essay-writing',       desc: 'Argumentative, analytical, descriptive — any format, any level, any subject.' },
  { icon: markRaw(BookOpen),      title: 'Research Papers',     href: '/services/research-papers',     desc: 'Original, citation-rich papers across STEM, business, humanities, and social sciences.' },
  { icon: markRaw(GraduationCap), title: 'Dissertations',       href: '/services/dissertations',       desc: 'Full thesis support from proposal through defence — chapters, methodology, data.' },
  { icon: markRaw(FileText),      title: 'Term Papers',         href: '/services/term-papers',         desc: 'Well-structured semester papers delivered before your deadline.' },
  { icon: markRaw(FileText),      title: 'Nursing Essays',      href: '/services/nursing-essays',      desc: 'SOAP notes, care plans, EBP papers — handled by registered nursing experts.' },
  { icon: markRaw(FileText),      title: 'Admission Essays',    href: '/services/admission-essays',    desc: 'Personal statements and college essays that get noticed.' },
  { icon: markRaw(FileText),      title: 'Case Studies',        href: '/services/case-studies',        desc: 'Deep-dive analysis with structured arguments and supporting evidence.' },
  { icon: markRaw(Zap),           title: 'Editing & Proofread', href: '/services/editing-proofreading',desc: 'Grammar, clarity, flow, and formatting corrected by professional editors.' },
  { icon: markRaw(FileText),      title: 'Coursework Help',     href: '/services/coursework',          desc: 'Ongoing assignment support — consistent writer, consistent voice.' },
]

const steps = [
  { n: '01', title: 'Fill in your brief',       desc: 'Share your topic, deadline, academic level, and any files or special instructions.' },
  { n: '02', title: 'Secure checkout',           desc: 'Pay securely. Your payment is held in escrow and only released when you approve the work.' },
  { n: '03', title: 'Get matched & communicate',desc: 'A verified expert is assigned. Message them directly, share updates, and track progress in real time.' },
  { n: '04', title: 'Review & download',         desc: 'Receive your paper. Request unlimited free revisions until you are completely satisfied.' },
]

const guarantees = [
  { icon: markRaw(Trophy),      title: 'Grade or money back',    desc: "If the work doesn't meet your stated grade target we rewrite it free or refund in full." },
  { icon: markRaw(CheckCircle2),title: '100% original work',     desc: 'Every paper is written from scratch and verified against plagiarism databases before delivery.' },
  { icon: markRaw(Bot),         title: 'Zero AI content',        desc: 'Human experts only. Every order includes a free AI-detection certificate on request.' },
  { icon: markRaw(Lock),        title: 'Your privacy protected', desc: 'Your identity, order details, and personal data are never shared with any third party.' },
  { icon: markRaw(RefreshCw),   title: 'Unlimited revisions',    desc: 'Within the revision window, request as many changes as you need at absolutely zero cost.' },
  { icon: markRaw(Users),       title: 'Dedicated writer',       desc: 'The same expert handles your revisions — context and tone stay consistent throughout.' },
]

const testimonials = [
  { text: "I was completely stuck on my nursing capstone. The writer understood exactly what I needed and delivered two days early. Passed with distinction.", name: 'Kezia M.',  subject: 'Nursing',   stars: 5 },
  { text: "Third time using GradeCrest. Every paper is genuinely written by a human — you can tell from the nuance in the arguments. Not a single AI phrase.", name: 'Tyler B.',  subject: 'Law',       stars: 5 },
  { text: "Ordered a 25-page dissertation chapter with 72 hours notice. It arrived on time, perfectly formatted, with every source I asked for.", name: 'Priya S.',  subject: 'Business',  stars: 5 },
  { text: "The editor caught things I never would have spotted. My final thesis went from good to genuinely excellent after the proofread.", name: 'James L.',  subject: 'History',   stars: 5 },
  { text: "I was sceptical about the grade guarantee but had to test it. They rewrote the intro without complaint and I got the A I needed.", name: 'Amara D.',  subject: 'Psychology',stars: 5 },
  { text: "Statistics paper, 48 hours, PhD level. I genuinely could not have done this alone. The methodology section alone was worth the price.", name: 'Marco T.',  subject: 'Statistics', stars: 5 },
  { text: "Fast, professional, and the writer actually read my previous papers to match my writing style. Incredible attention to detail.", name: 'Sophie R.', subject: 'Literature', stars: 5 },
  { text: "Got a distinction on my MBA case study. The writer had real industry knowledge — not just textbook answers.", name: 'Femi O.',   subject: 'MBA',       stars: 5 },
  { text: "I've used three different services. GradeCrest is the only one where the writer genuinely understood what my professor was looking for.", name: 'Chloe N.',  subject: 'Sociology', stars: 5 },
]

const faqs = [
  { q: 'Is GradeCrest safe and legitimate?',          a: 'Yes. GradeCrest provides 100% original model papers for reference. Every order includes a plagiarism report, and writers are verified experts.' },
  { q: 'How is the price calculated?',                a: 'Price depends on your academic level, deadline, and number of pages (275 words per page). You see the exact total before paying — no hidden fees.' },
  { q: 'Do your writers use AI?',                     a: 'No. Every paper is written by a verified human expert. We provide a free AI-detection certificate on every completed order upon request.' },
  { q: 'What happens if I am not satisfied?',         a: "Request a free revision — we'll revise until you're happy. If the work still does not meet your stated requirements, you receive a full refund." },
  { q: 'How fast can you deliver?',                   a: 'We deliver in as little as 6 hours for emergency orders. Standard turnaround is 14 days. The earlier you order, the better the price.' },
  { q: 'Can I communicate with my writer?',           a: 'Yes. Direct messaging is included with every order at no extra cost. Share files, ask questions, and check progress at any time.' },
  { q: 'Are my personal details kept private?',       a: 'Completely. We never share your name, email, order content, or any personal data with third parties, under any circumstances.' },
  { q: 'What academic levels do you cover?',          a: 'High school through PhD. Our experts hold postgraduate degrees and are matched to your level and subject.' },
]

const subjects = [
  'Nursing','Business','Psychology','Law','History','Literature','Philosophy',
  'Marketing','Finance','Accounting','Sociology','Political Science',
  'Engineering','Computer Science','Statistics','Biology','Chemistry','Physics',
  'Economics','Education','Public Health','Environmental Science',
  'Architecture','Media Studies','Anthropology','Criminal Justice',
]

const writers = [
  { name: 'Dr. Sarah K.',   degree: 'PhD · Nursing',       orders: 1840, rating: 5.0, subjects: ['Nursing', 'Health Sciences'] },
  { name: 'Prof. James W.', degree: "PhD · Literature",    orders: 2310, rating: 5.0, subjects: ['Literature', 'History']      },
  { name: 'Dr. Priya M.',   degree: "PhD · Business",      orders: 1560, rating: 4.9, subjects: ['MBA', 'Finance', 'Marketing']},
  { name: 'Dr. Emily C.',   degree: "Master's · Law",      orders:  920, rating: 5.0, subjects: ['Law', 'Criminology']         },
  { name: 'Dr. Caleb R.',   degree: "PhD · Statistics",    orders: 1280, rating: 5.0, subjects: ['Statistics', 'Data Analysis']},
  { name: 'Prof. Nadia F.', degree: "PhD · Psychology",    orders: 1730, rating: 4.9, subjects: ['Psychology', 'Sociology']   },
]

const heroWriters = [
  {
    initials: 'SK', name: 'Dr. Sarah K.', degree: 'PhD · Nursing & Health Sciences',
    specialty: 'Care Plans · Dissertations · EBP Research',
    orders: 1840, rating: 5.0, available: true,
    quote: 'Distinction on every nursing capstone I have handled this semester.',
  },
  {
    initials: 'JW', name: 'Prof. James W.', degree: 'PhD · Literature & History',
    specialty: 'Essays · Critical Analysis · Dissertations',
    orders: 2310, rating: 5.0, available: true,
    quote: 'Published author. I write the kind of argument your professor will remember.',
  },
  {
    initials: 'PM', name: 'Dr. Priya M.', degree: 'PhD · Business & Finance',
    specialty: 'MBA Papers · Case Studies · Financial Analysis',
    orders: 1560, rating: 4.9, available: false,
    quote: 'Former strategy consultant. I know what real business writing looks like.',
  },
]

// Animated stat counter (IntersectionObserver approach)
const statsRef = ref<HTMLElement | null>(null)
const statsVisible = ref(false)
onMounted(() => {
  if (!statsRef.value) return
  const obs = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) { statsVisible.value = true; obs.disconnect() }
  }, { threshold: 0.3 })
  obs.observe(statsRef.value)
})
</script>

<template>
  <div>

    <!-- ── HERO ─────────────────────────────────────────────────────────────── -->
    <section class="relative min-h-screen overflow-hidden bg-forest-950">

      <!-- Gold dot grid — unique welcoming pattern -->
      <div class="pointer-events-none absolute inset-0 bg-hero-grid bg-grid-40" />

      <!-- Gold bloom — upper right -->
      <div class="pointer-events-none absolute -top-40 right-0 h-[600px] w-[600px] rounded-full bg-gold-400/10 blur-[120px]" />
      <!-- Forest glow — lower left -->
      <div class="pointer-events-none absolute bottom-0 -left-32 h-[400px] w-[400px] rounded-full bg-gc-600/15 blur-[100px]" />
      <!-- Warm amber centre pulse -->
      <div class="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[700px] w-[700px] rounded-full bg-gold-500/5 blur-3xl" />

      <div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
        <div class="grid items-start gap-12 lg:grid-cols-2">

          <!-- Left: copy -->
          <div class="space-y-7 pt-4">
            <div class="inline-flex items-center gap-2 rounded-full border border-gold-400/30 bg-gold-400/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-gold-300">
              <span class="size-1.5 rounded-full bg-gold-400 animate-pulse" />
              Human experts · Zero AI
            </div>

            <h1 class="text-4xl font-bold leading-[1.1] text-white sm:text-5xl lg:text-6xl">
              The grade you need,<br />
              <span class="text-gold-400">written by experts</span><br />
              who know your subject.
            </h1>

            <p class="max-w-lg text-lg leading-relaxed text-slate-300">
              Essays, research papers, dissertations — delivered by verified human writers with postgraduate degrees. Not AI. Not outsourced. Real experts.
            </p>

            <!-- Trust signals row -->
            <div class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-slate-400">
              <span class="flex items-center gap-1.5">
                <Star class="size-4 fill-gold-400 text-gold-400" />
                <span class="font-semibold text-white">4.9</span> / 5 · 12,400+ reviews
              </span>
              <span class="hidden text-forest-700 sm:block">|</span>
              <span class="flex items-center gap-1.5">
                <BadgeCheck class="size-4 text-gold-400" />
                Grade or money back
              </span>
              <span class="hidden text-forest-700 sm:block">|</span>
              <span class="flex items-center gap-1.5">
                <Clock class="size-4 text-gold-400" />
                From 6 hours
              </span>
            </div>

            <div class="flex flex-wrap gap-3">
              <a href="/order"
                class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-4 text-base font-bold text-white shadow-lg transition-colors hover:bg-gc-700">
                Place your order <ArrowRight class="size-5" />
              </a>
              <NuxtLink to="/pricing"
                class="inline-flex items-center gap-2 rounded-xl border border-white/20 px-8 py-4 text-base font-semibold text-slate-300 transition-colors hover:border-white/40 hover:text-white">
                See pricing
              </NuxtLink>
            </div>

            <div class="flex flex-wrap gap-x-5 gap-y-1.5 text-xs text-slate-500">
              <span>✓ Free plagiarism report</span>
              <span>✓ AI-detection certificate</span>
              <span>✓ 100% confidential</span>
            </div>
          </div>

          <!-- Right: writer showcase cards -->
          <div class="space-y-3 lg:pt-4">
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-500">Writers available now</p>

            <div
              v-for="w in heroWriters" :key="w.name"
              class="group rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm transition-all hover:bg-white/10"
            >
              <div class="flex items-start gap-4">
                <!-- Avatar -->
                <div class="relative shrink-0">
                  <div class="flex size-12 items-center justify-center rounded-xl bg-gc-700 text-sm font-bold text-white">
                    {{ w.initials }}
                  </div>
                  <div
                    class="absolute -bottom-1 -right-1 flex size-5 items-center justify-center rounded-full text-[8px] font-extrabold leading-none shadow"
                    :class="w.available ? 'bg-gc-400 text-forest-900' : 'bg-slate-500 text-white'"
                  >{{ w.available ? '●' : '○' }}</div>
                </div>

                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-2">
                    <p class="text-sm font-bold text-white">{{ w.name }}</p>
                    <div class="flex items-center gap-1 text-xs">
                      <Star class="size-3 fill-gold-400 text-gold-400" />
                      <span class="font-semibold text-white">{{ w.rating.toFixed(1) }}</span>
                      <span class="text-slate-400">· {{ w.orders.toLocaleString() }} orders</span>
                    </div>
                  </div>
                  <p class="mt-0.5 text-xs font-medium text-gold-300">{{ w.degree }}</p>
                  <p class="mt-1 text-xs text-slate-400">{{ w.specialty }}</p>
                  <p class="mt-2 border-l-2 border-gold-500/40 pl-2.5 text-xs italic leading-relaxed text-slate-400">
                    "{{ w.quote }}"
                  </p>
                </div>
              </div>
            </div>

            <a href="/order" class="block pt-1 text-center text-xs font-semibold text-gold-400 transition-colors hover:text-gold-300">
              Get matched with your writer →
            </a>
          </div>

        </div>
      </div>

      <!-- Bottom fade to white -->
      <div class="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-white to-transparent" />
    </section>

    <!-- ── TRUST BAR ──────────────────────────────────────────────────────────── -->
    <section class="border-y border-slate-200 bg-white py-5">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 divide-x divide-slate-200 sm:grid-cols-4">
          <div class="flex flex-col items-center gap-0.5 px-4 py-2">
            <span class="flex items-center gap-1 text-amber-500">
              <Star v-for="i in 5" :key="i" class="size-3.5 fill-current" />
            </span>
            <span class="text-xs font-semibold text-ink">4.9 Trustpilot</span>
          </div>
          <div class="flex flex-col items-center gap-0.5 px-4 py-2">
            <span class="flex items-center gap-1 text-amber-500">
              <Star v-for="i in 5" :key="i" class="size-3.5 fill-current" />
            </span>
            <span class="text-xs font-semibold text-ink">4.8 SiteJabber</span>
          </div>
          <div class="flex flex-col items-center gap-0.5 px-4 py-2">
            <span class="text-sm font-bold text-ink">50,000+</span>
            <span class="text-xs text-graphite">Papers delivered</span>
          </div>
          <div class="flex flex-col items-center gap-0.5 px-4 py-2">
            <span class="text-sm font-bold text-ink">600+</span>
            <span class="text-xs text-graphite">Expert writers</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── STATS ──────────────────────────────────────────────────────────────── -->
    <section ref="statsRef" class="bg-mist py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 gap-6 sm:grid-cols-4">
          <div
            v-for="s in stats" :key="s.label"
            class="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-card"
          >
            <p class="text-3xl font-bold text-ink tabular-nums">{{ s.value }}</p>
            <p class="mt-1 text-sm text-graphite">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── HOW IT WORKS ───────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">Simple process</p>
          <h2 class="text-3xl font-bold text-ink">How it works</h2>
          <p class="mt-3 text-graphite max-w-xl mx-auto">From brief to delivered in four steps. No account needed to get a quote.</p>
        </div>
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="step in steps" :key="step.n"
            class="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-card"
          >
            <span class="text-4xl font-extrabold text-slate-100 select-none leading-none">{{ step.n }}</span>
            <h3 class="mt-2 text-base font-semibold text-ink">{{ step.title }}</h3>
            <p class="mt-1.5 text-sm text-graphite leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
        <div class="mt-10 text-center">
          <a href="/order"
            class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
            Start your order <ArrowRight class="size-4" />
          </a>
        </div>
      </div>
    </section>

    <!-- ── SERVICES ───────────────────────────────────────────────────────────── -->
    <section class="bg-mist py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">What we offer</p>
          <h2 class="text-3xl font-bold text-ink">Academic writing services</h2>
          <p class="mt-3 text-graphite max-w-xl mx-auto">100+ subjects across undergraduate, postgraduate, and doctoral levels.</p>
        </div>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
            v-for="svc in services" :key="svc.href"
            :to="svc.href"
            class="group flex gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-card hover:shadow-lift hover:-translate-y-0.5 transition-all"
          >
            <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 group-hover:bg-gc-50 transition-colors">
              <component :is="svc.icon" class="size-5 text-slate-500 group-hover:text-gc-600 transition-colors" />
            </div>
            <div>
              <h3 class="text-sm font-semibold text-ink">{{ svc.title }}</h3>
              <p class="mt-1 text-xs text-graphite leading-relaxed">{{ svc.desc }}</p>
            </div>
          </NuxtLink>
        </div>
        <div class="mt-8 text-center">
          <NuxtLink to="/services" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
            View all services <ArrowRight class="size-4" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── ZERO AI SECTION ───────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-forest-950 py-20">
      <div class="pointer-events-none absolute inset-0 bg-hero-grid bg-grid-40" />
      <div class="pointer-events-none absolute -top-20 right-0 h-96 w-96 rounded-full bg-gold-400/8 blur-3xl" />
      <div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-12 lg:grid-cols-2">

          <!-- Left copy -->
          <div class="space-y-6">
            <div class="inline-flex items-center gap-2 rounded-full border border-gold-400/30 bg-gold-400/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-gold-300">
              <Bot class="size-3.5" />
              Zero AI Content
            </div>
            <h2 class="text-3xl font-bold text-white sm:text-4xl">
              Every word written<br class="hidden sm:block" />
              by a human expert.
            </h2>
            <p class="max-w-md leading-relaxed text-slate-300">
              AI-generated text is detectable, inconsistent, and doesn't know your subject the way a PhD expert does. Every GradeCrest paper is written by a verified human — and we can prove it.
            </p>
            <ul class="space-y-3">
              <li v-for="point in [
                'Free AI-detection certificate on every order',
                'Free plagiarism report included as standard',
                'Writers verified with degree credentials',
                'Revision if AI content is ever detected',
              ]" :key="point" class="flex items-start gap-3 text-sm text-slate-300">
                <CheckCircle2 class="mt-0.5 size-5 shrink-0 text-gold-400" />
                {{ point }}
              </li>
            </ul>
          </div>

          <!-- Right: certificate card -->
          <div class="flex justify-center">
            <div class="w-full max-w-sm space-y-5 rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
              <div class="flex items-center justify-between border-b border-white/10 pb-4">
                <span class="text-sm font-bold text-white">Verification Certificate</span>
                <Shield class="size-5 text-gold-400" />
              </div>
              <div class="space-y-4">
                <div v-for="check in [
                  { label: 'AI content detected',  value: '0%',   ok: true  },
                  { label: 'Plagiarism score',      value: '0%',   ok: true  },
                  { label: 'Human writing score',   value: '100%', ok: true  },
                  { label: 'Word count verified',   value: '✓',    ok: true  },
                  { label: 'Writer credentials',    value: 'PhD',  ok: true  },
                ]" :key="check.label"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-slate-400">{{ check.label }}</span>
                  <span class="font-semibold" :class="check.ok ? 'text-gc-400' : 'text-rose-400'">{{ check.value }}</span>
                </div>
              </div>
              <div class="rounded-xl border border-gold-400/30 bg-gold-400/10 px-4 py-3 text-center">
                <p class="text-xs font-bold uppercase tracking-widest text-gold-300">Verified · Human Written</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── WRITERS ────────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">The team</p>
          <h2 class="text-3xl font-bold text-ink">Meet some of our experts</h2>
          <p class="mt-3 text-graphite max-w-xl mx-auto">600+ verified writers holding postgraduate degrees. Every credential is checked before a writer handles their first order.</p>
        </div>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="w in writers" :key="w.name"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card hover:shadow-lift transition-shadow"
          >
            <div class="flex items-start gap-4">
              <!-- Avatar initials -->
              <div class="flex size-12 shrink-0 items-center justify-center rounded-xl bg-gc-50 text-base font-bold text-gc-700">
                {{ w.name.split(' ').map(p => p[0]).join('').slice(0, 2) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="font-semibold text-ink text-sm">{{ w.name }}</p>
                <p class="text-xs text-graphite">{{ w.degree }}</p>
                <div class="mt-1 flex items-center gap-1">
                  <Star class="size-3.5 fill-amber-400 text-amber-400" />
                  <span class="text-xs font-semibold text-ink">{{ w.rating.toFixed(1) }}</span>
                  <span class="text-xs text-graphite">· {{ w.orders.toLocaleString() }} orders</span>
                </div>
              </div>
            </div>
            <div class="mt-3 flex flex-wrap gap-1.5">
              <span
                v-for="sub in w.subjects" :key="sub"
                class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-graphite"
              >{{ sub }}</span>
            </div>
          </div>
        </div>
        <div class="mt-8 text-center">
          <NuxtLink to="/writers" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
            View all 600+ writers <ArrowRight class="size-4" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── PRICING SECTION ───────────────────────────────────────────────────── -->
    <section class="bg-mist py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 items-start">
          <div class="space-y-6">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">Transparent pricing</p>
              <h2 class="text-3xl font-bold text-ink">Simple, honest pricing</h2>
              <p class="mt-3 text-graphite leading-relaxed">
                Price depends on your academic level, deadline, and page count. What you see is what you pay — no hidden fees, no surprises at checkout.
              </p>
            </div>
            <ul class="space-y-2.5">
              <li v-for="item in [
                'Title page included free',
                'Reference list included free',
                'Plagiarism report included free',
                'AI-detection certificate free on request',
                'Formatting (APA, MLA, Chicago…) included free',
                'Unlimited revisions within the revision window',
              ]" :key="item" class="flex items-center gap-3 text-sm text-ink">
                <CheckCircle2 class="size-4 text-gc-600 shrink-0" />
                {{ item }}
              </li>
            </ul>
            <NuxtLink to="/pricing" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
              View full pricing table <ArrowRight class="size-4" />
            </NuxtLink>
          </div>
          <div>
            <PricingCalculator />
          </div>
        </div>
      </div>
    </section>

    <!-- ── GUARANTEES ─────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">Our promise</p>
          <h2 class="text-3xl font-bold text-ink">What we guarantee</h2>
        </div>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="g in guarantees" :key="g.title"
            class="rounded-2xl border border-slate-200 bg-white p-6 shadow-card"
          >
            <component :is="g.icon" class="size-7 text-gc-600 mb-3" />
            <h3 class="text-sm font-semibold text-ink">{{ g.title }}</h3>
            <p class="mt-1.5 text-sm text-graphite leading-relaxed">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── TESTIMONIALS ───────────────────────────────────────────────────────── -->
    <section class="bg-mist py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">Student reviews</p>
          <h2 class="text-3xl font-bold text-ink">What students say</h2>
          <div class="mt-3 flex items-center justify-center gap-2">
            <span class="flex items-center gap-1 text-amber-500">
              <Star v-for="i in 5" :key="i" class="size-4 fill-current" />
            </span>
            <span class="text-sm font-semibold text-ink">4.9 / 5</span>
            <span class="text-sm text-graphite">from 12,400+ verified reviews</span>
          </div>
        </div>
        <!-- Masonry columns — no JS carousel needed -->
        <div class="columns-1 gap-4 sm:columns-2 lg:columns-3 [column-fill:balance]">
          <div
            v-for="t in testimonials" :key="t.name"
            class="mb-4 break-inside-avoid rounded-2xl border border-slate-200 bg-white p-5 shadow-card"
          >
            <div class="flex items-center gap-1 mb-3">
              <Star v-for="i in t.stars" :key="i" class="size-3.5 fill-amber-400 text-amber-400" />
            </div>
            <p class="text-sm text-ink leading-relaxed">"{{ t.text }}"</p>
            <div class="mt-3 flex items-center justify-between">
              <p class="text-xs font-semibold text-graphite">{{ t.name }}</p>
              <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-graphite">{{ t.subject }}</span>
            </div>
          </div>
        </div>
        <div class="mt-8 text-center">
          <NuxtLink to="/reviews" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
            Read all reviews <ArrowRight class="size-4" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── SUBJECT CLOUD ──────────────────────────────────────────────────────── -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-4">100+ subjects covered</p>
        <div class="flex flex-wrap justify-center gap-2">
          <NuxtLink
            v-for="sub in subjects" :key="sub"
            :to="`/services?subject=${encodeURIComponent(sub)}`"
            class="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm text-graphite hover:border-gc-300 hover:bg-gc-50 hover:text-gc-700 transition-colors"
          >
            {{ sub }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── FAQ ───────────────────────────────────────────────────────────────── -->
    <section class="bg-mist py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600 mb-2">Questions</p>
          <h2 class="text-3xl font-bold text-ink">Frequently asked questions</h2>
        </div>
        <div class="space-y-3">
          <details
            v-for="faq in faqs" :key="faq.q"
            class="group rounded-2xl border border-slate-200 bg-white shadow-card"
          >
            <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
              {{ faq.q }}
              <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-graphite transition-transform group-open:rotate-45">+</span>
            </summary>
            <p class="px-6 pb-5 text-sm text-graphite leading-relaxed">{{ faq.a }}</p>
          </details>
        </div>
        <div class="mt-8 text-center">
          <NuxtLink to="/faq" class="text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
            See all questions →
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── FINAL CTA ─────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-forest-950 py-20">
      <div class="pointer-events-none absolute inset-0 bg-hero-grid bg-grid-40" />
      <div class="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div class="size-[600px] rounded-full bg-gold-400/8 blur-3xl" />
      </div>
      <div class="relative mx-auto max-w-3xl space-y-7 px-4 text-center sm:px-6 lg:px-8">
        <div class="inline-flex items-center gap-2 rounded-full border border-gold-400/30 bg-gold-400/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-gold-300">
          <span class="size-1.5 animate-pulse rounded-full bg-gold-400" />
          Writers available now
        </div>
        <h2 class="text-3xl font-bold text-white sm:text-4xl">
          Ready to improve your grade?
        </h2>
        <p class="mx-auto max-w-xl text-lg text-slate-300">
          Join 20,000+ students who trust GradeCrest. Place your order in under 2 minutes.
        </p>
        <div class="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a href="/order"
            class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-10 py-4 text-base font-bold text-white shadow-lg transition-colors hover:bg-gc-700">
            Place your order <ArrowRight class="size-5" />
          </a>
          <NuxtLink to="/pricing"
            class="inline-flex items-center gap-2 text-sm font-semibold text-slate-400 transition-colors hover:text-white">
            View pricing first →
          </NuxtLink>
        </div>
        <p class="text-xs text-slate-500">Grade or money back · Zero AI content · 100% confidential</p>
      </div>
    </section>

    <!-- Mobile sticky CTA -->
    <div class="fixed inset-x-0 bottom-0 z-40 border-t border-slate-200 bg-white px-4 py-3 shadow-lift lg:hidden">
      <a href="/order"
        class="flex h-12 w-full items-center justify-center rounded-xl bg-gc-600 text-sm font-bold text-white">
        Place your order
      </a>
    </div>

  </div>
</template>
