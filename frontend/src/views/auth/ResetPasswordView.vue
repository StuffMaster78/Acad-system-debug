<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { ArrowLeft, CheckCircle2, Eye, EyeOff, KeyRound, Loader2, ShieldCheck } from "@lucide/vue";
import { authApi } from "@/api/auth";
import { usePortalContextStore } from "@/stores/portalContext";

const portalCtx = usePortalContextStore();
const route  = useRoute();
const router = useRouter();
const isDev  = import.meta.env.DEV;

const brandSlug = computed(() =>
  (isDev && (route.query.brand as string)) || portalCtx.website?.slug || ""
);
const backLink = computed(() =>
  isDev && route.query.brand
    ? `/auth/forgot-password?brand=${route.query.brand}`
    : "/auth/forgot-password"
);
const loginLink = computed(() =>
  isDev && route.query.brand
    ? `/auth/login?brand=${route.query.brand}`
    : "/auth/login"
);

const newPassword     = ref("");
const confirmPassword = ref("");
const otpCode         = ref("");
const isLoading       = ref(false);
const notice          = ref("");
const error           = ref("");
const showNew         = ref(false);
const showConfirm     = ref(false);

const token         = computed(() => String(route.query.token ?? ""));
const hasValidParams = computed(() => Boolean(token.value));

const validationError = computed(() => {
  if (newPassword.value && newPassword.value.length < 8) return "Password must be at least 8 characters.";
  if (confirmPassword.value && newPassword.value !== confirmPassword.value) return "Passwords do not match.";
  return "";
});

const canSubmit = computed(() =>
  hasValidParams.value &&
  newPassword.value.length >= 8 &&
  newPassword.value === confirmPassword.value &&
  otpCode.value.trim().length > 0
);

