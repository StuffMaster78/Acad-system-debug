<script setup lang="ts">
const portal = usePortalStore()
const allServices = useCmsServiceList()
const { getAll: getAllStaticServices } = useServices()
const menuServicesA = computed(() => {
  const list = allServices.value.length ? allServices.value : getAllStaticServices()
  return list.slice(0, 5)
})
const menuServicesB = computed(() => {
  const list = allServices.value.length ? allServices.value : getAllStaticServices()
  return list.slice(5)
})

const orderPaths = [
  { id: 'paper',   label: 'Papers & Essays',    desc: 'Research papers, essays, dissertations', href: '/order?type=paper',   icon: 'M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2zM14 2v6h6M16 13H8M16 17H8M10 9H8' },
  { id: 'design',  label: 'Design',             desc: 'Slides, infographics, posters',          href: '/order?type=design',  icon: 'M3 3h18v18H3zM3 9h18M9 21V9' },
  { id: 'diagram', label: 'Diagrams & Charts',  desc: 'Flowcharts, ER diagrams, mind maps',     href: '/order?type=diagram', icon: 'M6 3v12M18 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6M6 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6M18 9a9 9 0 0 1-9 9' },
  { id: 'combo',   label: 'Combo Order',        desc: 'Paper + design/diagram together',        href: '/order?type=combo',   icon: 'M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' },
  { id: 'special', label: 'Special Project',    desc: 'Custom quote — nursing sim, coding',     href: '/quote',              icon: 'M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z' },
  { id: 'class',   label: 'Full Class Support', desc: 'Entire course, whole semester',          href: '/class-support',      icon: 'm4 6 8-4 8 4M18 10l4 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8l4-2M14 22v-4a2 2 0 0 0-4 0v4M18 5v17M6 5v17' },
]

const nav = [
  { label: 'How it works', href: '/how-it-works' },
  { label: 'Researchers',  href: '/writers' },
  { label: 'Pricing',      href: '/pricing' },
  { label: 'Blog',         href: '/blog' },
  { label: 'Reviews',      href: '/reviews' },
  { label: 'FAQ',          href: '/faq' },
]

const route = useRoute()
const mobileOpen   = ref(false)
const servicesOpen = ref(false)
let closeTimer: ReturnType<typeof setTimeout> | null = null

watch(() => route.path, () => { mobileOpen.value = false; servicesOpen.value = false })

function openServices()  { if (closeTimer) clearTimeout(closeTimer); servicesOpen.value = true }
function scheduleClose() { closeTimer = setTimeout(() => { servicesOpen.value = false }, 120) }
</script>

