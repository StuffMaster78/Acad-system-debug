<script setup lang="ts">
import { Menu, X } from '@lucide/vue'

const app         = useAppUrl()
const route       = useRoute()
const mobileOpen  = ref(false)

watch(() => route.path, () => { mobileOpen.value = false })

const nav = [
  { label: 'Services',     href: '/services'    },
  { label: 'Pricing',      href: '/pricing'     },
  { label: 'Writers',      href: '/writers'     },
  { label: 'How it works', href: '/how-it-works'},
  { label: 'Reviews',      href: '/reviews'     },
]
</script>

<template>
  <header class="relative z-50 bg-white/95 border-b border-slate-200 backdrop-blur-sm shadow-sm">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">

      <!-- Logo -->
      <NuxtLink
        to="/"
        class="flex shrink-0 items-center gap-2 text-lg font-bold tracking-tight text-ink transition-colors"
      >
        <span class="flex size-8 items-center justify-center rounded-lg bg-gc-600 text-sm font-extrabold text-white">G</span>
        GradeCrest
      </NuxtLink>

      <!-- Desktop nav -->
      <nav class="hidden items-center gap-1 text-sm font-medium lg:flex" aria-label="Main navigation">
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :to="item.href"
          class="rounded-lg px-3 py-2 text-graphite hover:text-ink transition-colors"
          active-class="!text-gc-600 font-semibold"
        >{{ item.label }}</NuxtLink>
      </nav>

      <!-- Desktop CTAs -->
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
        :aria-expanded="mobileOpen"
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
        <nav class="flex flex-col gap-0.5 px-4 pb-3 pt-3" aria-label="Mobile navigation">
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
          <a
            :href="app.login"
            class="flex h-11 items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-ink"
            @click="mobileOpen = false"
          >Sign in</a>
          <NuxtLink
            to="/order"
            class="flex h-11 items-center justify-center rounded-xl bg-gc-600 text-sm font-semibold text-white"
            @click="mobileOpen = false"
          >Get started</NuxtLink>
        </div>
      </div>
    </Transition>
  </header>
</template>
