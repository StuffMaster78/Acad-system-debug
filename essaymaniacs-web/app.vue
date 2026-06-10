<script setup lang="ts">
const portal = usePortalStore()

useSeoMeta({
  titleTemplate: (title) => title ? `${title} — ${portal.brandName}` : portal.brandName,
  ogSiteName: () => portal.brandName,
  twitterCard: 'summary_large_image',
})

// Inject GA4 once portal context resolves with a measurement ID
watch(() => portal.ga4Id, (id) => {
  if (!id || typeof window === 'undefined') return
  const script = document.createElement('script')
  script.src = `https://www.googletagmanager.com/gtag/js?id=${id}`
  script.async = true
  document.head.appendChild(script)
  window.dataLayer = window.dataLayer || []
  function gtag(...args: unknown[]) { window.dataLayer.push(args) }
  gtag('js', new Date())
  gtag('config', id)
}, { immediate: true })
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