async function submit() {
  if (!canSubmit.value) return;
  error.value  = "";
  notice.value = "";
  isLoading.value = true;
  try {
    await authApi.resetPassword(token.value, otpCode.value.trim(), newPassword.value);
    notice.value = "Password updated! Redirecting to sign in…";
    setTimeout(() => router.push(loginLink.value), 2000);
  } catch {
    error.value = "Unable to reset your password. The link or code may have expired — request a new one.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>

  <!-- Shared form island used by all dark/glass themes via v-if chain below -->

  <!-- ═══════════════ GRADECREST ═══════════════ -->
  <div v-if="brandSlug === 'gradecrest'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#071a13] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0" style="background:radial-gradient(ellipse 60% 50% at 50% 40%,rgba(14,122,97,0.15) 0%,transparent 70%)" aria-hidden="true"/>

    <div class="relative z-10 w-full max-w-[420px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-emerald-500">// Set new password</p>
        <h1 class="text-3xl font-black text-white">Choose a new password</h1>
        <p class="text-sm text-emerald-200/40">Enter the code from your reset email, then set a new password.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl border border-emerald-900/50 bg-[#0a2318]/80 p-7 shadow-2xl shadow-black/60 backdrop-blur-xl space-y-4">
        <div v-if="!hasValidParams" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">
          Reset link is invalid. <RouterLink :to="backLink" class="underline text-emerald-400">Request a new one.</RouterLink>
        </div>
        <form v-else class="space-y-4" @submit.prevent="submit">
          <!-- OTP -->
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-emerald-400/60">One-time code</label>
            <div class="relative">
              <ShieldCheck class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-emerald-700"/>
              <input v-model="otpCode" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 pl-9 pr-4 text-sm text-white placeholder:text-emerald-800 tracking-widest outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-600/20 transition-all" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="123456" maxlength="8"/>
            </div>
          </div>
          <!-- New password -->
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-emerald-400/60">New password</label>
            <div class="relative">
              <input v-model="newPassword" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 pr-10 text-sm text-white placeholder:text-emerald-800 outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-600/20 transition-all" :type="showNew?'text':'password'" autocomplete="new-password" placeholder="At least 8 characters"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-700 hover:text-emerald-400 transition-colors" @click="showNew=!showNew"><EyeOff v-if="showNew" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <!-- Confirm -->
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-emerald-400/60">Confirm password</label>
            <div class="relative">
              <input v-model="confirmPassword" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 pr-10 text-sm text-white placeholder:text-emerald-800 outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-600/20 transition-all" :type="showConfirm?'text':'password'" autocomplete="new-password" placeholder="Repeat new password"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-700 hover:text-emerald-400 transition-colors" @click="showConfirm=!showConfirm"><EyeOff v-if="showConfirm" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <p v-if="validationError" class="text-xs text-red-400">{{ validationError }}</p>
          <div v-if="error" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-40 hover:brightness-110 active:scale-[0.98]" style="background:linear-gradient(135deg,#0e7a61,#0d9488);box-shadow:0 0 20px rgba(14,122,97,0.35)" :disabled="!canSubmit||isLoading" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><KeyRound v-else class="inline h-4 w-4 mr-2"/>{{ isLoading?'Saving…':'Set new password' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-emerald-800/40 bg-emerald-900/30 p-6 text-center space-y-2">
        <CheckCircle2 class="mx-auto h-10 w-10 text-emerald-400"/><p class="font-bold text-white">Password updated!</p><p class="text-sm text-emerald-200/45">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-emerald-700 hover:text-emerald-400 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to recovery
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ ESSAYMANIACS ═══════════════ -->
  <div v-else-if="brandSlug === 'essaymaniacs'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#1a0535] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0 flex items-center justify-center select-none" aria-hidden="true">
      <span class="text-[25vw] font-black leading-none text-purple-950/40 tracking-tighter">NEW</span>
    </div>
    <div class="pointer-events-none absolute -top-20 left-1/4 h-80 w-80 rounded-full bg-purple-700/20 blur-[100px]" aria-hidden="true"/>

    <div class="relative z-10 w-full max-w-[420px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[10px] font-bold uppercase tracking-[0.35em] text-purple-400">// New chapter</p>
        <h1 class="text-3xl font-black text-white">Set a new password</h1>
        <p class="text-sm text-purple-200/40">Enter your code and choose something you'll remember.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl bg-white p-7 shadow-2xl shadow-purple-900/50 space-y-4">
        <div v-if="!hasValidParams" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          Link is missing a token. <RouterLink :to="backLink" class="font-medium underline text-purple-600">Request a new one.</RouterLink>
        </div>
        <form v-else class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">One-time code</label>
            <div class="relative">
              <ShieldCheck class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-300"/>
              <input v-model="otpCode" class="h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-4 text-sm text-slate-900 placeholder:text-slate-300 tracking-widest outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="123456" maxlength="8"/>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">New password</label>
            <div class="relative">
              <input v-model="newPassword" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" :type="showNew?'text':'password'" autocomplete="new-password" placeholder="At least 8 characters"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors" @click="showNew=!showNew"><EyeOff v-if="showNew" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">Confirm password</label>
            <div class="relative">
              <input v-model="confirmPassword" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" :type="showConfirm?'text':'password'" autocomplete="new-password" placeholder="Repeat new password"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors" @click="showConfirm=!showConfirm"><EyeOff v-if="showConfirm" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <p v-if="validationError" class="text-xs text-rose-500">{{ validationError }}</p>
          <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 hover:brightness-105 active:scale-[0.98]" style="background:linear-gradient(135deg,#7c3aed,#6d28d9);box-shadow:0 0 20px rgba(124,58,237,0.3)" :disabled="!canSubmit||isLoading" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><KeyRound v-else class="inline h-4 w-4 mr-2"/>{{ isLoading?'Saving…':'Set new password' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl bg-white p-6 shadow-2xl shadow-purple-900/40 text-center space-y-2">
        <CheckCircle2 class="mx-auto h-10 w-10 text-purple-500"/><p class="font-bold text-slate-900">Password updated!</p><p class="text-sm text-slate-500">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-purple-400/50 hover:text-purple-300 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to recovery
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ NURSEMYGRADE ═══════════════ -->
  <div v-else-if="brandSlug === 'nursemygrade'" class="relative flex min-h-screen items-center justify-center bg-white px-5 py-16 font-sans">
    <div class="absolute left-0 top-0 h-full w-1.5 bg-gradient-to-b from-teal-400 via-teal-600 to-teal-800" aria-hidden="true"/>

    <div class="w-full max-w-[440px] space-y-6">
      <div class="flex items-center gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-teal-600">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="white" stroke-width="2.5" stroke-linecap="round"/></svg>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-teal-600">NurseMyGrade</p>
          <h1 class="text-2xl font-black text-slate-900">Set new password</h1>
        </div>
      </div>
      <p class="text-sm text-slate-500">Enter the 6-digit code from your reset email, then choose a new password.</p>

      <div v-if="!notice" class="rounded-2xl border border-slate-200 bg-white p-7 shadow-lg shadow-slate-100 space-y-4">
        <div v-if="!hasValidParams" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          Reset link is invalid. <RouterLink :to="backLink" class="font-medium underline text-teal-600">Request a new one.</RouterLink>
        </div>
        <form v-else class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">One-time code</label>
            <div class="relative">
              <ShieldCheck class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-300"/>
              <input v-model="otpCode" class="h-11 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-4 text-sm text-slate-900 placeholder:text-slate-300 tracking-widest outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="123456" maxlength="8"/>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">New password</label>
            <div class="relative">
              <input v-model="newPassword" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" :type="showNew?'text':'password'" autocomplete="new-password" placeholder="At least 8 characters"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-teal-500 transition-colors" @click="showNew=!showNew"><EyeOff v-if="showNew" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">Confirm password</label>
            <div class="relative">
              <input v-model="confirmPassword" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" :type="showConfirm?'text':'password'" autocomplete="new-password" placeholder="Repeat new password"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-teal-500 transition-colors" @click="showConfirm=!showConfirm"><EyeOff v-if="showConfirm" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <p v-if="validationError" class="text-xs text-rose-500">{{ validationError }}</p>
          <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 active:scale-[0.98]" style="background:linear-gradient(135deg,#0f766e,#0d9488);box-shadow:0 4px 14px rgba(15,118,110,0.35)" :disabled="!canSubmit||isLoading" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><KeyRound v-else class="inline h-4 w-4 mr-2"/>{{ isLoading?'Saving…':'Set new password' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-teal-200 bg-teal-50 p-6 text-center space-y-2">
        <CheckCircle2 class="mx-auto h-10 w-10 text-teal-500"/><p class="font-bold text-slate-900">Password updated!</p><p class="text-sm text-slate-500">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center gap-1.5 text-sm text-teal-600 hover:text-teal-800 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to recovery
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ RESEARCHPAPERMATE ═══════════════ -->
  <div v-else-if="brandSlug === 'researchpapermate'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#080f2a] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0" style="background-image:repeating-linear-gradient(transparent,transparent 47px,rgba(59,130,246,0.05) 47px,rgba(59,130,246,0.05) 48px);" aria-hidden="true"/>
    <div class="pointer-events-none absolute top-0 left-1/3 h-96 w-96 rounded-full bg-blue-900/25 blur-[120px]" aria-hidden="true"/>

    <div class="relative z-10 w-full max-w-[420px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[9px] font-semibold uppercase tracking-[0.4em] text-blue-400/50">ResearchPaperMate · Password reset</p>
        <h1 class="text-3xl font-black text-white">Set a new password</h1>
        <p class="text-sm text-blue-200/35">Enter the one-time code from your email, then choose a new password.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl border border-blue-900/50 bg-[#0d1b3e]/90 p-7 shadow-2xl shadow-black/70 backdrop-blur-sm space-y-4">
        <div v-if="!hasValidParams" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">
          Invalid token. <RouterLink :to="backLink" class="underline text-cyan-400">Request a new link.</RouterLink>
        </div>
        <form v-else class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.3em] text-blue-400/50">One-time code</label>
            <div class="relative">
              <ShieldCheck class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-blue-700"/>
              <input v-model="otpCode" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 pl-9 pr-4 text-sm text-white placeholder:text-blue-800 tracking-widest outline-none focus:border-cyan-700/60 focus:ring-2 focus:ring-cyan-700/20 transition-all" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="123456" maxlength="8"/>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.3em] text-blue-400/50">New password</label>
            <div class="relative">
              <input v-model="newPassword" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 pr-10 text-sm text-white placeholder:text-blue-800 outline-none focus:border-cyan-700/60 focus:ring-2 focus:ring-cyan-700/20 transition-all" :type="showNew?'text':'password'" autocomplete="new-password" placeholder="At least 8 characters"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-blue-800 hover:text-cyan-400 transition-colors" @click="showNew=!showNew"><EyeOff v-if="showNew" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <div>
            <label class="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.3em] text-blue-400/50">Confirm password</label>
            <div class="relative">
              <input v-model="confirmPassword" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 pr-10 text-sm text-white placeholder:text-blue-800 outline-none focus:border-cyan-700/60 focus:ring-2 focus:ring-cyan-700/20 transition-all" :type="showConfirm?'text':'password'" autocomplete="new-password" placeholder="Repeat new password"/>
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-blue-800 hover:text-cyan-400 transition-colors" @click="showConfirm=!showConfirm"><EyeOff v-if="showConfirm" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
          </div>
          <p v-if="validationError" class="text-xs text-red-400">{{ validationError }}</p>
          <div v-if="error" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-40 hover:brightness-110 active:scale-[0.98]" style="background:linear-gradient(135deg,#163e88,#1e40af,#0e7490);box-shadow:0 0 20px rgba(22,62,136,0.5)" :disabled="!canSubmit||isLoading" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><KeyRound v-else class="inline h-4 w-4 mr-2"/>{{ isLoading?'Saving…':'Set new password' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-cyan-900/40 bg-cyan-950/30 p-6 text-center space-y-2">
        <CheckCircle2 class="mx-auto h-10 w-10 text-cyan-400"/><p class="font-bold text-white">Password updated!</p><p class="text-sm text-blue-200/40">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-blue-700 hover:text-blue-400 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to recovery
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ GENERIC FALLBACK ═══════════════ -->
  <div v-else class="grid min-h-screen place-items-center bg-slate-50 px-4 py-10">
    <section class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-7 shadow-lg shadow-slate-200/60 space-y-6">
      <div class="space-y-1">
        <p class="text-xs font-semibold uppercase tracking-wide text-signal">Password recovery</p>
        <h1 class="text-2xl font-semibold text-ink">Set a new password</h1>
        <p class="text-sm leading-relaxed text-graphite">Enter the one-time code from the reset email, then choose a new password.</p>
      </div>

      <div v-if="!hasValidParams" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-berry">
        This reset link is missing a token. <RouterLink :to="backLink" class="mt-1 block font-medium underline">Request a new link.</RouterLink>
      </div>

      <form v-else-if="!notice" class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-graphite">One-time code</label>
          <div class="relative">
            <ShieldCheck class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"/>
            <input v-model="otpCode" class="focus-ring h-11 w-full rounded-lg border border-slate-200 pl-9 pr-3 text-sm tracking-widest" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="123456" maxlength="8"/>
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-graphite">New password</label>
          <div class="relative">
            <input v-model="newPassword" class="focus-ring h-11 w-full rounded-lg border border-slate-200 px-3.5 pr-10 text-sm" :type="showNew?'text':'password'" autocomplete="new-password" placeholder="At least 8 characters"/>
            <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors" @click="showNew=!showNew"><EyeOff v-if="showNew" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-graphite">Confirm password</label>
          <div class="relative">
            <input v-model="confirmPassword" class="focus-ring h-11 w-full rounded-lg border border-slate-200 px-3.5 pr-10 text-sm" :type="showConfirm?'text':'password'" autocomplete="new-password" placeholder="Repeat your new password"/>
            <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors" @click="showConfirm=!showConfirm"><EyeOff v-if="showConfirm" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
          </div>
        </div>
        <p v-if="validationError" class="text-sm text-berry">{{ validationError }}</p>
        <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-berry">{{ error }}</div>
        <button class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white transition-all hover:bg-slate-800 disabled:opacity-60" type="submit" :disabled="!canSubmit||isLoading">
          <Loader2 v-if="isLoading" class="h-4 w-4 animate-spin"/><KeyRound v-else class="h-4 w-4"/>{{ isLoading?'Saving…':'Set new password' }}
        </button>
      </form>

      <div v-else class="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center space-y-1">
        <CheckCircle2 class="mx-auto h-8 w-8 text-emerald-500"/>
        <p class="font-semibold text-emerald-900">Password updated!</p>
        <p class="text-sm text-emerald-700">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="focus-ring inline-flex items-center gap-1.5 text-sm font-medium text-graphite hover:text-ink transition-colors">
        <ArrowLeft class="h-4 w-4"/> Back to recovery
      </RouterLink>
    </section>
  </div>

</template>
