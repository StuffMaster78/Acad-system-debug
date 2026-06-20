<script setup lang="ts">
const route = useRoute()
const { getBySlug, getRelated } = useServices()

const { page: cmsPage, hasContent: hasCmsContent, loading: cmsLoading } = useServiceCms(route.params.slug as string)
const service = getBySlug(route.params.slug as string)

if (!service && !cmsPage.value) {
  throw createError({ statusCode: 404, message: 'Service not found' })
}

const displayTitle = computed(() => service?.title ?? cmsPage.value?.title ?? '')
const displayHero  = computed(() => service?.hero ?? { headline: displayTitle.value, sub: '' })
const displayPrice = computed(() => service?.priceFrom ?? parseFloat(cmsPage.value?.pricing_from ?? '15'))
const displayIcon  = computed(() => service?.icon ?? 'file-text')
const displayMeta  = computed(() => service?.meta ?? { title: displayTitle.value, description: '' })
const displayIncludes = computed(() => service?.includes ?? [])

const related = service ? getRelated(service.relatedSlugs) : []

const bodyBlocks = computed(() => cmsPage.value?.body ?? [])

const config  = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'https://nursemygrade.com'
const canonicalUrl = `${siteUrl}/services/${route.params.slug}`

useSeoMeta({
  title:         displayMeta.value.title || displayTitle.value,
  description:   displayMeta.value.description,
  ogTitle:       displayMeta.value.title || displayTitle.value,
  ogDescription: displayMeta.value.description,
})

