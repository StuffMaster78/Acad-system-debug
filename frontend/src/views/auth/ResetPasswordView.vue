<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { RouterLink } from "vue-router";
import { ArrowLeft, KeyRound } from "@lucide/vue";
import { authApi } from "@/api/auth";

const route = useRoute();
const router = useRouter();

const newPassword = ref("");
const confirmPassword = ref("");
const isLoading = ref(false);
const notice = ref("");
const error = ref("");

const token = computed(() => String(route.query.token ?? ""));
const uid = computed(() => String(route.query.uid ?? ""));
const hasValidParams = computed(() => Boolean(token.value && uid.value));

const validationError = computed(() => {
  if (newPassword.value && newPassword.value.length < 8) return "Password must be at least 8 characters.";
  if (confirmPassword.value && newPassword.value !== confirmPassword.value) return "Passwords do not match.";
  return "";
});

const canSubmit = computed(
  () => hasValidParams.value && newPassword.value.length >= 8 && newPassword.value === confirmPassword.value,
);

async function submit() {
  if (!canSubmit.value) return;
  error.value = "";
  notice.value = "";
  isLoading.value = true;
  try {
    await authApi.resetPassword(token.value, uid.value, newPassword.value);
    notice.value = "Password updated. Redirecting to sign in…";
    setTimeout(() => router.push("/auth/login"), 2000);
  } catch {
    error.value = "Unable to reset your password. The link may have expired — request a new one.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md rounded-md border border-slate-200 bg-white p-6 shadow-panel">
      <RouterLink
        class="focus-ring mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-graphite hover:text-ink"
        to="/auth/login"
      >
        <ArrowLeft class="h-4 w-4" />
        Back to sign in
      </RouterLink>

      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Password recovery</p>
        <h1 class="mt-2 text-2xl font-semibold text-ink">Set a new password</h1>
        <p class="mt-2 text-sm leading-6 text-graphite">
          Choose a strong password of at least 8 characters.
        </p>
      </div>

      <div v-if="!hasValidParams" class="mt-6 rounded-md border border-rose-200 bg-rose-50 px-3 py-3 text-sm text-berry">
        This reset link is missing required parameters. Please request a new password reset link.
        <RouterLink class="mt-2 block font-medium underline" to="/auth/forgot-password">
          Request a new link
        </RouterLink>
      </div>

      <form v-else class="mt-6 space-y-4" @submit.prevent="submit">
        <label class="block">
          <span class="text-sm font-medium text-graphite">New password</span>
          <input
            v-model="newPassword"
            class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
            type="password"
            autocomplete="new-password"
            placeholder="At least 8 characters"
          />
        </label>
        <label class="block">
          <span class="text-sm font-medium text-graphite">Confirm password</span>
          <input
            v-model="confirmPassword"
            class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
            type="password"
            autocomplete="new-password"
            placeholder="Repeat your new password"
          />
        </label>

        <p v-if="validationError" class="text-sm text-berry">{{ validationError }}</p>
        <p v-if="error" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
          {{ error }}
        </p>
        <p v-if="notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">
          {{ notice }}
        </p>

        <button
          class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
          type="submit"
          :disabled="!canSubmit || isLoading"
        >
          <KeyRound class="h-4 w-4" />
          {{ isLoading ? "Saving…" : "Set new password" }}
        </button>
      </form>
    </section>
  </div>
</template>
