<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Research Paper Writing Service from $15/Page | ResearchPaperMate',
  description: 'Research papers written by verified PhD and Master\'s specialists — not AI. From $15/page. Grade or money back. 14,700+ papers delivered, 4.8/5 rated.',
  ogTitle: 'ResearchPaperMate — Research Papers by Real Researchers',
  ogDescription: 'Human-written research papers, essays and dissertations across 100+ subjects. Grade or money back. Zero AI content.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://researchpapermate.com/' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ProfessionalService',
      name: 'ResearchPaperMate',
      description: 'Academic writing service providing research papers, essays, and assignments by verified human experts.',
      url: 'https://researchpapermate.com',
      priceRange: '$15–$50 per page',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '14700' },
    }),
  }],
})

// ── Hero sentinel for sticky bar ──────────────────────────────────────────────
const heroCta = ref<HTMLElement | null>(null)
const showStickyBar = ref(false)
let stickyObs: IntersectionObserver | null = null

onMounted(() => {
  if (!heroCta.value) return
  stickyObs = new IntersectionObserver(([entry]) => {
    showStickyBar.value = !entry.isIntersecting
  }, { threshold: 0 })
  stickyObs.observe(heroCta.value)
})
onUnmounted(() => stickyObs?.disconnect())

// ── Grade ticker ─────────────────────────────────────────────────────────────
const recentGrades = [
  { grade: 'A+', subject: 'Sociology · LSE' },
  { grade: 'A',  subject: 'Finance MBA · Warwick' },
  { grade: 'A',  subject: 'Nursing Research · KCL' },
  { grade: 'B+', subject: 'Quantitative Methods · UCL' },
  { grade: 'A+', subject: 'Clinical Psychology · Edinburgh' },
  { grade: 'A',  subject: 'Business Strategy · Manchester' },
  { grade: 'A',  subject: 'Data Analysis · Birmingham' },
  { grade: 'B+', subject: 'Literature Review · Bristol' },
  { grade: 'A+', subject: 'Biomedical Sciences · Oxford' },
  { grade: 'A',  subject: 'Environmental Law · Durham' },
]

// ── Services ─────────────────────────────────────────────────────────────────
const services = [
  { title: 'Research Papers',  href: '/services/research-papers',  badge: 'Most popular', desc: 'Original, citation-rich papers across STEM, business, humanities and social sciences.' },
  { title: 'Essays',           href: '/services/essays',           badge: null,           desc: 'Argumentative, analytical, descriptive — any format, any level, any subject.' },
  { title: 'Dissertations',    href: '/services/dissertations',    badge: 'Full support', desc: 'Proposal, literature review, methodology, data analysis, discussion — complete chapters.' },
  { title: 'Case Studies',     href: '/services/case-studies',     badge: null,           desc: 'In-depth analysis with structured arguments, evidence and clear recommendations.' },
  { title: 'Data Analysis',    href: '/services/data-analysis',    badge: null,           desc: 'SPSS, R, Python or Excel — full written interpretation and methodology.' },
  { title: 'Lab Reports',      href: '/services/lab-reports',      badge: null,           desc: 'Structured write-ups with correct methodology, results and discussion sections.' },
  { title: 'Literature Reviews', href: '/services/literature-reviews', badge: null,        desc: 'Systematic, narrative, and scoping reviews. Themes, gaps, synthesis.' },
  { title: 'Nursing Research', href: '/services/research-papers', badge: null,              desc: 'PICOT, SOAP, NCP, clinical case studies — specialist nursing writers.' },
  { title: 'Admission Essays', href: '/services/essays', badge: null,                       desc: 'Personal statements and application essays that stand out to admissions committees.' },
]

// ── Researchers ───────────────────────────────────────────────────────────────
const researchers = [
  {
    initials: 'AW', name: 'Dr. A. Williams', field: 'Research Methodology', degree: 'PhD',
    tags: ['Systematic Reviews', 'SPSS', 'Mixed Methods'],
    papers: 1840, rating: 4.97,
    quote: '3 peer-reviewed publications in qualitative research design.',
  },
  {
    initials: 'MT', name: 'Prof. M. Tanaka', field: 'Finance & Econometrics', degree: 'PhD',
    tags: ['Regression Analysis', 'Financial Modelling', 'EViews'],
    papers: 2310, rating: 5.0,
    quote: 'Former investment analyst — I speak the language of your marker.',
  },
  {
    initials: 'SR', name: 'Dr. S. Rashid', field: 'Biomedical Sciences', degree: 'PhD',
    tags: ['Literature Reviews', 'Lab Reports', 'Clinical Trials'],
    papers: 1120, rating: 4.98,
    quote: 'Published in Nature Reviews. I read primary sources, not Wikipedia.',
  },
]

