<script setup lang="ts">
const { getAll } = useServices()
const services = getAll().slice(0, 5)
</script>

<template>
  <aside class="space-y-6">
    <!-- Calculator -->
    <ClientOnly>
      <SidebarCalculator />
      <template #fallback>
        <div class="h-64 animate-pulse rounded-2xl bg-slate-100" />
      </template>
    </ClientOnly>

    <!-- CTA box -->
    <div class="rounded-2xl bg-brand-900 p-5 text-center">
      <p class="text-xs font-semibold uppercase tracking-wider text-brand-300">Expert help available</p>
      <h3 class="mt-2 font-serif text-lg font-bold text-white leading-snug">
        Need your paper written?
      </h3>
      <p class="mt-2 text-sm text-brand-200 leading-relaxed">
        200+ verified writers · From $10/page · Grade or money back
      </p>
      <NuxtLink
        to="/order"
        class="mt-4 block rounded-xl bg-white py-2.5 text-sm font-bold text-brand-700 transition-colors hover:bg-brand-50"
      >
        Place an order
      </NuxtLink>
      <div class="mt-3 flex justify-center gap-0.5">
        <svg v-for="i in 5" :key="i" class="h-3.5 w-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
        <span class="ml-1.5 text-xs text-brand-300">4.8/5 from 14,700+ orders</span>
      </div>
    </div>

    <!-- Quick service links -->
    <div class="rounded-2xl border border-slate-100 bg-white p-5">
      <h3 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Our services</h3>
      <ul class="space-y-2">
        <li v-for="s in services" :key="s.slug">
          <NuxtLink
            :href="`/services/${s.slug}`"
            class="flex items-center gap-2 text-sm text-slate-600 transition-colors hover:text-brand-600"
          >
            <span class="text-base">{{ s.icon }}</span>
            {{ s.navLabel }}
            <span class="ml-auto text-xs text-slate-300">→</span>
          </NuxtLink>
        </li>
        <li>
          <NuxtLink href="/services" class="text-xs font-medium text-brand-600 hover:underline">
            View all services →
          </NuxtLink>
        </li>
      </ul>
    </div>
  </aside>
</template>
