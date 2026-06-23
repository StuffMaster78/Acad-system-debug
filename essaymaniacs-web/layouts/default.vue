<template>
  <div class="flex min-h-screen flex-col">
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[9999] focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-brand-700 focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-brand-500">Skip to main content</a>
    <div class="sticky top-0 z-50">
      <AnnouncementBar />
      <SiteHeader />
    </div>
    <main id="main-content" class="flex-1">
      <slot />
    </main>
    <SiteFooter />
    <WhatsAppButton />
    <ChatWidget />
    <ClientOnly>
      <CookieConsentBanner />
      <CookieSettingsButton />
    </ClientOnly>
  </div>
</template>
