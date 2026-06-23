<script setup lang="ts">
const appUrl = useAppUrl()

const nav = [
  { label: 'How it works', href: '/how-it-works' },
  { label: 'Earnings',     href: '/earnings'      },
  { label: 'Blog',         href: '/blog'          },
  { label: 'FAQ',          href: '/faq'           },
  { label: 'Contact',      href: '/contact'       },
]

const route = useRoute()
const mobileOpen = ref(false)

watch(() => route.path, () => { mobileOpen.value = false })
</script>

<template>
  <header class="border-b border-slate-200 bg-white/95 backdrop-blur-sm">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">

      <!-- Logo -->
      <NuxtLink href="/" class="flex items-center gap-2.5">
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <rect x="1" y="1" width="28" height="28" rx="7" fill="#0f172a"/>
          <path d="M7 8l3.5 12L14 12l3.5 8L21 8" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="text-[1.1rem] font-bold leading-none tracking-tight">
          <span class="text-slate-900">Writers</span><span class="text-brand-500">Creek</span>
        </span>
      </NuxtLink>

      <!-- Desktop nav -->
      <nav class="hidden items-center gap-7 md:flex">
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :href="item.href"
          class="rounded-sm text-sm font-medium text-slate-600 transition-colors hover:text-brand-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          active-class="text-brand-600"
        >
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Desktop CTAs -->
      <div class="hidden items-center gap-4 md:flex">
        <div class="inline-flex items-center overflow-hidden rounded-full border border-slate-200 shadow-sm">
          <a
            :href="appUrl.login"
            class="flex h-9 items-center px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-500"
          >
            Sign in
          </a>
          <span class="h-5 w-px flex-shrink-0 bg-slate-200" />
          <NuxtLink
            to="/apply"
            class="flex h-9 items-center bg-brand-600 px-4 text-sm font-semibold text-white transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-white"
          >
            Apply now
          </NuxtLink>
        </div>
      </div>

      <!-- Mobile hamburger -->
      <button class="md:hidden rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500" :aria-expanded="mobileOpen" aria-label="Toggle menu" @click="mobileOpen = !mobileOpen">
        <svg class="h-6 w-6 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileOpen" class="border-t border-slate-100 bg-white px-4 pb-5 md:hidden">
      <nav class="flex flex-col gap-1 pt-4">
        <NuxtLink
          v-for="item in nav"
          :key="item.href"
          :href="item.href"
          class="rounded-lg px-2 py-2.5 text-sm font-medium text-slate-700 hover:bg-brand-50 hover:text-brand-600"
          @click="mobileOpen = false"
        >
          {{ item.label }}
        </NuxtLink>
        <div class="mt-3 flex flex-col gap-2 border-t border-slate-100 pt-3">
          <NuxtLink
            to="/apply"
            class="btn-primary text-center"
            @click="mobileOpen = false"
          >
            Apply now
          </NuxtLink>
          <a
            :href="appUrl.login"
            class="block rounded-lg border border-slate-200 py-2.5 text-center text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          >
            Writer sign in
          </a>
        </div>
      </nav>
    </div>
  </header>
</template>
