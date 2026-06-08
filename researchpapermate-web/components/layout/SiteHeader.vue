<script setup lang="ts">
const portal = usePortalStore()
const app = useAppUrl()

const nav = [
  { label: 'Services', href: '/services' },
  { label: 'Pricing',  href: '/pricing' },
  { label: 'Blog',     href: '/blog' },
  { label: 'Contact',  href: '/contact' },
]

const mobileOpen = ref(false)
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-slate-100 bg-white/95 backdrop-blur-sm">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <NuxtLink href="/" class="flex items-center gap-2">
        <img v-if="portal.logo" :src="portal.logo" :alt="portal.brandName" class="h-8 w-auto" />
        <span v-else class="font-serif text-xl font-bold text-brand-700">{{ portal.brandName }}</span>
      </NuxtLink>

      <nav class="hidden items-center gap-8 md:flex">
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

      <div class="hidden items-center gap-3 md:flex">
        <a :href="app.login" class="text-sm font-medium text-slate-600 hover:text-brand-600">
          Sign in
        </a>
        <a :href="app.register" class="btn-primary py-2">
          Get started
        </a>
      </div>

      <button class="md:hidden" @click="mobileOpen = !mobileOpen" aria-label="Toggle menu">
        <svg class="h-6 w-6 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div v-if="mobileOpen" class="border-t border-slate-100 bg-white px-4 pb-4 md:hidden">
      <nav class="flex flex-col gap-4 pt-4">
        <NuxtLink v-for="item in nav" :key="item.href" :href="item.href"
          class="text-sm font-medium text-slate-700 hover:text-brand-600" @click="mobileOpen = false">
          {{ item.label }}
        </NuxtLink>
        <a :href="app.register" class="btn-primary mt-2 text-center">
          Get started
        </a>
      </nav>
    </div>
  </header>
</template>
