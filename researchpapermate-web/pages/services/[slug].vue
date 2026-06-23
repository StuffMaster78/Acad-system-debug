<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()
const { getBySlug, getRelated } = useServices()

const slug = route.params.slug as string

// Await CMS data before the 404 guard so the guard sees real data.
// SSR: call Django directly with the correct Host header.
// Client: route through the /api/v2 dev-proxy (or apiBase in prod).
const apiBase = import.meta.server
  ? ((config as Record<string, unknown>).apiBaseInternal as string || 'http://localhost:8000')
  : (config.public.apiBase || '')
const svcFields = [
  'title', 'slug', 'pricing_from', 'pricing_to',
  'turnaround_hours_fastest', 'turnaround_hours_standard',
  'primary_cta_text', 'primary_cta_url',
  'reviewer', 'last_substantive_update', 'body',
].join(',')

const { data: _cmsRaw } = await useAsyncData<{ items: unknown[] } | null>(
  `svc-rpm-${slug}`,
  () => $fetch<{ items: unknown[] }>(`${apiBase}/api/v2/pages/`, {
    params: { type: 'cms_service_pages.ServicePage', slug, fields: svcFields },
    headers: import.meta.server
      ? { Host: (config as Record<string, unknown>).siteHostname as string || 'researchpapermate.com' }
      : undefined,
  }).catch(() => null),
)

import type { CmsServicePage } from '~/composables/useServiceCms'
const cmsPage = computed<CmsServicePage | null>(
  () => ((_cmsRaw.value as { items?: CmsServicePage[] } | null)?.items?.[0]) ?? null,
)
// Keep useServiceCms active for client-side navigation refreshes
const { hasContent: hasCmsContent, loading: cmsLoading } = useServiceCms(slug)
const service = getBySlug(slug)

if (!service && !cmsPage.value) {
  throw createError({ statusCode: 404, message: 'Service not found' })
}

const displayTitle = computed(() => service?.title ?? cmsPage.value?.title ?? '')
const displayHero  = computed(() => service?.hero ?? { headline: displayTitle.value, sub: '' })
const displayPrice = computed(() => service?.priceFrom ?? parseFloat(cmsPage.value?.pricing_from ?? '15'))
const displayIcon  = computed(() => service?.icon ?? 'file-text')
const displayMeta  = computed(() => service?.meta ?? { title: displayTitle.value, description: '' })
const displayIncludes = computed(() => service?.includes ?? [])

const related    = service ? getRelated(service.relatedSlugs) : []
const bodyBlocks  = computed(() => cmsPage.value?.body ?? [])

// ── Methodology selector ──────────────────────────────────────────────────
type Methodology = { label: string; paper: string; price: string; desc: string }

const METHODOLOGIES: Methodology[] = [
  { label: 'Essay / Report',    paper: 'essay',           price: '15', desc: 'Argumentative, analytical, reflective and critical essays across all disciplines.' },
  { label: 'Research Paper',    paper: 'research_paper',  price: '15', desc: 'Original research with full methodology, citations, and peer-reviewed sources.' },
  { label: 'Dissertation',      paper: 'dissertation',    price: '22', desc: 'Full dissertation or individual chapters — proposal through final defence.' },
  { label: 'Literature Review', paper: 'literature_review', price: '16', desc: 'Critically synthesised systematic, narrative, or integrative reviews.' },
  { label: 'Other',             paper: '',                price: String(displayPrice.value), desc: 'Capstone projects, case studies, term papers, and specialist work.' },
]

const activeMethod = ref(0)
const selectedMethod = computed(() => METHODOLOGIES[activeMethod.value])

// ── Drawer ────────────────────────────────────────────────────────────────
const drawerOpen = ref(false)
function openDrawer() { drawerOpen.value = true; document.body.style.overflow = 'hidden' }
function closeDrawer() { drawerOpen.value = false; document.body.style.overflow = '' }
onUnmounted(() => { document.body.style.overflow = '' })

const siteUrl = config.public.siteUrl || 'https://researchpapermate.com'
const canonicalUrl = `${siteUrl}/services/${slug}`

