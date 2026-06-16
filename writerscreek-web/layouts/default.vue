<template>
  <div class="flex min-h-screen flex-col bg-white font-sans antialiased">
    <div class="sticky top-0 z-50">
      <AnnouncementBar />
      <SiteHeader />
    </div>
    <main class="flex-1"><slot /></main>
    <SiteFooter />
    <CookieConsentBanner />
    <ExitIntentPopup />
  </div>
</template>
