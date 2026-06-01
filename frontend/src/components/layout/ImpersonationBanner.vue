<script setup lang="ts">
import { computed } from "vue";
import { ShieldAlert, LogOut } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { useAdminAccessStore } from "@/stores/adminAccess";

const auth = useAuthStore();
const access = useAdminAccessStore();

const show = computed(() => auth.isImpersonating);
const targetEmail = computed(() => auth.user?.email ?? "");

async function handleEnd() {
  await access.endImpersonation("Admin manually ended impersonation");
}
</script>

<template>
  <div
    v-if="show"
    class="sticky top-0 z-50 flex items-center justify-between gap-3 bg-amber-500 px-4 py-2 text-sm font-medium text-amber-950 shadow-md"
    role="alert"
    aria-live="polite"
  >
    <span class="flex items-center gap-2">
      <ShieldAlert class="h-4 w-4 shrink-0" aria-hidden="true" />
      You are impersonating
      <strong class="font-semibold">{{ targetEmail }}</strong>
      — all actions will be performed as this user.
    </span>

    <button
      class="flex items-center gap-1.5 rounded-md border border-amber-700 bg-amber-600 px-3 py-1 text-xs font-semibold text-white hover:bg-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
      :disabled="access.isMutating"
      @click="handleEnd"
    >
      <LogOut class="h-3.5 w-3.5" aria-hidden="true" />
      End impersonation
    </button>
  </div>
</template>