useSeoMeta({
  title:         displayMeta.value.title || displayTitle.value,
  description:   displayMeta.value.description,
  ogTitle:       displayMeta.value.title || displayTitle.value,
  ogDescription: displayMeta.value.description,
  ogImage:       cmsPage.value?.hero_image?.url ?? cmsPage.value?.thumbnail?.url ?? 'https://researchpapermate.com/og-default.png',
  ogType:        'website',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const faqSchema = service ? {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    { '@type': 'Question', name: 'How fast can you deliver?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 2 hours for urgent orders up to 4 pages. Most papers are matched with a qualified writer within minutes of placing your order.' } },
    { '@type': 'Question', name: 'Are your writers qualified?', acceptedAnswer: { '@type': 'Answer', text: "Yes. Every writer holds at minimum a Master's degree in their subject area, verified against the issuing institution. PhD-qualified writers are available for doctoral work." } },
    { '@type': 'Question', name: 'What if I need revisions?', acceptedAnswer: { '@type': 'Answer', text: 'Unlimited free revisions are included within the revision window, always handled by your original writer.' } },
    { '@type': 'Question', name: 'Is using an academic writing service legal?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. We provide model academic papers for reference and study — the same as a tutoring service or writing centre. Every order includes an academic-use acknowledgement.' } },
  ],
} : null

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home',     item: 'https://researchpapermate.com/' },
    { '@type': 'ListItem', position: 2, name: 'Services', item: 'https://researchpapermate.com/services' },
    { '@type': 'ListItem', position: 3, name: displayTitle.value, item: canonicalUrl },
  ],
}

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: [
    { type: 'application/ld+json', innerHTML: JSON.stringify(breadcrumbSchema) },
    ...(faqSchema ? [{ type: 'application/ld+json', innerHTML: JSON.stringify(faqSchema) }] : []),
  ],
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
        dateModified: cmsPage.value?.last_published_at ?? new Date().toISOString().slice(0, 10),
        provider: { '@type': 'Organization', name: 'ResearchPaperMate', url: 'https://researchpapermate.com' },
        speakable: { '@type': 'SpeakableSpecification', cssSelector: ['h1', '.service-hero-sub', '.service-description'] },
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
  <!-- Methodology selector + drawer calculator — scholarly, parchment-toned -->
  <div>

    <!-- ── Hero: parchment/white, left-aligned, minimal ──────────────────── -->
    <section class="bg-parchment-50 border-b border-parchment-200 py-12 sm:py-16" aria-label="Service overview">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="mb-7 flex items-center gap-1.5 text-xs text-claret-400">
          <NuxtLink to="/" class="hover:text-claret-700 transition-colors">Home</NuxtLink>
          <span>/</span>
          <NuxtLink to="/services" class="hover:text-claret-700 transition-colors">Services</NuxtLink>
          <span>/</span>
          <span class="text-claret-700" aria-current="page">{{ displayTitle }}</span>
        </nav>

        <div class="max-w-3xl">
          <h1 class="font-serif text-3xl font-bold text-claret-950 sm:text-4xl xl:text-5xl leading-tight">
            {{ displayHero.headline }}
          </h1>
          <p v-if="displayHero.sub" class="mt-3 text-claret-600 leading-relaxed text-lg">
            {{ displayHero.sub }}
          </p>

          <!-- Methodology tab selector -->
          <div class="mt-8" role="tablist" aria-label="Paper type selector">
            <div class="flex flex-wrap gap-2">
              <button
                v-for="(m, i) in METHODOLOGIES"
                :key="m.label"
                role="tab"
                :aria-selected="activeMethod === i"
                type="button"
                class="rounded-lg border px-3.5 py-2 text-xs font-semibold transition-all"
                :class="activeMethod === i
                  ? 'border-claret-600 bg-claret-600 text-white shadow-sm'
                  : 'border-parchment-300 bg-white text-claret-700 hover:border-claret-300 hover:bg-parchment-100'"
                @click="activeMethod = i"
              >{{ m.label }}</button>
            </div>

            <!-- Selected methodology description -->
            <Transition name="fade" mode="out-in">
              <div :key="activeMethod" class="mt-4 flex items-center justify-between gap-4 rounded-xl border border-parchment-200 bg-white px-5 py-4">
                <p class="text-sm text-slate-600 leading-relaxed">{{ selectedMethod.desc }}</p>
                <p class="shrink-0 text-right">
                  <span class="block text-xs text-claret-400 uppercase tracking-wider font-bold">From</span>
                  <span class="text-2xl font-bold text-claret-800">${{ selectedMethod.price }}</span>
                  <span class="text-xs text-claret-400">/page</span>
                </p>
              </div>
            </Transition>
          </div>

          <!-- CTA -->
          <div class="mt-6 flex flex-wrap items-center gap-4">
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-claret-700 px-8 py-3.5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-claret-800"
              @click="openDrawer"
            >
              Get a quote — from ${{ selectedMethod.price }}/page
            </button>
            <NuxtLink
              to="/order"
              class="text-sm font-semibold text-claret-600 hover:text-claret-800 transition-colors"
            >
              Order directly →
            </NuxtLink>
          </div>

          <!-- Trust line -->
          <p class="mt-5 text-xs text-claret-500">
            ✓ Grade or money back &nbsp;·&nbsp; ✓ Master's &amp; PhD writers &nbsp;·&nbsp; ✓ Free plagiarism report
          </p>
        </div>

      </div>
    </section>

    <!-- ── Main content: article + compact trust sidebar ─────────────────── -->
    <main class="bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div class="lg:grid lg:grid-cols-12 lg:gap-12">

          <!-- Article: 7/12 columns -->
          <article class="lg:col-span-7 space-y-12 min-w-0" aria-label="Service details">

            <!-- What's included -->
            <section v-if="displayIncludes.length" aria-labelledby="includes-heading">
              <h2 id="includes-heading" class="font-serif text-xl font-bold text-claret-900 mb-5">What's included</h2>
              <ul class="space-y-3" role="list">
                <li
                  v-for="item in displayIncludes"
                  :key="item"
                  class="flex items-start gap-3 text-sm text-slate-700"
                >
                  <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-100 mt-0.5">
                    <Icon name="check" class="h-3 w-3 text-amber-700" />
                  </span>
                  {{ item }}
                </li>
              </ul>
            </section>

            <!-- FAQ -->
            <section aria-labelledby="faq-heading">
              <h2 id="faq-heading" class="font-serif text-xl font-bold text-claret-900 mb-5">
                Common questions
              </h2>
              <div class="space-y-2">
                <details
                  v-for="faq in [
                    { q: 'How fast can you deliver?', a: 'As fast as 2 hours for urgent orders up to 4 pages. Most papers are matched with a qualified writer within minutes of placing your order.' },
                    { q: 'Are your writers qualified?', a: 'Yes. Every writer holds at minimum a Master\'s degree in their subject area, verified against the issuing institution. PhD-qualified writers are available for doctoral work.' },
                    { q: 'What if I need revisions?', a: 'Unlimited free revisions are included within the revision window, always handled by your original writer.' },
                    { q: 'Is using an academic writing service legal?', a: 'Yes. We provide model academic papers for reference and study — the same as a tutoring service or writing centre. Every order includes an academic-use acknowledgement.' },
                  ]"
                  :key="faq.q"
                  class="group rounded-xl border border-parchment-200 bg-parchment-50"
                >
                  <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 text-sm font-semibold text-claret-900">
                    {{ faq.q }}
                    <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-parchment-200 text-claret-600 text-xs font-bold transition-transform group-open:rotate-45">+</span>
                  </summary>
                  <p class="px-5 pb-4 pt-0 text-sm text-slate-600 leading-relaxed">{{ faq.a }}</p>
                </details>
              </div>
            </section>

            <!-- Related -->
            <section v-if="related.length" aria-labelledby="related-heading">
              <h2 id="related-heading" class="font-serif text-lg font-bold text-claret-900 mb-4">Related services</h2>
              <div class="flex flex-wrap gap-2">
                <NuxtLink
                  v-for="r in related"
                  :key="r.slug"
                  :to="`/services/${r.slug}`"
                  class="rounded-full border border-parchment-300 bg-parchment-50 px-4 py-2 text-xs font-medium text-claret-700 transition-colors hover:border-claret-300 hover:bg-claret-50"
                >
                  {{ r.navLabel }}
                </NuxtLink>
              </div>
            </section>

          </article>

          <!-- Trust sidebar: 5/12 columns, sticky -->
          <aside class="hidden lg:block lg:col-span-5" aria-label="Order and pricing">
            <div class="sticky top-24 space-y-4">

              <!-- Quote card -->
              <div class="overflow-hidden rounded-2xl border border-parchment-200 bg-white shadow-sm">
                <div class="border-b border-parchment-200 bg-parchment-50 px-5 py-4">
                  <p class="text-xs uppercase tracking-widest font-bold text-claret-400 mb-0.5">Starting from</p>
                  <p class="text-3xl font-bold text-claret-900">
                    ${{ selectedMethod.price }}<span class="text-sm font-normal text-claret-400">/page</span>
                  </p>
                  <p class="mt-0.5 text-xs text-claret-500">{{ selectedMethod.label }}</p>
                </div>
                <div class="p-5 space-y-3">
                  <button
                    type="button"
                    class="block w-full rounded-xl bg-claret-700 py-3 text-center text-sm font-bold text-white shadow-sm transition-colors hover:bg-claret-800"
                    @click="openDrawer"
                  >
                    Get a quote →
                  </button>
                  <NuxtLink
                    to="/order"
                    class="block w-full rounded-xl border border-claret-200 py-2.5 text-center text-xs font-semibold text-claret-700 transition-colors hover:bg-claret-50"
                  >
                    Place order directly
                  </NuxtLink>
                  <ul class="space-y-2 pt-1">
                    <li v-for="t in ['Grade or money back', 'Master\'s &amp; PhD writers', 'Free plagiarism report', 'Zero AI content', 'Unlimited revisions']" :key="t"
                      class="flex items-center gap-2 text-xs text-slate-600" v-html="`<svg class='h-3 w-3 shrink-0 text-amber-600' fill='none' stroke='currentColor' stroke-width='3' viewBox='0 0 24 24'><polyline points='20 6 9 17 4 12'/></svg>${t}`" />
                  </ul>
                </div>
              </div>

              <!-- Reviewer -->
              <div v-if="cmsPage?.reviewer" class="rounded-2xl border border-parchment-200 bg-parchment-50 p-4">
                <p class="text-xs text-claret-400 mb-1">Reviewed by</p>
                <p class="text-sm font-semibold text-claret-900">{{ cmsPage.reviewer.name }}</p>
                <p v-if="cmsPage.reviewer.role" class="text-xs text-claret-500 mt-0.5">{{ cmsPage.reviewer.role }}</p>
              </div>

              <!-- Star rating -->
              <div class="rounded-2xl border border-parchment-200 bg-parchment-50 p-4 text-center">
                <div class="flex justify-center gap-0.5 mb-2">
                  <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
                <p class="text-xs text-slate-500">4.9 · 22,000+ papers delivered</p>
              </div>

            </div>
          </aside>

        </div>
      </div>
    </main>

    <!-- ── Two-column SEO content — scholarly claret ─────────────────────── -->
    <section v-if="bodyBlocks.length" class="border-t border-parchment-200 bg-parchment-50 py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mb-10 pb-8 border-b border-parchment-300">
          <p class="text-xs font-bold uppercase tracking-widest text-claret-500 mb-2">Service overview</p>
          <h2 class="font-serif text-2xl font-bold text-claret-900 sm:text-3xl">
            About {{ displayTitle }}
          </h2>
        </div>
        <div class="service-body columns-1 md:columns-2 md:gap-x-12 [column-fill:balance]">
          <ServicePageBody :blocks="bodyBlocks" />
        </div>
        <div class="mt-10 flex items-center justify-between gap-6 rounded-2xl border border-claret-200 bg-white px-6 py-4 shadow-sm">
          <p class="text-sm font-semibold text-claret-900">
            Trusted by 10,000+ graduate students worldwide
          </p>
          <button type="button"
            class="shrink-0 rounded-xl bg-claret-700 px-6 py-2.5 text-sm font-bold text-white transition-colors hover:bg-claret-800"
            @click="openDrawer">
            Get a quote →
          </button>
        </div>
      </div>
    </section>

    <!-- ── Final CTA ──────────────────────────────────────────────────────── -->
    <section class="bg-claret-950 py-14 text-center" aria-label="Get started">
      <div class="mx-auto max-w-xl px-4 space-y-5">
        <h2 class="font-serif text-2xl font-bold text-white sm:text-3xl">Ready to get started?</h2>
        <p class="text-claret-300 text-sm">Expert academic writing. Grade or money back — guaranteed.</p>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-8 py-3.5 text-sm font-bold text-claret-950 shadow-sm hover:bg-amber-400 transition-colors"
          @click="openDrawer"
        >
          Get a quote →
        </button>
      </div>
    </section>

    <!-- ── Slide-in drawer with OrderCalculator ───────────────────────────── -->
    <Teleport to="body">
      <!-- Backdrop -->
      <Transition name="fade">
        <div
          v-if="drawerOpen"
          class="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
          aria-hidden="true"
          @click="closeDrawer"
        />
      </Transition>

      <!-- Panel -->
      <Transition name="slide-drawer">
        <div
          v-if="drawerOpen"
          role="dialog"
          aria-modal="true"
          aria-label="Pricing calculator"
          class="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-white shadow-2xl"
        >
          <!-- Drawer header -->
          <div class="flex items-center justify-between border-b border-parchment-200 bg-parchment-50 px-5 py-4">
            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-claret-400">Instant price</p>
              <p class="text-sm font-semibold text-claret-900">{{ displayTitle }}</p>
            </div>
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-full border border-parchment-300 text-claret-500 hover:bg-parchment-100 transition-colors"
              aria-label="Close"
              @click="closeDrawer"
            >
              ✕
            </button>
          </div>

          <!-- Calculator -->
          <div class="flex-1 overflow-y-auto p-5">
            <OrderCalculator />
          </div>

          <!-- Drawer footer -->
          <div class="border-t border-parchment-200 bg-parchment-50 px-5 py-4">
            <NuxtLink
              to="/order"
              class="block w-full rounded-xl bg-claret-700 py-3 text-center text-sm font-bold text-white hover:bg-claret-800 transition-colors shadow-sm"
              @click="closeDrawer"
            >
              Place order directly →
            </NuxtLink>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
