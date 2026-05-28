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
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5 text-xs text-graphite lg:px-8">
        <span>&copy; {{ new Date().getFullYear() }} WritingSystem. All rights reserved.</span>
        <nav class="flex gap-4">
          <RouterLink class="hover:text-ink transition-colors" to="/terms">Terms</RouterLink>
          <RouterLink class="hover:text-ink transition-colors" to="/privacy">Privacy</RouterLink>
        </nav>
      </div>
    </footer>
  </div>
</template>