// ── Steps ─────────────────────────────────────────────────────────────────────
const steps = [
  { n: '01', title: 'Fill in your brief',           desc: 'Paper type, subject, level, deadline. Attach rubrics or reading lists.' },
  { n: '02', title: 'Pay into secure escrow',       desc: 'Your money is held safely — released only after you approve the work.' },
  { n: '03', title: 'Your researcher works',        desc: 'Message them directly, share files, request progress updates.' },
  { n: '04', title: 'Download & request revisions', desc: 'Receive your paper. Unlimited free revisions within the window.' },
]

// ── Guarantees ────────────────────────────────────────────────────────────────
const guarantees = [
  { icon: '🎓', title: 'Grade or full refund',       desc: "We set a grade target. Miss it → free rewrite or complete refund. No conditions." },
  { icon: '✍️', title: 'Zero AI content',            desc: 'Every paper is handwritten. Request a free AI-detection report as proof.' },
  { icon: '🔒', title: '100% confidential',          desc: 'Your identity and order details are never shared with any third party.' },
  { icon: '📋', title: 'Plagiarism report included', desc: 'Checked against academic databases. Originality report included free.' },
  { icon: '🔁', title: 'Unlimited free revisions',   desc: 'Within the revision window, request as many changes as you need.' },
  { icon: '💬', title: 'Direct researcher access',   desc: 'Message your assigned expert directly — no tickets, no queues.' },
]

// ── Testimonials ──────────────────────────────────────────────────────────────
const testimonials = [
  {
    grade: 'A',
    subject: 'Business Strategy (MBA)',
    quote: "My writer clearly understood Porter's Five Forces at a graduate level. Sharp, well-sourced, exactly what the brief asked for.",
    name: 'Marcus L.',
    university: 'University of Edinburgh',
  },
  {
    grade: 'A+',
    subject: 'Nursing Literature Review',
    quote: "I needed a systematic review in APA 7. The writer found sources I hadn't come across and synthesised them perfectly. Above and beyond.",
    name: 'Priya T.',
    university: "King's College London",
  },
  {
    grade: 'B+',
    subject: 'Quantitative Data Analysis',
    quote: "Stats is not my thing. They ran the SPSS, wrote it up correctly, and explained every result so I actually understood it. Lifesaver.",
    name: 'Daniel O.',
    university: 'Northumbria University',
  },
  {
    grade: 'A',
    subject: 'Clinical Psychology Essay',
    quote: "I was genuinely worried about the turnaround — 48 hours for a 3,000-word essay. It was delivered in 36 and the references were impeccable.",
    name: 'Aisha M.',
    university: 'University of Glasgow',
  },
  {
    grade: 'A+',
    subject: 'Law Dissertation (LLM)',
    quote: "My supervisor commented on the depth of the legal analysis. The writer clearly had postgraduate law training. I'll use ResearchPaperMate again for sure.",
    name: 'James K.',
    university: 'Queen Mary University of London',
  },
  {
    grade: 'A',
    subject: 'Environmental Science Lab Report',
    quote: "Perfect methodology, correct citation format, delivered early. No back-and-forth needed — the brief was followed exactly.",
    name: 'Sophie R.',
    university: 'University of Leeds',
  },
]

// ── Methodology ───────────────────────────────────────────────────────────────
const methodology = [
  { step: '01', title: 'Source verification',  desc: 'Only peer-reviewed journals, institutional databases, and primary sources.' },
  { step: '02', title: 'Methodology match',    desc: 'Qualitative, quantitative, or mixed methods — chosen to match your brief.' },
  { step: '03', title: 'Argument structure',   desc: 'Clear thesis with evidence-led progression your marker can follow.' },
  { step: '04', title: 'Citation accuracy',    desc: 'APA 7, Harvard, MLA, Chicago, Vancouver — formatted to the standard.' },
]

