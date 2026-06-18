<script setup lang="ts">
import { ArrowRight, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Student Reviews — 12,400+ Verified Reviews | GradeCrest',
  description: 'Read verified student reviews of GradeCrest. 4.9/5 from 12,400+ reviews on Trustpilot, SiteJabber, and Google. Real students, real results.',
})

useSeoBase('https://gradecrest.com/reviews')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Reviews', url: 'https://gradecrest.com/reviews' },
])

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: 'GradeCrest',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.9', reviewCount: '12400', bestRating: '5' },
    }),
  }],
})

const platforms = [
  { name: 'Trustpilot',   rating: 4.9, count: '8,200+', color: 'text-emerald-600' },
  { name: 'SiteJabber',   rating: 4.8, count: '2,900+', color: 'text-blue-600'    },
  { name: 'Google',       rating: 4.9, count: '1,300+', color: 'text-slate-600'   },
]

const reviews = [
  { text: "I was completely stuck on my nursing capstone with three days to go. The writer understood exactly what my faculty wanted and delivered 12 hours early. Passed with distinction.", name: 'Kezia M.', subject: 'Nursing Capstone', level: "Master's", stars: 5, date: 'May 2026' },
  { text: "Third time using GradeCrest. Every paper is genuinely written by a human — you can tell from the nuance in the arguments. No AI phrases, no generic conclusions. Exceptional.", name: 'Tyler B.', subject: 'Constitutional Law Essay', level: 'Undergraduate', stars: 5, date: 'May 2026' },
  { text: "Ordered a 25-page dissertation chapter with 72 hours notice. It arrived on time, perfectly APA-formatted, with every source I specified. I could not have done this without them.", name: 'Priya S.', subject: 'Dissertation Chapter 3', level: "Master's", stars: 5, date: 'April 2026' },
  { text: "The editor caught things I never would have spotted — passive voice I had not noticed, inconsistent citation formatting, a whole section that needed restructuring. My thesis is so much stronger.", name: 'James L.', subject: 'Thesis Editing', level: 'PhD', stars: 5, date: 'April 2026' },
  { text: "I was sceptical about the grade guarantee but had to test it. First draft was good but not quite there. They rewrote the introduction without a single complaint and I got the A I needed.", name: 'Amara D.', subject: 'Psychology Essay', level: 'Undergraduate', stars: 5, date: 'March 2026' },
  { text: "Statistics paper, 48 hours, PhD level. I genuinely could not have done this alone. The methodology section was exactly what my supervisor had been asking for.", name: 'Marco T.', subject: 'Quantitative Dissertation', level: 'PhD', stars: 5, date: 'March 2026' },
  { text: "Fast, professional, and the writer actually read my previous papers to match my writing style. That level of attention to detail is rare. Absolutely recommend.", name: 'Sophie R.', subject: 'Literature Review', level: 'Undergraduate', stars: 5, date: 'February 2026' },
  { text: "Got a distinction on my MBA case study. The writer had real industry knowledge — not just textbook answers. You could tell they actually understood the business context.", name: 'Femi O.', subject: 'MBA Case Study', level: 'Postgraduate', stars: 5, date: 'February 2026' },
  { text: "I've used three different services. GradeCrest is the only one where the writer genuinely understood what my professor was looking for, not just what the assignment said on the surface.", name: 'Chloe N.', subject: 'Sociology Research Paper', level: 'Undergraduate', stars: 5, date: 'January 2026' },
  { text: "The nursing care plan was flawless. NANDA diagnoses, interventions, and rationale all perfectly structured. My clinical supervisor was impressed.", name: 'Dana P.', subject: 'Nursing Care Plan', level: 'BSN', stars: 5, date: 'January 2026' },
  { text: "Personal statement for med school. I gave them my bullet points and they turned it into a compelling narrative that actually sounds like me. Accepted to my first-choice programme.", name: 'Aryan K.', subject: 'Medical School Personal Statement', level: 'Undergraduate', stars: 5, date: 'December 2025' },
  { text: "Second opinion from a PhD economics expert on my dissertation findings was exactly what I needed. The feedback was detailed, direct, and genuinely improved my argument.", name: 'Lena V.', subject: 'Economics Dissertation', level: 'PhD', stars: 5, date: 'December 2025' },
]
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-forest-950 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gold-400 mb-3">Social proof</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Student Reviews</h1>
        <p class="mt-4 text-lg text-slate-300">12,400+ verified reviews across Trustpilot, SiteJabber, and Google.</p>
        <div class="mt-6 flex flex-wrap justify-center gap-6">
          <div v-for="p in platforms" :key="p.name" class="text-center">
            <div class="flex items-center justify-center gap-1 mb-1">
              <Star v-for="i in 5" :key="i" class="size-4 fill-amber-400 text-amber-400" />
            </div>
            <p class="text-white font-bold text-sm">{{ p.rating }} <span class="text-slate-400 font-normal">{{ p.name }}</span></p>
            <p class="text-xs text-slate-400">{{ p.count }} reviews</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Masonry reviews -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="columns-1 gap-4 sm:columns-2 lg:columns-3 [column-fill:balance]">
          <div
            v-for="r in reviews" :key="r.name"
            class="mb-4 break-inside-avoid rounded-2xl border border-slate-200 bg-white p-5 shadow-card"
          >
            <div class="flex items-center gap-1 mb-3">
              <Star v-for="i in r.stars" :key="i" class="size-3.5 fill-amber-400 text-amber-400" />
            </div>
            <p class="text-sm text-ink leading-relaxed">"{{ r.text }}"</p>
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-end justify-between gap-2">
              <div>
                <p class="text-xs font-semibold text-ink">{{ r.name }}</p>
                <p class="text-xs text-graphite">{{ r.subject }}</p>
              </div>
              <div class="text-right shrink-0">
                <span class="block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-graphite">{{ r.level }}</span>
                <span class="block text-[11px] text-slate-400 mt-1">{{ r.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-mist py-12 text-center">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="text-xl font-bold text-ink">Join 20,000+ satisfied students</h2>
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
