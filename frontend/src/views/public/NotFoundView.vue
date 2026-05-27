<script setup lang="ts">
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { roleHome } from "@/config/navigation";

const auth = useAuthStore();
const homeLink = auth.role ? roleHome[auth.role] : "/";
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-slate-50 px-4">
    <div class="text-center">
      <p class="text-sm font-semibold uppercase tracking-widest text-signal">404</p>
      <h1 class="mt-4 text-5xl font-semibold text-ink">Page not found</h1>
      <p class="mt-4 max-w-md text-base leading-7 text-graphite">
        The page you're looking for doesn't exist or was moved. Check the URL or go back to your workspace.
      </p>
      <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
        <RouterLink
          class="focus-ring inline-flex h-11 items-center justify-center rounded-md bg-ink px-6 text-sm font-semibold text-white hover:bg-slate-800"
          :to="homeLink"
        >
          Go to workspace
        </RouterLink>
        <RouterLink
          class="focus-ring inline-flex h-11 items-center justify-center rounded-md border border-slate-200 bg-white px-6 text-sm font-semibold text-ink hover:bg-slate-50"
          to="/"
        >
          Home
        </RouterLink>
      </div>
    </div>
  </div>
</template>
