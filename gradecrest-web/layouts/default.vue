<script setup lang="ts">
import SiteHeader from '~/components/layout/SiteHeader.vue'
import SiteFooter from '~/components/layout/SiteFooter.vue'

const settings = await fetchSiteSettings()

const faviconUrl = settings?.favicon_url ?? '/favicon.svg'
const ogImageUrl = settings?.og_image_url ?? '/og-default.svg'
const ga4Id      = settings?.google_analytics_id ?? ''

useHead({
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: faviconUrl },
    { rel: 'shortcut icon', href: faviconUrl },
  ],
  meta: [
    // Default OG image — individual pages override this with their own ogImage
    { property: 'og:image', content: ogImageUrl },
    { name: 'twitter:image', content: ogImageUrl },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
  ...(ga4Id ? {
    script: [
      {
        src: `https://www.googletagmanager.com/gtag/js?id=${ga4Id}`,
        async: true,
      },
      {
        innerHTML: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${ga4Id}')`,
      },
    ],
  } : {}),
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-white font-sans text-ink antialiased">
    <SiteHeader />
    <main class="flex-1">
      <slot />
    </main>
    <SiteFooter />
  </div>
</template>
