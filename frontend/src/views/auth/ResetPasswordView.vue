<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { ArrowLeft, KeyRound, ShieldCheck } from "@lucide/vue";
import { authApi } from "@/api/auth";

const route = useRoute();
const router = useRouter();

const newPassword = ref("");
const confirmPassword = ref("");
const otpCode = ref("");
const isLoading = ref(false);
const notice = ref("");
const error = ref("");

const token = computed(() => String(route.query.token ?? ""));
const hasValidParams = computed(() => Boolean(token.value));

const validationError = computed(() => {
  if (newPassword.value && newPassword.value.length < 8) return "Password must be at least 8 characters.";
  if (confirmPassword.value && newPassword.value !== confirmPassword.value) return "Passwords do not match.";
  return "";
});

const canSubmit = computed(
  () =>
    hasValidParams.value &&
    newPassword.value.length >= 8 &&
    newPassword.value === confirmPassword.value &&
    otpCode.value.trim().length > 0,
);

async function submit() {
  if (!canSubmit.value) return;
  error.value = "";
  notice.value = "";
  isLoading.value = true;
  try {
    await authApi.resetPassword(token.value, otpCode.value.trim(), newPassword.value);
    notice.value = "Password updated. Redirecting to sign in…";
    setTimeout(() => router.push("/auth/login"), 2000);
  } catch {
    error.value = "Unable to reset your password. The link or code may have expired — request a new one.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md rounded-xl border border-slate-200 bg-white p-7 shadow-panel">
      <RouterLink
        class="focus-ring mb-5 inline-flex items-center gap-1.5 text-sm font-medium text-graphite hover:text-ink"
        to="/auth/login"
      >
        <ArrowLeft class="h-4 w-4" />
        Back to sign in
      </RouterLink>

      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Password recovery</p>
        <h1 class="mt-2 text-2xl font-semibold text-ink">Set a new password</h1>
        <p class="mt-2 text-sm leading-6 text-graphite">
          Enter the one-time code from the reset email, then choose a new password.
        </p>
      </div>

      <div v-if="!hasValidParams" class="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-berry">
        This reset link is missing a token. Please request a new reset link.
        <RouterLink class="mt-2 block font-medium underline" to="/auth/forgot-password">
          Request a new link
        </RouterLink>
      </div>

      <form v-else class="mt-6 space-y-4" @submit.prevent="submit">
        <!-- OTP code -->
        <label class="block">
          <span class="text-sm font-medium text-graphite">One-time code</span>
          <p class="mt-0.5 text-xs text-graphite">Check your email for the 6-digit code sent with the reset link.</p>
          <div class="relative mt-1">
            <ShieldCheck class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              v-model="otpCode"
              class="focus-ring h-11 w-full rounded-md border border-slate-200 pl-9 pr-3 text-sm tracking-widest"
              type="text"
              inputmode="numeric"
              autocomplete="one-time-code"
              placeholder="123456"
              maxlength="8"
            />
          </div>
        </label>

        <!-- New password -->
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

        <!-- Confirm password -->
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

        <p v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2.5 text-sm text-berry">
          {{ error }}
        </p>
        <p v-if="notice" class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-signal">
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