<template>
  <header class="relative bg-claret-900">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">

      <!-- Logo -->
      <div class="flex items-center gap-3">
        <NuxtLink href="/" class="flex items-center gap-2.5">
          <img v-if="portal.logo" :src="portal.logo" :alt="portal.brandName" class="h-8 w-auto" />
          <span v-else class="flex items-center gap-2.5">
            <!-- RPM mark — document with amber rule -->
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M4 2h13l7 7v17a2 2 0 01-2 2H4a2 2 0 01-2-2V4a2 2 0 012-2z" fill="#7B2241"/>
              <path d="M17 2v5a2 2 0 002 2h5" fill="none" stroke="white" stroke-width="1" stroke-opacity="0.3"/>
              <rect x="6" y="12" width="8"  height="1.5" rx="0.75" fill="white" fill-opacity="0.9"/>
              <rect x="6" y="16" width="12" height="1.5" rx="0.75" fill="white" fill-opacity="0.6"/>
              <rect x="6" y="20" width="6"  height="1.5" rx="0.75" fill="#C8792A"/>
            </svg>
            <span class="text-[1.05rem] font-bold leading-none tracking-tight text-white">
              Research<span class="text-amber-400">Paper</span>Mate
            </span>
          </span>
        </NuxtLink>
      </div>

      <!-- Desktop nav -->
      <nav class="hidden items-center gap-5 md:flex">
        <!-- Services mega-menu -->
        <div class="relative" @mouseenter="openServices" @mouseleave="scheduleClose">
          <button
            class="flex items-center gap-1 rounded-sm text-sm font-medium text-white/80 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400"
            :class="servicesOpen ? 'text-white' : ''"
            :aria-expanded="servicesOpen"
            aria-haspopup="true"
            @click="servicesOpen = !servicesOpen"
          >
            Services
            <svg class="h-4 w-4 transition-transform" :class="servicesOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- Mega dropdown — white on claret header -->
          <div
            v-if="servicesOpen"
            class="absolute left-1/2 top-full z-50 mt-3 w-[760px] -translate-x-1/2 rounded-2xl border border-parchment-300 bg-parchment-100 p-6 shadow-2xl"
            @mouseenter="openServices"
            @mouseleave="scheduleClose"
          >
            <div class="grid grid-cols-4 gap-5">
              <div class="col-span-2">
                <p class="mb-3 text-[10px] font-bold uppercase tracking-widest text-ink-muted">Place an order</p>
                <div class="grid grid-cols-2 gap-1.5">
                  <NuxtLink
                    v-for="op in orderPaths"
                    :key="op.id"
                    :href="op.href"
                    class="group flex items-start gap-2.5 rounded-xl border border-transparent p-2.5 transition-colors hover:border-parchment-300 hover:bg-white"
                    @click="servicesOpen = false"
                  >
                    <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-claret-100 text-claret-900">
                      <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path :d="op.icon"/>
                      </svg>
                    </div>
                    <div class="min-w-0">
                      <p class="text-xs font-semibold text-ink-DEFAULT transition-colors group-hover:text-claret-900">{{ op.label }}</p>
                      <p class="mt-0.5 text-[10px] leading-tight text-ink-muted">{{ op.desc }}</p>
                    </div>
                  </NuxtLink>
                </div>
              </div>

              <div class="col-span-2 flex flex-col gap-3">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <p class="mb-2 text-[10px] font-bold uppercase tracking-widest text-ink-muted">Writing</p>
                    <ul class="space-y-0.5">
                      <li v-for="s in menuServicesA" :key="s.slug">
                        <NuxtLink :href="`/services/${s.slug}`"
                          class="block rounded-lg px-2 py-1.5 text-xs text-ink-secondary transition-colors hover:bg-white hover:text-claret-900"
                          @click="servicesOpen = false">
                          {{ s.navLabel }}
                        </NuxtLink>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <p class="mb-2 text-[10px] font-bold uppercase tracking-widest text-ink-muted">Research & More</p>
                    <ul class="space-y-0.5">
                      <li v-for="s in menuServicesB" :key="s.slug">
                        <NuxtLink :href="`/services/${s.slug}`"
                          class="block rounded-lg px-2 py-1.5 text-xs text-ink-secondary transition-colors hover:bg-white hover:text-claret-900"
                          @click="servicesOpen = false">
                          {{ s.navLabel }}
                        </NuxtLink>
                      </li>
                      <li>
                        <NuxtLink href="/services" class="block px-2 py-1.5 text-xs font-semibold text-claret-800 hover:underline" @click="servicesOpen = false">
                          All paper types →
                        </NuxtLink>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="rounded-xl bg-claret-900 p-3.5 text-center">
                  <p class="text-xs font-semibold text-white">Start from $15/page</p>
                  <p class="mt-0.5 text-xs text-claret-300">4.8★ · 14,700+ orders delivered</p>
                  <NuxtLink to="/order" class="mt-2.5 block rounded-lg bg-amber-500 py-2 text-xs font-bold text-white transition-colors hover:bg-amber-600" @click="servicesOpen = false">
                    Place an order
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>
        </div>

        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :href="item.href"
          class="rounded-sm text-sm font-medium text-white/80 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400"
          active-class="text-white"
        >
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Desktop CTAs — split capsule, claret flavour -->
      <div class="hidden items-center gap-3 md:flex">
        <NuxtLink to="/login" class="rounded-sm text-sm font-medium text-white/70 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400">
          Sign in
        </NuxtLink>
        <NuxtLink
          to="/order"
          class="inline-flex h-9 items-center gap-2 rounded-lg bg-amber-600 px-4 text-sm font-bold text-white shadow-sm transition-colors hover:bg-amber-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
        >
          Place order
          <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
        </NuxtLink>
      </div>

      <!-- Mobile hamburger -->
      <button class="md:hidden rounded-sm text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400" :aria-expanded="mobileOpen" aria-label="Toggle menu" @click="mobileOpen = !mobileOpen">
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileOpen" class="border-t border-claret-800 bg-claret-950 px-4 pb-5 md:hidden">
      <nav class="flex flex-col gap-1 pt-4">
        <p class="mb-1 text-[10px] font-bold uppercase tracking-widest text-claret-400">Place an order</p>
        <NuxtLink
          v-for="op in orderPaths"
          :key="op.id"
          :href="op.href"
          class="flex items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-white/80 hover:bg-claret-800 hover:text-white"
          @click="mobileOpen = false"
        >
          <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-claret-800">
            <svg class="h-3.5 w-3.5 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path :d="op.icon"/>
            </svg>
          </div>
          {{ op.label }}
        </NuxtLink>
        <div class="my-2 border-t border-claret-800"/>
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :href="item.href"
          class="rounded-lg px-2 py-2 text-sm font-medium text-white/80 hover:bg-claret-800 hover:text-white"
          @click="mobileOpen = false"
        >
          {{ item.label }}
        </NuxtLink>
        <div class="flex flex-col gap-2 pt-3">
          <NuxtLink to="/order" class="block rounded-lg bg-amber-600 py-3 text-center text-sm font-bold text-white hover:bg-amber-500" @click="mobileOpen = false">
            Place an order
          </NuxtLink>
          <NuxtLink to="/login" class="block rounded-lg border border-claret-700 py-2.5 text-center text-sm font-semibold text-white/70 hover:bg-claret-800" @click="mobileOpen = false">
            Sign in
          </NuxtLink>
        </div>
      </nav>
    </div>
  </header>
</template>
