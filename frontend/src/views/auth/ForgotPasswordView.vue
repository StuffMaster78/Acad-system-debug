<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ArrowLeft, Mail, Loader2 } from "@lucide/vue";
import { authApi } from "@/api/auth";
import { usePortalContextStore } from "@/stores/portalContext";

const portalCtx = usePortalContextStore();
const route = useRoute();
const isDev = import.meta.env.DEV;

const brandSlug = computed(() =>
  (isDev && (route.query.brand as string)) || portalCtx.website?.slug || ""
);

// Back link preserves brand in dev
const backLink = computed(() =>
  isDev && route.query.brand
    ? `/auth/login?brand=${route.query.brand}`
    : "/auth/login"
);

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

  <!-- ═══════════════ WRITER COSMOS ═══════════════ -->
  <div v-if="brandSlug === 'writerscreek'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#04060f] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0" style="background:radial-gradient(ellipse 70% 60% at 50% 40%,rgba(124,58,237,0.15) 0%,transparent 70%)" aria-hidden="true"/>
    <div class="pointer-events-none absolute inset-0 opacity-[0.025]" style="background-image:linear-gradient(rgba(139,92,246,0.5) 1px,transparent 1px),linear-gradient(90deg,rgba(139,92,246,0.5) 1px,transparent 1px);background-size:48px 48px;" aria-hidden="true"/>

    <div class="relative z-10 w-full max-w-[400px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-[#06b6d4]">// Password recovery</p>
        <h1 class="text-3xl font-black text-white">Reset your password</h1>
        <p class="text-sm text-white/40">We'll beam a reset link to your inbox.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl border border-white/10 bg-[#0c1225]/70 p-7 shadow-2xl shadow-black/50 backdrop-blur-xl space-y-4">
        <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.3em] text-white/40">Email address</label>
            <input v-model.trim="email" class="h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-white placeholder:text-white/20 outline-none focus:border-[#7c3aed]/50 focus:ring-2 focus:ring-[#7c3aed]/20 transition-all" type="email" autocomplete="email" placeholder="you@example.com" />
          </div>
          <div v-if="error" class="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-40 hover:brightness-110" style="background:linear-gradient(135deg,#7c3aed,#2563c8,#06b6d4);box-shadow:0 0 20px rgba(124,58,237,0.3)" :disabled="isLoading || !email" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/>
            <Mail v-else class="inline h-4 w-4 mr-2"/>
            {{ isLoading ? 'Sending…' : 'Send reset link' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-[#06b6d4]/20 bg-[#06b6d4]/10 p-6 text-center space-y-2">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#06b6d4]/20"><Mail class="h-6 w-6 text-[#06b6d4]"/></div>
        <p class="font-bold text-white">Signal transmitted</p>
        <p class="text-sm text-white/45">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-white/30 hover:text-white/60 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to sign in
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ GRADECREST ═══════════════ -->
  <div v-else-if="brandSlug === 'gradecrest'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#071a13] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0" style="background:radial-gradient(ellipse 60% 50% at 50% 40%,rgba(14,122,97,0.15) 0%,transparent 70%)" aria-hidden="true"/>
    <div class="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[20vw] font-black text-emerald-900/10 select-none pointer-events-none" aria-hidden="true">A+</div>

    <div class="relative z-10 w-full max-w-[400px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-emerald-500">// Password recovery</p>
        <h1 class="text-3xl font-black text-white">Forgot your password?</h1>
        <p class="text-sm text-emerald-200/40">Enter your email and we'll send a secure reset link.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl border border-emerald-900/50 bg-[#0a2318]/80 p-7 shadow-2xl shadow-black/60 backdrop-blur-xl space-y-4">
        <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-emerald-400/60">Email address</label>
            <input v-model.trim="email" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 text-sm text-white placeholder:text-emerald-800 outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-600/20 transition-all" type="email" autocomplete="email" placeholder="you@example.com" />
          </div>
          <div v-if="error" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-40 hover:brightness-110 active:scale-[0.98]" style="background:linear-gradient(135deg,#0e7a61,#0d9488);box-shadow:0 0 20px rgba(14,122,97,0.35)" :disabled="isLoading || !email" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ isLoading ? 'Sending…' : 'Send reset link' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-emerald-800/40 bg-emerald-900/30 p-6 text-center space-y-2">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-800/40"><Mail class="h-6 w-6 text-emerald-400"/></div>
        <p class="font-bold text-white">Reset link sent</p>
        <p class="text-sm text-emerald-200/45">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-emerald-700 hover:text-emerald-400 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to sign in
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ ESSAYMANIACS ═══════════════ -->
  <div v-else-if="brandSlug === 'essaymaniacs'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#1a0535] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden select-none" aria-hidden="true">
      <span class="text-[28vw] font-black leading-none text-purple-950/40 tracking-tighter">KEY</span>
    </div>
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div class="absolute -top-20 left-1/4 h-80 w-80 rounded-full bg-purple-700/20 blur-[100px]"/>
      <span class="absolute top-20 right-[10%] text-6xl font-serif text-purple-600/15 select-none">?</span>
      <span class="absolute bottom-20 left-[8%] text-7xl font-serif text-violet-600/15 select-none">@</span>
    </div>

    <div class="relative z-10 w-full max-w-[420px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[10px] font-bold uppercase tracking-[0.35em] text-purple-400">// Account recovery</p>
        <h1 class="text-3xl font-black text-white">Lost your password?</h1>
        <p class="text-sm text-purple-200/40">No stress. Enter your email and we'll sort it out.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl bg-white p-7 shadow-2xl shadow-purple-900/50 space-y-4">
        <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email address</label>
            <input v-model.trim="email" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" type="email" autocomplete="email" placeholder="you@example.com" />
          </div>
          <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 hover:brightness-105 active:scale-[0.98]" style="background:linear-gradient(135deg,#7c3aed,#6d28d9);box-shadow:0 0 20px rgba(124,58,237,0.3)" :disabled="isLoading || !email" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ isLoading ? 'Sending…' : 'Send reset link' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl bg-white p-6 shadow-2xl shadow-purple-900/40 text-center space-y-2">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-purple-100"><Mail class="h-6 w-6 text-purple-500"/></div>
        <p class="font-bold text-slate-900">Check your inbox!</p>
        <p class="text-sm text-slate-500">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-purple-400/60 hover:text-purple-300 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to sign in
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ NURSEMYGRADE ═══════════════ -->
  <div v-else-if="brandSlug === 'nursemygrade'" class="relative flex min-h-screen items-center justify-center bg-white px-5 py-16 font-sans">
    <!-- Teal accent bar left -->
    <div class="absolute left-0 top-0 h-full w-1.5 bg-gradient-to-b from-teal-400 via-teal-600 to-teal-800" aria-hidden="true"/>

    <div class="w-full max-w-[440px] space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-teal-600">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="white" stroke-width="2.5" stroke-linecap="round"/></svg>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-teal-600">NurseMyGrade</p>
          <h1 class="text-2xl font-black text-slate-900">Password recovery</h1>
        </div>
      </div>

      <p class="text-sm text-slate-500 leading-relaxed">Enter the email address on your NurseMyGrade account. We'll send a secure reset link — no questions asked.</p>

      <div v-if="!notice" class="rounded-2xl border border-slate-200 bg-white p-7 shadow-lg shadow-slate-100 space-y-4">
        <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email address</label>
            <input v-model.trim="email" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" type="email" autocomplete="email" placeholder="nurse@example.com" />
          </div>
          <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 active:scale-[0.98]" style="background:linear-gradient(135deg,#0f766e,#0d9488);box-shadow:0 4px 14px rgba(15,118,110,0.35)" :disabled="isLoading || !email" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ isLoading ? 'Sending…' : 'Send reset link' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-teal-200 bg-teal-50 p-6 text-center space-y-2">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-teal-100"><Mail class="h-6 w-6 text-teal-600"/></div>
        <p class="font-bold text-slate-900">Reset link sent</p>
        <p class="text-sm text-slate-500">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center gap-1.5 text-sm text-teal-600 hover:text-teal-800 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to sign in
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ RESEARCHPAPERMATE ═══════════════ -->
  <div v-else-if="brandSlug === 'researchpapermate'" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#080f2a] px-5 py-16 font-sans">
    <div class="pointer-events-none absolute inset-0" style="background-image:repeating-linear-gradient(transparent,transparent 47px,rgba(59,130,246,0.05) 47px,rgba(59,130,246,0.05) 48px);" aria-hidden="true"/>
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div class="absolute top-0 left-1/3 h-96 w-96 rounded-full bg-blue-900/25 blur-[120px]"/>
    </div>

    <div class="relative z-10 w-full max-w-[400px] space-y-5">
      <div class="text-center space-y-1">
        <p class="font-mono text-[9px] font-semibold uppercase tracking-[0.4em] text-blue-400/50">ResearchPaperMate · Account recovery</p>
        <h1 class="text-3xl font-black text-white">Reset your password</h1>
        <p class="text-sm text-blue-200/35">We'll send a secure reset link to your registered email.</p>
      </div>

      <div v-if="!notice" class="rounded-2xl border border-blue-900/50 bg-[#0d1b3e]/90 p-7 shadow-2xl shadow-black/70 backdrop-blur-sm space-y-4">
        <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.3em] text-blue-400/50">Email address</label>
            <input v-model.trim="email" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 text-sm text-white placeholder:text-blue-800 outline-none focus:border-cyan-700/60 focus:ring-2 focus:ring-cyan-700/20 transition-all" type="email" autocomplete="email" placeholder="researcher@example.com" />
          </div>
          <div v-if="error" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">{{ error }}</div>
          <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-40 hover:brightness-110 active:scale-[0.98]" style="background:linear-gradient(135deg,#163e88,#1e40af,#0e7490);box-shadow:0 0 20px rgba(22,62,136,0.5)" :disabled="isLoading || !email" type="submit">
            <Loader2 v-if="isLoading" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ isLoading ? 'Sending…' : 'Send reset link' }}
          </button>
        </form>
      </div>

      <div v-else class="rounded-2xl border border-cyan-900/40 bg-cyan-950/30 p-6 text-center space-y-2">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-cyan-900/40"><Mail class="h-6 w-6 text-cyan-400"/></div>
        <p class="font-bold text-white">Transmission sent</p>
        <p class="text-sm text-blue-200/40">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="flex items-center justify-center gap-1.5 text-sm text-blue-700 hover:text-blue-400 transition-colors">
        <ArrowLeft class="h-3.5 w-3.5"/> Back to sign in
      </RouterLink>
    </div>
  </div>

  <!-- ═══════════════ GENERIC FALLBACK ═══════════════ -->
  <div v-else class="grid min-h-screen place-items-center bg-slate-50 px-4 py-10">
    <section class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-7 shadow-lg shadow-slate-200/60 space-y-6">
      <div class="space-y-1">
        <p class="text-xs font-semibold uppercase tracking-wide text-signal">Password recovery</p>
        <h1 class="text-2xl font-semibold text-ink">Forgot your password?</h1>
        <p class="text-sm leading-relaxed text-graphite">Enter the email address on your account and we'll send a reset link.</p>
      </div>

      <form v-if="!notice" class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-graphite">Email address</label>
          <input v-model.trim="email" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors" type="email" autocomplete="email" placeholder="you@example.com" />
        </div>
        <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-berry">{{ error }}</div>
        <button class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white transition-all hover:bg-slate-800 disabled:opacity-60" type="submit" :disabled="isLoading || !email">
          <Loader2 v-if="isLoading" class="h-4 w-4 animate-spin"/><Mail v-else class="h-4 w-4"/>{{ isLoading ? 'Sending…' : 'Send reset link' }}
        </button>
      </form>

      <div v-else class="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center space-y-1">
        <Mail class="mx-auto h-7 w-7 text-emerald-500"/>
        <p class="font-semibold text-emerald-900">Check your inbox</p>
        <p class="text-sm text-emerald-700">{{ notice }}</p>
      </div>

      <RouterLink :to="backLink" class="focus-ring inline-flex items-center gap-1.5 text-sm font-medium text-graphite hover:text-ink transition-colors">
        <ArrowLeft class="h-4 w-4"/> Back to sign in
      </RouterLink>
    </section>
  </div>

</template>
