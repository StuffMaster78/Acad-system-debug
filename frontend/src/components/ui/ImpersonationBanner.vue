<script setup lang="ts">
import { ref } from "vue";
import { Eye, X } from "@lucide/vue";
import { impersonationApi } from "@/api/impersonation";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import type { AuthUser } from "@/types/roles";

const auth = useAuthStore();
const router = useRouter();
const ending = ref(false);
const errorMsg = ref("");

async function endImpersonation() {
  ending.value = true;
  errorMsg.value = "";
  try {
    const { data } = await impersonationApi.end("Admin ended impersonation");
    if (data.access_token && data.user) {
      auth.restoreFromImpersonation({
        access: data.access_token,
        refresh: data.refresh_token ?? "",
        user: data.user as unknown as AuthUser,
      });
    } else {
      auth.restoreFromImpersonation();
    }
    router.push("/admin/clients");
  } catch {
    errorMsg.value = "Could not end session. Try refreshing.";
  } finally {
    ending.value = false;
  }
}
</script>

<template>
  <div
    v-if="auth.isImpersonating"
    class="flex items-center justify-between gap-3 bg-amber-500 px-4 py-2 text-sm font-medium text-white"
  >
    <div class="flex items-center gap-2">
      <Eye class="h-4 w-4 flex-shrink-0" />
      <span>
        You are browsing as another user. All actions are logged.
        <span v-if="errorMsg" class="ml-2 text-amber-100">{{ errorMsg }}</span>
      </span>
    </div>
    <button
      class="flex items-center gap-1.5 rounded border border-white/40 px-2.5 py-1 text-xs font-semibold hover:bg-white/20 disabled:opacity-60"
      :disabled="ending"
      @click="endImpersonation"
    >
      <X class="h-3.5 w-3.5" />
      End session
    </button>
  </div>
</template>
