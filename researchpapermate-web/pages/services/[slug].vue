<script setup lang="ts">
const route = useRoute()
const { getBySlug, getRelated } = useServices()

const { page: cmsPage, hasContent: hasCmsContent, loading: cmsLoading } = useServiceCms(route.params.slug as string)

const service = getBySlug(route.params.slug as string)

if (!service && !cmsPage.value) {
  throw createError({ statusCode: 404, message: 'Service not found' })
}

const displayTitle   = computed(() => service?.title ?? cmsPage.value?.title ?? '')
const displayHero    = computed(() => service?.hero ?? { headline: displayTitle.value, sub: '' })
const displayPrice   = computed(() => service?.priceFrom ?? parseFloat(cmsPage.value?.pricing_from ?? '15'))
const displayIcon    = computed(() => service?.icon ?? 'file-text')
const displayMeta    = computed(() => service?.meta ?? { title: displayTitle.value, description: '' })

const related = service ? getRelated(service.relatedSlugs) : []
const serviceTab = ref("What's Included")

const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'https://researchpapermate.com'
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
    { '@type': 'Question', name: 'How fast can you deliver?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 2 hours for urgent orders up to 4 pages. Most papers are matched with a qualified writer within minutes of placing your order.' } },
    { '@type': 'Question', name: 'Are your writers qualified?', acceptedAnswer: { '@type': 'Answer', text: "Yes. Every writer holds at minimum a Master's degree in their subject area, verified against the issuing institution. PhD-qualified writers are available for doctoral work." } },
    { '@type': 'Question', name: 'What if I need revisions?', acceptedAnswer: { '@type': 'Answer', text: 'Unlimited free revisions are included within the revision window, always handled by your original writer.' } },
    { '@type': 'Question', name: 'Is using an academic writing service legal?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. We provide model academic papers for reference and study — the same as a tutoring service or writing centre. Every order includes an academic-use acknowledgement.' } },
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
        provider: { '@type': 'Organization', name: 'ResearchPaperMate', url: 'https://researchpapermate.com' },
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
    <section class="relative overflow-hidden bg-claret-950 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-64 w-64 rounded-full bg-claret-600 opacity-20 blur-[80px]" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <div class="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10 ring-1 ring-white/20">
          <Icon :name="displayIcon" class="h-7 w-7 text-white" />
        </div>
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">{{ displayHero.headline }}</h1>
        <p v-if="displayHero.sub" class="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-claret-200">{{ displayHero.sub }}</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-700 shadow-lg transition-colors hover:bg-parchment-100">
            Order from ${{ displayPrice }}/page
          </NuxtLink>
          <NuxtLink to="/pricing" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10">
            See full pricing
          </NuxtLink>
        </div>
        <div class="mt-6 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm text-claret-300">
          <span>✓ Grade or money back</span>
          <span>✓ Master's &amp; PhD writers</span>
          <span>✓ Free Turnitin report</span>
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
            <div class="mb-8 flex min-w-max gap-1 rounded-2xl bg-slate-100 p-1.5">
              <button
                v-for="tab in ['What\'s Included', 'What You Receive', 'Who It\'s For', 'Our Guarantees']"
                :key="tab"
                class="shrink-0 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all"
                :class="serviceTab === tab ? 'bg-white text-claret-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
                @click="serviceTab = tab"
              >{{ tab }}</button>
            </div>
          </div>

          <!-- Tab: What's Included -->
          <div v-if="serviceTab === 'What\'s Included'" class="space-y-4">
            <div class="grid gap-3 sm:grid-cols-2">
              <div
                v-for="(item, i) in service.includes"
                :key="item"
                class="flex items-start gap-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm"
              >
                <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-claret-600 text-xs font-bold text-white">
                  {{ i + 1 }}
                </span>
                <span class="text-sm leading-relaxed text-slate-700">{{ item }}</span>
              </div>
            </div>
            <div class="mt-6 flex items-center justify-between gap-4 rounded-2xl border border-amber-100 bg-parchment-100 p-5">
              <div>
                <p class="font-semibold text-claret-900">Ready to place your order?</p>
                <p class="mt-0.5 text-sm text-claret-700">From ${{ displayPrice }}/page · Grade or money back</p>
              </div>
              <NuxtLink to="/order" class="shrink-0 btn-primary">Order now</NuxtLink>
            </div>
          </div>

          <!-- Tab: What You Receive -->
          <div v-else-if="serviceTab === 'What You Receive'" class="space-y-3">
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
            <div class="mt-4 rounded-2xl bg-claret-900 p-5 text-white">
              <p class="font-semibold">Everything is included — no hidden extras</p>
              <p class="mt-1 text-sm text-slate-300">Plagiarism report, title page, reference list, and revisions are all free.</p>
            </div>
          </div>

          <!-- Tab: Who It's For -->
          <div v-else-if="serviceTab === 'Who It\'s For'">
            <div class="rounded-2xl border border-slate-100 bg-white p-7 shadow-sm">
              <div class="mb-5 flex items-start gap-4">
                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-100">
                  <Icon :name="displayIcon" class="h-6 w-6 text-amber-700" />
                </div>
                <div>
                  <h3 class="font-serif text-xl font-bold text-slate-900">{{ service.navLabel }}</h3>
                  <p class="text-sm text-amber-700">From ${{ displayPrice }}/page</p>
                </div>
              </div>
              <p class="leading-relaxed text-slate-700">{{ service.whoFor }}</p>
            </div>
            <div class="mt-5 grid gap-4 sm:grid-cols-3">
              <div v-for="level in ['Undergraduate', `Master\\'s Level`, 'PhD / Doctoral']" :key="level"
                class="rounded-xl border border-amber-100 bg-parchment-100 p-4 text-center">
                <p class="text-sm font-semibold text-claret-800">{{ level }}</p>
              </div>
            </div>
            <div class="mt-5 rounded-2xl bg-claret-950 p-5 text-center">
              <p class="font-semibold text-white">Not sure if this service fits your assignment?</p>
              <NuxtLink to="/contact" class="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-claret-300 transition-colors hover:text-white">
                Talk to our team → we'll confirm in minutes
              </NuxtLink>
            </div>
          </div>

          <!-- Tab: Guarantees -->
          <div v-else-if="serviceTab === 'Our Guarantees'">
            <div class="grid gap-4 sm:grid-cols-2">
              <div v-for="g in [
                { icon: 'trophy',       title: 'Grade or money back',         desc: 'If the paper doesn\'t meet your stated requirements after revisions, we refund in full.', color: 'bg-amber-100 text-amber-600' },
                { icon: 'graduation-cap', title: 'Master\'s & PhD writers',   desc: 'Every writer is degree-verified in their subject. PhD writers available for doctoral work.', color: 'bg-amber-100 text-amber-700' },
                { icon: 'shield-check', title: 'Free Turnitin report',        desc: 'Every paper is checked for plagiarism before delivery. Report included at no extra charge.', color: 'bg-green-100 text-green-600' },
                { icon: 'bot',          title: 'Zero AI content',             desc: '100% human-written by a real expert. Free AI-detection report available on request.', color: 'bg-blue-100 text-blue-600' },
                { icon: 'refresh-cw',   title: 'Unlimited free revisions',    desc: 'Request changes within the revision window — always free, always by your original writer.', color: 'bg-violet-100 text-violet-600' },
                { icon: 'lock',         title: 'Complete confidentiality',    desc: 'Your identity and order details are never shared with any third party.', color: 'bg-slate-100 text-slate-600' },
              ]" :key="g.title" class="flex gap-4 rounded-xl border border-slate-100 bg-white p-5 shadow-sm">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl" :class="g.color.split(' ')[0]">
                  <Icon :name="g.icon" class="h-5 w-5" :class="g.color.split(' ')[1]" />
                </div>
                <div>
                  <p class="text-sm font-semibold text-slate-900">{{ g.title }}</p>
                  <p class="mt-1 text-xs leading-relaxed text-slate-500">{{ g.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Related services (always visible below tabs) -->
          <div v-if="related.length" class="mt-10">
            <h2 class="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">Related services</h2>
            <div class="flex gap-3 snap-x snap-mandatory overflow-x-auto pb-2" style="scrollbar-width: none;">
              <NuxtLink
                v-for="r in related"
                :key="r.slug"
                :href="`/services/${r.slug}`"
                class="group flex w-52 shrink-0 snap-start items-center gap-3 rounded-xl border border-slate-100 bg-white px-4 py-3 shadow-sm transition-all hover:border-amber-200 hover:shadow-md"
              >
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-100 transition-colors group-hover:bg-claret-600">
                  <Icon :name="r.icon" class="h-4 w-4 text-amber-700 transition-colors group-hover:text-white" />
                </div>
                <div class="min-w-0">
                  <p class="truncate text-xs font-semibold text-slate-800 group-hover:text-claret-700">{{ r.navLabel }}</p>
                  <p class="text-xs text-amber-700">From ${{ r.priceFrom }}/page</p>
                </div>
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Fallback if no static data -->
        <div v-else class="rounded-2xl border border-amber-100 bg-parchment-100 p-8 text-center">
          <Icon name="graduation-cap" class="mx-auto mb-4 h-12 w-12 text-amber-700" />
          <p class="text-lg font-semibold text-slate-900">Expert writers ready</p>
          <p class="mt-2 text-slate-600">Place your order and we'll match you with the right specialist for this service.</p>
          <NuxtLink to="/order" class="btn-primary mt-6 inline-flex">Place an order</NuxtLink>
        </div>

        <!-- Right: sticky sidebar -->
        <div class="lg:sticky lg:top-24 lg:self-start space-y-5">
          <MultiStepOrderForm />
          <div class="rounded-2xl bg-claret-950 p-5 text-center text-white">
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-white/10">
              <Icon name="graduation-cap" class="h-6 w-6 text-white" />
            </div>
            <p class="text-sm font-semibold">Master's &amp; PhD writers</p>
            <p class="mt-1 text-xs text-claret-300">4.8★ · 14,700+ papers delivered</p>
            <NuxtLink to="/order" class="mt-4 block rounded-xl bg-white py-2.5 text-sm font-bold text-claret-700 transition-colors hover:bg-parchment-100">
              Place an order
            </NuxtLink>
          </div>
          <div v-if="related.length" class="rounded-2xl border border-slate-100 bg-white p-5">
            <p class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Related services</p>
            <ul class="space-y-2">
              <li v-for="r in related" :key="r.slug">
                <NuxtLink :href="`/services/${r.slug}`"
                  class="flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm text-slate-600 transition-colors hover:bg-parchment-100 hover:text-claret-700">
                  <Icon :name="r.icon" class="h-4 w-4 shrink-0 text-amber-600" />
                  {{ r.navLabel }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>

    <!-- ── Long-form editorial content ─────────────────────────────────────
         CMS content (Wagtail) when available; static SEO fallback always shown
         so every service page is substantive before staff have added CMS copy.
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

        <!-- CMS content from Wagtail -->
        <template v-else-if="hasCmsContent && cmsPage">
          <div v-if="cmsPage.reviewer" class="mb-8 flex items-center gap-2 text-sm text-slate-500">
            <Icon name="check-circle" class="h-4 w-4 text-amber-600" />
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

        <!-- Static fallback — always present until CMS copy is added -->
        <template v-else-if="service">
          <div class="grid gap-16 lg:grid-cols-[1fr_340px]">

            <!-- Left: editorial content -->
            <div class="prose prose-slate prose-lg max-w-none
                         prose-headings:font-serif prose-headings:font-bold
                         prose-a:text-amber-700 prose-strong:text-slate-900">

              <h2>Why {{ service.navLabel }} Matters for Students</h2>
              <p>{{ displayHero.sub }}</p>
              <p>
                Academic programmes are demanding. Between part-time work, family responsibilities, multiple modules,
                and tight submission deadlines, producing consistently high-quality written work is genuinely difficult.
                That's why thousands of students — from first-year undergraduates through doctoral candidates — rely on
                qualified subject specialists to support their academic writing.
              </p>

              <h2>What Sets Our Approach to {{ service.navLabel }} Apart</h2>
              <div class="not-prose my-6 grid gap-4 sm:grid-cols-2">
                <div v-for="(item, i) in service.includes" :key="item"
                  class="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-claret-600 text-xs font-bold text-white">{{ i + 1 }}</span>
                  <span class="text-sm leading-relaxed text-slate-700">{{ item }}</span>
                </div>
              </div>

              <h2>What You Receive</h2>
              <ul>
                <li v-for="item in service.delivers" :key="item">{{ item }}</li>
              </ul>

              <h2>Who This Service is For</h2>
              <p>{{ service.whoFor }}</p>

              <h2>We Understand the Challenges Students Face</h2>
              <p>
                Academic writing isn't just about putting words on a page — it's demonstrating subject mastery,
                constructing a coherent argument, citing sources correctly, and meeting the exact formatting
                requirements of your institution, all under deadline pressure. Our writers are subject specialists
                who have done this professionally. They write the way your marker expects — because they know
                academic standards from the inside.
              </p>

              <h3>Common Challenges We Solve</h3>
              <ul>
                <li><strong>Time pressure:</strong> Work, family, and multiple deadlines leave little room for long-form writing. We work to your deadline — as fast as 2 hours for shorter assignments.</li>
                <li><strong>Subject depth:</strong> Generic writers can produce surface-level work. Our writers are degree-holders in your subject — the difference shows in the quality of the argument.</li>
                <li><strong>Citation accuracy:</strong> APA, MLA, Harvard, Chicago — every style handled correctly, every time.</li>
                <li><strong>Source quality:</strong> We draw from peer-reviewed journals, academic databases, and credible primary sources — not outdated or unreliable material.</li>
              </ul>

              <h2>How to Order {{ service.navLabel }}</h2>
              <ol>
                <li><strong>Submit your brief:</strong> Complete the order form with your assignment details, word count, deadline, and any rubric or reading list requirements.</li>
                <li><strong>Get matched:</strong> We assign a writer whose subject background and degree level match your assignment.</li>
                <li><strong>Track progress:</strong> Message your writer directly through your dashboard, share additional files, and follow real-time progress.</li>
                <li><strong>Download and review:</strong> Receive your paper with a free Turnitin report. Request unlimited free revisions within the review window.</li>
              </ol>

            </div>

            <!-- Right: sticky conversion panel -->
            <div class="space-y-5 lg:sticky lg:top-24 lg:self-start">

              <!-- Price card -->
              <div class="rounded-2xl bg-claret-950 p-6 text-white">
                <div class="mb-4 flex items-start justify-between">
                  <div>
                    <p class="text-sm text-claret-300">Starting from</p>
                    <p class="text-4xl font-bold">${{ displayPrice }}<span class="text-lg font-normal text-claret-300">/page</span></p>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
                    <Icon :name="displayIcon" class="h-6 w-6 text-white" />
                  </div>
                </div>
                <NuxtLink to="/order"
                  class="block w-full rounded-xl bg-white py-3.5 text-center text-base font-bold text-claret-700 transition-colors hover:bg-parchment-100">
                  Place an order
                </NuxtLink>
                <NuxtLink to="/contact"
                  class="mt-2 block w-full rounded-xl border border-white/20 py-2.5 text-center text-sm font-semibold text-claret-200 transition-colors hover:bg-white/10">
                  Talk to us first
                </NuxtLink>
              </div>

              <!-- Quick FAQ -->
              <div class="rounded-2xl border border-slate-100 bg-white p-5">
                <p class="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">Common questions</p>
                <div class="divide-y divide-slate-100">
                  <div v-for="faq in [
                    { q: 'How fast can you deliver?', a: 'As fast as 2 hours for urgent orders up to 4 pages. Most papers are matched with a writer within minutes.' },
                    { q: 'Are your writers qualified?', a: 'Yes — every writer holds at minimum a Master\'s degree in their field. PhD writers are available for doctoral work.' },
                    { q: 'What if I need revisions?', a: 'Unlimited free revisions within the revision window — always handled by your original writer at no extra cost.' },
                  ]" :key="faq.q" class="py-3">
                    <p class="text-sm font-semibold text-slate-900">{{ faq.q }}</p>
                    <p class="mt-1 text-xs leading-relaxed text-slate-500">{{ faq.a }}</p>
                  </div>
                </div>
                <NuxtLink href="/contact" class="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-amber-700 hover:underline">
                  More questions → talk to our team
                </NuxtLink>
              </div>

              <!-- Testimonial -->
              <div class="rounded-2xl border border-amber-100 bg-parchment-100 p-5">
                <div class="mb-3 flex gap-0.5">
                  <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                  </svg>
                </div>
                <p class="text-sm italic leading-relaxed text-slate-700">"I had three submissions in one week during my dissertation semester. My writer knew the subject inside out — not just how to write. Got a distinction."</p>
                <p class="mt-3 text-xs font-semibold text-slate-600">— Master's Student, University of Manchester</p>
              </div>

            </div>
          </div>
        </template>

      </div>
    </div>

    <!-- Sample templates -->
    <ClientOnly>
      <ServiceTemplates
        v-if="service"
        :service-slug="service.slug"
        :service-name="service.navLabel"
      />
    </ClientOnly>

    <!-- Final CTA strip -->
    <div v-if="service" class="bg-claret-700 py-12 text-center">
      <h2 class="font-serif text-2xl font-bold text-white sm:text-3xl">
        Ready to get your {{ service.navLabel.toLowerCase() }} done?
      </h2>
      <p class="mt-3 text-claret-100">
        A qualified subject-specialist writer is ready. Grade guaranteed or full refund.
      </p>
      <NuxtLink to="/order" class="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-base font-bold text-claret-700 shadow-lg transition-colors hover:bg-parchment-100">
        Place an order — from ${{ displayPrice }}/page
      </NuxtLink>
    </div>

  </div>
</template>
