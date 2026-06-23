<script setup lang="ts">
import SiteHeader from '~/components/layout/SiteHeader.vue'
import SiteFooter from '~/components/layout/SiteFooter.vue'
import AnnouncementBar from '~/components/marketing/AnnouncementBar.vue'
import CookieConsentBanner from '~/components/privacy/CookieConsentBanner.vue'
import ExitIntentPopup from '~/components/marketing/ExitIntentPopup.vue'

const settings = await fetchSiteSettings()

const faviconUrl = settings?.favicon_url ?? '/favicon.svg'
const ogImageUrl = settings?.og_image_url ?? '/og-default.png'
const ga4Id      = settings?.google_analytics_id ?? ''
const consent = useCookieConsent()

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
})

onMounted(async () => {
  await consent.init()
  injectConsentAwareGa4(ga4Id, consent.analyticsAllowed.value)
})

watch(consent.analyticsAllowed, (allowed) => {
  injectConsentAwareGa4(ga4Id, allowed)
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-white font-sans text-ink antialiased">
    <!-- Sticky wrapper keeps bar + nav together as one scrolling unit -->
    <div class="sticky top-0 z-50">
      <AnnouncementBar />
      <SiteHeader />
    </div>
    <main class="flex-1">
      <slot />
    </main>
    <SiteFooter />
    <CookieConsentBanner />
    <CookieSettingsButton />
    <ChatWidget />
    <ExitIntentPopup />
  </div>
</template>
