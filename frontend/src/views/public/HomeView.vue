<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, LogIn } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { roleHome } from "@/config/navigation";

const auth = useAuthStore();
const portalCtx = usePortalContextStore();
const router = useRouter();

onMounted(() => {
  if (auth.isAuthenticated && auth.role) {
    router.replace(roleHome[auth.role]);
  }
});
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-12">
    <div class="w-full max-w-sm text-center">
      <!-- Brand logo / initials when on a registered domain -->
      <div v-if="portalCtx.branding" class="mb-6 flex flex-col items-center gap-3">
        <img
          v-if="portalCtx.branding.logo_url"
          :src="portalCtx.branding.logo_url"
          :alt="portalCtx.branding.brand_name"
          class="h-12 w-auto object-contain"
        />
        <div
          v-else
          class="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-base font-bold text-ink"
        >
          {{ portalCtx.branding.brand_name.slice(0, 2).toUpperCase() }}
        </div>
        <p class="text-lg font-semibold text-ink">{{ portalCtx.branding.brand_name }}</p>
      </div>

      <h1 class="text-2xl font-semibold text-ink">
        {{ portalCtx.branding ? `Welcome to ${portalCtx.branding.brand_name}` : "Platform access" }}
      </h1>
      <p class="mt-2 text-sm text-graphite">
        Sign in to open your workspace.
      </p>

      <RouterLink
        class="focus-ring mt-8 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink text-sm font-semibold text-white hover:bg-graphite"
        to="/auth/login"
      >
        <LogIn class="h-4 w-4" />
        Sign in
      </RouterLink>

      <p class="mt-6 text-xs text-slate-400">
        Access is by invitation only.
      </p>
    </div>
  </div>
</template>
