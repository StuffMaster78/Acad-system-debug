<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { usePortalContextStore } from "@/stores/portalContext";

const portalCtx = usePortalContextStore();

const brandName = computed(() => portalCtx.branding?.brand_name || "WritingSystem");
const brandLogo = computed(() => portalCtx.branding?.logo_url || "");
const brandInitials = computed(() => {
  const words = brandName.value.trim().split(/\s+/);
  return words.length >= 2
    ? (words[0][0] + words[1][0]).toUpperCase()
    : brandName.value.slice(0, 2).toUpperCase();
});

// Show client-surface nav links when: no portal resolved (dev/generic) OR surface is client
const showClientNav = computed(() =>
  portalCtx.surface === "client" || (!portalCtx.portal && !portalCtx.website)
);
</script>

<template>
  <div class="flex min-h-screen flex-col bg-slate-50 text-ink">
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-4 lg:px-8">
        <!-- Brand — driven by portal context when available -->
        <RouterLink to="/" class="flex items-center gap-2.5 group">
          <div v-if="brandLogo" class="h-8 w-auto overflow-hidden">
            <img :src="brandLogo" :alt="brandName" class="h-full w-auto object-contain" />
          </div>
          <div
            v-else
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-signal text-white text-xs font-bold tracking-tight select-none"
          >
            {{ brandInitials }}
          </div>
          <span class="text-base font-bold tracking-tight text-ink transition-colors group-hover:text-signal">
            {{ brandName }}
          </span>
        </RouterLink>

        <!-- Nav — client-surface links only shown on client domains -->
        <nav class="flex items-center gap-1 text-sm font-medium">
          <template v-if="showClientNav">
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
              class="rounded-lg px-3.5 py-2 text-graphite transition-colors hover:bg-slate-100 hover:text-ink"
              active-class="bg-slate-100 text-ink"
              to="/resources"
            >
              Resources
            </RouterLink>
            <RouterLink
              class="rounded-lg px-3 py-2 text-sm font-medium text-graphite transition-colors hover:bg-slate-100 hover:text-ink"
              active-class="bg-slate-100 text-ink"
              to="/help"
            >
              Help
            </RouterLink>
          </template>
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
          <span class="text-xs text-graphite">
            &copy; {{ new Date().getFullYear() }} {{ brandName }}. All rights reserved.
          </span>
          <nav class="flex flex-wrap gap-x-5 gap-y-2 text-xs text-graphite">
            <template v-if="showClientNav">
              <RouterLink class="hover:text-ink transition-colors" to="/resources">Resources</RouterLink>
              <RouterLink class="hover:text-ink transition-colors" to="/authors">Our Authors</RouterLink>
              <RouterLink class="hover:text-ink transition-colors" to="/help">Help Center</RouterLink>
            </template>
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
