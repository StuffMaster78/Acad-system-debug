<script setup lang="ts">
import { Menu, X } from '@lucide/vue'

const app    = useAppUrl()
const route  = useRoute()
const mobileOpen   = ref(false)
const servicesOpen = ref(false)
const scrolled     = ref(false)
let closeTimer: ReturnType<typeof setTimeout> | null = null

const isHome = computed(() => route.path === '/')

const headerClass = computed(() => 'bg-white/95 border-b border-slate-200 backdrop-blur-sm shadow-sm')
const logoClass   = computed(() => 'text-ink')
const linkClass   = computed(() => 'text-graphite hover:text-ink')

onMounted(() => {
  window.addEventListener('scroll', () => { scrolled.value = window.scrollY > 60 }, { passive: true })
})

watch(() => route.path, () => { mobileOpen.value = false; servicesOpen.value = false })

function openServices()  { if (closeTimer) clearTimeout(closeTimer); servicesOpen.value = true }
function scheduleClose() { closeTimer = setTimeout(() => { servicesOpen.value = false }, 130) }

// ── Featured order types (left column of mega-menu) ────────────────────────
const ORDER_SVG: Record<string, string> = {
  essay:       'M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2zM14 2v6h6M16 13H8M16 17H8M10 9H8',
  research:    'M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
  dissertation:'M22 10v6M2 10l10-5 10 5-10 5z M6 12v5c3 3 9 3 12 0v-5',
  nursing:     'M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z',
  class:       'm4 6 8-4 8 4M18 10l4 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8l4-2M14 22v-4a2 2 0 0 0-4 0v4M18 5v17M6 5v17',
  editing:     'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z',
}

const featuredServices = [
  { id: 'essay',       label: 'Essay Writing',        desc: 'Argumentative, analytical, reflective — any format, any level',       href: '/services/essay-writing',       color: 'text-gc-600',     border: 'border-gc-200',  bg: 'bg-gc-50'  },
  { id: 'research',    label: 'Research Papers',      desc: 'Citation-rich, peer-reviewed papers across 100+ subjects',            href: '/services/research-papers',     color: 'text-emerald-600',border: 'border-emerald-200', bg: 'bg-emerald-50' },
  { id: 'dissertation',label: 'Dissertations',        desc: 'Proposal through final chapter — BSc, MSc and PhD level',             href: '/services/dissertations',       color: 'text-gold-700',   border: 'border-gold-200', bg: 'bg-gold-50' },
  { id: 'nursing',     label: 'Nursing Essays',       desc: 'SOAP notes, care plans, EBP papers by registered nurses',            href: '/services/nursing-essays',      color: 'text-amber-700',  border: 'border-amber-200',bg: 'bg-amber-50'},
  { id: 'class',       label: 'Online Class Help',    desc: 'Assignments, quizzes and discussions for online courses',             href: '/services/online-class-help',   color: 'text-violet-600', border: 'border-violet-200',bg: 'bg-violet-50'},
  { id: 'editing',     label: 'Editing & Proofreading',desc: 'Grammar, argument, structure and citation accuracy',                href: '/services/editing-proofreading',color: 'text-slate-600',  border: 'border-slate-200',bg: 'bg-slate-50'},
]

// ── CMS service list for right columns (Wagtail-driven) ─────────────────────
const { data: cmsServices } = await useAsyncData(
  'header-service-pages',
  () => fetchCmsServicePages(),
  { default: () => [], server: false },
)

const staticServices = [
  { slug: 'essay-writing',        navLabel: 'Essay Writing'       },
  { slug: 'research-papers',      navLabel: 'Research Papers'     },
  { slug: 'dissertations',        navLabel: 'Dissertations'       },
  { slug: 'term-papers',          navLabel: 'Term Papers'         },
  { slug: 'case-studies',         navLabel: 'Case Studies'        },
  { slug: 'literature-review',    navLabel: 'Literature Reviews'  },
  { slug: 'nursing-essays',       navLabel: 'Nursing Essays'      },
  { slug: 'data-analysis',        navLabel: 'Data Analysis'       },
  { slug: 'capstone-projects',    navLabel: 'Capstone Projects'   },
  { slug: 'admission-essays',     navLabel: 'Admission Essays'    },
  { slug: 'coursework',           navLabel: 'Coursework Help'     },
  { slug: 'editing-proofreading', navLabel: 'Editing & Proofread' },
]

