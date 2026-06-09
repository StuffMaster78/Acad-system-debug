<script setup lang="ts">
const route = useRoute()
const { getBySlug, getRelated } = useServices()

// useFetch inside useServiceCms is awaited at SSG time, so cmsPage.value
// is populated before the 404 check below runs.
const { page: cmsPage, hasContent: hasCmsContent, loading: cmsLoading } = useServiceCms(route.params.slug as string)

// Static enrichment — may be null for pages created purely in Wagtail
const service = getBySlug(route.params.slug as string)

// Only 404 if neither the local catalogue nor Wagtail has this slug
if (!service && !cmsPage.value) {
  throw createError({ statusCode: 404, message: 'Service not found' })
}

// Display values — static data where available, Wagtail data as fallback
const displayTitle   = computed(() => service?.title ?? cmsPage.value?.title ?? '')
const displayHero    = computed(() => service?.hero ?? { headline: displayTitle.value, sub: '' })
const displayPrice   = computed(() => service?.priceFrom ?? parseFloat(cmsPage.value?.pricing_from ?? '15'))
const displayIcon    = computed(() => service?.icon ?? 'file-text')
const displayMeta    = computed(() => service?.meta ?? { title: displayTitle.value, description: '' })

const related = service ? getRelated(service.relatedSlugs) : []