/* Body prose */
.service-body :deep(h2) { font-family: Georgia, serif; font-weight: 700; color: #3D1025; margin-top: 2.5rem; margin-bottom: 1rem; font-size: 1.375rem; }
.service-body :deep(h3) { font-weight: 600; color: #5C1A38; margin-top: 2rem; margin-bottom: 0.75rem; font-size: 1.125rem; }
.service-body :deep(p)  { color: #4b5563; line-height: 1.8; margin-bottom: 1rem; font-size: 0.9375rem; }
.service-body :deep(ul), .service-body :deep(ol) { padding-left: 1.5rem; color: #4b5563; font-size: 0.9375rem; margin-bottom: 1rem; }
.service-body :deep(li) { margin-bottom: 0.5rem; line-height: 1.65; }
.service-body :deep(strong) { color: #3D1025; font-weight: 600; }
.service-body :deep(table) { display: block; overflow-x: auto; border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }
.service-body :deep(th), .service-body :deep(td) { padding: 0.625rem 1rem; border: 1px solid #fce4ee; font-size: 0.875rem; }
.service-body :deep(th) { background: #fdf2f6; font-weight: 600; color: #7B2241; }
.service-body :deep(a)  { color: #9e1540; text-decoration: underline; }

/* Drawer transition */
.slide-drawer-enter-active, .slide-drawer-leave-active { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-drawer-enter-from, .slide-drawer-leave-to { transform: translateX(100%); }

/* Backdrop + method tab */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
