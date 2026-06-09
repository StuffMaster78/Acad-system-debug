<script setup lang="ts">
import { computed, ref } from "vue";
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

// Mobile drawer
const drawerOpen = ref(false);
function closeDrawer() { drawerOpen.value = false; }

// Close drawer on route change
import { watch } from "vue";
watch(() => route.path, closeDrawer);
</script>

<template>
  <div class="flex min-h-screen flex-col bg-slate-50 text-ink">

    <!-- ── Header ──────────────────────────────────────────────────────── -->
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 lg:px-8">

        <!-- Brand -->
        <RouterLink to="/" class="flex items-center gap-2.5 group shrink-0" @click="closeDrawer">
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

        <!-- Desktop nav (hidden below lg) -->
        <nav class="hidden lg:flex items-center gap-1 text-sm font-medium">
          <template v-if="showClientNav">
            <RouterLink class="nav-link" active-class="nav-link-active" to="/services">Services</RouterLink>
            <RouterLink class="nav-link" active-class="nav-link-active" to="/blog">Blog</RouterLink>
            <RouterLink class="nav-link" active-class="nav-link-active" to="/resources">Resources</RouterLink>
            <RouterLink class="nav-link" active-class="nav-link-active" to="/help">Help</RouterLink>
          </template>
          <RouterLink class="nav-link" active-class="nav-link-active" to="/apply">Become a writer</RouterLink>
          <RouterLink
            class="ml-2 inline-flex h-9 items-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-ink shadow-sm transition-colors hover:bg-slate-50"
            to="/auth/register"
          >
            Get started
          </RouterLink>
          <RouterLink
            class="ml-1 inline-flex h-9 items-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-800"
            to="/auth/login"
          >
            Sign in
          </RouterLink>
        </nav>

        <!-- Mobile: CTA + burger (shown below lg) -->
        <div class="flex items-center gap-2 lg:hidden">
          <RouterLink
            class="inline-flex h-9 items-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-800"
            to="/auth/register"
            @click="closeDrawer"
          >
            Get started
          </RouterLink>
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:bg-slate-50"
            :aria-label="drawerOpen ? 'Close menu' : 'Open menu'"
            @click="drawerOpen = !drawerOpen"
          >
            <X v-if="drawerOpen" class="h-5 w-5" />
            <Menu v-else class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Mobile drawer — drops below the header bar -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="drawerOpen"
          class="lg:hidden border-t border-slate-200 bg-white px-4 pb-5 pt-3 shadow-md"
        >
          <nav class="flex flex-col gap-0.5">
            <template v-if="showClientNav">
              <RouterLink class="mobile-nav-link" active-class="mobile-nav-link-active" to="/services" @click="closeDrawer">Services</RouterLink>
              <RouterLink class="mobile-nav-link" active-class="mobile-nav-link-active" to="/blog" @click="closeDrawer">Blog</RouterLink>
              <RouterLink class="mobile-nav-link" active-class="mobile-nav-link-active" to="/resources" @click="closeDrawer">Resources</RouterLink>
              <RouterLink class="mobile-nav-link" active-class="mobile-nav-link-active" to="/help" @click="closeDrawer">Help</RouterLink>
            </template>
            <RouterLink class="mobile-nav-link" active-class="mobile-nav-link-active" to="/apply" @click="closeDrawer">Become a writer</RouterLink>

            <div class="mt-3 flex flex-col gap-2 border-t border-slate-100 pt-3">
              <RouterLink
                class="flex h-11 items-center justify-center rounded-xl border border-slate-200 text-sm font-semibold text-ink transition-colors hover:bg-slate-50"
                to="/auth/login"
                @click="closeDrawer"
              >
                Sign in
              </RouterLink>
              <RouterLink
                class="flex h-11 items-center justify-center rounded-xl bg-brand-700 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
                to="/auth/register"
                @click="closeDrawer"
              >
                Get started — it's free
              </RouterLink>
            </div>
          </nav>
        </div>
      </Transition>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <!-- ── Footer ──────────────────────────────────────────────────────── -->
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

<style scoped>
.nav-link {
  @apply rounded-lg px-3.5 py-2 text-graphite transition-colors hover:bg-slate-100 hover:text-ink;
}
.nav-link-active {
  @apply bg-slate-100 text-ink;
}
.mobile-nav-link {
  @apply flex items-center rounded-lg px-3 py-2.5 text-sm font-medium text-graphite transition-colors hover:bg-slate-50 hover:text-ink;
}
.mobile-nav-link-active {
  @apply bg-brand-50 text-brand-700;
}
</style>
