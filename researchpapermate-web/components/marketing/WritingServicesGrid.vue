<script setup lang="ts">
const { getAll } = useServices()
const cmsServices = useCmsServiceList()

const services = computed(() => {
  const cms = cmsServices.value
  const stat = getAll()
  if (cms.length) {
    return cms.map(s => {
      const local = stat.find(l => l.slug === s.slug)
      return { slug: s.slug, navLabel: s.navLabel, icon: local?.icon ?? 'file-text', priceFrom: s.priceFrom }
    })
  }
  return stat.map(s => ({ slug: s.slug, navLabel: s.navLabel, icon: s.icon, priceFrom: s.priceFrom }))
})

const serviceLinks = [
  { label: 'Research Paper Writing Help',      href: '/research-papers' },
  { label: 'Custom Essay Writing Service',     href: '/essays' },
  { label: 'Dissertation Writing Help',        href: '/dissertations' },
  { label: 'Thesis Writing Service',           href: '/dissertations' },
  { label: 'Case Study Writing Help',          href: '/case-studies' },
  { label: 'Lab Report Writing Service',       href: '/lab-reports' },
  { label: 'Data Analysis & Statistics',       href: '/data-analysis' },
  { label: 'Literature Review Writing',        href: '/literature-reviews' },
  { label: 'Coursework & Assignment Help',     href: '/coursework' },
  { label: 'Presentation Writing Help',        href: '/presentations' },
  { label: 'Argumentative Essay Help',         href: '/essays' },
  { label: 'Analytical Essay Writing',         href: '/essays' },
  { label: 'Reflective Essay Service',         href: '/essays' },
  { label: 'Term Paper Writing Help',          href: '/research-papers' },
  { label: 'Capstone Project Help',            href: '/dissertations' },
  { label: 'Annotated Bibliography Help',      href: '/literature-reviews' },
  { label: 'Scholarship Essay Writing',        href: '/essays' },
  { label: 'Business Case Study Help',         href: '/case-studies' },
  { label: 'SPSS & R Data Analysis',           href: '/data-analysis' },
  { label: 'Systematic Literature Review',     href: '/literature-reviews' },
  { label: 'PowerPoint Presentation Help',     href: '/presentations' },
  { label: 'Compare & Contrast Essay',         href: '/essays' },
  { label: 'Science Lab Report Help',          href: '/lab-reports' },
  { label: 'Nursing Essay Writing',            href: '/essays' },
]
</script>

<template>
  <section class="bg-slate-50 py-16" id="writing-services">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- Section header -->
      <div class="mb-12 text-center">
        <span class="mb-4 inline-block rounded-full bg-brand-100 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-brand-700">
          What We Do
        </span>
        <h2 class="section-heading">The Writing Services We Offer</h2>
        <p class="section-sub mx-auto max-w-2xl">
          Every academic assignment type, covered by subject-specialist writers with Master's and PhD credentials.
          Click any service for a dedicated page with full details and pricing.
        </p>
      </div>

      <!-- Services grid -->
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
          <span class="text-sm font-medium leading-tight text-slate-700 transition-colors group-hover:text-brand-700">
            {{ item.label }}
          </span>
          <Icon name="chevron-right" class="ml-auto h-3.5 w-3.5 shrink-0 text-slate-300 transition-colors group-hover:text-brand-500" />
        </NuxtLink>
      </div>

      <p class="mt-4 text-center text-xs text-slate-400">
        Additional services can be added in the Wagtail admin → Service Pages.
        <NuxtLink href="/services" class="ml-1 font-medium text-brand-500 hover:underline">View all →</NuxtLink>
      </p>

      <!-- Calculator + CTA -->
      <div class="mt-14 grid items-start gap-10 lg:grid-cols-2">

        <!-- Calculator -->
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 class="mb-1 font-serif text-xl font-bold text-slate-900">Get an instant price</h3>
          <p class="mb-6 text-sm text-slate-500">Select your paper type, level, and deadline — see your price in seconds.</p>
          <ClientOnly>
            <OrderCalculator />
            <template #fallback>
              <div class="h-56 animate-pulse rounded-xl bg-slate-100" />
            </template>
          </ClientOnly>
        </div>

        <!-- CTA panel -->
        <div class="flex h-full flex-col justify-between rounded-2xl bg-brand-900 p-8 text-white">
          <div>
            <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10">
              <Icon name="graduation-cap" class="h-7 w-7 text-white" />
            </div>
            <h3 class="font-serif text-2xl font-bold">Ready to get started?</h3>
            <p class="mt-3 leading-relaxed text-brand-200">
              Tell us your brief and we'll match you with a subject-specialist writer. Fast, confidential, grade-guaranteed.
            </p>
            <ul class="mt-6 space-y-2.5 text-sm text-brand-200">
              <li class="flex items-center gap-2.5">
                <Icon name="check-circle" class="h-4 w-4 shrink-0 text-green-400" />
                Master's and PhD writers matched to your subject
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
                Delivery as fast as 2 hours for urgent orders
              </li>
            </ul>
          </div>

          <div class="mt-8 flex flex-col gap-3">
            <NuxtLink to="/order" class="block rounded-xl bg-white py-3.5 text-center text-base font-bold text-brand-700 transition-colors hover:bg-brand-50">
              Place an order — from $15/page
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
