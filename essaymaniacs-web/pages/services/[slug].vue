<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()
const { getBySlug, getRelated } = useServices()

const slug = route.params.slug as string

const apiBase = import.meta.server
  ? ((config as Record<string, unknown>).apiBaseInternal as string || 'http://localhost:8000')
  : (config.public.apiBase || '')
const svcFields = [
  'title', 'slug', 'hero_headline', 'hero_sub',
  'pricing_from', 'pricing_to', 'turnaround_hours_fastest', 'turnaround_hours_standard',
  'includes_items', 'delivers_items', 'who_for',
  'primary_cta_text', 'primary_cta_url', 'reviewer', 'last_substantive_update', 'body',
].join(',')

const { data: _cmsRaw } = await useAsyncData<{ items: unknown[] } | null>(
  `svc-em-${slug}`,
  () => $fetch<{ items: unknown[] }>(`${apiBase}/api/v2/pages/`, {
    params: { type: 'cms_service_pages.ServicePage', slug, fields: svcFields },
    headers: import.meta.server
      ? { Host: (config as Record<string, unknown>).siteHostname as string || 'essaymaniacs.com' }
      : undefined,
  }).catch(() => null),
)

import type { CmsServicePage } from '~/composables/useServiceCms'
const cmsPage = computed<CmsServicePage | null>(
  () => ((_cmsRaw.value as { items?: CmsServicePage[] } | null)?.items?.[0]) ?? null,
)
const { hasContent: hasCmsContent, loading: cmsLoading } = useServiceCms(slug)
const service = getBySlug(slug)

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
    ? cmsPage.value.includes_items.map((i: { value: string }) => i.value)
    : (service?.includes ?? [])
)
const displayWhoFor = computed(() => cmsPage.value?.who_for || service?.whoFor || '')

const related    = service ? getRelated(service.relatedSlugs) : []
const bodyBlocks = computed(() => cmsPage.value?.body ?? [])

// Sticky bottom bar visibility
const showBar = ref(false)
onMounted(() => {
  const onScroll = () => { showBar.value = window.scrollY > 320 }
  window.addEventListener('scroll', onScroll, { passive: true })
  onUnmounted(() => window.removeEventListener('scroll', onScroll))
})

const siteUrl = config.public.siteUrl || 'https://essaymaniacs.com'
const canonicalUrl = `${siteUrl}/services/${slug}`

useSeoMeta({
  title:         displayMeta.value.title || displayTitle.value,
  description:   displayMeta.value.description,
  ogTitle:       displayMeta.value.title || displayTitle.value,
  ogDescription: displayMeta.value.description,
  ogImage:       cmsPage.value?.hero_image?.url ?? cmsPage.value?.thumbnail?.url ?? 'https://essaymaniacs.com/og-default.svg',
  ogType:        'website',
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
  script: faqSchema ? [{ type: 'application/ld+json', innerHTML: JSON.stringify(faqSchema) }] : [],
})

if (cmsPage.value?.schema) {
  useHead({ script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(cmsPage.value.schema) }] })
} else {
  useHead({
    script: [{
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
    }],
  })
}
</script>

