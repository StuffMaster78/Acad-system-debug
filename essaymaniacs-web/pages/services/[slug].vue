<script setup lang="ts">
const route = useRoute()
const { getBySlug, getRelated } = useServices()

const { page: cmsPage, hasContent: hasCmsContent, loading: cmsLoading } = useServiceCms(route.params.slug as string)
const service = getBySlug(route.params.slug as string)

if (!service && !cmsPage.value) {
  throw createError({ statusCode: 404, message: 'Service not found' })
}

const displayTitle    = computed(() => service?.title ?? cmsPage.value?.title ?? '')
const displayHero     = computed(() => ({
  headline: cmsPage.value?.hero_headline || service?.hero.headline || displayTitle.value,
  sub:      cmsPage.value?.hero_sub      || service?.hero.sub      || '',
}))
const displayPrice    = computed(() => service?.priceFrom ?? parseFloat(cmsPage.value?.pricing_from ?? '10'))
const displayIcon     = computed(() => service?.icon ?? 'pen-line')
const displayMeta     = computed(() => service?.meta ?? { title: displayTitle.value, description: '' })
const displayIncludes = computed(() =>
  cmsPage.value?.includes_items?.length
    ? cmsPage.value.includes_items.map(i => i.value)
    : (service?.includes ?? [])
)
const displayDelivers = computed(() =>
  cmsPage.value?.delivers_items?.length
    ? cmsPage.value.delivers_items.map(i => i.value)
    : (service?.delivers ?? [])
)
const displayWhoFor   = computed(() => cmsPage.value?.who_for || service?.whoFor || '')

const related = service ? getRelated(service.relatedSlugs) : []

const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'https://essaymaniacs.com'
const canonicalUrl = `${siteUrl}/services/${route.params.slug}`

useSeoMeta({
  title: displayMeta.value.title || displayTitle.value,
  description: displayMeta.value.description,
  ogTitle: displayMeta.value.title || displayTitle.value,
  ogDescription: displayMeta.value.description,
})

const faqSchema = service ? {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    { '@type': 'Question', name: 'How fast can you deliver?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 2 hours for urgent orders up to 4 pages. Most essays are matched with a writer within minutes of placing your order.' } },
    { '@type': 'Question', name: 'Are your writers qualified?', acceptedAnswer: { '@type': 'Answer', text: "Yes. Every writer holds at minimum a Master's degree in their subject area. PhD-qualified writers are available for doctoral work." } },
    { '@type': 'Question', name: 'What if I need revisions?', acceptedAnswer: { '@type': 'Answer', text: 'Unlimited free revisions within the revision window, always handled by your original writer at no extra cost.' } },
    { '@type': 'Question', name: 'Is using an essay writing service legal?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. We provide model academic papers for reference and study, the same as a tutoring service or writing centre. Every order includes an academic-use acknowledgement.' } },
  ],
} : null

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Service',
        name: displayTitle.value,
        description: displayMeta.value.description,
        provider: { '@type': 'Organization', name: 'EssayManiacs', url: 'https://essaymaniacs.com' },
        offers: {
          '@type': 'Offer',
          price: displayPrice.value,
          priceCurrency: 'USD',
          priceSpecification: { '@type': 'UnitPriceSpecification', price: displayPrice.value, priceCurrency: 'USD', unitText: 'page' },
        },
      }),
    },
    ...(faqSchema ? [{ type: 'application/ld+json', innerHTML: JSON.stringify(faqSchema) }] : []),
  ],
})
</script>

