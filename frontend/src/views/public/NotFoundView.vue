<script setup lang="ts">
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { roleHome } from "@/config/navigation";

const auth = useAuthStore();
const homeLink = auth.role ? roleHome[auth.role] : "/";
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-slate-50 px-6 text-center">
    <div class="w-full max-w-md">

      <p class="text-[8rem] font-extrabold leading-none text-slate-100 select-none">404</p>
      <p class="mt-1 text-xs font-semibold uppercase tracking-widest text-brand-700">Page not found</p>
      <h1 class="mt-3 text-3xl font-bold text-ink">We couldn't find that page</h1>
      <p class="mt-4 text-base leading-7 text-graphite">
        The page you're looking for doesn't exist or was moved.
        Check the URL or go back to your workspace.
      </p>

      <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
        <RouterLink
          class="focus-ring inline-flex h-11 items-center justify-center rounded-lg bg-brand-700 px-6 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
          :to="homeLink"
        >
          {{ auth.role ? 'Go to workspace' : 'Go home' }}
        </RouterLink>
        <RouterLink
          class="focus-ring inline-flex h-11 items-center justify-center rounded-lg border border-slate-200 bg-white px-6 text-sm font-semibold text-ink transition-colors hover:bg-slate-50"
          to="/"
        >
          Home
        </RouterLink>
      </div>

      <!-- Quick links for unauthenticated visitors -->
      <div v-if="!auth.role" class="mt-10 border-t border-slate-200 pt-8">
        <p class="mb-4 text-xs font-semibold uppercase tracking-wider text-graphite">Explore</p>
        <div class="flex flex-wrap justify-center gap-2">
          <RouterLink
            v-for="link in [{ label: 'Services', to: '/services' }, { label: 'Blog', to: '/blog' }, { label: 'Help', to: '/help' }]"
            :key="link.to"
            :to="link.to"
            class="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-medium text-graphite transition-colors hover:border-brand-300 hover:text-brand-700"
          >
            {{ link.label }}
          </RouterLink>
        </div>
      </div>

    </div>
  </div>
</template>
