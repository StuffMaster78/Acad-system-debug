<script setup lang="ts">
import { Menu, X, ChevronDown } from '@lucide/vue'

const app        = useAppUrl()
const route      = useRoute()
const mobileOpen = ref(false)
const svcOpen    = ref(false)
const scrolled   = ref(false)
let closeTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  const onScroll = () => { scrolled.value = window.scrollY > 8 }
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
  onUnmounted(() => window.removeEventListener('scroll', onScroll))
})

watch(() => route.path, () => {
  mobileOpen.value = false
  svcOpen.value    = false
})

function openSvc()  { if (closeTimer) clearTimeout(closeTimer); svcOpen.value = true }
function closeSvc() { closeTimer = setTimeout(() => { svcOpen.value = false }, 150) }

const nav = [
  { label: 'Pricing',      href: '/pricing'      },
  { label: 'Writers',      href: '/writers'      },
  { label: 'How it works', href: '/how-it-works' },
  { label: 'Reviews',      href: '/reviews'      },
]

const featuredServices = [
  { label: 'Essay Writing',          href: '/services/essay-writing-service',           desc: 'Any type, any level'        },
  { label: 'Research Papers',        href: '/services/research-paper-writing-service',  desc: 'All subjects covered'       },
  { label: 'Dissertations',          href: '/services/dissertation-writing-service',    desc: 'Proposal to defence'        },
  { label: 'Coursework Help',        href: '/services/coursework',                      desc: 'Module-by-module support'   },
  { label: 'Data Analysis',          href: '/services/data-analysis',                   desc: 'SPSS, R, Python, Excel'     },
  { label: 'Editing & Proofreading', href: '/services/assignment-editing-service',      desc: 'Polish any draft'           },
]
</script>

