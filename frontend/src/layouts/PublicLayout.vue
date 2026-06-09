<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { Menu, X } from "@lucide/vue";
import { usePortalContextStore } from "@/stores/portalContext";

const portalCtx = usePortalContextStore();
const route = useRoute();

const brandName = computed(() => portalCtx.branding?.brand_name || "WritingSystem");
const brandLogo = computed(() => portalCtx.branding?.logo_url || "");
const brandInitials = computed(() => {
  const words = brandName.value.trim().split(/\s+/);
  return words.length >= 2
    ? (words[0][0] + words[1][0]).toUpperCase()
    : brandName.value.slice(0, 2).toUpperCase();
});

const showClientNav = computed(() =>
  portalCtx.surface === "client" || (!portalCtx.portal && !portalCtx.website)
);

const drawerOpen = ref(false);
function closeDrawer() { drawerOpen.value = false; }
watch(() => route.path, closeDrawer);
</script>

<template>
  <div class="flex min-h-screen flex-col bg-slate-50 text-ink">

    <!-- ── Header ──────────────────────────────────────────────────────── -->
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white shadow-sm">
      <!-- Main bar -->
      <div class="mx-auto flex h-16 max-w-screen-xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">

        <!-- Brand -->
        <RouterLink to="/" class="flex shrink-0 items-center gap-2.5 group" @click="closeDrawer">
          <div v-if="brandLogo" class="h-8 w-auto overflow-hidden">
            <img :src="brandLogo" :alt="brandName" class="h-full w-auto object-contain" />
          </div>
          <div
            v-else
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-white text-xs font-bold tracking-tight select-none"
          >
            {{ brandInitials }}
          </div>
          <span class="text-base font-bold tracking-tight text-ink transition-colors group-hover:text-brand-700">
            {{ brandName }}
          </span>
        </RouterLink>

        <!-- Desktop nav (lg+) -->
        <nav class="hidden lg:flex items-center gap-1 text-sm font-medium">
          <template v-if="showClientNav">
            <RouterLink class="nav-link" active-class="nav-link-active" to="/services">Services</RouterLink>
            <RouterLink class="nav-link" active-class="nav-link-active" to="/blog">Blog</RouterLink>
            <RouterLink class="nav-link" active-class="nav-link-active" to="/resources">Resources</RouterLink>
            <RouterLink class="nav-link" active-class="nav-link-active" to="/help">Help</RouterLink>
          </template>
          <RouterLink class="nav-link" active-class="nav-link-active" to="/apply">Become a writer</RouterLink>
        </nav>

        <!-- Desktop CTAs (lg+) -->
        <div class="hidden lg:flex items-center gap-2">
          <RouterLink
            class="inline-flex h-9 items-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-ink shadow-sm transition-colors hover:bg-slate-50"
            to="/auth/login"
          >
            Sign in
          </RouterLink>
          <RouterLink
            class="inline-flex h-9 items-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-800"
            to="/auth/register"
          >
            Get started
          </RouterLink>
        </div>

        <!-- Mobile right: CTA + burger -->
        <div class="flex items-center gap-2 lg:hidden">
          <RouterLink
            class="inline-flex h-9 items-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
            to="/auth/register"
            @click="closeDrawer"
          >
            Get started
          </RouterLink>
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:bg-slate-50"
            :aria-label="drawerOpen ? 'Close menu' : 'Open menu'"
            :aria-expanded="drawerOpen"
            @click="drawerOpen = !drawerOpen"
          >
            <X v-if="drawerOpen" class="h-5 w-5" />
            <Menu v-else class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Mobile drawer (v-show keeps it in DOM; no animation class race) -->
      <div
        v-show="drawerOpen"
        class="lg:hidden border-t border-slate-100 bg-white"
      >
        <nav class="mx-auto max-w-screen-xl px-4 py-3 sm:px-6">
          <!-- Nav links -->
          <div class="flex flex-col gap-0.5">
            <template v-if="showClientNav">
              <RouterLink to="/services" class="drawer-link" active-class="drawer-link-active" @click="closeDrawer">Services</RouterLink>
              <RouterLink to="/blog" class="drawer-link" active-class="drawer-link-active" @click="closeDrawer">Blog</RouterLink>
              <RouterLink to="/resources" class="drawer-link" active-class="drawer-link-active" @click="closeDrawer">Resources</RouterLink>
              <RouterLink to="/help" class="drawer-link" active-class="drawer-link-active" @click="closeDrawer">Help</RouterLink>
            </template>
            <RouterLink to="/apply" class="drawer-link" active-class="drawer-link-active" @click="closeDrawer">Become a writer</RouterLink>
          </div>

          <!-- Auth CTAs -->
          <div class="mt-3 flex flex-col gap-2 border-t border-slate-100 pt-3 pb-2">
            <RouterLink
              to="/auth/login"
              class="flex h-11 w-full items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-ink transition-colors hover:bg-slate-50"
              @click="closeDrawer"
            >
              Sign in
            </RouterLink>
            <RouterLink
              to="/auth/register"
              class="flex h-11 w-full items-center justify-center rounded-xl bg-brand-700 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
              @click="closeDrawer"
            >
              Get started — it's free
            </RouterLink>
          </div>
        </nav>
      </div>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <!-- ── Footer ──────────────────────────────────────────────────────── -->
    <footer class="border-t border-slate-200 bg-white">
      <div class="mx-auto max-w-screen-xl px-4 py-8 sm:px-6 lg:px-8">
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
            <RouterLink class="hover:text-ink transition-colors" to="/legal/terms_of_service">Terms</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/privacy_policy">Privacy</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/refund_policy">Refunds</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/cookie_policy">Cookies</RouterLink>
            <RouterLink class="hover:text-ink transition-colors" to="/legal/acceptable_use_policy">Acceptable Use</RouterLink>
          </nav>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
.nav-link {
  @apply rounded-lg px-3.5 py-2 text-graphite transition-colors hover:bg-slate-100 hover:text-ink;
}
.nav-link-active {
  @apply bg-slate-100 text-ink;
}
.drawer-link {
  @apply flex items-center rounded-lg px-3 py-2.5 text-sm font-medium text-graphite transition-colors hover:bg-slate-50 hover:text-ink;
}
.drawer-link-active {
  @apply bg-brand-50 text-brand-700 font-semibold;
}
</style>
