<script setup lang="ts">
const portal = usePortalStore()
const allServices = useCmsServiceList()
const { getAll: getAllStaticServices } = useServices()
// Split services into two columns for the mega-menu
const menuServicesA = computed(() => {
  const list = allServices.value.length ? allServices.value : getAllStaticServices()
  return list.slice(0, 5)
})
const menuServicesB = computed(() => {
  const list = allServices.value.length ? allServices.value : getAllStaticServices()
  return list.slice(5)
})

const orderPaths = [
  { id: 'paper',   label: 'Essays & Papers',       desc: 'Essays, research papers, term papers',     href: '/order?type=paper',   color: 'text-brand-600'  },
  { id: 'special', label: 'Dissertations',         desc: 'Proposal, chapters, methodology, defence', href: '/services/dissertations', color: 'text-rose-600' },
  { id: 'combo',   label: 'Admission Essays',      desc: 'Personal statements, scholarship essays',  href: '/services/admission-essays', color: 'text-amber-600' },
  { id: 'diagram', label: 'Proofreading',          desc: 'Grammar, structure, citations checked',    href: '/services/proofreading', color: 'text-teal-600' },
  { id: 'design',  label: 'Presentations',         desc: 'Slides, speaker notes, speech scripts',   href: '/services/presentations', color: 'text-violet-600' },
  { id: 'class',   label: 'Full Class Support',    desc: 'Entire course, whole semester',            href: '/class-support',      color: 'text-green-600'  },
]

const nav = [
  { label: 'How it works', href: '/how-it-works' },
  { label: 'Our writers',  href: '/writers' },
  { label: 'Pricing',      href: '/pricing' },
  { label: 'Blog',         href: '/blog' },
  { label: 'FAQ',          href: '/faq' },
  { label: 'Reviews',      href: '/reviews' },
  { label: 'Contact',      href: '/contact' },
]

const route = useRoute()
const mobileOpen   = ref(false)
const servicesOpen = ref(false)
let closeTimer: ReturnType<typeof setTimeout> | null = null

// Close mobile menu on route change
watch(() => route.path, () => { mobileOpen.value = false; servicesOpen.value = false })

function openServices()   { if (closeTimer) clearTimeout(closeTimer); servicesOpen.value = true }
function scheduleClose()  { closeTimer = setTimeout(() => { servicesOpen.value = false }, 120) }