<template>
  <div>

    <!-- ── Breadcrumb ────────────────────────────────────────────────── -->
    <div class="border-b border-slate-100 bg-white px-4 py-3 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <Breadcrumbs :items="[{ label: 'Services', href: '/services' }, { label: displayTitle }]" />
      </div>
    </div>

    <!-- ── Split hero ────────────────────────────────────────────────── -->
    <section class="bg-brand-900">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid min-h-[360px] items-center gap-8 py-16 lg:grid-cols-[1fr_380px]">

          <!-- Left: copy -->
          <div>
            <div class="mb-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-brand-300 ring-1 ring-white/20">
              <Icon :name="displayIcon" class="h-3.5 w-3.5" />
              From ${{ displayPrice }}/page
            </div>
            <h1 class="font-serif text-4xl font-bold leading-tight text-white sm:text-5xl">
              {{ displayHero.headline }}
            </h1>
            <p v-if="displayHero.sub" class="mt-5 max-w-xl text-lg leading-relaxed text-brand-200">
              {{ displayHero.sub }}
            </p>
            <ul class="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm text-brand-300">
              <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Grade or money back</li>
              <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Zero AI content</li>
              <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Free revisions</li>
            </ul>
          </div>

          <!-- Right: floating price card -->
          <div class="rounded-3xl bg-white/10 p-7 ring-1 ring-white/20 backdrop-blur-sm">
            <p class="text-brand-300 text-sm">Starting from</p>
            <p class="mt-1 text-5xl font-bold text-white">${{ displayPrice }}<span class="text-xl font-normal text-brand-300">/page</span></p>
            <div class="my-5 h-px bg-white/10" />
            <ul class="space-y-3 text-sm text-brand-200">
              <li class="flex items-center gap-2.5">
                <svg class="h-4 w-4 shrink-0 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                Free plagiarism report
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="h-4 w-4 shrink-0 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                Unlimited free revisions
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="h-4 w-4 shrink-0 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                Grade or money back
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="h-4 w-4 shrink-0 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                As fast as 2 hours
              </li>
            </ul>
            <div class="mt-6 space-y-3">
              <NuxtLink to="/order" class="block rounded-xl bg-white py-3.5 text-center text-base font-bold text-brand-700 transition-colors hover:bg-brand-50">
                Place an order
              </NuxtLink>
              <NuxtLink to="/contact" class="block rounded-xl border border-white/20 py-3 text-center text-sm font-semibold text-brand-200 transition-colors hover:bg-white/10">
                Ask us first
              </NuxtLink>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── Main content ──────────────────────────────────────────────── -->
    <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="grid gap-12 lg:grid-cols-[1fr_340px]">

        <!-- Left: reading flow -->
        <div class="space-y-12">

          <!-- What's included — numbered grid -->
          <div v-if="displayIncludes.length">
            <h2 class="mb-6 font-serif text-2xl font-bold text-slate-900">What's included</h2>
            <div class="grid gap-4 sm:grid-cols-2">
              <div
                v-for="(item, i) in displayIncludes"
                :key="item"
                class="flex items-start gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5"
              >
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-brand-700 text-sm font-bold text-white">
                  {{ i + 1 }}
                </span>
                <p class="text-sm leading-relaxed text-slate-700">{{ item }}</p>
              </div>
            </div>
            <!-- Inline CTA -->
            <div class="mt-6 flex items-center gap-4 rounded-2xl bg-brand-50 p-5">
              <div class="flex-1">
                <p class="font-semibold text-brand-900">Ready to order?</p>
                <p class="text-sm text-brand-700">From ${{ displayPrice }}/page · Grade or money back</p>
              </div>
              <NuxtLink to="/order" class="shrink-0 btn-primary py-2 text-sm">Order now</NuxtLink>
            </div>
          </div>

          <!-- What you receive — checklist -->
          <div v-if="displayDelivers.length">
            <h2 class="mb-6 font-serif text-2xl font-bold text-slate-900">What you receive</h2>
            <ul class="space-y-3">
              <li
                v-for="item in displayDelivers"
                :key="item"
                class="flex items-start gap-4 rounded-xl border border-slate-200 bg-white px-5 py-4"
              >
                <svg class="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                <p class="text-sm text-slate-700">{{ item }}</p>
              </li>
            </ul>
            <div class="mt-4 rounded-xl bg-slate-900 px-5 py-4 text-sm text-slate-300">
              Everything included — no hidden extras. Title page, reference list, and revisions are all free.
            </div>
          </div>

          <!-- Who it's for -->
          <div v-if="displayWhoFor">
            <h2 class="mb-4 font-serif text-2xl font-bold text-slate-900">Who this is for</h2>
            <p class="text-base leading-relaxed text-slate-700">{{ displayWhoFor }}</p>
            <div class="mt-5 grid grid-cols-3 gap-3">
              <div
                v-for="level in ['Undergraduate', `Master's`, 'PhD / Doctoral']"
                :key="level"
                class="rounded-xl border border-brand-100 bg-brand-50 py-3 text-center text-sm font-semibold text-brand-800"
              >{{ level }}</div>
            </div>
          </div>

          <!-- Related services -->
          <div v-if="related.length">
            <h2 class="mb-5 text-xs font-bold uppercase tracking-wider text-slate-400">Related services</h2>
            <div class="flex gap-3 overflow-x-auto pb-2" style="scrollbar-width: none;">
              <NuxtLink
                v-for="r in related"
                :key="r.slug"
                :href="`/services/${r.slug}`"
                class="group flex w-52 shrink-0 items-center gap-3 rounded-2xl border border-slate-100 bg-white px-4 py-3 transition-all hover:border-brand-200 hover:shadow-sm"
              >
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-700">
                  <Icon :name="r.icon" class="h-4 w-4 text-brand-700 transition-colors group-hover:text-white" />
                </div>
                <div class="min-w-0">
                  <p class="truncate text-xs font-semibold text-slate-800">{{ r.navLabel }}</p>
                  <p class="text-xs text-brand-600">From ${{ r.priceFrom }}/page</p>
                </div>
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Right: sticky sidebar -->
        <div class="lg:sticky lg:top-24 lg:self-start space-y-5">
          <MultiStepOrderForm />

          <!-- Quick FAQ -->
          <div class="rounded-3xl border border-slate-100 bg-white p-6">
            <p class="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">Quick questions</p>
            <div class="space-y-4 divide-y divide-slate-100">
              <div v-for="faq in [
                { q: 'How fast?', a: 'As fast as 2 hours. Most essays matched within minutes of ordering.' },
                { q: 'Are writers qualified?', a: `Master's degree minimum, matched to your subject. PhD writers available.` },
                { q: 'Free revisions?', a: 'Unlimited within the revision window. Always by your original writer.' },
              ]" :key="faq.q" class="pt-4 first:pt-0">
                <p class="text-sm font-semibold text-slate-900">{{ faq.q }}</p>
                <p class="mt-1 text-xs leading-relaxed text-slate-500">{{ faq.a }}</p>
              </div>
            </div>
            <NuxtLink href="/faq" class="mt-4 inline-flex text-xs font-semibold text-brand-600 hover:underline">
              Full FAQ →
            </NuxtLink>
          </div>

          <!-- Testimonial -->
          <div class="rounded-3xl border border-brand-100 bg-brand-50 p-6">
            <div class="mb-3 flex gap-0.5">
              <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
            <p class="text-sm italic leading-relaxed text-slate-700">"I was genuinely impressed — the writer actually knew the subject. Not generic, not AI. A real expert."</p>
            <p class="mt-3 text-xs font-semibold text-slate-600">— Student, University of Edinburgh</p>
          </div>

        </div>
      </div>
    </div>

    <!-- ── CMS or static long-form SEO content ──────────────────────── -->
    <div class="border-t border-slate-100 bg-slate-50">
      <div class="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">

        <div v-if="cmsLoading" class="space-y-4">
          <div v-for="i in 3" :key="i" class="space-y-2">
            <div class="h-6 w-1/2 animate-pulse rounded bg-slate-200" />
            <div class="h-4 w-full animate-pulse rounded bg-slate-200" />
            <div class="h-4 w-4/5 animate-pulse rounded bg-slate-200" />
          </div>
        </div>

        <template v-else-if="hasCmsContent && cmsPage">
          <div v-if="cmsPage.reviewer" class="mb-8 flex items-center gap-2 text-sm text-slate-500">
            <Icon name="check-circle" class="h-4 w-4 text-brand-500" />
            Reviewed by <strong class="text-slate-700">{{ cmsPage.reviewer.name }}</strong>
            <span v-if="cmsPage.last_substantive_update" class="text-slate-400">
              · Updated {{ new Date(cmsPage.last_substantive_update).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}
            </span>
          </div>
          <ServicePageBody :blocks="cmsPage.body" />
          <div v-if="cmsPage.primary_cta_text && cmsPage.primary_cta_url" class="mt-10 text-center">
            <NuxtLink :href="cmsPage.primary_cta_url" class="btn-primary px-10 py-4 text-base">
              {{ cmsPage.primary_cta_text }}
            </NuxtLink>
          </div>
        </template>

        <template v-else-if="service">
          <div class="prose prose-slate prose-lg max-w-none
                       prose-headings:font-serif prose-headings:font-bold
                       prose-a:text-brand-600 prose-strong:text-slate-900">

            <h2>Why {{ service.navLabel }} Matters</h2>
            <p>{{ displayHero.sub }}</p>
            <p>
              Academic work is demanding. Between deadlines, multiple modules, and the pressure to perform, producing well-structured, properly cited work consistently is genuinely hard. Our writers are subject specialists — not generic content writers — who understand what your marker is looking for because they have worked in the same field.
            </p>

            <h2>What Sets Our Approach Apart</h2>
            <div class="not-prose my-6 grid gap-4 sm:grid-cols-2">
              <div v-for="(item, i) in service.includes" :key="item"
                class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
                <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">{{ i + 1 }}</span>
                <span class="text-sm leading-relaxed text-slate-700">{{ item }}</span>
              </div>
            </div>

            <h2>What You Receive</h2>
            <ul>
              <li v-for="item in service.delivers" :key="item">{{ item }}</li>
            </ul>

            <h2>Who This Is For</h2>
            <p>{{ service.whoFor }}</p>

            <h2>Common Challenges We Solve</h2>
            <ul>
              <li><strong>Time pressure:</strong> Multiple deadlines, work, family — we work to your schedule, as fast as 2 hours.</li>
              <li><strong>Subject depth:</strong> Generic writers produce surface-level work. Our writers are degree-holders in your subject.</li>
              <li><strong>Citation accuracy:</strong> APA, MLA, Harvard, Chicago — formatted correctly, every time.</li>
              <li><strong>Source quality:</strong> Peer-reviewed journals and academic databases, not unreliable web sources.</li>
            </ul>

            <h2>How to Order {{ service.navLabel }}</h2>
            <ol>
              <li><strong>Submit your brief:</strong> Essay type, subject, academic level, deadline, word count, and any rubric files.</li>
              <li><strong>Get matched:</strong> We assign a writer whose subject background and degree level fit your assignment.</li>
              <li><strong>Communicate directly:</strong> Message your writer, share additional files, track progress in real time.</li>
              <li><strong>Download and review:</strong> Receive your essay with a free plagiarism report. Request revisions if needed.</li>
            </ol>

          </div>
        </template>

      </div>
    </div>

    <!-- ── Sample templates for this service ────────────────────────── -->
    <ClientOnly>
      <ServiceTemplates
        v-if="service"
        :service-slug="service.slug"
        :service-name="service.navLabel"
      />
    </ClientOnly>

    <!-- ── Final CTA ─────────────────────────────────────────────────── -->
    <div v-if="service" class="bg-brand-700 py-12 text-center">
      <h2 class="font-serif text-2xl font-bold text-white sm:text-3xl">
        Ready to get your {{ service.navLabel.toLowerCase() }} done?
      </h2>
      <p class="mt-3 text-brand-100">Subject-obsessed writer ready. Grade guaranteed or full refund.</p>
      <NuxtLink to="/order" class="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-base font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
        Place an order — from ${{ displayPrice }}/page
      </NuxtLink>
    </div>

  </div>
</template>
