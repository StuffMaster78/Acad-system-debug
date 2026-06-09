<script setup lang="ts">
const portal = usePortalStore()
const year = new Date().getFullYear()
const { getAll } = useServices()
const allServices = getAll()

// Grouped service columns
const col2 = [
  { label: 'Nursing Essays',          href: '/services/nursing-essays' },
  { label: 'Care Plans',              href: '/services/care-plans' },
  { label: 'SOAP Notes',              href: '/services/soap-notes' },
  { label: 'Research Papers',         href: '/services/nursing-research-papers' },
  { label: 'Capstone Projects',       href: '/services/capstone-projects' },
  { label: 'Dissertations',           href: '/services/nursing-dissertations' },
]

const col3 = [
  { label: 'Case Studies',            href: '/services/nursing-case-studies' },
  { label: 'Concept Maps',            href: '/services/concept-maps' },
  { label: 'Coursework Help',         href: '/services/nursing-coursework' },
  { label: 'Shadow Health',           href: '/services/shadow-health' },
  { label: 'iHuman Patients',         href: '/services/ihuman-patients' },
  { label: 'Online Class Help',       href: '/services/online-nursing-classes' },
]

const col4 = [
  { label: 'BSN Writing',             href: '/services/bsn-writing' },
  { label: 'MSN Writing Help',        href: '/services/msn-help' },
  { label: 'APA Nursing Papers',      href: '/services/apa-nursing-papers' },
  { label: 'Nursing Reports',         href: '/services/nursing-report' },
  { label: 'Nursing Presentations',   href: '/services/nursing-presentation' },
  { label: 'All services →',          href: '/services' },
]

const col5 = [
  { label: 'Place an Order',          href: '/order' },
  { label: 'Custom Quote',            href: '/quote' },
  { label: 'Class Support',           href: '/class-support' },
  { label: 'Pricing',                 href: '/pricing' },
  { label: 'About Us',                href: '/about' },
  { label: 'Contact',                 href: '/contact' },
]

const col6 = [
  { label: 'Care Plan Guide',         href: '/blog/nursing-care-plan-guide' },
  { label: 'SOAP Note Guide',         href: '/blog/soap-notes-guide-for-nursing-students' },
  { label: 'APA 7th for Nursing',     href: '/blog/apa-7th-edition-guide-nursing-papers' },
  { label: 'Shadow Health Tips',      href: '/blog/tips-for-succeeding-in-shadow-health-assessments' },
  { label: 'iHuman Tips',             href: '/blog/ihuman-tips-help-and-tricks' },
  { label: 'Nursing Blog →',          href: '/blog' },
]

const col7 = [
  { label: 'Privacy Policy',          href: '/privacy' },
  { label: 'Terms of Use',            href: '/terms' },
  { label: 'Refund Policy',           href: '/refunds' },
  { label: 'Apply as Writer',         href: '/apply' },
  { label: 'Our Authors',             href: '/authors' },
]

// Social icons
const SOCIAL_ICONS: Record<string, string> = {
  twitter:   `<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.911-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>`,
  instagram: `<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162S8.597 18.163 12 18.163s6.162-2.759 6.162-6.162S15.403 5.838 12 5.838zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>`,
  facebook:  `<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>`,
  youtube:   `<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>`,
  tiktok:    `<path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>`,
  linkedin:  `<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>`,
}

const social = computed(() => portal.socialLinks)
</script>

