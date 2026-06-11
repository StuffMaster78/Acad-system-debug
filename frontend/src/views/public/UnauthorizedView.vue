<script setup lang="ts">
import { RouterLink, useRouter } from "vue-router";
import { ShieldOff } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { roleHome } from "@/config/navigation";

const auth = useAuthStore();
const router = useRouter();
const homeLink = auth.role ? roleHome[auth.role] : { name: "login" };
const homeLinkLabel = auth.isAuthenticated ? "Go to workspace" : "Sign in";

function goBack() {
  if (window.history.length > 1) router.back();
  else router.push(homeLink);
}
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-slate-50 px-6 text-center">
    <div class="w-full max-w-md">

      <div class="flex justify-center mb-4">
        <div class="flex size-16 items-center justify-center rounded-2xl bg-rose-50 border border-rose-100">
          <ShieldOff class="size-8 text-rose-400" />
        </div>
      </div>

      <p class="text-[8rem] font-extrabold leading-none text-slate-100 select-none">403</p>
      <p class="mt-1 text-xs font-semibold uppercase tracking-widest text-rose-600">Access denied</p>
      <h1 class="mt-3 text-3xl font-bold text-ink">You don't have access</h1>
      <p class="mt-4 text-base leading-7 text-graphite">
        <span v-if="auth.isAuthenticated">
          Your account doesn't have permission to view this page.
          If you think this is a mistake, contact your administrator.
        </span>
        <span v-else>
          You need to be signed in to access this page.
          Please log in and try again.
        </span>
      </p>

      <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
        <RouterLink
          class="focus-ring inline-flex h-11 items-center justify-center rounded-lg bg-brand-700 px-6 text-sm font-semibold text-white transition-colors hover:bg-brand-800"
          :to="homeLink"
        >
          {{ homeLinkLabel }}
        </RouterLink>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center rounded-lg border border-slate-200 bg-white px-6 text-sm font-semibold text-ink transition-colors hover:bg-slate-50"
          type="button"
          @click="goBack"
        >
          Go back
        </button>
      </div>

    </div>
  </div>
</template>
