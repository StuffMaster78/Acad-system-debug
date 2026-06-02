<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { CheckCircle2, Loader2, XCircle } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { roleHome } from "@/config/navigation";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const state = ref<"loading" | "success" | "error">("loading");
const message = ref("");

onMounted(async () => {
  const token = route.query.token as string | undefined;
  if (!token) {
    state.value = "error";
    message.value = "No token found in this link. Please request a new one.";
    return;
  }

  try {
    await auth.loginWithMagicLink(token);
    state.value = "success";
    message.value = "You're signed in. Redirecting…";
    setTimeout(() => {
      const dest = auth.role ? roleHome[auth.role] : "/client";
      router.replace(dest);
    }, 1200);
  } catch {
    state.value = "error";
    message.value = "This link is invalid or has already been used. Links expire after 15 minutes.";
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
          <p class="mt-2 text-sm text-graphite">Verifying your magic link.</p>
        </template>

        <template v-else-if="state === 'success'">
          <CheckCircle2 class="mx-auto h-10 w-10 text-emerald-500" />
          <h1 class="mt-5 text-xl font-semibold text-ink">Signed in</h1>
          <p class="mt-2 text-sm text-graphite">{{ message }}</p>
        </template>

        <template v-else>
          <XCircle class="mx-auto h-10 w-10 text-rose-500" />
          <h1 class="mt-5 text-xl font-semibold text-ink">Link expired or invalid</h1>
          <p class="mt-2 text-sm text-graphite">{{ message }}</p>
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