<template>
  <footer class="border-t border-slate-200 bg-slate-900 text-slate-300">

    <!-- Trust strip -->
    <div class="border-b border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <div class="flex items-center gap-2">
          <div class="flex gap-0.5">
            <svg v-for="i in 5" :key="i" class="h-4 w-4 text-[#00b67a]" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <span class="text-sm font-semibold text-white">4.98/5</span>
          <span class="text-sm text-slate-400">on Trustpilot</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <div class="flex items-center gap-1.5 text-sm">
          <span class="font-bold text-green-400">✓</span>
          <span><strong class="text-white">9,800+</strong> nursing papers delivered</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <div class="flex items-center gap-1.5 text-sm">
          <span class="font-bold text-green-400">✓</span>
          <span>Grade or money back</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <div class="flex items-center gap-1.5 text-sm">
          <span class="font-bold text-green-400">✓</span>
          <span>BSN, MSN &amp; DNP writers · zero AI</span>
        </div>
      </div>
    </div>

    <!-- Main 6-column grid -->
    <div class="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
      <!-- 8-column compact grid: brand + 7 link columns -->
      <div class="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-4 lg:grid-cols-8">

        <!-- Col 1: Brand (spans 2 on lg) -->
        <div class="col-span-2 sm:col-span-2 lg:col-span-2">
          <NuxtLink href="/" class="font-serif text-lg font-bold text-white">{{ portal.brandName }}</NuxtLink>
          <p class="mt-2 text-xs text-slate-400 leading-relaxed max-w-[180px]">Expert nursing papers by BSN, MSN &amp; DNP nurses.</p>
          <div v-if="social.length" class="mt-4 flex flex-wrap gap-1.5">
            <a v-for="s in social" :key="s.name" :href="s.href" :aria-label="s.name" target="_blank" rel="noreferrer"
              class="flex h-6 w-6 items-center justify-center rounded-md bg-slate-800 text-slate-400 hover:bg-brand-700 hover:text-white transition-colors">
              <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 24 24"><g v-html="SOCIAL_ICONS[s.icon] ?? ''" /></svg>
            </a>
          </div>
          <div class="mt-3 flex items-center gap-1.5 text-xs text-slate-600">
            <span class="h-1.5 w-1.5 rounded-full bg-green-500 inline-block" /> 24/7 support
          </div>
          <div class="mt-3 rounded-lg bg-slate-800 px-3 py-2">
            <p class="text-xs text-slate-500 leading-snug">Model papers for academic reference only.</p>
          </div>
        </div>

        <!-- Col 2 -->
        <div>
          <h4 class="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Writing</h4>
          <ul class="space-y-1.5">
            <li v-for="s in col2" :key="s.href">
              <NuxtLink :href="s.href" class="text-xs text-slate-400 hover:text-white transition-colors">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Col 3 -->
        <div>
          <h4 class="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Clinical</h4>
          <ul class="space-y-1.5">
            <li v-for="s in col3" :key="s.href">
              <NuxtLink :href="s.href" class="text-xs text-slate-400 hover:text-white transition-colors">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Col 4 -->
        <div>
          <h4 class="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Specialty</h4>
          <ul class="space-y-1.5">
            <li v-for="s in col4" :key="s.href">
              <NuxtLink :href="s.href"
                class="text-xs transition-colors"
                :class="s.label.endsWith('→') ? 'font-semibold text-brand-400 hover:text-brand-300' : 'text-slate-400 hover:text-white'">
                {{ s.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Col 5 -->
        <div>
          <h4 class="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Quick Links</h4>
          <ul class="space-y-1.5">
            <li v-for="s in col5" :key="s.href">
              <NuxtLink :href="s.href" class="text-xs text-slate-400 hover:text-white transition-colors">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Col 6 -->
        <div>
          <h4 class="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Resources</h4>
          <ul class="space-y-1.5">
            <li v-for="s in col6" :key="s.href">
              <NuxtLink :href="s.href"
                class="text-xs transition-colors"
                :class="s.label.endsWith('→') ? 'font-semibold text-brand-400 hover:text-brand-300' : 'text-slate-400 hover:text-white'">
                {{ s.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Col 7 -->
        <div>
          <h4 class="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Company</h4>
          <ul class="space-y-1.5">
            <li v-for="s in col7" :key="s.href">
              <NuxtLink :href="s.href" class="text-xs text-slate-400 hover:text-white transition-colors">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

      </div>
    </div>

    <!-- Bottom bar -->
    <div class="border-t border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-5 sm:px-6 lg:px-8">
        <p class="text-xs text-slate-500">&copy; {{ year }} {{ portal.brandName }}. All rights reserved.</p>
        <p class="text-xs text-slate-600 max-w-xl text-center leading-relaxed">
          {{ portal.disclosure?.text }}
        </p>
      </div>
    </div>

  </footer>
</template>
