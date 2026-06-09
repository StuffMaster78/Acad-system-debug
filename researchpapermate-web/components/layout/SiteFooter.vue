<script setup lang="ts">
const portal = usePortalStore()
const year = new Date().getFullYear()

// CMS-driven — new service pages created in Wagtail appear automatically
const cmsServices = useCmsServiceList()
const serviceLinks = computed(() =>
  cmsServices.value.slice(0, 8).map(s => ({
    label: s.navLabel,
    href: `/services/${s.slug}`,
  }))
)

const companyLinks = [
  { label: 'About',           href: '/about' },
  { label: 'Blog',            href: '/blog' },
  { label: 'Pricing',         href: '/pricing' },
  { label: 'Contact',         href: '/contact' },
  { label: 'Apply as Writer', href: '/apply' },
]

const legalLinks = [
  { label: 'Privacy Policy', href: '/privacy' },
  { label: 'Terms of Use',   href: '/terms' },
  { label: 'Refund Policy',  href: '/refunds' },
]

const social = [
  {
    name: 'Twitter / X',
    href: '#',
    icon: `<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.911-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>`,
  },
  {
    name: 'Instagram',
    href: '#',
    icon: `<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162S8.597 18.163 12 18.163s6.162-2.759 6.162-6.162S15.403 5.838 12 5.838zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>`,
  },
  {
    name: 'Facebook',
    href: '#',
    icon: `<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>`,
  },
  {
    name: 'YouTube',
    href: '#',
    icon: `<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>`,
  },
]

const trustItems = [
  { stars: true,  text: '4.8/5 on Trustpilot' },
  { icon: '✓',    text: '14,700+ papers delivered' },
  { icon: '✓',    text: 'Grade or money back' },
  { icon: '✓',    text: '100% human-written' },
]
</script>

<template>
  <footer class="border-t border-slate-200 bg-slate-900 text-slate-300">

    <!-- Trust strip -->
    <div class="border-b border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <!-- Stars + Trustpilot -->
        <div class="flex items-center gap-2">
          <div class="flex gap-0.5">
            <svg v-for="i in 5" :key="i" class="h-4 w-4 text-[#00b67a]" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <span class="text-sm font-semibold text-white">4.8/5</span>
          <span class="text-sm text-slate-400">on Trustpilot</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <div class="flex items-center gap-1.5 text-sm">
          <span class="font-bold text-green-400">✓</span>
          <span><strong class="text-white">14,700+</strong> papers delivered</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <div class="flex items-center gap-1.5 text-sm">
          <span class="font-bold text-green-400">✓</span>
          <span>Grade or money back</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <div class="flex items-center gap-1.5 text-sm">
          <span class="font-bold text-green-400">✓</span>
          <span>100% human-written · zero AI</span>
        </div>
      </div>
    </div>

    <!-- Main footer grid -->
    <div class="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
      <div class="grid grid-cols-2 gap-10 md:grid-cols-4 lg:grid-cols-[2fr_1fr_1fr_1fr]">

        <!-- Brand column -->
        <div class="col-span-2 md:col-span-1">
          <span class="font-serif text-xl font-bold text-white">{{ portal.brandName }}</span>
          <p class="mt-3 text-sm text-slate-400 leading-relaxed">{{ portal.tagline }}</p>

          <!-- Social icons -->
          <div class="mt-6 flex gap-3">
            <a
              v-for="s in social"
              :key="s.name"
              :href="s.href"
              :aria-label="s.name"
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800 text-slate-400 transition-colors hover:bg-brand-700 hover:text-white"
            >
              <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <!-- eslint-disable-next-line vue/no-v-html -->
                <g v-html="s.icon" />
              </svg>
            </a>
          </div>

          <!-- 24/7 indicator -->
          <div class="mt-5 flex items-center gap-2 text-sm text-slate-400">
            <span class="inline-block h-2 w-2 rounded-full bg-green-500"></span>
            24/7 support available
          </div>
        </div>

        <!-- Services links -->
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-500">Services</h4>
          <ul class="mt-4 space-y-3">
            <li v-for="link in serviceLinks" :key="link.href">
              <NuxtLink :href="link.href" class="text-sm text-slate-400 transition-colors hover:text-white">
                {{ link.label }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink href="/services" class="text-xs font-medium text-brand-400 hover:text-brand-300">
                View all services →
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Company links -->
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-500">Company</h4>
          <ul class="mt-4 space-y-3">
            <li v-for="link in companyLinks" :key="link.href">
              <NuxtLink :href="link.href" class="text-sm text-slate-400 transition-colors hover:text-white">
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Legal links -->
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-500">Legal</h4>
          <ul class="mt-4 space-y-3">
            <li v-for="link in legalLinks" :key="link.href">
              <NuxtLink :href="link.href" class="text-sm text-slate-400 transition-colors hover:text-white">
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

      </div>
    </div>

    <!-- Bottom bar -->
    <div class="border-t border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-6 sm:px-6 lg:px-8">
        <p class="text-xs text-slate-500">
          &copy; {{ year }} {{ portal.brandName }}. All rights reserved.
        </p>
        <p class="text-xs text-slate-600 max-w-xl text-center leading-relaxed">
          {{ portal.disclosure?.text }}
        </p>
      </div>
    </div>

  </footer>
</template>