// ── Subjects ──────────────────────────────────────────────────────────────────
const subjects = [
  'Nursing', 'Business', 'Psychology', 'Biology', 'Chemistry', 'History',
  'Law', 'Finance', 'Sociology', 'Literature', 'Statistics', 'Engineering',
  'Public Health', 'Marketing', 'Economics', 'Philosophy', 'Education', 'Politics',
]

// ── Pricing tiers ─────────────────────────────────────────────────────────────
const pricingTiers = [
  {
    name: 'Standard',
    from: '$15',
    unit: '/page',
    turnaround: '14 days',
    level: "Bachelor's & below",
    features: ['Peer-reviewed sources', 'Standard citation style', 'Free plagiarism report', '1 free revision round'],
    cta: 'Start standard',
    highlight: false,
  },
  {
    name: 'Advanced',
    from: '$22',
    unit: '/page',
    turnaround: '7 days',
    level: "Master's & MBA",
    features: ['All Standard features', 'Primary & secondary research', 'Expert subject match', '3 free revision rounds'],
    cta: 'Start advanced',
    highlight: true,
  },
  {
    name: 'Elite',
    from: '$35',
    unit: '/page',
    turnaround: '3 days',
    level: 'PhD & Doctorate',
    features: ['All Advanced features', 'PhD-only researcher pool', 'Unlimited revisions', 'Priority queue + 24h support'],
    cta: 'Start elite',
    highlight: false,
  },
]
</script>

