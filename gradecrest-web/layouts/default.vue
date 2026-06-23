<script setup lang="ts">
import SiteHeader from '~/components/layout/SiteHeader.vue'
import SiteFooter from '~/components/layout/SiteFooter.vue'
import AnnouncementBar from '~/components/marketing/AnnouncementBar.vue'
import CookieConsentBanner from '~/components/privacy/CookieConsentBanner.vue'
import ExitIntentPopup from '~/components/marketing/ExitIntentPopup.vue'

const { data: settings } = await useAsyncData('gc-site-settings', fetchSiteSettings)

const faviconUrl = computed(() => settings.value?.favicon_url ?? '/favicon.svg')
const ogImageUrl = computed(() => settings.value?.og_image_url ?? '/og-default.png')
const ga4Id      = computed(() => settings.value?.google_analytics_id ?? '')
const consent = useCookieConsent()

useHead({
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: faviconUrl },
    { rel: 'shortcut icon', href: faviconUrl },
  ],
  meta: [
    { property: 'og:image', content: ogImageUrl },
    { name: 'twitter:image', content: ogImageUrl },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
})

onMounted(async () => {
  await consent.init()
  injectConsentAwareGa4(ga4Id.value, consent.analyticsAllowed.value)
})

watch(consent.analyticsAllowed, (allowed) => {
  injectConsentAwareGa4(ga4Id.value, allowed)
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-white font-sans text-ink antialiased">
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[9999] focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-gc-700 focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-gc-500">Skip to main content</a>
    <!-- Sticky wrapper keeps bar + nav together as one scrolling unit -->
    <div class="sticky top-0 z-50">
      <AnnouncementBar />
      <SiteHeader />
    </div>
    <main id="main-content" class="flex-1">
      <slot />
    </main>
    <SiteFooter />
    <CookieConsentBanner />
    <CookieSettingsButton />
    <ChatWidget />
    <ExitIntentPopup />
  </div>
</template>