<template>
  <header
    class="sticky top-0 z-50 transition-all duration-200"
    :class="scrolled
      ? 'bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-sm'
      : 'bg-white border-b border-slate-100'"
  >
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">

      <!-- Logo — G with graduation cap, matching live brand colors (teal + orange) -->
      <NuxtLink to="/" class="flex shrink-0 items-center gap-2 font-bold tracking-tight text-ink">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" aria-hidden="true">
          <!-- Teal-green rounded background -->
          <rect width="36" height="36" rx="8" fill="#16803d"/>
          <!-- Mortarboard flat board (white) -->
          <rect x="6" y="6" width="24" height="4" rx="2" fill="white"/>
          <!-- Centre post of cap -->
          <rect x="16" y="4" width="4" height="4" rx="1" fill="white"/>
          <!-- Orange tassel dot -->
          <circle cx="30" cy="7" r="2.5" fill="#ea580c"/>
          <!-- G letterform in white -->
          <text
            x="18" y="30"
            font-family="Georgia,'Times New Roman',serif"
            font-size="21"
            font-weight="700"
            fill="white"
            text-anchor="middle"
          >G</text>
        </svg>
        <span class="text-[1.05rem]">
          <span style="color:#16803d">Grade</span><span style="color:#ea580c">Crest</span>
        </span>
      </NuxtLink>

      <!-- Desktop nav -->
      <nav class="hidden items-center gap-0.5 text-sm font-medium lg:flex" aria-label="Main navigation">

        <!-- Services with hover mega-menu -->
        <div class="relative" @mouseenter="openSvc" @mouseleave="closeSvc">
          <NuxtLink
            to="/services"
            class="flex items-center gap-1 rounded-lg px-3 py-2 text-graphite transition-colors hover:text-ink"
            :class="route.path.startsWith('/services') ? '!text-gc-600 font-semibold' : ''"
            @click="svcOpen = false"
          >
            Services
            <ChevronDown class="size-3.5 transition-transform" :class="svcOpen ? 'rotate-180' : ''" />
          </NuxtLink>

          <!-- Dropdown -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="opacity-0 translate-y-1"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 translate-y-1"
          >
            <div
              v-if="svcOpen"
              class="absolute left-0 top-full z-50 mt-2 w-80 rounded-2xl border border-slate-200 bg-white p-3 shadow-xl"
              @mouseenter="openSvc"
              @mouseleave="closeSvc"
            >
              <p class="mb-2 px-2 text-[10px] font-bold uppercase tracking-widest text-slate-400">Popular services</p>
              <div class="space-y-0.5">
                <NuxtLink
                  v-for="svc in featuredServices"
                  :key="svc.href"
                  :to="svc.href"
                  class="flex items-start gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-gc-50"
                  @click="svcOpen = false"
                >
                  <div class="mt-0.5 size-1.5 shrink-0 rounded-full bg-gc-500 mt-2" />
                  <div class="min-w-0">
                    <p class="text-xs font-semibold text-ink">{{ svc.label }}</p>
                    <p class="text-[11px] text-graphite">{{ svc.desc }}</p>
                  </div>
                </NuxtLink>
              </div>
              <div class="mt-2 border-t border-slate-100 pt-2">
                <NuxtLink
                  to="/services"
                  class="flex items-center justify-center gap-1.5 rounded-xl px-3 py-2 text-xs font-semibold text-gc-700 transition-colors hover:bg-gc-50"
                  @click="svcOpen = false"
                >
                  Browse all 174 services →
                </NuxtLink>
              </div>
            </div>
          </Transition>
        </div>

        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :to="item.href"
          class="rounded-lg px-3 py-2 text-graphite transition-colors hover:text-ink"
          active-class="!text-gc-600 font-semibold"
        >{{ item.label }}</NuxtLink>
      </nav>

      <!-- Desktop CTAs + trust badge -->
      <div class="hidden items-center gap-3 lg:flex">
        <!-- Trust micro-badge -->
        <div class="hidden items-center gap-1.5 xl:flex">
          <span class="text-gold-500 text-xs">★</span>
          <span class="text-xs text-graphite font-medium">4.9 · 10k+ orders</span>
        </div>

        <!-- Split pill -->
        <div class="flex items-center">
          <a
            :href="app.login"
            class="-mr-px flex h-9 items-center rounded-l-full rounded-r-[5px] border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          >Sign in</a>
          <NuxtLink
            to="/order"
            class="flex h-9 items-center rounded-r-full rounded-l-[5px] bg-gc-600 px-5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-gc-700"
          >Order now</NuxtLink>
        </div>
      </div>

      <!-- Mobile: price anchor + burger -->
      <div class="flex items-center gap-3 lg:hidden">
        <span class="text-xs font-semibold text-graphite">From $13/page</span>
        <button
          class="flex size-9 items-center justify-center rounded-lg text-graphite transition-colors hover:bg-slate-100"
          :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
          :aria-expanded="mobileOpen"
          @click="mobileOpen = !mobileOpen"
        >
          <X v-if="mobileOpen" class="size-5" />
          <Menu v-else class="size-5" />
        </button>
      </div>
    </div>

    <!-- Mobile drawer -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="mobileOpen" class="border-t border-slate-100 bg-white lg:hidden">

        <!-- Featured services quick-links -->
        <div class="px-4 pt-3 pb-2">
          <p class="mb-2 text-[10px] font-bold uppercase tracking-widest text-slate-400">Services</p>
          <div class="grid grid-cols-2 gap-1.5">
            <NuxtLink
              v-for="svc in featuredServices"
              :key="svc.href"
              :to="svc.href"
              class="rounded-lg bg-slate-50 px-3 py-2 text-xs font-medium text-ink hover:bg-gc-50 hover:text-gc-700 transition-colors"
              @click="mobileOpen = false"
            >{{ svc.label }}</NuxtLink>
          </div>
          <NuxtLink
            to="/services"
            class="mt-2 block text-center text-xs font-semibold text-gc-600 py-1"
            @click="mobileOpen = false"
          >All services →</NuxtLink>
        </div>

        <!-- Nav links -->
        <nav class="flex flex-col gap-0.5 border-t border-slate-100 px-4 pb-3 pt-3" aria-label="Mobile navigation">
          <NuxtLink
            v-for="item in nav"
            :key="item.href"
            :to="item.href"
            class="rounded-lg px-3 py-2.5 text-sm font-medium text-graphite hover:bg-slate-50 hover:text-ink transition-colors"
            active-class="!text-gc-600 bg-gc-50 font-semibold"
            @click="mobileOpen = false"
          >{{ item.label }}</NuxtLink>
        </nav>

        <!-- CTAs -->
        <div class="flex flex-col gap-2 border-t border-slate-100 px-4 py-3">
          <a
            :href="app.login"
            class="flex h-11 items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-ink transition-colors hover:bg-slate-50"
            @click="mobileOpen = false"
          >Sign in</a>
          <NuxtLink
            to="/order"
            class="flex h-11 items-center justify-center rounded-xl bg-gc-600 text-sm font-semibold text-white transition-colors hover:bg-gc-700"
            @click="mobileOpen = false"
          >Order now — from $13/page</NuxtLink>
        </div>
      </div>
    </Transition>
  </header>
</template>