<template>
  <!-- Editorial single-column layout with sticky bottom pricing bar -->
  <div class="pb-20 lg:pb-24">

    <!-- ── Full-width purple hero ─────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-16 sm:py-24" aria-label="Service overview">
      <!-- Subtle texture -->
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(135deg,rgba(139,92,246,0.15)_0%,transparent_50%)]" />
      <div class="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-brand-600 opacity-20 blur-[120px]" />

      <div class="relative mx-auto max-w-3xl px-4 sm:px-6 text-center">

        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="mb-8 flex items-center justify-center gap-1.5 text-xs text-brand-400">
          <NuxtLink to="/" class="hover:text-brand-200 transition-colors">Home</NuxtLink>
          <span>/</span>
          <NuxtLink to="/services" class="hover:text-brand-200 transition-colors">Services</NuxtLink>
          <span>/</span>
          <span class="text-brand-300" aria-current="page">{{ displayTitle }}</span>
        </nav>

        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl lg:text-6xl leading-tight">
          {{ displayHero.headline }}
        </h1>

        <p v-if="displayHero.sub" class="mx-auto mt-5 max-w-xl text-lg text-brand-300 leading-relaxed">
          {{ displayHero.sub }}
        </p>

        <!-- CTAs -->
        <div class="mt-10 flex flex-wrap justify-center gap-4">
          <NuxtLink
            to="/order"
            class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
          >
            Order from ${{ displayPrice }}/page →
          </NuxtLink>
          <a
            href="#calculator"
            class="inline-flex items-center gap-2 rounded-xl border border-brand-500 px-8 py-3.5 text-sm font-semibold text-brand-200 transition-colors hover:bg-brand-800"
          >
            Get instant price ↓
          </a>
        </div>

        <!-- Trust strip -->
        <div class="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-brand-400">
          <span>✓ Grade or money back</span>
          <span>✓ Master's &amp; PhD writers</span>
          <span>✓ Zero AI content</span>
          <span>✓ Free plagiarism report</span>
        </div>

      </div>
    </section>

    <!-- ── Single-column content ──────────────────────────────────────────── -->
    <main class="bg-white">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 py-14 space-y-16">

        <!-- Who it's for -->
        <section v-if="displayWhoFor" aria-labelledby="who-heading">
          <h2 id="who-heading" class="font-serif text-2xl font-bold text-slate-900 mb-4">Who this is for</h2>
          <p class="text-slate-600 leading-relaxed text-[15px]">{{ displayWhoFor }}</p>
        </section>

        <!-- What's included -->
        <section v-if="displayIncludes.length" aria-labelledby="includes-heading">
          <h2 id="includes-heading" class="font-serif text-2xl font-bold text-slate-900 mb-5">What's included</h2>
          <div class="grid gap-3 sm:grid-cols-2">
            <div
              v-for="item in displayIncludes"
              :key="item"
              class="flex items-start gap-3 rounded-xl border border-brand-100 bg-brand-50/40 p-4"
            >
              <Icon name="check-circle" class="h-4 w-4 shrink-0 mt-0.5 text-brand-500" />
              <span class="text-sm text-slate-700 leading-relaxed">{{ item }}</span>
            </div>
          </div>
        </section>

        <!-- Pricing calculator — id="calculator" for anchor link from hero -->
        <section id="calculator" aria-labelledby="calc-heading" class="scroll-mt-20">
          <h2 id="calc-heading" class="font-serif text-2xl font-bold text-slate-900 mb-5">Get an instant price</h2>
          <OrderCalculator />
        </section>

        <!-- FAQ -->
        <section aria-labelledby="faq-heading">
          <h2 id="faq-heading" class="font-serif text-2xl font-bold text-slate-900 mb-5">
            Frequently asked questions
          </h2>
          <div class="space-y-2">
            <details
              v-for="faq in [
                { q: 'How fast can you deliver?', a: 'As fast as 2 hours for urgent orders up to 4 pages. Most essays are matched with a writer within minutes of placing your order.' },
                { q: 'Are your writers qualified?', a: 'Yes. Every writer holds at minimum a Master\'s degree in their subject area. PhD-qualified writers are available for doctoral work.' },
                { q: 'What if I need revisions?', a: 'Unlimited free revisions within the revision window, always handled by your original writer at no extra cost.' },
                { q: 'Is using an essay writing service legal?', a: 'Yes. We provide model academic papers for reference and study, the same as a tutoring service or writing centre.' },
              ]"
              :key="faq.q"
              class="group rounded-2xl border border-slate-200 bg-white shadow-sm"
            >
              <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-slate-900">
                {{ faq.q }}
                <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-600 text-xs font-bold transition-transform group-open:rotate-45">+</span>
              </summary>
              <p class="px-6 pb-5 pt-1 text-sm text-slate-500 leading-relaxed">{{ faq.a }}</p>
            </details>
          </div>
        </section>

        <!-- Related services -->
        <section v-if="related.length" aria-labelledby="related-heading">
          <h2 id="related-heading" class="font-serif text-lg font-bold text-slate-900 mb-4">Related services</h2>
          <div class="flex flex-wrap gap-3">
            <NuxtLink
              v-for="r in related"
              :key="r.slug"
              :to="`/services/${r.slug}`"
              class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:border-brand-300 hover:text-brand-700"
            >
              {{ r.navLabel }}
            </NuxtLink>
          </div>
        </section>

      </div>
    </main>

    <!-- ── Two-column SEO content — academic, ink-and-paper ──────────────── -->
    <section v-if="bodyBlocks.length" class="border-t border-brand-100 bg-white py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <!-- Section intro -->
        <div class="mb-10 flex items-center gap-4">
          <span class="h-px flex-1 bg-brand-200" />
          <h2 class="whitespace-nowrap font-serif text-lg font-bold text-brand-900">
            About this service
          </h2>
          <span class="h-px flex-1 bg-brand-200" />
        </div>
        <!-- Two-column article text — CSS columns auto-balance content -->
        <div class="service-body columns-1 md:columns-2 md:gap-x-12 [column-fill:balance]">
          <ServicePageBody :blocks="bodyBlocks" />
        </div>
        <!-- Inline CTA -->
        <div class="mt-10 text-center">
          <NuxtLink to="/order"
            class="inline-flex items-center gap-2 rounded-xl bg-brand-700 px-8 py-3.5 text-sm font-bold text-white hover:bg-brand-800 transition-colors shadow-sm">
            Start your order →
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── Final CTA ──────────────────────────────────────────────────────── -->
    <section class="bg-brand-800 py-14 text-center" aria-label="Get started">
      <div class="mx-auto max-w-xl px-4 space-y-5">
        <h2 class="font-serif text-2xl font-bold text-white sm:text-3xl">Ready to get started?</h2>
        <p class="text-brand-300 text-sm">
          Place your order in under 2 minutes. Grade or money back — no conditions.
        </p>
        <NuxtLink
          to="/order"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg hover:bg-brand-50 transition-colors"
        >
          Order {{ displayTitle.toLowerCase() }} →
        </NuxtLink>
      </div>
    </section>

    <!-- ── Sticky bottom pricing bar (appears after scroll) ───────────────── -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="translate-y-full opacity-0"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="translate-y-full opacity-0"
    >
      <div
        v-if="showBar"
        class="fixed bottom-0 inset-x-0 z-40 border-t border-brand-700 bg-brand-900/95 backdrop-blur-sm px-4 py-3"
      >
        <div class="mx-auto flex max-w-3xl items-center justify-between gap-4">
          <div>
            <p class="text-xs text-brand-400 uppercase tracking-wider font-bold">{{ displayTitle }}</p>
            <p class="text-white font-bold">From <span class="text-gold-300 text-lg">${{ displayPrice }}</span>/page</p>
          </div>
          <div class="flex gap-3">
            <a
              href="#calculator"
              class="flex h-11 items-center gap-1 rounded-xl border border-brand-600 px-4 text-sm font-semibold text-brand-300 hover:bg-brand-800 transition-colors"
            >
              Price it
            </a>
            <NuxtLink
              to="/order"
              class="flex h-11 items-center gap-2 rounded-xl bg-white px-5 text-sm font-bold text-brand-700 hover:bg-brand-50 shadow-sm transition-colors"
            >
              Order now →
            </NuxtLink>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.service-body :deep(h2) { font-family: Georgia, serif; font-weight: 700; color: #1e1b4b; margin-top: 2.5rem; margin-bottom: 1rem; font-size: 1.5rem; }
.service-body :deep(h3) { font-weight: 600; color: #312e81; margin-top: 2rem; margin-bottom: 0.75rem; font-size: 1.125rem; }
.service-body :deep(p)  { color: #475569; line-height: 1.75; margin-bottom: 1rem; font-size: 0.9375rem; }
.service-body :deep(ul), .service-body :deep(ol) { padding-left: 1.5rem; color: #475569; font-size: 0.9375rem; margin-bottom: 1rem; }
.service-body :deep(li) { margin-bottom: 0.5rem; line-height: 1.65; }
.service-body :deep(strong) { color: #1e1b4b; font-weight: 600; }
.service-body :deep(table) { display: block; overflow-x: auto; border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }
.service-body :deep(th), .service-body :deep(td) { padding: 0.625rem 1rem; border: 1px solid #ede9fe; font-size: 0.875rem; }
.service-body :deep(th) { background: #f5f3ff; font-weight: 600; color: #4c1d95; }
.service-body :deep(a)  { color: #7c3aed; text-decoration: underline; }
</style>
