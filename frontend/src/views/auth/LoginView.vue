<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { Loader2, Mail, ShieldCheck } from "@lucide/vue";
import { roleHome } from "@/config/navigation";
import { useAuthStore, MfaRequiredError } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { authApi } from "@/api/auth";
import type { UserRole } from "@/types/roles";

const auth = useAuthStore();
const portalCtx = usePortalContextStore();
const route = useRoute();
const router = useRouter();

const isBranded = computed(() => !!(portalCtx.portal || portalCtx.website));
const isWriterSurface = computed(
  () =>
    portalCtx.surface === "writer" ||
    route.name === "writer-login" ||
    route.meta?.surface === "writer" ||
    (isDev && route.query.surface === "writer"),
);
const brandName = computed(() => portalCtx.branding?.brand_name || "");
const brandLogo = computed(() => portalCtx.branding?.logo_url || "");

type Tab = "password" | "magic";
const tab = ref<Tab>("password");

const error = ref("");
const mfaRequired = ref(false);
const mfaUserId = ref(0);
const mfaCode = ref("");
const mfaError = ref("");
const form = reactive({ email: "", password: "" });

const magicEmail = ref("");
const magicState = ref<"idle" | "sending" | "sent">("idle");
const magicError = ref("");

const isDev = import.meta.env.DEV;
const previewRoles: UserRole[] = ["client", "writer", "editor", "support", "admin", "superadmin"];

const canSubmit = computed(() => form.email.length > 3 && form.password.length > 0 && !auth.isLoading);
const canSendMagic = computed(() => magicEmail.value.includes("@") && magicState.value !== "sending");

async function submit() {
  error.value = "";
  mfaRequired.value = false;
  mfaUserId.value = 0;
  mfaCode.value = "";
  mfaError.value = "";
  try {
    await auth.login(form);
    const redirect = route.query.redirect?.toString();
    await router.push(redirect || (auth.role ? roleHome[auth.role] : "/client"));
  } catch (err) {
    if (err instanceof MfaRequiredError) {
      mfaRequired.value = true;
      mfaUserId.value = err.userId;
    } else {
      error.value = "We could not sign you in with those details.";
    }
  }
}

async function submitMfa() {
  mfaError.value = "";
  try {
    await auth.submitMfa(mfaUserId.value, mfaCode.value.trim());
    const redirect = route.query.redirect?.toString();
    await router.push(redirect || (auth.role ? roleHome[auth.role] : "/client"));
  } catch {
    mfaError.value = "Invalid code. Please check your authenticator app and try again.";
  }
}

async function sendMagicLink() {
  magicError.value = "";
  magicState.value = "sending";
  try {
    await authApi.requestMagicLink(magicEmail.value);
    magicState.value = "sent";
  } catch {
    magicError.value = "Could not send the link. Please check the email address and try again.";
    magicState.value = "idle";
  }
}

async function preview(role: UserRole) {
  auth.previewAs(role);
  await router.push(roleHome[role]);
}

// ─── Writer cosmos: stars ────────────────────────────────────────────────────
function hashRng(seed: number) {
  let s = Math.sin(seed) * 43758.5453123;
  return s - Math.floor(s);
}
const STARS = Array.from({ length: 180 }, (_, i) => ({
  x: hashRng(i * 127.1) * 100,
  y: hashRng(i * 311.7) * 100,
  r: [1, 1, 1, 1, 1, 1.5, 2][Math.floor(hashRng(i * 52.7) * 7)],
  op: 0.35 + hashRng(i * 231.3) * 0.65,
  dur: `${3 + hashRng(i * 79.3) * 5}s`,
  del: `${hashRng(i * 193.1) * 8}s`,
}));

