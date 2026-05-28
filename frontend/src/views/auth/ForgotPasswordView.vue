<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { ArrowLeft, Mail } from "@lucide/vue";
import { authApi } from "@/api/auth";

const email = ref("");
const isLoading = ref(false);
const notice = ref("");
const error = ref("");

async function submit() {
  if (!email.value.trim()) return;
  error.value = "";
  notice.value = "";
  isLoading.value = true;
  try {
    await authApi.forgotPassword(email.value.trim());
    notice.value = "If that email is registered, a reset link has been sent. Check your inbox.";
    email.value = "";
  } catch {
    error.value = "Unable to send a reset link right now. Please try again shortly.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md rounded-md border border-slate-200 bg-white p-6">
      <RouterLink
        class="focus-ring mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-graphite hover:text-ink"
        to="/auth/login"
      >
        <ArrowLeft class="h-4 w-4" />
        Back to sign in
      </RouterLink>

      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Password recovery</p>
        <h1 class="mt-2 text-2xl font-semibold text-ink">Forgot your password?</h1>
        <p class="mt-2 text-sm leading-6 text-graphite">
          Enter the email address on your account and we'll send a reset link.
        </p>
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <label class="block">
          <span class="text-sm font-medium text-graphite">Email address</span>
          <input
            v-model.trim="email"
            class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
            type="email"
            autocomplete="email"
            placeholder="you@example.com"
          />
        </label>

        <p v-if="error" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
          {{ error }}
        </p>
        <p v-if="notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">
          {{ notice }}
        </p>

        <button
          class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
          type="submit"
          :disabled="isLoading || !email"
        >
          <Mail class="h-4 w-4" />
          {{ isLoading ? "Sending…" : "Send reset link" }}
        </button>
      </form>
    </section>
  </div>
</template>