const menuServices = computed(() => {
  const list = cmsServices.value?.length
    ? cmsServices.value.map(s => ({ slug: s.slug, navLabel: s.nav_label || s.title }))
    : staticServices
  return list
})

const menuServicesA = computed(() => menuServices.value.slice(0, 6))
const menuServicesB = computed(() => menuServices.value.slice(6))

const nav = [
  { label: 'Pricing',      href: '/pricing'      },
  { label: 'Writers',      href: '/writers'      },
  { label: 'How it works', href: '/how-it-works' },
  { label: 'Reviews',      href: '/reviews'      },
]
</script>

<template>
  <header
    class="relative z-50 transition-all duration-300"
    :class="headerClass"
  >
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">

      <!-- Logo -->
      <NuxtLink to="/" class="flex shrink-0 items-center gap-2 text-lg font-bold tracking-tight transition-colors" :class="logoClass">
        <span class="flex size-8 items-center justify-center rounded-lg bg-gc-600 text-sm font-extrabold text-white">G</span>
        GradeCrest
      </NuxtLink>

      <!-- Desktop nav -->
      <nav class="hidden items-center gap-1 text-sm font-medium lg:flex">

        <!-- Services mega-menu -->
        <div class="relative" @mouseenter="openServices" @mouseleave="scheduleClose">
          <button
            class="flex items-center gap-1 rounded-lg px-3 py-2 transition-colors"
            :class="[linkClass, servicesOpen ? '!text-gc-600 font-semibold' : '']"
            @click="servicesOpen = !servicesOpen"
          >
            Services
            <svg class="size-4 transition-transform duration-200" :class="servicesOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- Mega-menu dropdown -->
          <div
            v-if="servicesOpen"
            class="absolute left-1/2 top-full z-50 mt-2 w-[820px] -translate-x-1/2 rounded-2xl border border-slate-100 bg-white p-6 shadow-xl"
            @mouseenter="openServices"
            @mouseleave="scheduleClose"
          >
            <div class="grid grid-cols-4 gap-5">

              <!-- Col 1–2: Featured order types -->
              <div class="col-span-2">
                <p class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Popular services</p>
                <div class="grid grid-cols-2 gap-2">
                  <NuxtLink
                    v-for="svc in featuredServices"
                    :key="svc.id"
                    :to="svc.href"
                    class="group flex items-start gap-3 rounded-xl border border-transparent p-2.5 transition-colors hover:border-slate-100 hover:bg-slate-50"
                    @click="servicesOpen = false"
                  >
                    <div class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border" :class="[svc.bg, svc.border]">
                      <svg class="h-4 w-4" :class="svc.color" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path :d="ORDER_SVG[svc.id]" />
                      </svg>
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-slate-800 transition-colors group-hover:text-gc-700">{{ svc.label }}</p>
                      <p class="mt-0.5 text-xs leading-tight text-slate-400">{{ svc.desc }}</p>
                    </div>
                  </NuxtLink>
                </div>
              </div>

              <!-- Col 3–4: Full CMS-driven service list + CTA -->
              <div class="col-span-2 flex flex-col gap-3">
                <div class="grid grid-cols-2 gap-x-4">
                  <div>
                    <p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">All writing</p>
                    <ul class="space-y-0.5">
                      <li v-for="s in menuServicesA" :key="s.slug">
                        <NuxtLink
                          :to="`/services/${s.slug}`"
                          class="block rounded-lg px-2 py-1.5 text-xs text-slate-600 transition-colors hover:bg-gc-50 hover:text-gc-700"
                          @click="servicesOpen = false"
                        >{{ s.navLabel }}</NuxtLink>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">Specialist & more</p>
                    <ul class="space-y-0.5">
                      <li v-for="s in menuServicesB" :key="s.slug">
                        <NuxtLink
                          :to="`/services/${s.slug}`"
                          class="block rounded-lg px-2 py-1.5 text-xs text-slate-600 transition-colors hover:bg-gc-50 hover:text-gc-700"
                          @click="servicesOpen = false"
                        >{{ s.navLabel }}</NuxtLink>
                      </li>
                      <li>
                        <NuxtLink to="/services" class="block px-2 py-1.5 text-xs font-semibold text-gc-600 hover:underline" @click="servicesOpen = false">
                          All services →
                        </NuxtLink>
                      </li>
                    </ul>
                  </div>
                </div>

                <!-- CTA card -->
                <div class="rounded-xl bg-forest-950 p-3 text-center">
                  <p class="text-xs font-semibold text-white">From $13/page · 600+ expert writers</p>
                  <p class="mt-0.5 text-xs text-gold-300">4.9★ · 50,000+ papers delivered</p>
                  <NuxtLink
                    to="/order"
                    class="mt-2 block rounded-lg bg-gc-600 py-1.5 text-xs font-bold text-white transition-colors hover:bg-gc-700"
                    @click="servicesOpen = false"
                  >Place an order</NuxtLink>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- Other nav links -->
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :to="item.href"
          class="rounded-lg px-3 py-2 transition-colors"
          :class="linkClass"
          active-class="!text-gc-600 font-semibold"
        >{{ item.label }}</NuxtLink>
      </nav>

      <!-- Desktop CTAs — asymmetric-radius split capsule -->
      <div class="hidden items-center lg:flex">
        <a
          :href="app.login"
          class="-mr-px flex h-9 items-center rounded-l-full rounded-r-[5px] border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
        >Sign in</a>
        <NuxtLink
          to="/order"
          class="flex h-9 items-center rounded-r-full rounded-l-[5px] bg-gc-600 px-5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-gc-700"
        >Get started</NuxtLink>
      </div>

      <!-- Mobile burger -->
      <button
        class="flex size-9 items-center justify-center rounded-lg transition-colors lg:hidden text-graphite hover:bg-slate-100"
        :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
        @click="mobileOpen = !mobileOpen"
      >
        <X v-if="mobileOpen" class="size-5" />
        <Menu v-else class="size-5" />
      </button>
    </div>

    <!-- Mobile drawer -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="mobileOpen" class="border-t border-slate-100 bg-white lg:hidden">
        <nav class="flex flex-col gap-0.5 px-4 pb-1 pt-3">
          <!-- Services section -->
          <p class="mb-1 mt-2 text-xs font-bold uppercase tracking-wider text-slate-400">Popular services</p>
          <NuxtLink
            v-for="svc in featuredServices"
            :key="svc.id"
            :to="svc.href"
            class="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-gc-50 hover:text-gc-700"
            @click="mobileOpen = false"
          >{{ svc.label }}</NuxtLink>
          <NuxtLink to="/services" class="px-3 py-2 text-xs font-semibold text-gc-600" @click="mobileOpen = false">All services →</NuxtLink>

          <div class="my-2 border-t border-slate-100" />

          <NuxtLink
            v-for="item in nav"
            :key="item.href"
            :to="item.href"
            class="rounded-lg px-3 py-2.5 text-sm font-medium text-graphite hover:bg-slate-50 hover:text-ink"
            active-class="!text-gc-600 bg-gc-50 font-semibold"
            @click="mobileOpen = false"
          >{{ item.label }}</NuxtLink>
        </nav>
        <div class="flex flex-col gap-2 border-t border-slate-100 px-4 py-3">
          <a :href="app.login" class="flex h-11 items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-ink" @click="mobileOpen = false">Sign in</a>
          <NuxtLink to="/order" class="flex h-11 items-center justify-center rounded-xl bg-gc-600 text-sm font-semibold text-white" @click="mobileOpen = false">Get started</NuxtLink>
        </div>
      </div>
    </Transition>
  </header>
</template>
