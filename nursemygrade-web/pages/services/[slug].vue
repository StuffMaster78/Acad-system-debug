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

const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'https://nursemygrade.com'
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
    { '@type': 'Question', name: 'How fast can you deliver?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 3 hours for urgent orders. Most papers are matched with a qualified nurse writer within minutes of placing your order.' } },
    { '@type': 'Question', name: 'Are your writers real nurses?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. Every writer holds at minimum a BSN with active clinical experience. MSN and DNP writers are available for advanced nursing work.' } },
    { '@type': 'Question', name: 'What if I need revisions?', acceptedAnswer: { '@type': 'Answer', text: 'Unlimited free revisions are included within the revision window, always handled by your original writer.' } },
    { '@type': 'Question', name: 'Is using a nursing writing service legal?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. We provide model nursing papers for reference and study — similar to a tutoring service or writing centre. Every order includes an academic use acknowledgement.' } },
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
        provider: { '@type': 'Organization', name: 'NurseMyGrade', url: 'https://nursemygrade.com' },
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
    <!-- Breadcrumb bar -->
    <div class="border-b border-slate-100 bg-white px-4 py-3 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <Breadcrumbs :items="[
          { label: 'Services', href: '/services' },
          { label: displayTitle },
        ]" />
      </div>
    </div>

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

    <!-- ── Long-form editorial content ─────────────────────────────────────
         When Wagtail content exists: renders the StreamField blocks entered
         by staff for this service. When not yet added: renders a structured
         static layout built from the service's core data so the page is
         always complete and SEO-ready.
    ──────────────────────────────────────────────────────────────────── -->
    <div class="border-t border-slate-100 bg-white">
      <div class="section max-w-5xl">

        <!-- Loading skeleton -->
        <div v-if="cmsLoading" class="space-y-6">
          <div v-for="i in 4" :key="i" class="space-y-3">
            <div class="h-7 w-1/2 animate-pulse rounded-lg bg-slate-100" />
            <div class="h-4 w-full animate-pulse rounded bg-slate-100" />
            <div class="h-4 w-5/6 animate-pulse rounded bg-slate-100" />
          </div>
        </div>

        <!-- CMS content from Wagtail — rendered when staff have added it -->
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

        <!-- Static fallback — generated from service data; replaced by CMS content above once staff add it -->
        <template v-else-if="service">
          <div class="grid gap-16 lg:grid-cols-[1fr_340px]">

            <!-- Left: editorial content -->
            <div class="prose prose-slate prose-lg max-w-none
                         prose-headings:font-serif prose-headings:font-bold
                         prose-a:text-brand-600 prose-strong:text-slate-900">

              <h2>Why {{ service.navLabel }} Matters for Nursing Students</h2>
              <p>{{ displayHero.sub }}</p>
              <p>
                Nursing programmes are demanding. Between clinical rotations, simulation labs, pharmacology exams,
                and family responsibilities, producing high-quality academic work consistently is genuinely difficult.
                That's why thousands of nursing students — from first-year ADN programmes through DNP candidacy — rely
                on qualified nursing professionals to support their academic writing.
              </p>

              <h2>What Sets Our Approach to {{ service.navLabel }} Apart</h2>
              <div class="not-prose grid gap-4 sm:grid-cols-2 my-6">
                <div v-for="(item, i) in service.includes" :key="item"
                  class="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">{{ i + 1 }}</span>
                  <span class="text-sm text-slate-700 leading-relaxed">{{ item }}</span>
                </div>
              </div>

              <h2>What You Receive</h2>
              <ul>
                <li v-for="item in service.delivers" :key="item">{{ item }}</li>
              </ul>

              <h2>Who This Service is For</h2>
              <p>{{ service.whoFor }}</p>

              <h2>We Understand Your Challenges as a Nursing Student</h2>
              <p>
                Nursing coursework isn't just writing — it's demonstrating clinical reasoning, applying NANDA diagnoses
                correctly, citing current evidence-based practice, and following APA 7th edition precisely, all while
                managing clinical hours and personal commitments. Our writers are nurses who've done this themselves.
                They write the way nursing instructors expect — because they know what nursing instructors expect.
              </p>

              <h3>Common Challenges We Solve</h3>
              <ul>
                <li><strong>Time constraints:</strong> Clinical rotations, exams, and life leave little time for academic writing. We work to your deadline — as fast as 3 hours.</li>
                <li><strong>Clinical accuracy:</strong> Generic academic writers don't understand NANDA, NIC, NOC, or ADPIE. Our nurses do — it's what they use in practice.</li>
                <li><strong>APA 7th edition:</strong> Nursing programmes require perfect APA 7th formatting. Every paper we deliver is correctly formatted.</li>
                <li><strong>Evidence-based sources:</strong> We source from CINAHL, PubMed, Cochrane, and current peer-reviewed nursing journals — not Wikipedia or outdated textbooks.</li>
              </ul>

              <h2>How to Order {{ service.navLabel }}</h2>
              <ol>
                <li><strong>Submit your brief:</strong> Complete the order form with your assignment details, word count, deadline, and any rubric or patient scenario.</li>
                <li><strong>Get matched:</strong> We assign a nurse writer whose clinical speciality matches your assignment within minutes.</li>
                <li><strong>Track progress:</strong> Message your writer directly through your dashboard, share additional files, and follow real-time progress.</li>
                <li><strong>Download and review:</strong> Receive your paper with a free Turnitin report. Request unlimited free revisions within the review window.</li>
              </ol>

            </div>

            <!-- Right: sticky conversion panel -->
            <div class="space-y-5 lg:sticky lg:top-24 lg:self-start">

              <!-- Price card -->
              <div class="rounded-2xl bg-brand-900 p-6 text-white">
                <div class="flex items-start justify-between mb-4">
                  <div>
                    <p class="text-sm text-brand-300">Starting from</p>
                    <p class="text-4xl font-bold">${{ displayPrice }}<span class="text-lg font-normal text-brand-300">/page</span></p>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
                    <Icon :name="displayIcon" class="h-6 w-6 text-white" />
                  </div>
                </div>
                <NuxtLink to="/order"
                  class="block w-full rounded-xl bg-white py-3.5 text-center text-base font-bold text-brand-700 hover:bg-brand-50 transition-colors">
                  Place an order
                </NuxtLink>
                <NuxtLink to="/contact"
                  class="mt-2 block w-full rounded-xl border border-white/20 py-2.5 text-center text-sm font-semibold text-brand-200 hover:bg-white/10 transition-colors">
                  Talk to us first
                </NuxtLink>
              </div>

              <!-- Nursing FAQ -->
              <div class="rounded-2xl border border-slate-100 bg-white p-5">
                <p class="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">Common questions</p>
                <div class="divide-y divide-slate-100">
                  <div v-for="faq in [
                    { q: 'How fast can you deliver?', a: 'As fast as 3 hours for urgent orders. Most papers are matched with a writer within minutes of placing your order.' },
                    { q: 'Are your writers real nurses?', a: 'Yes. Every writer holds at minimum a BSN with active clinical experience. MSN and DNP writers are available for advanced work.' },
                    { q: 'What if I need revisions?', a: 'Unlimited free revisions within the revision window — always handled by your original writer.' },
                  ]" :key="faq.q" class="py-3">
                    <p class="text-sm font-semibold text-slate-900">{{ faq.q }}</p>
                    <p class="mt-1 text-xs text-slate-500 leading-relaxed">{{ faq.a }}</p>
                  </div>
                </div>
                <NuxtLink href="/contact" class="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-brand-600 hover:underline">
                  More questions → talk to our team
                </NuxtLink>
              </div>

              <!-- Testimonial -->
              <div class="rounded-2xl border border-brand-100 bg-brand-50 p-5">
                <div class="flex gap-0.5 mb-3">
                  <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                  </svg>
                </div>
                <p class="text-sm text-slate-700 italic leading-relaxed">"I was drowning in assignments during my clinical rotation. NurseMyGrade matched me with an MSN writer who clearly understood nursing — not just writing. Got an A."</p>
                <p class="mt-3 text-xs font-semibold text-slate-600">— BSN Student, University of Florida</p>
              </div>

            </div>
          </div>
        </template>

      </div>
    </div>

    <!-- Final CTA strip -->
    <div v-if="service" class="bg-brand-700 py-12 text-center">
      <h2 class="font-serif text-2xl font-bold text-white sm:text-3xl">
        Ready to get your {{ service.navLabel.toLowerCase() }} done?
      </h2>
      <p class="mt-3 text-brand-100">
        A qualified nursing writer is ready. Grade guaranteed or full refund.
      </p>
      <NuxtLink to="/order" class="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-base font-bold text-brand-700 hover:bg-brand-50 transition-colors shadow-lg">
        Place an order — from ${{ displayPrice }}/page
      </NuxtLink>
    </div>

  </div>
</template>
