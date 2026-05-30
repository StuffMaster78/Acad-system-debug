<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="flex min-h-screen flex-col bg-slate-50 text-ink">
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-4 lg:px-8">
        <!-- Brand -->
        <RouterLink to="/" class="flex items-center gap-2.5 group">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-signal text-white text-xs font-bold tracking-tight select-none">
            WS
          </div>
          <span class="text-base font-bold tracking-tight text-ink transition-colors group-hover:text-signal">
            WritingSystem
          </span>
        </RouterLink>

        <!-- Nav -->
        <nav class="flex items-center gap-1 text-sm font-medium">
          <RouterLink
            class="rounded-lg px-3.5 py-2 text-graphite transition-colors hover:bg-slate-100 hover:text-ink"
            active-class="bg-slate-100 text-ink"
            to="/services"
          >
            Services
          </RouterLink>
          <RouterLink
            class="rounded-lg px-3.5 py-2 text-graphite transition-colors hover:bg-slate-100 hover:text-ink"
            active-class="bg-slate-100 text-ink"
            to="/blog"
          >
            Blog
          </RouterLink>
          <RouterLink
            class="rounded-lg px-3 py-2 text-sm font-medium text-graphite transition-colors hover:bg-slate-100 hover:text-ink"
            active-class="bg-slate-100 text-ink"
            to="/help"
          >
            Help
          </RouterLink>
          <RouterLink
            class="ml-1 inline-flex h-9 items-center rounded-lg bg-ink px-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-slate-800"
            to="/auth/login"
          >
            Sign in
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <footer class="border-t border-slate-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 py-8 lg:px-8">
        <div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <span class="text-xs text-graphite">&copy; {{ new Date().getFullYear() }} WritingSystem. All rights reserved.</span>
          <nav class="flex flex-wrap gap-x-5 gap-y-2 text-xs text-graphite">
            <RouterLink class="hover:text-ink transition-colors" to="/help">Help Center</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/terms_of_service">Terms of Service</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/privacy_policy">Privacy Policy</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/refund_policy">Refund Policy</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/cookie_policy">Cookie Policy</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/acceptable_use_policy">Acceptable Use</RouterLink>
          </nav>
        </div>
      </div>
    </footer>
  </div>
</template>
