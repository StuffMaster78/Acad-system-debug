<template>
  <div class="flex min-h-screen flex-col">
    <AnnouncementBar />
    <SiteHeader />
    <main class="flex-1">
      <slot />
    </main>
    <SiteFooter />
    <WhatsAppButton />
  </div>
</template>
