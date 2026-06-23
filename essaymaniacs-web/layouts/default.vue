<template>
  <div class="flex min-h-screen flex-col">
    <div class="sticky top-0 z-50">
      <AnnouncementBar />
      <SiteHeader />
    </div>
    <main class="flex-1">
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
