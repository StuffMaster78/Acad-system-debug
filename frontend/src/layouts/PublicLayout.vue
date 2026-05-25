<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-ink">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-6">
        <RouterLink to="/" class="text-base font-semibold">Writing System</RouterLink>
        <nav class="flex items-center gap-2 text-sm font-medium text-graphite">
          <RouterLink class="rounded-md px-3 py-2 hover:bg-slate-100" to="/services">
            Services
          </RouterLink>
          <RouterLink class="rounded-md px-3 py-2 hover:bg-slate-100" to="/auth/login">
            Sign in
          </RouterLink>
        </nav>
      </div>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>
