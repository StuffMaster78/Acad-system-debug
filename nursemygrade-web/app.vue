<script setup lang="ts">
import CookieConsentBanner from '~/components/privacy/CookieConsentBanner.vue'
import ExitIntentPopup from '~/components/marketing/ExitIntentPopup.vue'

const portal = usePortalStore()
const consent = useCookieConsent()

useSeoMeta({
  titleTemplate: (title) => title ? `${title} — ${portal.brandName}` : portal.brandName,
  ogSiteName: () => portal.brandName,
  twitterCard: 'summary_large_image',
})

onMounted(async () => {
  await consent.init()
  injectConsentAwareGa4(portal.ga4Id, consent.analyticsAllowed.value)
})

watch([() => portal.ga4Id, consent.analyticsAllowed], ([id, allowed]) => {
  injectConsentAwareGa4(id, allowed)
}, { immediate: true })
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
    <CookieConsentBanner />
    <ExitIntentPopup />
  </NuxtLayout>
</template>
