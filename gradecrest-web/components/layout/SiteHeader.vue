<script setup lang="ts">
import { Menu, X } from '@lucide/vue'

const app    = useAppUrl()
const route  = useRoute()
const mobileOpen = ref(false)
const scrolled   = ref(false)

const isHome = computed(() => route.path === '/')

// Transparent over hero on homepage, solid white elsewhere
const headerClass = computed(() => {
  if (!isHome.value) return 'bg-white border-b border-slate-200 shadow-sm'
  return scrolled.value
    ? 'bg-white border-b border-slate-200 shadow-sm'
    : 'bg-transparent'
})

const logoClass = computed(() =>
  isHome.value && !scrolled.value ? 'text-white' : 'text-ink'
)
const linkClass = computed(() =>
  isHome.value && !scrolled.value ? 'text-white/80 hover:text-white' : 'text-graphite hover:text-ink'
)

onMounted(() => {
  window.addEventListener('scroll', () => { scrolled.value = window.scrollY > 60 }, { passive: true })
})

const nav = [
  { label: 'Services',    href: '/services'      },
  { label: 'Pricing',     href: '/pricing'        },
  { label: 'Writers',     href: '/writers'        },
  { label: 'How it works',href: '/how-it-works'   },
  { label: 'Reviews',     href: '/reviews'        },
]

watch(() => route.path, () => { mobileOpen.value = false })
</script>

<template>
  <header
    class="fixed inset-x-0 top-0 z-50 transition-all duration-300"
    :class="headerClass"
  >
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">

      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2 font-bold text-lg tracking-tight transition-colors" :class="logoClass">
        <span class="flex size-8 items-center justify-center rounded-lg bg-gc-600 text-white text-sm font-extrabold">G</span>
        GradeCrest
      </NuxtLink>

      <!-- Desktop nav -->
      <nav class="hidden lg:flex items-center gap-1 text-sm font-medium">
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :to="item.href"
          class="rounded-lg px-3 py-2 transition-colors"
          :class="linkClass"
          active-class="!text-gc-600 font-semibold"
        >
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Desktop CTAs — asymmetric-radius split capsule (fly.io style) -->
      <div class="hidden lg:flex items-center">
        <a
          :href="app.login"
          class="-mr-px flex h-9 items-center rounded-l-full rounded-r-[5px] border px-4 text-sm font-semibold transition-colors"
          :class="isHome && !scrolled
            ? 'border-white/20 bg-white/10 text-white hover:bg-white/20'
            : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'"
        >Sign in</a>
        <a
          :href="app.order"
          class="flex h-9 items-center rounded-r-full rounded-l-[5px] px-5 text-sm font-semibold shadow-sm transition-colors"
          :class="isHome && !scrolled
            ? 'bg-white text-gc-700 hover:bg-gc-50'
            : 'bg-gc-600 text-white hover:bg-gc-700'"
        >Get started</a>
      </div>

      <!-- Mobile burger -->
      <button
        class="flex size-9 items-center justify-center rounded-lg lg:hidden transition-colors"
        :class="isHome && !scrolled ? 'text-white hover:bg-white/10' : 'text-graphite hover:bg-slate-100'"
        @click="mobileOpen = !mobileOpen"
        :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
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
      <div v-if="mobileOpen" class="lg:hidden border-t border-slate-100 bg-white">
        <nav class="flex flex-col gap-0.5 px-4 pt-3 pb-1">
          <NuxtLink
            v-for="item in nav"
            :key="item.href"
            :to="item.href"
            class="rounded-lg px-3 py-2.5 text-sm font-medium text-graphite hover:bg-slate-50 hover:text-ink"
            active-class="!text-gc-600 bg-gc-50 font-semibold"
          >
            {{ item.label }}
          </NuxtLink>
        </nav>
        <div class="flex flex-col gap-2 border-t border-slate-100 px-4 py-3">
          <a :href="app.login" class="flex h-11 items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-ink">Sign in</a>
          <a :href="app.order" class="flex h-11 items-center justify-center rounded-xl bg-gc-600 text-sm font-semibold text-white">Get started</a>
        </div>
      </div>
    </Transition>
  </header>
</template>
