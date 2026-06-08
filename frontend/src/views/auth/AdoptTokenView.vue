<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { CheckCircle2, Loader2, XCircle } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { roleHome } from "@/config/navigation";

const router = useRouter();
const auth = useAuthStore();
const state = ref<"loading" | "success" | "error">("loading");

onMounted(async () => {
  // Tokens arrive in the URL fragment so they're never sent to any server.
  const hash = window.location.hash.substring(1);
  const params = new URLSearchParams(hash);
  const access = params.get("access");
  const refresh = params.get("refresh");

  // Clear the fragment immediately so tokens don't persist in browser history.
  history.replaceState(null, "", window.location.pathname + window.location.search);

  if (!access || !refresh) {
    state.value = "error";
    return;
  }

  try {
    await auth.adoptTokens(access, refresh);
    state.value = "success";
    setTimeout(() => {
      router.replace(auth.role ? roleHome[auth.role] : "/client");
    }, 800);
  } catch {
    state.value = "error";
    auth.clearSession();
  }
});
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md">
      <div class="rounded-lg border border-slate-200 bg-white p-10 shadow-lg shadow-slate-200/60 text-center">

        <template v-if="state === 'loading'">
          <Loader2 class="mx-auto h-10 w-10 animate-spin text-signal" />
          <h1 class="mt-5 text-xl font-semibold text-ink">Signing you in…</h1>
          <p class="mt-2 text-sm text-graphite">Setting up your session.</p>
        </template>

        <template v-else-if="state === 'success'">
          <CheckCircle2 class="mx-auto h-10 w-10 text-emerald-500" />
          <h1 class="mt-5 text-xl font-semibold text-ink">Signed in</h1>
          <p class="mt-2 text-sm text-graphite">Redirecting to your dashboard…</p>
        </template>

        <template v-else>
          <XCircle class="mx-auto h-10 w-10 text-rose-500" />
          <h1 class="mt-5 text-xl font-semibold text-ink">Sign-in failed</h1>
          <p class="mt-2 text-sm text-graphite">The session could not be established. Please sign in again.</p>
          <a
            href="/auth/login"
            class="mt-5 inline-block text-sm font-semibold text-signal hover:underline"
          >
            Back to sign in
          </a>
        </template>

      </div>
    </section>
  </div>
</template>