// ─── Writer cosmos: floating word particles ──────────────────────────────────
const WORDS = [
  "thesis", "research", "citation", "hypothesis", "essay",
  "abstract", "bibliography", "analysis", "methodology", "synthesis",
  "argument", "evidence", "dissertation", "literature", "paradigm",
  "inference", "empirical", "cohort", "axiom", "narrative",
];
const particles = Array.from({ length: 20 }, (_, i) => ({
  word: WORDS[i % WORDS.length],
  x: hashRng(i * 41.3) * 90 + 5,
  dur: `${24 + hashRng(i * 83.1) * 18}s`,
  del: `${hashRng(i * 167.7) * 20}s`,
  op: 0.08 + hashRng(i * 317.5) * 0.14,
  size: ["text-xs", "text-sm", "text-base"][Math.floor(hashRng(i * 59.7) * 3)],
  rotate: (hashRng(i * 113.3) - 0.5) * 30,
}));

// ─── Writer cosmos: typewriter ───────────────────────────────────────────────
const HEADLINES = ["academic papers", "dissertations", "research reports", "essays", "thesis work"];
const headlineIdx = ref(0);
const typeText = ref("");
const isDeleting = ref(false);
let typeTimer: ReturnType<typeof setTimeout> | null = null;

function runTypewriter() {
  const current = HEADLINES[headlineIdx.value];
  const cur = typeText.value;
  if (!isDeleting.value) {
    typeText.value = current.slice(0, cur.length + 1);
    if (typeText.value === current) {
      typeTimer = setTimeout(() => {
        isDeleting.value = true;
        runTypewriter();
      }, 1800);
      return;
    }
    typeTimer = setTimeout(runTypewriter, 85);
  } else {
    typeText.value = current.slice(0, cur.length - 1);
    if (typeText.value === "") {
      isDeleting.value = false;
      headlineIdx.value = (headlineIdx.value + 1) % HEADLINES.length;
    }
    typeTimer = setTimeout(runTypewriter, 42);
  }
}

onMounted(() => {
  typeTimer = setTimeout(runTypewriter, 1200);
});
onBeforeUnmount(() => {
  if (typeTimer) clearTimeout(typeTimer);
});
</script>