const faqSchema = service ? {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    { '@type': 'Question', name: 'How fast can you deliver?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 3 hours for urgent orders. Most papers are matched with a qualified nurse writer within minutes of placing your order.' } },
    { '@type': 'Question', name: 'Are your writers real nurses?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. Every writer holds at minimum a BSN with active clinical experience. MSN and DNP writers are available for advanced nursing work.' } },
    { '@type': 'Question', name: 'What if I need revisions?', acceptedAnswer: { '@type': 'Answer', text: 'Unlimited free revisions are included within the revision window, always handled by your original writer.' } },
    { '@type': 'Question', name: 'Is using a nursing writing service legal?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. We provide model nursing papers for reference and study — similar to a tutoring service or writing centre. Every order includes an academic use acknowledgement.' } },
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
        provider: { '@type': 'Organization', name: 'NurseMyGrade', url: 'https://nursemygrade.com' },
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
  <!-- Clinical record card layout: form LEFT, content RIGHT in hero; article + sticky summary below -->
  <div class="pb-20 lg:pb-0">

    <!-- ── Breadcrumb ──────────────────────────────────────────────────────── -->
    <div class="border-b border-brand-100 bg-white px-4 py-3 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <Breadcrumbs :items="[{ label: 'Services', href: '/services' }, { label: displayTitle }]" />
      </div>
    </div>

    <!-- ── Hero: light teal bg, form LEFT, copy RIGHT ─────────────────────── -->
    <section class="bg-gradient-to-br from-brand-50 to-white py-12 sm:py-16" aria-label="Service overview">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-10 lg:grid-cols-2 lg:items-start xl:gap-16">

          <!-- LEFT: clinical intake form -->
          <div>
            <MultiStepOrderForm />
          </div>

          <!-- RIGHT: credentials + title + trust -->
          <div class="flex flex-col justify-center lg:order-first xl:order-last">

            <!-- Credential level badges -->
            <div class="mb-5 flex flex-wrap gap-2">
              <span
                v-for="level in ['BSN', 'MSN', 'DNP / PhD']"
                :key="level"
                class="inline-flex items-center gap-1.5 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700"
              >
                <span class="h-1.5 w-1.5 rounded-full bg-brand-500" />
                {{ level }} writers
              </span>
            </div>

            <h1 class="font-serif text-3xl font-bold text-brand-900 sm:text-4xl xl:text-5xl leading-tight">
              {{ displayHero.headline }}
            </h1>

            <p v-if="displayHero.sub" class="mt-3 text-brand-600 leading-relaxed">
              {{ displayHero.sub }}
            </p>

            <!-- Trust signals -->
            <div class="mt-6 space-y-2.5">
              <div
                v-for="signal in [
                  { icon: 'trophy',       text: 'Grade or money back — no conditions' },
                  { icon: 'stethoscope',  text: 'Written by credentialed nursing professionals' },
                  { icon: 'shield-check', text: 'Free Turnitin plagiarism report included' },
                  { icon: 'bot',          text: '100% human-written — zero AI content' },
                ]"
                :key="signal.text"
                class="flex items-center gap-3 text-sm text-slate-700"
              >
                <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-100">
                  <Icon :name="signal.icon" class="h-3.5 w-3.5 text-brand-600" />
                </span>
                {{ signal.text }}
              </div>
            </div>

            <!-- Social proof -->
            <div class="mt-6 flex items-center gap-2 text-sm text-slate-500">
              <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span class="font-semibold text-slate-700">4.98</span>
              <span>· 9,800+ nursing papers delivered</span>
            </div>

            <!-- Mobile CTA -->
            <div class="mt-7 lg:hidden">
              <NuxtLink
                to="/order"
                class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-7 py-3.5 text-sm font-bold text-white transition-colors hover:bg-brand-700 shadow-sm"
              >
                Order from ${{ displayPrice }}/page →
              </NuxtLink>
            </div>

          </div>
        </div>
      </div>
    </section>

    <!-- ── Main content ────────────────────────────────────────────────────── -->
    <main class="bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div class="lg:grid lg:grid-cols-3 lg:gap-12 xl:gap-16">

          <!-- Article: long-form content, left 2/3 -->
          <article class="lg:col-span-2 space-y-12 min-w-0" aria-label="Service details">

            <!-- Who it's for -->
            <section v-if="service?.whoFor" aria-labelledby="who-heading">
              <h2 id="who-heading" class="font-serif text-xl font-bold text-brand-900 mb-3">Who this service is for</h2>
              <p class="text-slate-600 leading-relaxed">{{ service.whoFor }}</p>
            </section>

            <!-- What's included -->
            <section v-if="displayIncludes.length" aria-labelledby="includes-heading">
              <h2 id="includes-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">What's included</h2>
              <div class="grid gap-3 sm:grid-cols-2">
                <div
                  v-for="(item, i) in displayIncludes"
                  :key="item"
                  class="flex items-start gap-3 rounded-xl border border-brand-100 bg-brand-50 p-4"
                >
                  <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-[11px] font-bold text-white">
                    {{ i + 1 }}
                  </span>
                  <span class="text-sm text-slate-700 leading-relaxed">{{ item }}</span>
                </div>
              </div>
            </section>

            <!-- CMS body -->
            <div v-if="bodyBlocks.length && hasCmsContent" class="service-body">
              <ServicePageBody :blocks="bodyBlocks" />
            </div>

            <!-- Guarantees -->
            <section aria-labelledby="guarantees-heading">
              <h2 id="guarantees-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">Our guarantees</h2>
              <div class="grid gap-3 sm:grid-cols-2">
                <div
                  v-for="g in [
                    { icon: 'trophy',       title: 'Grade or money back',      desc: 'Full refund if the work doesn\'t meet your stated requirements after revisions.' },
                    { icon: 'stethoscope',  title: 'Written by real nurses',   desc: 'BSN minimum, MSN and DNP writers available. Credentials verified before assignment.' },
                    { icon: 'shield-check', title: 'Free Turnitin report',     desc: 'Every paper checked before delivery. Report included at no extra charge.' },
                    { icon: 'refresh-cw',   title: 'Unlimited free revisions', desc: 'Within the revision window, always by your original writer.' },
                  ]"
                  :key="g.title"
                  class="flex gap-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm"
                >
                  <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-100">
                    <Icon :name="g.icon" class="h-4 w-4 text-brand-600" />
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-slate-900">{{ g.title }}</p>
                    <p class="mt-0.5 text-xs text-slate-500 leading-relaxed">{{ g.desc }}</p>
                  </div>
                </div>
              </div>
            </section>

            <!-- FAQ -->
            <section aria-labelledby="faq-heading">
              <h2 id="faq-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">
                Common questions about {{ displayTitle.toLowerCase() }}
              </h2>
              <div class="divide-y divide-slate-100 rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
                <details
                  v-for="faq in [
                    { q: 'How fast can you deliver?', a: 'As fast as 3 hours for urgent orders. Most papers are matched with a qualified nurse writer within minutes of placing your order.' },
                    { q: 'Are your writers real nurses?', a: 'Yes. Every writer holds at minimum a BSN with active clinical experience. MSN and DNP writers are available for advanced nursing work.' },
                    { q: 'What if I need revisions?', a: 'Unlimited free revisions are included within the revision window, always handled by your original writer.' },
                    { q: 'Is using a nursing writing service legal?', a: 'Yes. We provide model nursing papers for reference and study — similar to a tutoring service or writing centre. Every order includes an academic use acknowledgement.' },
                  ]"
                  :key="faq.q"
                  class="group px-5 py-4"
                >
                  <summary class="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold text-slate-900">
                    {{ faq.q }}
                    <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 transition-transform group-open:rotate-45 text-xs font-bold">+</span>
                  </summary>
                  <p class="mt-3 text-sm text-slate-500 leading-relaxed">{{ faq.a }}</p>
                </details>
              </div>
            </section>

          </article>

          <!-- Aside: sticky clinical summary card, right 1/3 -->
          <aside class="hidden lg:block" aria-label="Order summary">
            <div class="sticky top-24 space-y-4">

              <!-- Price card -->
              <div class="overflow-hidden rounded-2xl border border-brand-100 bg-white shadow-sm">
                <div class="bg-brand-700 px-5 py-4">
                  <p class="text-[10px] font-bold uppercase tracking-widest text-brand-300 mb-1">Starting from</p>
                  <p class="text-3xl font-bold text-white">
                    ${{ displayPrice }}<span class="text-sm font-normal text-brand-300">/page</span>
                  </p>
                </div>
                <div class="p-5 space-y-4">
                  <NuxtLink
                    to="/order"
                    class="block w-full rounded-xl bg-brand-600 py-3 text-center text-sm font-bold text-white transition-colors hover:bg-brand-700 shadow-sm"
                  >
                    Order now →
                  </NuxtLink>
                  <NuxtLink
                    to="/pricing"
                    class="block w-full rounded-xl border border-brand-200 py-2.5 text-center text-xs font-semibold text-brand-600 transition-colors hover:bg-brand-50"
                  >
                    See full pricing
                  </NuxtLink>
                  <ul class="space-y-2 pt-1">
                    <li v-for="t in ['Grade or money back', 'Written by BSN/MSN/DNP nurses', 'Free Turnitin report', 'Zero AI content', 'Unlimited free revisions']" :key="t"
                      class="flex items-center gap-2 text-xs text-slate-600">
                      <Icon name="check" class="h-3.5 w-3.5 shrink-0 text-brand-500" />
                      {{ t }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Reviewer -->
              <div v-if="cmsPage?.reviewer" class="rounded-2xl border border-brand-100 bg-brand-50 p-4">
                <div class="flex items-center gap-2 text-xs text-slate-500 mb-1">
                  <Icon name="check-circle" class="h-3.5 w-3.5 text-brand-500" />
                  Content reviewed by
                </div>
                <p class="text-sm font-semibold text-slate-900">{{ cmsPage.reviewer.name }}</p>
                <p v-if="cmsPage.reviewer.role" class="text-xs text-slate-500 mt-0.5">{{ cmsPage.reviewer.role }}</p>
              </div>

              <!-- Related -->
              <div v-if="related.length" class="rounded-2xl border border-slate-100 bg-white p-5">
                <p class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Related services</p>
                <ul class="space-y-1.5">
                  <li v-for="r in related" :key="r.slug">
                    <NuxtLink
                      :to="`/services/${r.slug}`"
                      class="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-slate-600 transition-colors hover:bg-brand-50 hover:text-brand-700"
                    >
                      <Icon :name="r.icon" class="h-3.5 w-3.5 shrink-0 text-brand-400" />
                      {{ r.navLabel }}
                    </NuxtLink>
                  </li>
                </ul>
              </div>

            </div>
          </aside>

        </div>
      </div>
    </main>

    <!-- ── Final CTA ──────────────────────────────────────────────────────── -->
    <section class="bg-brand-700 py-14 text-center" aria-label="Get started">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="font-serif text-2xl font-bold text-white sm:text-3xl">
          Ready to work with a nurse writer?
        </h2>
        <p class="text-brand-100 text-sm leading-relaxed">
          From ${{ displayPrice }}/page · Matched within minutes · Grade or money back
        </p>
        <NuxtLink
          to="/order"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Place your order →
        </NuxtLink>
      </div>
    </section>

    <!-- ── Mobile fixed CTA bar ────────────────────────────────────────────── -->
    <div class="fixed bottom-0 inset-x-0 z-30 border-t border-slate-200 bg-white/95 backdrop-blur-sm px-4 py-3 flex gap-3 lg:hidden">
      <NuxtLink to="/pricing" class="flex h-11 flex-1 items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-slate-700">
        See pricing
      </NuxtLink>
      <NuxtLink to="/order" class="flex h-11 flex-[2] items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white">
        Order from ${{ displayPrice }}/page
      </NuxtLink>
    </div>

  </div>
</template>

<style scoped>
.service-body :deep(h2) { font-family: Georgia, serif; font-weight: 700; color: #134e4a; margin-top: 2rem; margin-bottom: 0.75rem; font-size: 1.25rem; }
.service-body :deep(h3) { font-weight: 600; color: #115e59; margin-top: 1.5rem; margin-bottom: 0.5rem; }
.service-body :deep(p)  { color: #475569; line-height: 1.7; margin-bottom: 0.75rem; font-size: 0.9375rem; }
.service-body :deep(ul), .service-body :deep(ol) { padding-left: 1.25rem; color: #475569; font-size: 0.9375rem; }
.service-body :deep(li) { margin-bottom: 0.375rem; line-height: 1.6; }
.service-body :deep(table) { display: block; overflow-x: auto; border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
.service-body :deep(th), .service-body :deep(td) { padding: 0.5rem 0.75rem; border: 1px solid #ccfbf1; font-size: 0.875rem; }
.service-body :deep(th) { background: #f0fdfa; font-weight: 600; color: #134e4a; }
.service-body :deep(a)  { color: #0d9488; text-decoration: underline; }
</style>