useSeoMeta({
  title: displayMeta.value.title || displayTitle.value,
  description: displayMeta.value.description,
  ogTitle: displayMeta.value.title || displayTitle.value,
  ogDescription: displayMeta.value.description,
})

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
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-20">
      <div class="section py-0">
        <div class="mx-auto max-w-3xl text-center">
          <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20">
            <Icon :name="displayIcon" class="h-9 w-9 text-white" />
          </div>
          <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">
            {{ displayHero.headline }}
          </h1>
          <p v-if="displayHero.sub" class="mx-auto mt-5 max-w-2xl text-lg text-brand-100 leading-relaxed">
            {{ displayHero.sub }}
          </p>
          <div class="mt-8 flex flex-wrap justify-center gap-4">
            <NuxtLink to="/order" class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-8 py-3.5 text-base shadow-lg">
              Order from ${{ displayPrice }}/page
            </NuxtLink>
            <NuxtLink to="/pricing" class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-3.5 text-base">
              See full pricing
            </NuxtLink>
          </div>
          <ul class="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-brand-200">
            <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Grade or money back</li>
            <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Written by BSN/MSN/DNP nurses</li>
            <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Free Turnitin report</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Main content + sidebar -->
    <div class="section">
      <div class="grid gap-10 lg:grid-cols-[1fr_300px]">

        <!-- Left: service detail -->
        <div>
          <!-- What's included (static enrichment — only when local data exists) -->
          <div v-if="service" class="card">
            <h2 class="mb-5 font-serif text-2xl font-bold text-slate-900">What's included</h2>
            <ul class="space-y-3">
              <li v-for="item in service.includes" :key="item" class="flex items-start gap-3">
                <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs text-white font-bold">✓</span>
                <span class="text-slate-700">{{ item }}</span>
              </li>
            </ul>
          </div>

          <!-- What we deliver -->
          <div v-if="service" class="card mt-6">
            <h2 class="mb-5 font-serif text-2xl font-bold text-slate-900">What you receive</h2>
            <ul class="space-y-3">
              <li v-for="item in service.delivers" :key="item" class="flex items-start gap-3">
                <Icon name="check-circle" class="mt-0.5 h-5 w-5 shrink-0 text-brand-500" />
                <span class="text-slate-700">{{ item }}</span>
              </li>
            </ul>
          </div>

          <!-- Who it's for -->
          <div v-if="service" class="card mt-6">
            <h2 class="mb-3 font-serif text-xl font-bold text-slate-900">Who this is for</h2>
            <p class="text-slate-600 leading-relaxed">{{ service.whoFor }}</p>
          </div>

          <!-- Guarantees row -->
          <div class="mt-6 grid gap-4 sm:grid-cols-3">
            <div v-for="g in [
              { icon: 'trophy',      label: 'Grade or money back',      color: 'bg-amber-50 text-amber-600' },
              { icon: 'stethoscope', label: 'Written by BSN/MSN/DNP',   color: 'bg-brand-50 text-brand-600' },
              { icon: 'refresh-cw',  label: 'Free Turnitin report',     color: 'bg-green-50 text-green-600' },
            ]" :key="g.label" class="rounded-xl bg-brand-50 p-4 text-center">
              <div class="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl" :class="g.color.split(' ')[0]">
                <Icon :name="g.icon" class="h-5 w-5" :class="g.color.split(' ')[1]" />
              </div>
              <p class="text-sm font-semibold text-brand-800">{{ g.label }}</p>
            </div>
          </div>

          <!-- Related services -->
          <div v-if="related.length" class="mt-10">
            <h2 class="mb-5 font-serif text-xl font-bold text-slate-900">Related services</h2>
            <div class="grid gap-4 sm:grid-cols-3">
              <NuxtLink
                v-for="r in related"
                :key="r.slug"
                :href="`/services/${r.slug}`"
                class="card group flex items-center gap-3 transition-shadow hover:shadow-md"
              >
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100">
                  <Icon :name="r.icon" class="h-5 w-5 text-brand-600" />
                </div>
                <div>
                  <p class="font-semibold text-slate-900 group-hover:text-brand-700 transition-colors text-sm">{{ r.navLabel }}</p>
                  <p class="text-xs text-brand-600">From ${{ r.priceFrom }}/page</p>
                </div>
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Right: sticky sidebar -->
        <div class="lg:sticky lg:top-24 lg:self-start space-y-5">
          <!-- Quick quote calculator -->
          <div class="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
            <p class="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">Get an instant quote</p>
            <ClientOnly>
              <SidebarCalculator />
              <template #fallback><div class="h-48 animate-pulse rounded-xl bg-slate-100" /></template>
            </ClientOnly>
          </div>
          <!-- Nursing writer badge -->
          <div class="rounded-2xl bg-brand-900 p-5 text-white text-center">
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-white/10">
              <Icon name="stethoscope" class="h-6 w-6 text-white" />
            </div>
            <p class="text-sm font-semibold">BSN, MSN &amp; DNP writers</p>
            <p class="mt-1 text-xs text-brand-300">4.98★ · 9,800+ nursing papers</p>
            <NuxtLink to="/order" class="mt-4 block rounded-xl bg-white py-2.5 text-sm font-bold text-brand-700 hover:bg-brand-50 transition-colors">
              Place an order
            </NuxtLink>
          </div>
          <!-- Related services -->
          <div v-if="related.length" class="rounded-2xl border border-slate-100 bg-white p-5">
            <p class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Related services</p>
            <ul class="space-y-2">
              <li v-for="r in related" :key="r.slug">
                <NuxtLink :href="`/services/${r.slug}`"
                  class="flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm text-slate-600 hover:bg-brand-50 hover:text-brand-700 transition-colors">
                  <Icon :name="r.icon" class="h-4 w-4 shrink-0 text-brand-500" />
                  {{ r.navLabel }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>

    <!-- ── CMS Editorial Content ─────────────────────────────────────────
         Edited in Wagtail by admins/editors. Drives SEO for this service.
         Only rendered when content has been published for this service slug.
    ──────────────────────────────────────────────────────────────────── -->
    <div v-if="hasCmsContent || cmsLoading" class="border-t border-slate-100 bg-white">
      <div class="section max-w-4xl">

        <!-- Skeleton while fetching -->
        <div v-if="cmsLoading" class="space-y-4">
          <div class="h-8 w-2/3 animate-pulse rounded-lg bg-slate-100" />
          <div class="h-4 w-full animate-pulse rounded bg-slate-100" />
          <div class="h-4 w-5/6 animate-pulse rounded bg-slate-100" />
          <div class="h-4 w-4/5 animate-pulse rounded bg-slate-100" />
        </div>

        <!-- Rendered StreamField blocks -->
        <template v-else-if="hasCmsContent && cmsPage">
          <!-- Reviewed-by badge if set -->
          <div v-if="cmsPage.reviewer" class="mb-8 flex items-center gap-2 text-sm text-slate-500">
            <Icon name="check-circle" class="h-4 w-4 text-brand-500" />
            Reviewed by <strong class="text-slate-700">{{ cmsPage.reviewer.name }}</strong>
            <span v-if="cmsPage.last_substantive_update" class="text-slate-400">
              · Updated {{ new Date(cmsPage.last_substantive_update).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}
            </span>
          </div>

          <ServicePageBody :blocks="cmsPage.body" />

          <!-- CTA if set differently from default -->
          <div v-if="cmsPage.primary_cta_text && cmsPage.primary_cta_url" class="mt-10 text-center">
            <NuxtLink :href="cmsPage.primary_cta_url" class="btn-primary px-10 py-4 text-base">
              {{ cmsPage.primary_cta_text }}
            </NuxtLink>
          </div>
        </template>

      </div>
    </div>

  </div>
</template>