<template>
  <!-- ═══════════════════════════════════════════════════════════════
       WRITER SURFACE — Cosmos / space / writing theme
  ═══════════════════════════════════════════════════════════════ -->
  <div v-if="isWriterSurface" class="writer-cosmos relative flex min-h-screen w-full overflow-hidden bg-[#04060f] font-sans">

    <!-- ── Starfield ──────────────────────────────────────────────── -->
    <div class="pointer-events-none absolute inset-0 z-0">
      <svg
        width="100%" height="100%"
        xmlns="http://www.w3.org/2000/svg"
        class="absolute inset-0"
        aria-hidden="true"
      >
        <circle
          v-for="(s, i) in STARS"
          :key="i"
          :cx="`${s.x}%`"
          :cy="`${s.y}%`"
          :r="s.r"
          fill="white"
          :fill-opacity="s.op"
          :style="{ animation: `wink ${s.dur} ${s.del} ease-in-out infinite` }"
        />
      </svg>
    </div>

    <!-- ── Ambient [#7c3aed] glows ───────────────────────────────────── -->
    <div class="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div class="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-[#7c3aed]/20 blur-[128px]" />
      <div class="absolute -right-24 top-1/3 h-80 w-80 rounded-full bg-[#06b6d4]/15 blur-[100px]" />
      <div class="absolute bottom-0 left-1/2 h-72 w-[600px] -translate-x-1/2 rounded-full bg-[#8b5cf6]/10 blur-[120px]" />
    </div>

    <!-- ── Floating academic word particles ──────────────────────── -->
    <div class="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
      <span
        v-for="(p, i) in particles"
        :key="i"
        class="absolute font-mono tracking-widest text-white uppercase"
        :class="p.size"
        :style="{
          left: `${p.x}%`,
          bottom: '-2rem',
          opacity: p.op,
          transform: `rotate(${p.rotate}deg)`,
          animation: `floatUp ${p.dur} ${p.del} linear infinite`,
        }"
      >{{ p.word }}</span>
    </div>

    <!-- ── Subtle grid overlay ───────────────────────────────────── -->
    <div
      class="pointer-events-none absolute inset-0 z-0 opacity-[0.03]"
      style="background-image: linear-gradient(rgba(139,92,246,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.5) 1px, transparent 1px); background-size: 48px 48px;"
      aria-hidden="true"
    />

    <!-- ═══════════════════════════════════════════════════════════
         LEFT PANEL — narrative, stats, immersion
    ═══════════════════════════════════════════════════════════ -->
    <div class="relative z-10 hidden flex-col justify-between p-10 lg:flex lg:w-[58%] xl:p-16">

      <!-- Logo mark -->
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-[#7c3aed]/20 ring-1 ring-[#7c3aed]/30">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="font-mono text-sm font-semibold tracking-widest text-white/70 uppercase">WritersCreek</span>
      </div>

      <!-- Main headline + typewriter -->
      <div class="space-y-8">
        <div class="space-y-4">
          <!-- Overline -->
          <p class="font-mono text-xs font-semibold uppercase tracking-[0.3em] text-[#06b6d4]">
            // writer command center
          </p>

          <!-- Headline -->
          <h1 class="text-5xl font-black leading-[1.08] tracking-tight text-white xl:text-6xl">
            Where great<br/>
            <span class="bg-gradient-to-r from-[#8b5cf6] via-[#06b6d4] to-white bg-clip-text text-transparent">
              writing
            </span><br/>
            <span class="text-white/90">launches.</span>
          </h1>

          <!-- Typewriter -->
          <div class="flex h-9 items-center gap-3">
            <span class="font-mono text-xs uppercase tracking-[0.2em] text-white/40">&gt;</span>
            <span class="font-mono text-base text-white/80">{{ typeText }}<span class="inline-block w-0.5 h-5 bg-[#06b6d4] align-middle ml-0.5 animate-pulse" /></span>
          </div>
        </div>

        <!-- Stats row -->
        <div class="flex flex-wrap gap-6">
          <div
            v-for="stat in [
              { val: '92+', lbl: 'Active writers' },
              { val: '4.9★', lbl: 'Avg. rating' },
              { val: '$0', lbl: 'To get started' },
            ]"
            :key="stat.lbl"
            class="group flex flex-col"
          >
            <span class="font-mono text-2xl font-black text-white">{{ stat.val }}</span>
            <span class="mt-0.5 text-xs text-white/45 group-hover:text-white/60 transition-colors">{{ stat.lbl }}</span>
          </div>
        </div>

        <!-- Feature pills -->
        <div class="flex flex-wrap gap-2">
          <span
            v-for="feat in ['Flexible schedule', 'Earn in USD', 'Weekly payouts', 'Remote worldwide']"
            :key="feat"
            class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-white/60 backdrop-blur-sm hover:border-[#7c3aed]/40 hover:text-white/80 transition-all"
          >{{ feat }}</span>
        </div>
      </div>

      <!-- Bottom: apply link -->
      <div class="space-y-3">
        <div class="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <p class="text-sm text-white/40">
          Not a writer yet?
          <RouterLink to="/apply" class="ml-1 font-semibold text-[#06b6d4] hover:text-white transition-colors hover:underline">
            Apply for access →
          </RouterLink>
        </p>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════
         RIGHT PANEL — login form
    ═══════════════════════════════════════════════════════════ -->
    <div class="relative z-10 flex w-full items-center justify-center px-5 py-10 lg:w-[42%] lg:px-10">
      <div class="w-full max-w-[400px]">

        <!-- Mobile-only logo + headline -->
        <div class="mb-8 lg:hidden">
          <div class="flex items-center gap-2.5 mb-6">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[#7c3aed]/20 ring-1 ring-[#7c3aed]/30">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="font-mono text-sm font-semibold tracking-widest text-white/60 uppercase">WritersCreek</span>
          </div>
          <h1 class="text-3xl font-black text-white leading-tight">Writer<br/><span class="text-[#06b6d4]">access.</span></h1>
        </div>

        <!-- Glass card -->
        <div class="rounded-2xl border border-white/10 bg-[#0c1225]/70 p-7 shadow-2xl shadow-black/50 backdrop-blur-xl">

          <!-- Card header -->
          <div class="mb-7">
            <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-[#06b6d4] mb-2">// authenticate</p>
            <h2 class="text-xl font-bold text-white">Sign in to your workspace</h2>
            <p class="mt-1 text-sm text-white/45">Your writing. Your earnings. Your terms.</p>
          </div>

          <!-- Tab switcher -->
          <div class="mb-6 flex gap-1 rounded-xl border border-white/10 bg-[#070b18]/50 p-1">
            <button
              class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all"
              :class="tab === 'password' ? 'bg-white/10 text-white shadow-sm' : 'text-white/40 hover:text-white/60'"
              type="button"
              @click="tab = 'password'; error = ''; mfaRequired = false"
            >Password</button>
            <button
              class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all"
              :class="tab === 'magic' ? 'bg-white/10 text-white shadow-sm' : 'text-white/40 hover:text-white/60'"
              type="button"
              @click="tab = 'magic'; magicState = 'idle'; magicError = ''"
            >Magic link</button>
          </div>

          <!-- ── Password tab ── -->
          <form v-if="tab === 'password'" class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-white/50" for="wl-email">Email</label>
              <input
                id="wl-email"
                v-model="form.email"
                class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-white placeholder:text-white/25 outline-none focus:border-[#7c3aed]/50 focus:ring-2 focus:ring-[#7c3aed]/20 transition-all"
                autocomplete="email"
                type="email"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <div class="mb-1.5 flex items-center justify-between">
                <label class="text-xs font-semibold uppercase tracking-widest text-white/50" for="wl-password">Password</label>
                <RouterLink class="text-xs font-medium text-[#06b6d4]/80 hover:text-[#06b6d4] transition-colors" to="/auth/forgot-password">
                  Forgot?
                </RouterLink>
              </div>
              <input
                id="wl-password"
                v-model="form.password"
                class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-white placeholder:text-white/25 outline-none focus:border-[#7c3aed]/50 focus:ring-2 focus:ring-[#7c3aed]/20 transition-all"
                autocomplete="current-password"
                type="password"
                placeholder="••••••••"
                required
              />
            </div>

            <Transition enter-active-class="transition-all duration-200" enter-from-class="opacity-0 -translate-y-1" leave-active-class="transition-all duration-150" leave-to-class="opacity-0">
              <div v-if="error" class="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300" role="alert">
                <span class="shrink-0">⚠</span> {{ error }}
              </div>
            </Transition>

            <!-- MFA panel -->
            <div v-if="mfaRequired" class="space-y-3">
              <div class="flex items-center gap-3 rounded-xl border border-amber-400/20 bg-amber-400/10 px-4 py-3">
                <ShieldCheck class="h-4 w-4 shrink-0 text-amber-400" />
                <p class="text-sm font-semibold text-amber-300">Two-factor auth required</p>
              </div>
              <div>
                <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-white/50" for="wl-mfa">Authenticator code</label>
                <input
                  id="wl-mfa"
                  v-model="mfaCode"
                  type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6"
                  placeholder="6-digit code"
                  class="cosmos-input w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-center text-sm tracking-[0.4em] text-white placeholder:tracking-normal placeholder:text-white/25 outline-none focus:border-[#7c3aed]/50 focus:ring-2 focus:ring-[#7c3aed]/20 transition-all"
                  @keyup.enter="submitMfa"
                />
              </div>
              <p v-if="mfaError" class="text-xs text-red-400">{{ mfaError }}</p>
              <button
                type="button"
                class="cosmos-btn h-11 w-full rounded-xl text-sm font-bold text-white disabled:opacity-50 transition-all"
                :disabled="mfaCode.trim().length < 6 || auth.isLoading"
                @click="submitMfa"
              >
                <Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2" />
                {{ auth.isLoading ? "Verifying…" : "Verify identity" }}
              </button>
              <button type="button" class="w-full text-center text-xs text-white/30 hover:text-white/50 transition-colors" @click="mfaRequired = false; mfaCode = ''; mfaError = ''">
                ← Back to sign in
              </button>
            </div>

            <button
              v-if="!mfaRequired"
              class="cosmos-btn h-11 w-full rounded-xl text-sm font-bold text-white disabled:opacity-40 transition-all"
              :disabled="!canSubmit"
              type="submit"
            >
              <Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2" />
              {{ auth.isLoading ? "Launching…" : "Sign in to workspace" }}
            </button>
          </form>

          <!-- ── Magic link tab ── -->
          <div v-else class="space-y-4">
            <template v-if="magicState !== 'sent'">
              <p class="text-sm text-white/45">Enter your email and we'll beam a one-click link straight to your inbox. Expires in 15 minutes.</p>
              <div>
                <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-white/50" for="wl-magic">Email</label>
                <input
                  id="wl-magic"
                  v-model="magicEmail"
                  class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-white placeholder:text-white/25 outline-none focus:border-[#7c3aed]/50 focus:ring-2 focus:ring-[#7c3aed]/20 transition-all"
                  autocomplete="email" type="email" placeholder="you@example.com"
                  @keydown.enter.prevent="canSendMagic && sendMagicLink()"
                />
              </div>
              <div v-if="magicError" class="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300" role="alert">{{ magicError }}</div>
              <button
                class="cosmos-btn h-11 w-full rounded-xl text-sm font-bold text-white disabled:opacity-40 transition-all"
                :disabled="!canSendMagic"
                type="button"
                @click="sendMagicLink"
              >
                <Loader2 v-if="magicState === 'sending'" class="inline h-4 w-4 animate-spin mr-2" />
                <Mail v-else class="inline h-4 w-4 mr-2" />
                {{ magicState === 'sending' ? 'Transmitting…' : 'Send magic link' }}
              </button>
            </template>

            <template v-else>
              <div class="rounded-xl border border-[#06b6d4]/20 bg-[#06b6d4]/10 p-6 text-center">
                <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[#06b6d4]/20">
                  <Mail class="h-6 w-6 text-[#06b6d4]" />
                </div>
                <p class="font-bold text-white">Signal sent!</p>
                <p class="mt-1 text-sm text-white/55">Link transmitted to <strong class="text-white/80">{{ magicEmail }}</strong>. Works once, expires in 15 min.</p>
              </div>
              <button class="w-full text-center text-xs text-white/30 hover:text-white/50 transition-colors" type="button" @click="magicState = 'idle'; magicError = ''">
                Try a different email
              </button>
            </template>
          </div>

          <!-- Mobile: apply link -->
          <div class="mt-6 pt-5 border-t border-white/8 text-center lg:hidden">
            <p class="text-xs text-white/35">
              Not a writer yet?
              <RouterLink to="/apply" class="ml-1 font-semibold text-[#06b6d4] hover:underline">Apply for access</RouterLink>
            </p>
          </div>
        </div>

        <!-- Dev preview panel -->
        <div v-if="isDev" class="mt-4 rounded-xl border border-white/10 bg-[#0c1225]/50 p-4 backdrop-blur-sm">
          <p class="font-mono text-[10px] font-semibold uppercase tracking-widest text-white/30 mb-2">// dev preview</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="roleName in previewRoles"
              :key="roleName"
              class="h-8 rounded-lg border border-white/10 bg-white/5 px-2 text-xs font-semibold capitalize text-white/50 transition-all hover:border-[#7c3aed]/30 hover:bg-[#7c3aed]/10 hover:text-white/80"
              type="button"
              @click="preview(roleName)"
            >{{ roleName }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       ALL OTHER SURFACES — existing clean design (unchanged)
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md">
      <div class="rounded-lg border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">
        <div class="mb-6">
          <div v-if="isBranded" class="mb-4 flex items-center gap-3">
            <img v-if="brandLogo" :src="brandLogo" :alt="brandName" class="h-9 w-auto object-contain" />
            <span v-else class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-ink">{{ brandName.slice(0, 2).toUpperCase() }}</span>
            <span class="text-base font-semibold text-ink">{{ brandName }}</span>
          </div>
          <h1 class="text-2xl font-semibold tracking-tight text-ink">{{ isBranded ? `Sign in to ${brandName}` : "Sign in" }}</h1>
          <p class="mt-1.5 text-sm text-graphite">{{ isBranded ? "Use your account email and password to continue." : "Use your platform account to open the correct workspace." }}</p>
        </div>

        <div class="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
          <button class="flex-1 rounded-md py-2 text-xs font-semibold transition-all" :class="tab === 'password' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'" type="button" @click="tab = 'password'; error = ''; mfaRequired = false">Password</button>
          <button class="flex-1 rounded-md py-2 text-xs font-semibold transition-all" :class="tab === 'magic' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'" type="button" @click="tab = 'magic'; magicState = 'idle'; magicError = ''">Magic link</button>
        </div>

        <form v-if="tab === 'password'" class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink" for="email">Email</label>
            <input id="email" v-model="form.email" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300" autocomplete="email" type="email" placeholder="you@example.com" required />
          </div>
          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label class="text-sm font-medium text-ink" for="password">Password</label>
              <RouterLink class="text-xs font-medium text-signal hover:underline" to="/auth/forgot-password">Forgot password?</RouterLink>
            </div>
            <input id="password" v-model="form.password" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300" autocomplete="current-password" type="password" placeholder="••••••••" required />
          </div>
          <Transition enter-active-class="transition-all duration-200" enter-from-class="opacity-0 -translate-y-1" leave-active-class="transition-all duration-150" leave-to-class="opacity-0">
            <div v-if="error" class="flex items-start gap-2.5 rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">
              <span class="mt-0.5 h-4 w-4 shrink-0 text-rose-500" aria-hidden="true"></span>{{ error }}
            </div>
          </Transition>
          <div v-if="mfaRequired" class="space-y-3">
            <div class="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm">
              <ShieldCheck class="mt-0.5 h-4 w-4 shrink-0 text-amber-600" aria-hidden="true" />
              <p class="font-semibold text-amber-900">Two-factor authentication required</p>
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink" for="mfa-code">Authenticator code</label>
              <input id="mfa-code" v-model="mfaCode" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="6-digit code" class="focus-ring w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm tracking-widest placeholder:tracking-normal placeholder:text-slate-400" @keyup.enter="submitMfa" />
            </div>
            <p v-if="mfaError" class="text-xs text-rose-600">{{ mfaError }}</p>
            <button type="button" class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60" :disabled="mfaCode.trim().length < 6 || auth.isLoading" @click="submitMfa">
              <Loader2 v-if="auth.isLoading" class="h-4 w-4 animate-spin" aria-hidden="true" />{{ auth.isLoading ? "Verifying…" : "Verify" }}
            </button>
            <button type="button" class="w-full text-center text-xs text-graphite underline-offset-2 hover:underline" @click="mfaRequired = false; mfaCode = ''; mfaError = ''">Back to sign in</button>
          </div>
          <button v-if="!mfaRequired" class="focus-ring relative inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60" :disabled="!canSubmit" type="submit">
            <Loader2 v-if="auth.isLoading" class="h-4 w-4 animate-spin" aria-hidden="true" />{{ auth.isLoading ? "Signing in…" : "Sign in" }}
          </button>
        </form>

        <div v-else class="space-y-4">
          <template v-if="magicState !== 'sent'">
            <p class="text-sm text-graphite">Enter your email and we'll send a one-click sign-in link. No password needed. Links expire in 15 minutes and work once only.</p>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink" for="magic-email">Email</label>
              <input id="magic-email" v-model="magicEmail" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300" autocomplete="email" type="email" placeholder="you@example.com" @keydown.enter.prevent="canSendMagic && sendMagicLink()" />
            </div>
            <div v-if="magicError" class="rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">{{ magicError }}</div>
            <button class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60" :disabled="!canSendMagic" type="button" @click="sendMagicLink">
              <Loader2 v-if="magicState === 'sending'" class="h-4 w-4 animate-spin" />
              <Mail v-else class="h-4 w-4" />{{ magicState === 'sending' ? 'Sending…' : 'Send magic link' }}
            </button>
          </template>
          <template v-else>
            <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-5 text-center">
              <Mail class="mx-auto h-8 w-8 text-emerald-500" />
              <p class="mt-3 font-semibold text-emerald-900">Check your inbox</p>
              <p class="mt-1 text-sm text-emerald-800">A sign-in link was sent to <strong>{{ magicEmail }}</strong>. Click it to sign in — it works once and expires in 15 minutes.</p>
            </div>
            <button class="w-full text-center text-xs text-graphite hover:text-ink hover:underline" type="button" @click="magicState = 'idle'; magicError = ''">Try a different email</button>
          </template>
        </div>
      </div>

      <p v-if="portalCtx.surface !== 'writer'" class="mt-4 text-center text-sm text-graphite">
        New to {{ brandName ?? 'the platform' }}?
        <RouterLink to="/auth/register" class="ml-1 font-semibold text-berry hover:underline">Create a free account</RouterLink>
      </p>

      <div v-if="isDev" class="mt-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wider text-graphite">Preview workspace</p>
        <div class="mt-3 grid grid-cols-3 gap-2">
          <button v-for="roleName in previewRoles" :key="roleName" class="focus-ring h-9 rounded-lg border border-slate-200 bg-slate-50 px-2 text-xs font-semibold capitalize text-ink transition-colors hover:border-slate-300 hover:bg-white" type="button" @click="preview(roleName)">{{ roleName }}</button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ── Writer cosmos animations ── */
@keyframes wink {
  0%, 100% { opacity: var(--op, 0.6); }
  50%       { opacity: calc(var(--op, 0.6) * 0.2); }
}
@keyframes floatUp {
  0%   { transform: translateY(0) rotate(var(--rot, 0deg)); opacity: var(--op, 0.1); }
  10%  { opacity: var(--op, 0.1); }
  90%  { opacity: var(--op, 0.1); }
  100% { transform: translateY(-105vh) rotate(var(--rot, 0deg)); opacity: 0; }
}

.cosmos-input {
  caret-color: #06b6d4;
}
.cosmos-input::placeholder {
  color: rgba(255,255,255,0.2);
}

.cosmos-btn {
  background: linear-gradient(135deg, #7c3aed 0%, #2563c8 60%, #06b6d4 100%);
  box-shadow: 0 0 24px rgba(124, 58, 237, 0.35), 0 4px 12px rgba(0,0,0,0.4);
  position: relative;
  overflow: hidden;
}
.cosmos-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, transparent 60%);
  pointer-events: none;
}
.cosmos-btn:hover:not(:disabled) {
  box-shadow: 0 0 36px rgba(124, 58, 237, 0.5), 0 6px 20px rgba(0,0,0,0.5);
  filter: brightness(1.08);
}
.cosmos-btn:active:not(:disabled) {
  transform: scale(0.985);
}
.cosmos-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