<template>
  <!-- ─── HERO — deep claret, journal aesthetic ──────────────────────────── -->
  <section class="relative overflow-hidden bg-claret-950">
    <!-- Subtle texture overlay -->
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_20%_40%,rgba(123,34,65,0.6),transparent)]"/>
    <!-- Fine grid lines — nod to graph paper / academic notebooks -->
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:48px_48px]"/>

    <div class="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-16 pb-20 sm:pt-24 sm:pb-28">
      <div class="grid items-center gap-12 lg:grid-cols-2">

        <!-- Left: headline + CTAs -->
        <div>
          <!-- Trust badge -->
          <div class="mb-6 flex flex-wrap items-center gap-3">
            <div class="inline-flex items-center gap-2 rounded-full border border-claret-700 bg-claret-900/60 px-4 py-1.5 text-xs font-semibold text-claret-200 backdrop-blur-sm">
              <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-amber-400"/>
              PhD &amp; Master's verified — live researchers available now
            </div>
            <div class="inline-flex items-center gap-1.5 rounded-full border border-green-800 bg-green-950/60 px-3 py-1.5 text-xs font-semibold text-green-300 backdrop-blur-sm">
              <span class="h-1.5 w-1.5 rounded-full bg-green-400"/>
              42 orders placed today
            </div>
          </div>

          <!-- Headline — serif display font -->
          <h1 class="font-serif text-5xl font-normal leading-[1.07] tracking-tight text-white sm:text-6xl lg:text-[3.6rem]">
            Research that<br />
            holds up when<br />
            <em class="not-italic text-amber-400">your marker</em><br />
            reads closely.
          </h1>

          <p class="mt-6 max-w-lg text-lg leading-relaxed text-claret-200">
            Every paper is written by a verified researcher with a postgraduate degree in your subject — someone who has read the primary sources, not summarised Wikipedia.
          </p>

          <!-- Price anchor -->
          <div class="mt-7 flex items-center gap-3">
            <span class="rounded-lg bg-claret-900/80 px-4 py-2 text-sm font-semibold text-amber-300 ring-1 ring-claret-700">
              From $15/page
            </span>
            <span class="text-sm text-claret-300">· 4.8★ · 14,700+ papers · Grade guaranteed</span>
          </div>

          <!-- CTAs -->
          <div class="mt-8 flex flex-wrap gap-3">
            <a href="/order"
              class="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-amber-900/30 transition-colors hover:bg-amber-500">
              Start my paper
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
            </a>
            <a href="/pricing"
              class="inline-flex items-center gap-2 rounded-xl border border-claret-600 bg-claret-900/60 px-7 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:border-claret-400 hover:bg-claret-800/60">
              View pricing
            </a>
          </div>

          <!-- Micro-trust row -->
          <div ref="heroCta" class="mt-6 flex flex-wrap gap-x-5 gap-y-1.5 text-xs text-claret-300">
            <span>✓ Grade or money back</span>
            <span>✓ Zero AI content</span>
            <span>✓ Free plagiarism report</span>
            <span>✓ No payment until you approve</span>
          </div>

          <!-- Trust badges row -->
          <div class="mt-5">
            <TrustBadges />
          </div>
        </div>

        <!-- Right: researcher credential cards -->
        <div class="space-y-3">
          <p class="text-[10px] font-bold uppercase tracking-widest text-claret-400 mb-4">Some of our researchers</p>
          <div
            v-for="r in researchers"
            :key="r.name"
            class="group rounded-2xl border border-claret-800 bg-claret-900/50 p-5 backdrop-blur-sm transition-all hover:border-claret-600 hover:bg-claret-900/80"
          >
            <div class="flex items-start gap-4">
              <div class="relative shrink-0">
                <div class="flex size-12 items-center justify-center rounded-xl bg-claret-800 text-sm font-bold text-white">
                  {{ r.initials }}
                </div>
                <div class="absolute -bottom-1 -right-1 flex size-5 items-center justify-center rounded-full bg-amber-500 text-[9px] font-extrabold text-white shadow">
                  {{ r.degree }}
                </div>
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <p class="text-sm font-bold text-white">{{ r.name }}</p>
                    <p class="text-xs text-amber-400 font-medium">{{ r.field }}</p>
                  </div>
                  <div class="shrink-0 text-right text-xs text-claret-300">
                    <span class="text-amber-400">★</span> {{ r.rating }}
                    <span class="ml-1 text-claret-400">· {{ r.papers.toLocaleString() }}p</span>
                  </div>
                </div>
                <div class="mt-2 flex flex-wrap gap-1">
                  <span v-for="tag in r.tags" :key="tag" class="rounded-full border border-claret-700 bg-claret-800/60 px-2 py-0.5 text-[10px] text-claret-300">{{ tag }}</span>
                </div>
                <p class="mt-2 text-xs italic leading-relaxed text-claret-300 border-l-2 border-amber-700 pl-2.5">
                  "{{ r.quote }}"
                </p>
              </div>
            </div>
          </div>
          <a href="/writers" class="block text-center text-xs font-semibold text-amber-400 transition-colors hover:text-amber-300 pt-1">
            Meet all 200+ researchers →
          </a>
        </div>

      </div>
    </div>
  </section>

  <!-- ─── GRADE TICKER — scrolling social proof ─────────────────────────── -->
  <section class="border-y border-claret-900/20 bg-claret-900 py-3 overflow-hidden">
    <div class="flex gap-8 animate-[marquee_35s_linear_infinite] whitespace-nowrap">
      <div
        v-for="(g, i) in [...recentGrades, ...recentGrades]"
        :key="`${g.subject}-${i}`"
        class="inline-flex shrink-0 items-center gap-2.5"
      >
        <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-amber-500 text-xs font-extrabold text-white">{{ g.grade }}</span>
        <span class="text-xs text-claret-200">{{ g.subject }}</span>
        <span class="h-1 w-1 rounded-full bg-claret-700"/>
      </div>
    </div>
  </section>

  <!-- ─── STATS BAR — warm parchment ───────────────────────────────────── -->
  <section class="bg-parchment-100 border-b border-parchment-300">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-2 divide-x divide-parchment-300 md:grid-cols-4 md:divide-y-0">
        <div class="py-8 px-6 text-center">
          <p class="font-serif text-3xl text-claret-900">14,700+</p>
          <p class="mt-1 text-sm font-semibold text-ink-secondary">Papers delivered</p>
          <p class="mt-0.5 text-xs text-ink-muted">Across 100+ subjects</p>
        </div>
        <div class="py-8 px-6 text-center">
          <p class="font-serif text-3xl text-claret-900">200+</p>
          <p class="mt-1 text-sm font-semibold text-ink-secondary">Expert researchers</p>
          <p class="mt-0.5 text-xs text-ink-muted">Master's &amp; PhD level</p>
        </div>
        <div class="py-8 px-6 text-center">
          <p class="font-serif text-3xl text-claret-900">4.8/5</p>
          <p class="mt-1 text-sm font-semibold text-ink-secondary">Average rating</p>
          <p class="mt-0.5 text-xs text-ink-muted">Based on 8,200+ reviews</p>
        </div>
        <div class="py-8 px-6 text-center">
          <p class="font-serif text-3xl text-claret-900">98%</p>
          <p class="mt-1 text-sm font-semibold text-ink-secondary">On-time delivery</p>
          <p class="mt-0.5 text-xs text-ink-muted">Delivered by deadline</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── THREE DIFFERENCES — parchment ───────────────────────────────── -->
  <section class="bg-parchment-100 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 text-center">
        <p class="mb-3 text-[11px] font-bold uppercase tracking-widest text-amber-700">Why ResearchPaperMate</p>
        <h2 class="font-serif text-4xl text-ink-DEFAULT sm:text-5xl">The research service<br /><em class="not-italic text-claret-800">built differently.</em></h2>
      </div>
      <div class="grid gap-6 md:grid-cols-3">
        <div class="rounded-2xl border border-parchment-300 bg-white p-8 shadow-sm">
          <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-claret-900 text-2xl">👩‍🔬</div>
          <h3 class="text-lg font-bold text-ink-DEFAULT">Written by a researcher, not generated by one.</h3>
          <p class="mt-3 text-sm leading-relaxed text-ink-secondary">Every paper is handwritten by a verified specialist — a real human who has read the literature, worked in the field, and understands what your marker wants.</p>
        </div>
        <div class="rounded-2xl border border-parchment-300 bg-white p-8 shadow-sm">
          <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-claret-900 text-2xl">🎯</div>
          <h3 class="text-lg font-bold text-ink-DEFAULT">Your exact subject, not a generalist.</h3>
          <p class="mt-3 text-sm leading-relaxed text-ink-secondary">We match you with a writer who holds qualifications in your specific discipline. A nursing paper goes to a nursing specialist. A finance dissertation to a finance PhD.</p>
        </div>
        <div class="rounded-2xl border border-amber-200 bg-amber-50 p-8 shadow-sm">
          <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-500 text-2xl">🏆</div>
          <h3 class="text-lg font-bold text-ink-DEFAULT">Grade guaranteed, or your money back.</h3>
          <p class="mt-3 text-sm leading-relaxed text-ink-secondary">We stand behind the quality of every paper. If the work doesn't meet your stated grade target, we rewrite it free or issue a full refund — no conditions, no runaround.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── PRICING — parchment, clean tiers ─────────────────────────────── -->
  <section class="bg-parchment-200 py-20 border-y border-parchment-300">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 text-center">
        <p class="mb-3 text-[11px] font-bold uppercase tracking-widest text-amber-700">Transparent pricing</p>
        <h2 class="font-serif text-4xl text-ink-DEFAULT sm:text-5xl">No surprises. No hidden fees.</h2>
        <p class="mt-4 text-ink-secondary">Price is determined by academic level, deadline, and pages. No upsells.</p>
      </div>
      <div class="grid gap-5 md:grid-cols-3">
        <div
          v-for="tier in pricingTiers"
          :key="tier.name"
          class="relative rounded-2xl p-8 transition-all"
          :class="tier.highlight
            ? 'bg-claret-900 text-white shadow-xl shadow-claret-900/20 ring-2 ring-amber-500'
            : 'bg-white border border-parchment-300 shadow-sm'"
        >
          <div v-if="tier.highlight" class="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-amber-500 px-4 py-1 text-xs font-bold text-white shadow">Most chosen</div>
          <p class="text-sm font-bold uppercase tracking-widest" :class="tier.highlight ? 'text-amber-400' : 'text-amber-700'">{{ tier.name }}</p>
          <div class="mt-3 flex items-end gap-1">
            <span class="font-serif text-5xl" :class="tier.highlight ? 'text-white' : 'text-claret-900'">{{ tier.from }}</span>
            <span class="mb-2 text-sm" :class="tier.highlight ? 'text-claret-300' : 'text-ink-muted'">{{ tier.unit }}</span>
          </div>
          <p class="mt-1 text-sm" :class="tier.highlight ? 'text-claret-300' : 'text-ink-muted'">From · {{ tier.turnaround }} · {{ tier.level }}</p>
          <ul class="mt-6 space-y-2.5">
            <li v-for="f in tier.features" :key="f" class="flex items-center gap-2.5 text-sm" :class="tier.highlight ? 'text-claret-100' : 'text-ink-secondary'">
              <span class="flex h-4 w-4 shrink-0 items-center justify-center rounded-full" :class="tier.highlight ? 'bg-amber-500' : 'bg-claret-100'">
                <svg class="h-2.5 w-2.5" :class="tier.highlight ? 'text-white' : 'text-claret-900'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
              </span>
              {{ f }}
            </li>
          </ul>
          <a
            :href="`/order`"
            class="mt-8 block rounded-xl py-3 text-center text-sm font-bold transition-colors"
            :class="tier.highlight
              ? 'bg-amber-500 text-white hover:bg-amber-400'
              : 'bg-claret-900 text-white hover:bg-claret-800'"
          >
            {{ tier.cta }}
          </a>
        </div>
      </div>
      <div class="mt-8 flex flex-col items-center gap-2">
        <div class="inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-1.5 text-xs font-semibold text-amber-800">
          ⚡ Rush delivery available — as fast as 2 hours
        </div>
        <p class="text-center text-xs text-ink-muted">
          Prices are per page (275 words). Rush deadlines (under 6h) have a surcharge. <a href="/pricing" class="text-amber-700 hover:underline">Full pricing →</a>
        </p>
      </div>
    </div>
  </section>

  <!-- ─── SERVICES — claret background ─────────────────────────────────── -->
  <section class="bg-claret-950 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-10 flex items-end justify-between">
        <div>
          <p class="mb-2 text-[11px] font-bold uppercase tracking-widest text-amber-500">100+ subjects covered</p>
          <h2 class="font-serif text-4xl text-white sm:text-5xl">Every paper type.<br />Every subject.</h2>
        </div>
        <a href="/services" class="hidden text-sm font-semibold text-amber-400 transition-colors hover:text-amber-300 sm:block">All services →</a>
      </div>
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <a
          v-for="svc in services"
          :key="svc.title"
          :href="svc.href"
          class="group relative flex flex-col rounded-2xl border border-claret-800 bg-claret-900/60 p-6 backdrop-blur-sm transition-all hover:border-claret-600 hover:bg-claret-900"
        >
          <div v-if="svc.badge" class="absolute right-4 top-4 rounded-full bg-amber-500/20 px-2.5 py-0.5 text-[10px] font-bold text-amber-400 ring-1 ring-amber-500/30">{{ svc.badge }}</div>
          <h3 class="text-sm font-bold text-white transition-colors group-hover:text-amber-300">{{ svc.title }}</h3>
          <p class="mt-2 flex-1 text-sm leading-relaxed text-claret-300">{{ svc.desc }}</p>
          <span class="mt-4 text-xs font-semibold text-amber-500 opacity-0 transition-opacity group-hover:opacity-100">Order now →</span>
        </a>
      </div>
      <!-- Subject tags -->
      <div class="mt-8 flex flex-wrap gap-2">
        <span v-for="sub in subjects" :key="sub" class="rounded-full border border-claret-700 bg-claret-900/60 px-3 py-1 text-xs text-claret-300 transition-colors hover:border-amber-700 hover:text-amber-300 cursor-default">{{ sub }}</span>
        <span class="rounded-full border border-dashed border-claret-700 px-3 py-1 text-xs text-claret-500">+80 more</span>
      </div>
    </div>
  </section>

  <!-- ─── RESEARCH METHODOLOGY — parchment ─────────────────────────────── -->
  <section class="bg-parchment-100 py-20 border-y border-parchment-300">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="grid items-center gap-14 lg:grid-cols-2">
        <div>
          <p class="mb-3 text-[11px] font-bold uppercase tracking-widest text-amber-700">Our research standard</p>
          <h2 class="font-serif text-4xl text-ink-DEFAULT sm:text-5xl leading-tight">
            Papers that hold up<br /><em class="not-italic text-claret-800">when your marker<br />reads them closely.</em>
          </h2>
          <p class="mt-5 max-w-md text-ink-secondary leading-relaxed">
            We don't just write. We research — properly. Every paper follows an academic methodology your supervisor would recognise.
          </p>
          <a href="/order" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-claret-900 px-6 py-3.5 text-sm font-bold text-white transition-colors hover:bg-claret-800">
            Start a research paper
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
          </a>
        </div>
        <div class="space-y-3">
          <div
            v-for="m in methodology"
            :key="m.step"
            class="flex gap-4 rounded-xl border border-parchment-300 bg-white p-5 transition-colors hover:border-amber-200"
          >
            <div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-claret-900 text-xs font-bold text-amber-400">
              {{ m.step }}
            </div>
            <div>
              <p class="text-sm font-bold text-ink-DEFAULT">{{ m.title }}</p>
              <p class="mt-1 text-sm leading-relaxed text-ink-secondary">{{ m.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── HOW IT WORKS — white ────────────────────────────────────────── -->
  <section class="bg-white py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-14 text-center">
        <p class="mb-3 text-[11px] font-bold uppercase tracking-widest text-amber-700">Simple process</p>
        <h2 class="font-serif text-4xl text-ink-DEFAULT sm:text-5xl">Brief in. Paper out.<br />Four steps.</h2>
      </div>
      <div class="relative grid gap-8 md:grid-cols-4 md:gap-0">
        <!-- Connector line -->
        <div class="hidden md:block absolute top-5 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-claret-200 via-amber-400 to-claret-200"/>
        <div v-for="step in steps" :key="step.n" class="flex flex-col items-center px-4 text-center">
          <div class="relative z-10 mb-5 flex size-10 items-center justify-center rounded-full border-2 border-amber-400 bg-white text-sm font-extrabold text-claret-900 shadow-sm">
            {{ step.n }}
          </div>
          <h3 class="text-sm font-bold text-ink-DEFAULT">{{ step.title }}</h3>
          <p class="mt-2 text-xs leading-relaxed text-ink-secondary">{{ step.desc }}</p>
        </div>
      </div>
      <div class="mt-12 text-center">
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-8 py-4 text-sm font-bold text-white shadow-sm transition-colors hover:bg-amber-500">
          Place my order — from $15/page
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
        </a>
      </div>
    </div>
  </section>

  <!-- ─── TESTIMONIALS — parchment, grade badges prominent ────────────── -->
  <section class="bg-parchment-200 py-20 border-y border-parchment-300">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 text-center">
        <p class="mb-3 text-[11px] font-bold uppercase tracking-widest text-amber-700">Student outcomes</p>
        <h2 class="font-serif text-4xl text-ink-DEFAULT sm:text-5xl">Real students.<br />Real universities.<br /><em class="not-italic text-claret-800">Real grades.</em></h2>
      </div>
      <div class="grid gap-6 md:grid-cols-3">
        <div
          v-for="t in testimonials"
          :key="t.name"
          class="relative overflow-hidden rounded-2xl border border-parchment-300 bg-white p-7 shadow-sm transition-shadow hover:shadow-md"
        >
          <!-- Grade badge — top right, dominant -->
          <div class="absolute right-6 top-6 flex size-16 flex-col items-center justify-center rounded-2xl bg-claret-900 text-white shadow-lg">
            <span class="text-2xl font-extrabold leading-none text-amber-400">{{ t.grade }}</span>
            <span class="mt-0.5 text-[9px] font-bold uppercase tracking-wider text-claret-300">grade</span>
          </div>
          <p class="text-[10px] font-bold uppercase tracking-widest text-amber-700">{{ t.subject }}</p>
          <blockquote class="mt-3 pr-20 text-sm italic leading-relaxed text-ink-secondary">"{{ t.quote }}"</blockquote>
          <div class="mt-5 flex items-center gap-2 border-t border-parchment-300 pt-4">
            <div class="flex size-8 items-center justify-center rounded-full bg-claret-100 text-xs font-bold text-claret-900">{{ t.name.charAt(0) }}</div>
            <div>
              <p class="text-xs font-bold text-ink-DEFAULT">{{ t.name }}</p>
              <p class="text-xs text-ink-muted">{{ t.university }}</p>
            </div>
            <div class="ml-auto flex gap-0.5">
              <svg v-for="i in 5" :key="i" class="h-3 w-3 text-amber-500" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            </div>
          </div>
        </div>
      </div>
      <div class="mt-8 text-center">
        <a href="/reviews" class="text-sm font-semibold text-amber-700 transition-colors hover:text-amber-600">Read all 8,200+ reviews →</a>
      </div>
    </div>
  </section>

  <!-- ─── GUARANTEES — deep claret ─────────────────────────────────────── -->
  <section class="bg-claret-950 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 text-center">
        <p class="mb-3 text-[11px] font-bold uppercase tracking-widest text-amber-500">Our promise</p>
        <h2 class="font-serif text-4xl text-white sm:text-5xl">We stand behind<br /><em class="not-italic text-amber-400">every paper.</em></h2>
        <p class="mt-3 text-claret-300">Not small print. Actual commitments.</p>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="g in guarantees"
          :key="g.title"
          class="flex gap-4 rounded-2xl bg-claret-900/60 p-6 ring-1 ring-claret-800 transition-colors hover:bg-claret-900 hover:ring-amber-800"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-claret-800 text-xl">{{ g.icon }}</div>
          <div>
            <h3 class="font-semibold text-white">{{ g.title }}</h3>
            <p class="mt-1.5 text-sm leading-relaxed text-claret-300">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── FAQ ───────────────────────────────────────────────────────────── -->
  <HomeFaq />

  <!-- ─── STICKY ORDER BAR — slides in when hero CTA leaves view ────────── -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="translate-y-full"
      enter-to-class="translate-y-0"
      leave-active-class="transition-transform duration-200 ease-in"
      leave-from-class="translate-y-0"
      leave-to-class="translate-y-full"
    >
      <div
        v-if="showStickyBar"
        class="fixed bottom-20 sm:bottom-0 inset-x-0 z-[48] border-t border-claret-800 bg-claret-950/95 backdrop-blur-md shadow-2xl"
      >
        <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <div class="hidden items-center gap-3 sm:flex">
            <span class="h-2 w-2 rounded-full bg-amber-400 animate-pulse"/>
            <p class="text-sm font-semibold text-white">ResearchPaperMate</p>
            <span class="text-claret-600">·</span>
            <p class="text-sm text-claret-300">From $15/page · Grade guaranteed · 200+ PhD researchers</p>
          </div>
          <p class="text-sm text-claret-300 sm:hidden">From $15/page · Grade guaranteed</p>
          <div class="flex shrink-0 items-center gap-3">
            <div class="hidden items-center gap-1 sm:flex">
              <svg v-for="i in 5" :key="i" class="h-3 w-3 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
              <span class="ml-1 text-xs text-claret-300">4.8</span>
            </div>
            <a
              href="/order"
              class="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-sm font-bold text-white shadow-lg transition-colors hover:bg-amber-400"
            >
              Start my paper
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
            </a>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- ─── FINAL CTA — amber on deep claret ─────────────────────────────── -->
  <section class="bg-claret-900 py-24">
    <div class="mx-auto max-w-3xl px-4 text-center sm:px-6">
      <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-claret-700 bg-claret-950/60 px-4 py-1.5 text-xs font-semibold text-claret-300">
        <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-amber-400"/>
        Researchers available now — response in minutes
      </div>
      <h2 class="font-serif text-4xl text-white sm:text-5xl">
        Your research paper<br />deserves a real researcher.
      </h2>
      <p class="mt-5 text-lg leading-relaxed text-claret-200">
        Tell us your subject and deadline. We'll match you with a PhD-verified specialist and you'll have a draft in hand — not a generated paragraph.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <a href="/order"
          class="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-8 py-4 text-sm font-bold text-white shadow-lg shadow-amber-900/30 transition-colors hover:bg-amber-400">
          Place my order — from $15/page
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
        </a>
        <a href="/contact"
          class="inline-flex items-center rounded-xl border border-claret-600 bg-claret-900/60 px-8 py-4 text-sm font-semibold text-white transition-colors hover:border-claret-400 hover:bg-claret-800/60">
          Talk to us first
        </a>
      </div>
      <div class="mt-8 flex flex-wrap justify-center gap-x-8 gap-y-2 text-xs text-claret-400">
        <span>✓ Grade guaranteed</span>
        <span>✓ No payment until you approve</span>
        <span>✓ Free revisions</span>
        <span>✓ 24/7 support</span>
      </div>
    </div>
  </section>
</template>


<style scoped>
@keyframes marquee {
  0%   { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
</style>
