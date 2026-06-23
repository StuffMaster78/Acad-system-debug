<script setup lang="ts">
import PromoStrip from '~/components/marketing/PromoStrip.vue'

const portal = usePortalStore()
const consent = useCookieConsent()
const promo   = usePromoDisplay()

useSeoMeta({
  titleTemplate: (title) => title ? `${title} — ${portal.brandName}` : portal.brandName,
  ogSiteName: () => portal.brandName,
  twitterCard: 'summary_large_image',
  ogImageWidth:  1200,
  ogImageHeight: 630,
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
  </NuxtLayout>
</template>
