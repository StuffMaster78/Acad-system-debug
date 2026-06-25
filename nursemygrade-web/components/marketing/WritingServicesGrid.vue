<script setup lang="ts">
// Static list used as fallback; Wagtail CMS enriches in production
const { getAll } = useServices()
const cmsServices = useCmsServiceList()

// Merge: prefer CMS slugs if available, pad with static list so page always has content
const services = computed(() => {
  const cms = cmsServices.value
  const stat = getAll()
  if (cms.length) {
    // Return CMS list, enriched with static icon/priceFrom
    return cms.map(s => {
      const local = stat.find(l => l.slug === s.slug)
      return { slug: s.slug, navLabel: s.navLabel, icon: local?.icon ?? 'file-text', priceFrom: s.priceFrom }
    })
  }
  return stat.map(s => ({ slug: s.slug, navLabel: s.navLabel, icon: s.icon, priceFrom: s.priceFrom }))
})

// All 24 marketing service links — maps live-site labels to our slugs
const serviceLinks = [
  { label: 'Capstone Project Writing Help',       href: '/capstone-projects' },
  { label: 'Online Nursing Essay Writing Help',   href: '/nursing-essays' },
  { label: 'Online Nursing Papers Help',          href: '/buy-nursing-papers' },
  { label: 'SOAP Medical Note Writer',            href: '/soap-notes' },
  { label: 'Shadow Health Help & Answers',        href: '/shadow-health' },
  { label: 'Nursing Classes Help',                href: '/online-nursing-classes' },
  { label: 'BSN Writing Services',                href: '/bsn-writing' },
  { label: 'Nursing Research Paper Writing',      href: '/nursing-research-papers' },
  { label: 'Nursing Report Writing Services',     href: '/nursing-report' },
  { label: 'Buy a Nursing Presentation (PPT)',    href: '/nursing-presentation' },
  { label: 'Nursing Thesis Writing Service',      href: '/nursing-dissertations' },
  { label: 'MSN Writing Help',                    href: '/msn-help' },
  { label: 'APA Nursing Papers',                  href: '/apa-nursing-papers' },
  { label: 'Write My Concept Map',                href: '/concept-maps' },
  { label: 'Nursing Assignments Help',            href: '/nursing-coursework' },
  { label: 'Medical Paper Writing Services',      href: '/medical-paper-writing' },
  { label: 'Buy Nursing Papers for Sale',         href: '/nursing-homework' },
  { label: 'Nursing Coursework Help Online',      href: '/nursing-coursework' },
  { label: 'Nursing Care Plan Writing',           href: '/care-plans' },
  { label: 'Nursing Homework Help Online',        href: '/nursing-homework' },
  { label: 'Nursing Dissertation Help Online',    href: '/nursing-dissertations' },
  { label: 'Do My Nursing Case Study',            href: '/nursing-case-studies' },
  { label: 'Health & Medical Writers',            href: '/health-medical-writers' },
  { label: 'Postgrad Nursing Help',               href: '/postgrad-nursing' },
]
</script>

<template>
  <section class="bg-slate-50 py-16" id="writing-services">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- Section header -->
      <div class="text-center mb-12">
        <span class="inline-block rounded-full bg-brand-100 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-brand-700 mb-4">
          What We Do
        </span>
        <h2 class="section-heading">The Writing Services We Offer</h2>
        <p class="section-sub max-w-2xl mx-auto">
          Every nursing assignment type, covered by BSN, MSN, and DNP nurses.
          Click any service for a dedicated page with full details and pricing.
        </p>
      </div>

      <!-- Services grid — scrollable on mobile, 3-col on desktop -->
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <NuxtLink
          v-for="item in serviceLinks"
          :key="item.label"
          :href="item.href"
          class="group flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3.5 transition-all hover:border-brand-300 hover:bg-brand-50 hover:shadow-sm"
        >
          <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-100 transition-colors group-hover:bg-brand-600">
            <Icon name="pen-line" class="h-4 w-4 text-brand-600 transition-colors group-hover:text-white" />
          </span>
          <span class="text-sm font-medium text-slate-700 group-hover:text-brand-700 transition-colors leading-tight">
            {{ item.label }}
          </span>
          <Icon name="chevron-right" class="ml-auto h-3.5 w-3.5 shrink-0 text-slate-300 transition-colors group-hover:text-brand-500" />
        </NuxtLink>
      </div>

      <!-- Wagtail CMS note — only visible in dev -->
      <p class="mt-4 text-center text-xs text-slate-400">
        Additional services can be added by your content team in the Wagtail admin → Service Pages.
        <NuxtLink href="/services" class="font-medium text-brand-500 hover:underline ml-1">View all →</NuxtLink>
      </p>

      <!-- Calculator + CTA -->
      <div class="mt-14 grid gap-10 lg:grid-cols-2 items-start">

        <!-- Calculator -->
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 class="font-serif text-xl font-bold text-slate-900 mb-1">Get an instant price</h3>
          <p class="text-sm text-slate-500 mb-6">Select your paper type, level, and deadline — see your price in seconds.</p>
          <ClientOnly>
            <MultiStepOrderForm />
            <template #fallback>
              <div class="h-56 animate-pulse rounded-xl bg-slate-100" />
            </template>
          </ClientOnly>
        </div>

        <!-- CTA panel -->
        <div class="rounded-2xl bg-brand-900 p-8 text-white flex flex-col justify-between h-full">
          <div>
            <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10">
              <Icon name="stethoscope" class="h-7 w-7 text-white" />
            </div>
            <h3 class="font-serif text-2xl font-bold">Ready to get started?</h3>
            <p class="mt-3 text-brand-200 leading-relaxed">
              Tell us your assignment and we'll match you with a BSN, MSN, or DNP nurse who specialises in your subject. Fast, confidential, grade-guaranteed.
            </p>
            <ul class="mt-6 space-y-2.5 text-sm text-brand-200">
              <li class="flex items-center gap-2.5">
                <Icon name="check-circle" class="h-4 w-4 shrink-0 text-green-400" />
                Written by a credentialed nurse — not a generic writer
              </li>
              <li class="flex items-center gap-2.5">
                <Icon name="check-circle" class="h-4 w-4 shrink-0 text-green-400" />
                Free Turnitin plagiarism report with every order
              </li>
              <li class="flex items-center gap-2.5">
                <Icon name="check-circle" class="h-4 w-4 shrink-0 text-green-400" />
                Grade or money back — no questions asked
              </li>
              <li class="flex items-center gap-2.5">
                <Icon name="check-circle" class="h-4 w-4 shrink-0 text-green-400" />
                Delivery as fast as 3 hours for urgent orders
              </li>
            </ul>
          </div>

          <div class="mt-8 flex flex-col gap-3">
            <NuxtLink to="/order" class="block rounded-xl bg-white py-3.5 text-center text-base font-bold text-brand-700 transition-colors hover:bg-brand-50">
              Place an order — from $24/page
            </NuxtLink>
            <NuxtLink to="/contact" class="block rounded-xl border border-white/20 py-3 text-center text-sm font-semibold text-brand-200 transition-colors hover:bg-white/10">
              Talk to us first →
            </NuxtLink>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
