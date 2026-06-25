<script setup lang="ts">
import CookieConsentBanner from '~/components/privacy/CookieConsentBanner.vue'
import PromoStrip from '~/components/marketing/PromoStrip.vue'

const portal = usePortalStore()
const consent = useCookieConsent()
const promo   = usePromoDisplay()

useSeoMeta({
  titleTemplate: (title) => title ? `${title} — ${portal.brandName}` : portal.brandName,
  ogSiteName:    () => portal.brandName,
  ogImage:       () => portal.ogImage ?? undefined,
  twitterCard:   'summary_large_image',
  ogImageWidth:  1200,
  ogImageHeight: 630,
})

// Site-wide schema.org Organisation + WebSite — overridden per-page as needed
useHead({
  script: computed(() => portal.schemaOrgName ? [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Organization',
        name: portal.schemaOrgName,
        url: `https://${portal.ctx.website?.domain ?? 'nursemygrade.com'}`,
        ...(portal.schemaOrgLogo ? { logo: portal.schemaOrgLogo } : {}),
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: portal.schemaOrgName,
        url: `https://${portal.ctx.website?.domain ?? 'nursemygrade.com'}`,
      }),
    },
  ] : []),
})

onMounted(async () => {
  await consent.init()
  injectConsentAwareGa4(portal.ga4Id, consent.analyticsAllowed.value)
  void promo.init()
})

watch([() => portal.ga4Id, consent.analyticsAllowed], ([id, allowed]) => {
  injectConsentAwareGa4(id, allowed)
}, { immediate: true })
</script>

<template>
  <NuxtLayout>
    <PromoStrip />
    <NuxtPage />
    <CookieConsentBanner />
  </NuxtLayout>
</template>
