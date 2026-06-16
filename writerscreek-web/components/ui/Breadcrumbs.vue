<script setup lang="ts">
const props = defineProps<{
  items: { label: string; href?: string }[]
}>()

const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'https://writerscreek.com'

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: props.items.map((item, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        name: item.label,
        ...(item.href ? { item: `${siteUrl}${item.href}` } : {}),
      })),
    }),
  }],
})
</script>

<template>
  <nav aria-label="Breadcrumb" class="flex items-center gap-1.5 text-sm text-slate-500">
    <NuxtLink href="/" class="hover:text-brand-600 transition-colors shrink-0">Home</NuxtLink>
    <template v-for="(item, i) in items" :key="i">
      <svg class="h-3.5 w-3.5 shrink-0 text-slate-300" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 18l6-6-6-6"/>
      </svg>
      <NuxtLink
        v-if="item.href && i < items.length - 1"
        :href="item.href"
        class="hover:text-brand-600 transition-colors truncate max-w-[200px]"
      >{{ item.label }}</NuxtLink>
      <span v-else class="font-medium text-slate-800 truncate max-w-[240px]" aria-current="page">{{ item.label }}</span>
    </template>
  </nav>
</template>
