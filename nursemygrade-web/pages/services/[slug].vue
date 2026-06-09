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
const serviceTab = ref("What's Included")

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

        <!-- Left: tabbed service content -->
        <div v-if="service">

          <!-- Tab navigation — scrollable on mobile -->
          <div class="overflow-x-auto" style="scrollbar-width: none;">
            <div class="flex min-w-max gap-1 rounded-2xl bg-slate-100 p-1.5 mb-8">
              <button
                v-for="tab in ['What\'s Included', 'What You Receive', 'Who It\'s For', 'Our Guarantees']"
                :key="tab"
                class="shrink-0 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all"
                :class="serviceTab === tab ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
                @click="serviceTab = tab"
              >{{ tab }}</button>
            </div>
          </div>

          <!-- Tab: What's Included -->
          <div v-if="serviceTab === 'What\'s Included'" class="space-y-4 animate-fade-in">
            <div class="grid gap-3 sm:grid-cols-2">
              <div
                v-for="(item, i) in service.includes"
                :key="item"
                class="flex items-start gap-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm"
              >
                <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
                  {{ i + 1 }}
                </span>
                <span class="text-sm text-slate-700 leading-relaxed">{{ item }}</span>
              </div>
            </div>
            <div class="mt-6 rounded-2xl bg-brand-50 border border-brand-100 p-5 flex items-center justify-between gap-4">
              <div>
                <p class="font-semibold text-brand-900">Ready to place your order?</p>
                <p class="text-sm text-brand-700 mt-0.5">From ${{ displayPrice }}/page · Grade or money back</p>
              </div>
              <NuxtLink to="/order" class="shrink-0 btn-primary">Order now</NuxtLink>
            </div>
          </div>

          <!-- Tab: What You Receive -->
          <div v-else-if="serviceTab === 'What You Receive'" class="space-y-3 animate-fade-in">
            <div
              v-for="item in service.delivers"
              :key="item"
              class="flex items-center gap-4 rounded-xl border border-slate-100 bg-white p-4 shadow-sm"
            >
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-green-100">
                <Icon name="check-circle" class="h-5 w-5 text-green-600" />
              </div>
              <p class="text-sm text-slate-700">{{ item }}</p>
            </div>
            <div class="mt-4 rounded-2xl bg-slate-900 p-5 text-white">
              <p class="font-semibold">Everything is included — no hidden extras</p>
              <p class="text-sm text-slate-300 mt-1">Plagiarism report, title page, reference list, and revisions are all free.</p>
            </div>
          </div>

          <!-- Tab: Who It's For -->
          <div v-else-if="serviceTab === 'Who It\'s For'" class="animate-fade-in">
            <div class="rounded-2xl border border-slate-100 bg-white p-7 shadow-sm">
              <div class="flex items-start gap-4 mb-5">
                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-100">
                  <Icon :name="displayIcon" class="h-6 w-6 text-brand-600" />
                </div>
                <div>
                  <h3 class="font-serif text-xl font-bold text-slate-900">{{ service.navLabel }}</h3>
                  <p class="text-sm text-brand-600">From ${{ displayPrice }}/page</p>
                </div>
              </div>
              <p class="text-slate-700 leading-relaxed">{{ service.whoFor }}</p>
            </div>
            <div class="mt-5 grid gap-4 sm:grid-cols-3">
              <div v-for="level in ['ADN / BSN Students', 'MSN / NP Students', 'DNP / PhD Students']" :key="level"
                class="rounded-xl border border-brand-100 bg-brand-50 p-4 text-center">
                <p class="text-sm font-semibold text-brand-800">{{ level }}</p>
              </div>
            </div>
            <div class="mt-5 rounded-2xl bg-brand-900 p-5 text-center">
              <p class="text-white font-semibold">Not sure if this service fits your assignment?</p>
              <NuxtLink to="/contact" class="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-brand-300 hover:text-white transition-colors">
                Talk to our team → we'll confirm in minutes
              </NuxtLink>
            </div>
          </div>

          <!-- Tab: Guarantees -->
          <div v-else-if="serviceTab === 'Our Guarantees'" class="animate-fade-in">
            <div class="grid gap-4 sm:grid-cols-2">
              <div v-for="g in [
                { icon: 'trophy',       title: 'Grade or money back',      desc: 'If the paper doesn\'t meet your stated requirements after revisions, we refund in full.', color: 'bg-amber-100 text-amber-600' },
                { icon: 'stethoscope',  title: 'Written by real nurses',   desc: 'Every writer holds at minimum a BSN with clinical experience. MSN and DNP available.', color: 'bg-brand-100 text-brand-600' },
                { icon: 'shield-check', title: 'Free Turnitin report',     desc: 'Every paper is checked for plagiarism before delivery. Report included free.', color: 'bg-green-100 text-green-600' },
                { icon: 'bot',          title: 'Zero AI content',          desc: '100% human-written by a qualified nurse. Free AI-detection report on request.', color: 'bg-blue-100 text-blue-600' },
                { icon: 'refresh-cw',   title: 'Unlimited free revisions', desc: 'Request changes within the revision window — always free, always by your original writer.', color: 'bg-violet-100 text-violet-600' },
                { icon: 'lock',         title: 'Complete confidentiality', desc: 'Your identity and order details are never shared with any third party.', color: 'bg-slate-100 text-slate-600' },
              ]" :key="g.title" class="flex gap-4 rounded-xl border border-slate-100 bg-white p-5 shadow-sm">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl" :class="g.color.split(' ')[0]">
                  <Icon :name="g.icon" class="h-5 w-5" :class="g.color.split(' ')[1]" />
                </div>
                <div>
                  <p class="font-semibold text-slate-900 text-sm">{{ g.title }}</p>
                  <p class="mt-1 text-xs text-slate-500 leading-relaxed">{{ g.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Related services (always visible below tabs) -->
          <div v-if="related.length" class="mt-10">
            <h2 class="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">Related services</h2>
            <div class="flex gap-3 overflow-x-auto snap-x snap-mandatory pb-2" style="scrollbar-width: none;">
              <NuxtLink
                v-for="r in related"
                :key="r.slug"
                :href="`/services/${r.slug}`"
                class="group snap-start shrink-0 flex items-center gap-3 rounded-xl border border-slate-100 bg-white px-4 py-3 shadow-sm transition-all hover:border-brand-200 hover:shadow-md w-52"
              >
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-100 group-hover:bg-brand-600 transition-colors">
                  <Icon :name="r.icon" class="h-4 w-4 text-brand-600 group-hover:text-white transition-colors" />
                </div>
                <div class="min-w-0">
                  <p class="truncate text-xs font-semibold text-slate-800 group-hover:text-brand-700">{{ r.navLabel }}</p>
                  <p class="text-xs text-brand-600">From ${{ r.priceFrom }}/page</p>
                </div>
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Fallback if no static data: simple CTA card -->
        <div v-else class="rounded-2xl border border-brand-100 bg-brand-50 p-8 text-center">
          <Icon name="stethoscope" class="mx-auto mb-4 h-12 w-12 text-brand-600" />
          <p class="text-lg font-semibold text-slate-900">Expert nursing writers ready</p>
          <p class="mt-2 text-slate-600">Place your order and we'll match you with the right nurse for this service.</p>
          <NuxtLink to="/order" class="btn-primary mt-6 inline-flex">Place an order</NuxtLink>
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