// Inline SVG paths (avoids SSR issues with @lucide/vue in layout components)
const ORDER_SVG: Record<string, string> = {
  paper:   'M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2zM14 2v6h6M16 13H8M16 17H8M10 9H8',
  design:  'M3 3h18v18H3zM3 9h18M9 21V9',
  diagram: 'M6 3v12M18 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6M6 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6M18 9a9 9 0 0 1-9 9',
  combo:   'M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
  special: 'M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z',
  class:   'm4 6 8-4 8 4M18 10l4 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8l4-2M14 22v-4a2 2 0 0 0-4 0v4M18 5v17M6 5v17',
}
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-slate-100 bg-white/95 backdrop-blur-sm">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">

      <!-- Logo + rating badge -->
      <div class="flex items-center gap-3">
        <NuxtLink href="/" class="flex items-center gap-2">
          <img v-if="portal.logo" :src="portal.logo" :alt="portal.brandName" class="h-8 w-auto" />
          <span v-else class="flex items-center gap-2">
            <!-- EssayManiacs pen + spark mark -->
            <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <defs>
                <linearGradient id="em-mark" x1="2" y1="2" x2="28" y2="28" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#c4b5fd"/>
                  <stop offset="100%" stop-color="#6d28d9"/>
                </linearGradient>
              </defs>
              <!-- Rounded square background -->
              <rect x="1" y="1" width="28" height="28" rx="7" fill="url(#em-mark)"/>
              <!-- Pen / writing line -->
              <path d="M9 21l2-6 9-9a2 2 0 012.8 2.8L13 18l-6 2z" fill="white" fill-opacity="0.9"/>
              <path d="M18 7l3 3" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-opacity="0.6"/>
              <!-- Spark dot -->
              <circle cx="22" cy="8" r="1.5" fill="white" fill-opacity="0.85"/>
            </svg>
            <span class="text-[1.1rem] font-bold leading-none tracking-tight">
              <span class="text-slate-900">Essay</span><span class="text-brand-600">Maniacs</span>
            </span>
          </span>
        </NuxtLink>
        <div class="hidden items-center gap-1 sm:flex">
          <div class="flex gap-0.5">
            <svg v-for="i in 5" :key="i" class="h-3 w-3 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <span class="text-xs font-semibold text-slate-700">4.8</span>
          <span class="text-xs text-slate-400">/ 5</span>
        </div>
      </div>

      <!-- Desktop nav -->
      <nav class="hidden items-center gap-6 md:flex">

        <!-- Services mega-menu trigger -->
        <div
          class="relative"
          @mouseenter="openServices"
          @mouseleave="scheduleClose"
        >
          <button
            class="flex items-center gap-1 text-sm font-medium text-slate-600 transition-colors hover:text-brand-600"
            :class="servicesOpen ? 'text-brand-600' : ''"
            @click="servicesOpen = !servicesOpen"
          >
            Services
            <svg class="h-4 w-4 transition-transform duration-200" :class="servicesOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>

          <!-- Mega-menu dropdown -->
          <div
            v-if="servicesOpen"
            class="absolute left-1/2 top-full z-50 mt-2 w-[780px] -translate-x-1/2 rounded-2xl border border-slate-100 bg-white p-6 shadow-xl"
            @mouseenter="openServices"
            @mouseleave="scheduleClose"
          >
            <div class="grid grid-cols-4 gap-5">

              <!-- Col 1-2: Order types -->
              <div class="col-span-2">
                <p class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Place an order</p>
                <div class="grid grid-cols-2 gap-2">
                  <NuxtLink
                    v-for="op in orderPaths"
                    :key="op.id"
                    :href="op.href"
                    class="group flex items-start gap-3 rounded-xl border border-transparent p-2.5 transition-colors hover:border-slate-100 hover:bg-slate-50"
                    @click="servicesOpen = false"
                  >
                    <div class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border"
                      :class="op.color.replace('text-', 'border-').replace('600', '200') + ' ' + op.color.replace('text-', 'bg-').replace('600', '50')">
                      <svg class="h-4 w-4" :class="op.color" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="ORDER_SVG[op.id]" /></svg>
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-slate-800 transition-colors group-hover:text-brand-700">{{ op.label }}</p>
                      <p class="mt-0.5 text-xs leading-tight text-slate-400">{{ op.desc }}</p>
                    </div>
                  </NuxtLink>
                </div>
              </div>

              <!-- Col 3-4: Paper types in two mini-columns + CTA -->
              <div class="col-span-2 flex flex-col gap-3">
                <div class="grid grid-cols-2 gap-x-4">
                  <div>
                    <p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">Writing</p>
                    <ul class="space-y-0.5">
                      <li v-for="s in menuServicesA" :key="s.slug">
                        <NuxtLink :href="`/services/${s.slug}`"
                          class="block rounded-lg px-2 py-1.5 text-xs text-slate-600 transition-colors hover:bg-brand-50 hover:text-brand-700"
                          @click="servicesOpen = false">
                          {{ s.navLabel }}
                        </NuxtLink>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">Research & More</p>
                    <ul class="space-y-0.5">
                      <li v-for="s in menuServicesB" :key="s.slug">
                        <NuxtLink :href="`/services/${s.slug}`"
                          class="block rounded-lg px-2 py-1.5 text-xs text-slate-600 transition-colors hover:bg-brand-50 hover:text-brand-700"
                          @click="servicesOpen = false">
                          {{ s.navLabel }}
                        </NuxtLink>
                      </li>
                      <li>
                        <NuxtLink href="/services" class="block px-2 py-1.5 text-xs font-semibold text-brand-600 hover:underline" @click="servicesOpen = false">
                          All paper types →
                        </NuxtLink>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="rounded-xl bg-brand-900 p-3 text-center">
                  <p class="text-xs font-semibold text-white">Essays from $10/page</p>
                  <p class="mt-0.5 text-xs text-brand-300">4.8★ · 20,000+ orders delivered</p>
                  <NuxtLink to="/order" class="mt-2 block rounded-lg bg-white py-1.5 text-xs font-bold text-brand-700 transition-colors hover:bg-brand-50" @click="servicesOpen = false">
                    Place an order
                  </NuxtLink>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- Other nav items -->
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :href="item.href"
          class="text-sm font-medium text-slate-600 transition-colors hover:text-brand-600"
          active-class="text-brand-600"
        >
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Desktop right actions -->
      <div class="hidden items-center gap-3 md:flex">
        <div class="flex items-center gap-1.5 text-xs text-slate-500">
          <span class="inline-block h-1.5 w-1.5 rounded-full bg-green-500"></span>
          24/7 support
        </div>
        <NuxtLink to="/login" class="text-sm font-medium text-slate-600 hover:text-brand-600">
          Sign in
        </NuxtLink>
        <NuxtLink to="/order" class="btn-primary py-2 text-sm">
          Get started
        </NuxtLink>
      </div>

      <!-- Mobile hamburger -->
      <button class="md:hidden" @click="mobileOpen = !mobileOpen" aria-label="Toggle menu">
        <svg class="h-6 w-6 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileOpen" class="border-t border-slate-100 bg-white px-4 pb-4 md:hidden">
      <nav class="flex flex-col gap-1 pt-4">
        <p class="mt-2 mb-1 text-xs font-bold uppercase tracking-wider text-slate-400">Place an order</p>
        <NuxtLink
          v-for="op in orderPaths"
          :key="op.id"
          :href="op.href"
          class="flex items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-slate-700 hover:bg-brand-50"
          @click="mobileOpen = false"
        >
          <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border"
            :class="op.color.replace('text-','border-').replace('600','200') + ' ' + op.color.replace('text-','bg-').replace('600','50')">
            <svg class="h-3.5 w-3.5" :class="op.color" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path :d="ORDER_SVG[op.id]" />
            </svg>
          </div>
          {{ op.label }}
        </NuxtLink>
        <div class="my-2 border-t border-slate-100"></div>
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :href="item.href"
          class="rounded-lg px-2 py-2 text-sm font-medium text-slate-700 hover:bg-brand-50 hover:text-brand-600"
          @click="mobileOpen = false"
        >
          {{ item.label }}
        </NuxtLink>
        <div class="flex items-center gap-1.5 px-2 py-2 text-xs text-slate-400">
          <span class="inline-block h-1.5 w-1.5 rounded-full bg-green-500"></span>
          24/7 support available
        </div>
        <div class="flex flex-col gap-2 pt-1">
          <NuxtLink to="/order" class="btn-primary text-center" @click="mobileOpen = false">
            Place an order
          </NuxtLink>
          <NuxtLink
            to="/login"
            class="block rounded-lg border border-slate-200 py-2.5 text-center text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
            @click="mobileOpen = false"
          >
            Sign in
          </NuxtLink>
        </div>
      </nav>
    </div>
  </header>
</template>
