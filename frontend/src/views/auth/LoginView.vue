<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { Eye, EyeOff, Loader2, Mail, ShieldCheck } from "@lucide/vue";
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
// Brand slug drives the themed login page.
// Dev: ?brand=gradecrest overrides so you can preview without a real domain.
// Prod: resolved from portalCtx.website.slug (set by Host: header).
const brandSlug = computed(() =>
  (isDev && (route.query.brand as string)) || portalCtx.website?.slug || ""
);
const forgotLink = computed(() =>
  isDev && brandSlug.value
    ? `/auth/forgot-password?brand=${brandSlug.value}`
    : "/auth/forgot-password"
);

type Tab = "password" | "magic";
const tab = ref<Tab>("password");

const error = ref("");
const mfaRequired = ref(false);
const mfaUserId = ref(0);
const mfaCode = ref("");
const mfaError = ref("");
const form = reactive({ email: "", password: "" });
const showPassword = ref(false);

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
              <label class="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-white/50" for="wl-password">Password</label>
              <div class="relative">
                <input
                  id="wl-password"
                  v-model="form.password"
                  class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 pr-10 text-sm text-white placeholder:text-white/25 outline-none focus:border-[#7c3aed]/50 focus:ring-2 focus:ring-[#7c3aed]/20 transition-all"
                  autocomplete="current-password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="••••••••"
                  required
                />
                <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors" @click="showPassword = !showPassword">
                  <EyeOff v-if="showPassword" class="h-4 w-4" /><Eye v-else class="h-4 w-4" />
                </button>
              </div>
              <RouterLink tabindex="-1" class="mt-1.5 block text-right text-xs font-medium text-[#06b6d4]/70 hover:text-[#06b6d4] transition-colors" :to="forgotLink">Forgot password?</RouterLink>
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
       GRADECREST — Emerald academic prestige, dark forest split
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else-if="brandSlug === 'gradecrest'" class="relative min-h-screen flex overflow-hidden bg-[#071a13] font-sans">
    <!-- Radial glow -->
    <div class="pointer-events-none absolute inset-0" style="background:radial-gradient(ellipse 60% 50% at 30% 50%, rgba(14,122,97,0.18) 0%, transparent 70%)" aria-hidden="true" />
    <!-- Subtle grid -->
    <div class="pointer-events-none absolute inset-0 opacity-[0.04]" style="background-image:linear-gradient(rgba(52,211,153,0.6) 1px,transparent 1px),linear-gradient(90deg,rgba(52,211,153,0.6) 1px,transparent 1px);background-size:40px 40px;" aria-hidden="true" />

    <!-- LEFT PANEL -->
    <div class="relative z-10 hidden lg:flex w-[55%] flex-col justify-between p-14">
      <!-- Logo -->
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-800/60 bg-emerald-900/40">
          <span class="text-xl font-black text-emerald-400">G</span>
        </div>
        <span class="text-sm font-bold tracking-widest text-emerald-300/70 uppercase">GradeCrest</span>
      </div>

      <!-- Hero -->
      <div class="space-y-6">
        <div class="text-[130px] font-black leading-none text-emerald-900/30 select-none">A+</div>
        <div class="space-y-3 -mt-6">
          <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-emerald-500">// Verified academic specialists</p>
          <h1 class="text-5xl font-black leading-[1.08] text-white">Expert writing,<br/><span class="text-emerald-400">guaranteed grades.</span></h1>
          <p class="text-base text-emerald-100/50 max-w-sm leading-relaxed">Human-written academic work by verified subject specialists. Delivered to your deadline.</p>
        </div>
        <!-- Stats -->
        <div class="flex gap-6 pt-2">
          <div v-for="s in [['50k+','Students helped'],['98%','On-time delivery'],['4.9★','Avg. rating']]" :key="s[0]" class="flex flex-col">
            <span class="text-2xl font-black text-white">{{ s[0] }}</span>
            <span class="text-xs text-emerald-400/60 mt-0.5">{{ s[1] }}</span>
          </div>
        </div>
      </div>

      <p class="text-xs text-emerald-700">© GradeCrest · All academic work is 100% original</p>
    </div>

    <!-- RIGHT PANEL: form -->
    <div class="relative z-10 flex flex-1 items-center justify-center px-6 py-10">
      <div class="w-full max-w-[390px] space-y-5">
        <!-- Mobile logo -->
        <div class="flex items-center gap-2 mb-6 lg:hidden">
          <div class="h-8 w-8 rounded-lg border border-emerald-800 bg-emerald-900/60 flex items-center justify-center"><span class="font-black text-emerald-400 text-sm">G</span></div>
          <span class="text-sm font-bold text-emerald-300/70 uppercase tracking-widest">GradeCrest</span>
        </div>

        <div class="rounded-2xl border border-emerald-900/50 bg-[#0a2318]/80 p-7 shadow-2xl shadow-black/60 backdrop-blur-xl space-y-5">
          <div>
            <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-emerald-500 mb-1.5">// Secure access</p>
            <h2 class="text-xl font-bold text-white">Sign in to GradeCrest</h2>
            <p class="text-sm text-emerald-200/40 mt-0.5">Your academic portal awaits.</p>
          </div>

          <!-- Tabs -->
          <div class="flex gap-1 rounded-xl border border-emerald-900/60 bg-[#06130e]/60 p-1">
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='password'?'bg-emerald-800/60 text-white shadow-sm':'text-emerald-400/60 hover:text-emerald-300'" type="button" @click="tab='password';error='';mfaRequired=false">Password</button>
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='magic'?'bg-emerald-800/60 text-white shadow-sm':'text-emerald-400/60 hover:text-emerald-300'" type="button" @click="tab='magic';magicState='idle';magicError=''">Magic link</button>
          </div>

          <form v-if="tab==='password'" class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="block text-xs font-semibold uppercase tracking-widest text-emerald-400/60 mb-1.5" for="gc-email">Email</label>
              <input id="gc-email" v-model="form.email" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 text-sm text-white placeholder:text-emerald-700 outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-600/20 transition-all" type="email" autocomplete="email" placeholder="you@example.com" required />
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-widest text-emerald-400/60 mb-1.5" for="gc-pw">Password</label>
              <div class="relative">
                <input id="gc-pw" v-model="form.password" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 pr-10 text-sm text-white placeholder:text-emerald-700 outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-600/20 transition-all" :type="showPassword?'text':'password'" autocomplete="current-password" placeholder="••••••••" required />
                <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-700 hover:text-emerald-400 transition-colors" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
              </div>
              <RouterLink tabindex="-1" class="mt-1.5 block text-right text-xs text-emerald-500/70 hover:text-emerald-400 transition-colors" :to="forgotLink">Forgot password?</RouterLink>
            </div>
            <div v-if="error" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">{{ error }}</div>
            <div v-if="mfaRequired" class="space-y-3">
              <div class="flex items-center gap-2 rounded-xl border border-amber-800/40 bg-amber-950/40 px-4 py-3"><ShieldCheck class="h-4 w-4 text-amber-400 shrink-0"/><p class="text-sm font-semibold text-amber-300">2-factor authentication required</p></div>
              <input v-model="mfaCode" type="text" inputmode="numeric" maxlength="6" placeholder="6-digit code" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 text-center text-sm tracking-[0.4em] text-white placeholder:tracking-normal placeholder:text-emerald-700 outline-none focus:border-emerald-600/60 transition-all" @keyup.enter="submitMfa" />
              <p v-if="mfaError" class="text-xs text-red-400">{{ mfaError }}</p>
              <button type="button" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#0e7a61,#0d9488)" :disabled="mfaCode.trim().length<6||auth.isLoading" @click="submitMfa"><Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Verifying…':'Verify identity' }}</button>
              <button type="button" class="w-full text-center text-xs text-emerald-600 hover:text-emerald-400 transition-colors" @click="mfaRequired=false;mfaCode='';mfaError=''">← Back to sign in</button>
            </div>
            <button v-if="!mfaRequired" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 hover:brightness-110 active:scale-[0.98]" style="background:linear-gradient(135deg,#0e7a61,#0d9488);box-shadow:0 0 20px rgba(14,122,97,0.4)" :disabled="!canSubmit" type="submit">
              <Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Signing in…':'Sign in to GradeCrest' }}
            </button>
          </form>

          <div v-else class="space-y-4">
            <template v-if="magicState!=='sent'">
              <p class="text-sm text-emerald-200/40">Enter your email and we'll beam a one-click sign-in link. Works once, expires in 15 minutes.</p>
              <input v-model="magicEmail" class="h-11 w-full rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 text-sm text-white placeholder:text-emerald-700 outline-none focus:border-emerald-600/60 transition-all" type="email" autocomplete="email" placeholder="you@example.com" @keydown.enter.prevent="canSendMagic&&sendMagicLink()" />
              <div v-if="magicError" class="text-sm text-red-400">{{ magicError }}</div>
              <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#0e7a61,#0d9488)" :disabled="!canSendMagic" type="button" @click="sendMagicLink"><Loader2 v-if="magicState==='sending'" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ magicState==='sending'?'Sending…':'Send magic link' }}</button>
            </template>
            <template v-else>
              <div class="rounded-xl border border-emerald-800/40 bg-emerald-900/30 p-5 text-center"><Mail class="mx-auto h-7 w-7 text-emerald-400"/><p class="mt-3 font-bold text-white">Link sent!</p><p class="mt-1 text-sm text-emerald-200/50">Check <strong class="text-emerald-300">{{ magicEmail }}</strong> — link expires in 15 min.</p></div>
              <button class="w-full text-center text-xs text-emerald-600 hover:text-emerald-400" type="button" @click="magicState='idle';magicError=''">Try a different email</button>
            </template>
          </div>
        </div>

        <p class="text-center text-sm text-emerald-700">New to GradeCrest? <RouterLink to="/auth/register" class="font-semibold text-emerald-400 hover:text-emerald-300 hover:underline">Create a free account</RouterLink></p>
        <div v-if="isDev" class="rounded-xl border border-emerald-900/40 bg-[#0a2318]/50 p-4 backdrop-blur-sm"><p class="font-mono text-[10px] text-emerald-700 mb-2">// dev preview</p><div class="grid grid-cols-3 gap-2"><button v-for="r in previewRoles" :key="r" class="h-8 rounded-lg border border-emerald-900/40 bg-emerald-950/30 text-xs font-semibold capitalize text-emerald-400/60 hover:text-emerald-300 transition-all" type="button" @click="preview(r as UserRole)">{{ r }}</button></div></div>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       ESSAYMANIACS — Electric purple, bold typographic energy
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else-if="brandSlug === 'essaymaniacs'" class="relative min-h-screen overflow-hidden bg-[#1a0535] font-sans flex items-center justify-center">
    <!-- Giant ESSAY bg text -->
    <div class="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden select-none" aria-hidden="true">
      <span class="text-[28vw] font-black leading-none text-purple-950/50 tracking-tighter">ESSAY</span>
    </div>
    <!-- Glow blobs -->
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div class="absolute -top-20 left-1/4 h-80 w-80 rounded-full bg-purple-700/25 blur-[100px]"/>
      <div class="absolute bottom-0 right-1/3 h-72 w-72 rounded-full bg-violet-500/20 blur-[80px]"/>
    </div>
    <!-- Floating punctuation -->
    <div class="pointer-events-none absolute inset-0 overflow-hidden select-none" aria-hidden="true">
      <span class="absolute top-16 left-[8%] text-7xl font-serif text-purple-600/20 leading-none">"</span>
      <span class="absolute top-1/3 left-[3%] text-5xl font-serif text-violet-500/15 leading-none">¶</span>
      <span class="absolute bottom-24 left-[12%] text-8xl font-serif text-purple-700/20 leading-none">"</span>
      <span class="absolute top-10 right-[10%] text-6xl font-serif text-purple-500/15 leading-none">§</span>
      <span class="absolute bottom-16 right-[8%] text-7xl font-serif text-violet-600/20 leading-none">…</span>
    </div>

    <!-- Content: two columns -->
    <div class="relative z-10 flex w-full max-w-5xl items-center gap-12 px-8 py-12">

      <!-- LEFT COPY -->
      <div class="hidden lg:block flex-1 space-y-6">
        <p class="font-mono text-[10px] font-bold uppercase tracking-[0.35em] text-purple-400">// word nerd headquarters</p>
        <h1 class="text-6xl font-black leading-[1.0] text-white">
          Essays that<br/>
          <span class="bg-gradient-to-r from-purple-400 via-fuchsia-400 to-violet-300 bg-clip-text text-transparent">hit different.</span>
        </h1>
        <p class="text-lg text-purple-200/50 max-w-sm leading-relaxed">Academic writing by people who are genuinely obsessed with words, structure, and your grade.</p>
        <div class="flex flex-wrap gap-2 pt-1">
          <span v-for="t in ['Plagiarism-free','Any subject','24/7 support','Grades guaranteed']" :key="t" class="rounded-full border border-purple-800/40 bg-purple-900/30 px-3 py-1 text-xs font-medium text-purple-300/70">{{ t }}</span>
        </div>
        <div class="flex gap-8 pt-2">
          <div v-for="s in [['200k+','Essays written'],['4.8★','Avg. rating'],['3hrs','Fastest delivery']]" :key="s[0]">
            <p class="text-2xl font-black text-white">{{ s[0] }}</p>
            <p class="text-xs text-purple-400/50 mt-0.5">{{ s[1] }}</p>
          </div>
        </div>
      </div>

      <!-- FORM CARD: white on purple -->
      <div class="w-full max-w-[400px] shrink-0 space-y-4">
        <!-- Mobile heading -->
        <div class="lg:hidden space-y-2 text-center mb-4">
          <h1 class="text-3xl font-black text-white">Essays that <span class="text-purple-400">hit different.</span></h1>
        </div>

        <div class="rounded-2xl bg-white p-7 shadow-2xl shadow-purple-900/60 space-y-5">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Sign in to EssayManiacs</h2>
            <p class="text-sm text-slate-400 mt-0.5">Back to your word nerd portal.</p>
          </div>

          <div class="flex gap-1 rounded-xl bg-slate-100 p-1">
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='password'?'bg-white text-slate-900 shadow-sm':'text-slate-500 hover:text-slate-700'" type="button" @click="tab='password';error='';mfaRequired=false">Password</button>
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='magic'?'bg-white text-slate-900 shadow-sm':'text-slate-500 hover:text-slate-700'" type="button" @click="tab='magic';magicState='idle';magicError=''">Magic link</button>
          </div>

          <form v-if="tab==='password'" class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5" for="em-email">Email</label>
              <input id="em-email" v-model="form.email" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" type="email" autocomplete="email" placeholder="you@example.com" required />
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5" for="em-pw">Password</label>
              <div class="relative">
                <input id="em-pw" v-model="form.password" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" :type="showPassword?'text':'password'" autocomplete="current-password" placeholder="••••••••" required />
                <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
              </div>
              <RouterLink tabindex="-1" class="mt-1.5 block text-right text-xs text-purple-500 hover:text-purple-700 transition-colors" :to="forgotLink">Forgot password?</RouterLink>
            </div>
            <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
            <div v-if="mfaRequired" class="space-y-3">
              <div class="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3"><ShieldCheck class="h-4 w-4 text-amber-500 shrink-0"/><p class="text-sm font-semibold text-amber-800">2-factor auth required</p></div>
              <input v-model="mfaCode" type="text" inputmode="numeric" maxlength="6" placeholder="6-digit code" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-center text-sm tracking-[0.4em] text-slate-900 placeholder:tracking-normal placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" @keyup.enter="submitMfa" />
              <p v-if="mfaError" class="text-xs text-rose-500">{{ mfaError }}</p>
              <button type="button" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 hover:brightness-105 active:scale-[0.98]" style="background:linear-gradient(135deg,#7c3aed,#6d28d9)" :disabled="mfaCode.trim().length<6||auth.isLoading" @click="submitMfa"><Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Verifying…':'Verify' }}</button>
              <button type="button" class="w-full text-center text-xs text-slate-400 hover:text-slate-600" @click="mfaRequired=false;mfaCode='';mfaError=''">← Back to sign in</button>
            </div>
            <button v-if="!mfaRequired" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 hover:brightness-105 active:scale-[0.98]" style="background:linear-gradient(135deg,#7c3aed,#6d28d9);box-shadow:0 0 24px rgba(124,58,237,0.35)" :disabled="!canSubmit" type="submit">
              <Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Loading…':'Sign in' }}
            </button>
          </form>

          <div v-else class="space-y-4">
            <template v-if="magicState!=='sent'">
              <p class="text-sm text-slate-500">One-click sign-in link, straight to your inbox. Expires in 15 minutes.</p>
              <input v-model="magicEmail" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all" type="email" autocomplete="email" placeholder="you@example.com" @keydown.enter.prevent="canSendMagic&&sendMagicLink()" />
              <div v-if="magicError" class="text-sm text-rose-500">{{ magicError }}</div>
              <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#7c3aed,#6d28d9)" :disabled="!canSendMagic" type="button" @click="sendMagicLink"><Loader2 v-if="magicState==='sending'" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ magicState==='sending'?'Sending…':'Send magic link' }}</button>
            </template>
            <template v-else>
              <div class="rounded-xl border border-purple-200 bg-purple-50 p-5 text-center"><Mail class="mx-auto h-7 w-7 text-purple-500"/><p class="mt-3 font-bold text-slate-900">Check your inbox!</p><p class="mt-1 text-sm text-slate-500">Link sent to <strong>{{ magicEmail }}</strong>. One-time use, 15 min.</p></div>
              <button class="w-full text-center text-xs text-slate-400 hover:text-slate-600" type="button" @click="magicState='idle';magicError=''">Try a different email</button>
            </template>
          </div>
        </div>

        <p class="text-center text-sm text-purple-400/60">New here? <RouterLink to="/auth/register" class="font-semibold text-purple-300 hover:text-white hover:underline">Create a free account</RouterLink></p>
        <div v-if="isDev" class="rounded-xl border border-purple-900/40 bg-purple-950/30 p-4"><p class="font-mono text-[10px] text-purple-700 mb-2">// dev preview</p><div class="grid grid-cols-3 gap-2"><button v-for="r in previewRoles" :key="r" class="h-8 rounded-lg border border-purple-800/30 text-xs font-semibold capitalize text-purple-400/50 hover:text-purple-300 transition-all" type="button" @click="preview(r as UserRole)">{{ r }}</button></div></div>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       NURSEMYGRADE — Clinical split: clean white left, teal right
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else-if="brandSlug === 'nursemygrade'" class="min-h-screen flex font-sans">

    <!-- LEFT: white clinical panel -->
    <div class="hidden lg:flex lg:w-[48%] flex-col justify-between bg-white px-12 py-12 border-r border-slate-100">
      <!-- Logo -->
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-600">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="white" stroke-width="2.5" stroke-linecap="round"/></svg>
        </div>
        <span class="text-base font-bold text-slate-800 tracking-tight">NurseMyGrade</span>
      </div>

      <!-- Hero content -->
      <div class="space-y-6">
        <!-- ECG decoration -->
        <div class="text-teal-200 select-none" aria-hidden="true">
          <svg width="200" height="40" viewBox="0 0 200 40" fill="none"><polyline points="0,20 30,20 40,5 50,35 60,20 80,20 90,10 100,30 110,20 200,20" stroke="#0d9488" stroke-width="1.5" fill="none" opacity="0.4"/></svg>
        </div>
        <h1 class="text-4xl font-black leading-[1.1] text-slate-900">
          Nursing papers<br/>
          <span class="text-teal-600">by actual nurses.</span>
        </h1>
        <p class="text-base text-slate-500 max-w-sm leading-relaxed">Peer-reviewed quality. Clinical precision. Delivered to your deadline — by verified healthcare professionals.</p>
        <!-- Trust badges -->
        <div class="grid grid-cols-2 gap-3">
          <div v-for="b in [['🎓','Verified RN writers'],['📋','APA / AMA / MLA'],['🔒','HIPAA-aware handling'],['⚡','4h rush available']]" :key="b[0]" class="flex items-center gap-2 rounded-xl bg-teal-50 border border-teal-100 px-3 py-2.5">
            <span class="text-lg leading-none">{{ b[0] }}</span>
            <span class="text-xs font-medium text-teal-800">{{ b[1] }}</span>
          </div>
        </div>
      </div>

      <!-- Footer cite -->
      <div class="flex items-center gap-3 border-t border-slate-100 pt-5">
        <div class="flex -space-x-2">
          <div v-for="i in 4" :key="i" class="h-8 w-8 rounded-full border-2 border-white" :style="`background:hsl(${170+i*10},50%,${40+i*5}%)`"/>
        </div>
        <p class="text-xs text-slate-400">Trusted by 30,000+ nursing students worldwide</p>
      </div>
    </div>

    <!-- RIGHT: teal panel with form -->
    <div class="flex flex-1 items-center justify-center bg-[#0f766e] px-8 py-12">
      <div class="w-full max-w-[390px] space-y-4">
        <!-- Mobile logo -->
        <div class="flex items-center gap-2 mb-5 lg:hidden">
          <div class="h-8 w-8 rounded-xl bg-white/20 flex items-center justify-center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="white" stroke-width="2.5" stroke-linecap="round"/></svg></div>
          <span class="text-sm font-bold text-white">NurseMyGrade</span>
        </div>

        <div class="rounded-2xl bg-white p-7 shadow-2xl shadow-teal-900/30 space-y-5">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Sign in to your account</h2>
            <p class="text-sm text-slate-400 mt-0.5">Access your orders and drafts.</p>
          </div>

          <div class="flex gap-1 rounded-xl bg-slate-100 p-1">
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='password'?'bg-white text-slate-900 shadow-sm':'text-slate-500 hover:text-slate-700'" type="button" @click="tab='password';error='';mfaRequired=false">Password</button>
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='magic'?'bg-white text-slate-900 shadow-sm':'text-slate-500 hover:text-slate-700'" type="button" @click="tab='magic';magicState='idle';magicError=''">Magic link</button>
          </div>

          <form v-if="tab==='password'" class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5" for="nmg-email">Email</label>
              <input id="nmg-email" v-model="form.email" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" type="email" autocomplete="email" placeholder="nurse@example.com" required />
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5" for="nmg-pw">Password</label>
              <div class="relative">
                <input id="nmg-pw" v-model="form.password" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 pr-10 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" :type="showPassword?'text':'password'" autocomplete="current-password" placeholder="••••••••" required />
                <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-teal-500 transition-colors" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
              </div>
              <RouterLink tabindex="-1" class="mt-1.5 block text-right text-xs text-teal-600 hover:text-teal-800 transition-colors" :to="forgotLink">Forgot password?</RouterLink>
            </div>
            <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
            <div v-if="mfaRequired" class="space-y-3">
              <div class="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3"><ShieldCheck class="h-4 w-4 text-amber-500 shrink-0"/><p class="text-sm font-semibold text-amber-800">2-factor auth required</p></div>
              <input v-model="mfaCode" type="text" inputmode="numeric" maxlength="6" placeholder="6-digit code" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-center text-sm tracking-[0.4em] text-slate-900 placeholder:tracking-normal placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" @keyup.enter="submitMfa" />
              <p v-if="mfaError" class="text-xs text-rose-500">{{ mfaError }}</p>
              <button type="button" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#0f766e,#0d9488)" :disabled="mfaCode.trim().length<6||auth.isLoading" @click="submitMfa"><Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Verifying…':'Verify' }}</button>
              <button type="button" class="w-full text-center text-xs text-slate-400 hover:text-slate-600" @click="mfaRequired=false;mfaCode='';mfaError=''">← Back to sign in</button>
            </div>
            <button v-if="!mfaRequired" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 active:scale-[0.98]" style="background:linear-gradient(135deg,#0f766e,#0d9488);box-shadow:0 4px 14px rgba(15,118,110,0.4)" :disabled="!canSubmit" type="submit">
              <Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Signing in…':'Sign in' }}
            </button>
          </form>

          <div v-else class="space-y-4">
            <template v-if="magicState!=='sent'">
              <p class="text-sm text-slate-500">One-click sign-in link to your inbox. No password required.</p>
              <input v-model="magicEmail" class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm text-slate-900 placeholder:text-slate-300 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition-all" type="email" autocomplete="email" placeholder="nurse@example.com" @keydown.enter.prevent="canSendMagic&&sendMagicLink()" />
              <div v-if="magicError" class="text-sm text-rose-500">{{ magicError }}</div>
              <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#0f766e,#0d9488)" :disabled="!canSendMagic" type="button" @click="sendMagicLink"><Loader2 v-if="magicState==='sending'" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ magicState==='sending'?'Sending…':'Send magic link' }}</button>
            </template>
            <template v-else>
              <div class="rounded-xl border border-teal-200 bg-teal-50 p-5 text-center"><Mail class="mx-auto h-7 w-7 text-teal-500"/><p class="mt-3 font-bold text-slate-900">Check your inbox</p><p class="mt-1 text-sm text-slate-500">Link sent to <strong>{{ magicEmail }}</strong>.</p></div>
              <button class="w-full text-center text-xs text-slate-400 hover:text-slate-600" type="button" @click="magicState='idle';magicError=''">Try a different email</button>
            </template>
          </div>
        </div>

        <p class="text-center text-sm text-teal-200/60">New to NurseMyGrade? <RouterLink to="/auth/register" class="font-semibold text-white hover:underline">Create a free account</RouterLink></p>
        <div v-if="isDev" class="rounded-xl border border-teal-800/40 bg-teal-900/30 p-4"><p class="font-mono text-[10px] text-teal-600 mb-2">// dev preview</p><div class="grid grid-cols-3 gap-2"><button v-for="r in previewRoles" :key="r" class="h-8 rounded-lg border border-teal-800/30 text-xs font-semibold capitalize text-teal-300/50 hover:text-teal-200 transition-all" type="button" @click="preview(r as UserRole)">{{ r }}</button></div></div>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       RESEARCHPAPERMATE — Deep navy, scholarly journal aesthetic
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else-if="brandSlug === 'researchpapermate'" class="relative min-h-screen flex overflow-hidden bg-[#080f2a] font-sans">
    <!-- Lined paper texture -->
    <div class="pointer-events-none absolute inset-0" style="background-image:repeating-linear-gradient(transparent,transparent 47px,rgba(59,130,246,0.05) 47px,rgba(59,130,246,0.05) 48px);" aria-hidden="true"/>
    <!-- Glow -->
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div class="absolute top-0 left-1/3 h-96 w-96 rounded-full bg-blue-900/30 blur-[120px]"/>
      <div class="absolute bottom-0 right-1/4 h-80 w-80 rounded-full bg-cyan-900/20 blur-[100px]"/>
    </div>

    <!-- LEFT PANEL -->
    <div class="relative z-10 hidden lg:flex w-[58%] flex-col justify-between p-14 border-r border-blue-900/30">
      <!-- Top: journal header decoration -->
      <div class="space-y-1">
        <div class="flex items-center gap-4">
          <div class="h-10 w-10 rounded-xl bg-blue-900/60 border border-blue-800/60 flex items-center justify-center">
            <span class="font-black text-cyan-400 text-sm">R</span>
          </div>
          <div>
            <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.35em] text-blue-400/50">ResearchPaperMate</p>
            <p class="font-mono text-[9px] text-blue-600/40">Vol. I — Academic Writing Services</p>
          </div>
        </div>
      </div>

      <!-- Center: main content -->
      <div class="space-y-6">
        <!-- Abstract-style note -->
        <p class="font-mono text-xs text-blue-400/35 border-l-2 border-blue-800/40 pl-4">¹ Abstract: Reliable academic writing by humans,<br/>from $15/page. Cited. Formatted. Delivered.</p>

        <h1 class="text-5xl font-black leading-[1.08] text-white">
          Research-grade<br/>writing.
          <span class="text-cyan-400"> Cited.<br/>Structured. Yours.</span>
        </h1>
        <p class="text-base text-blue-200/45 max-w-sm leading-relaxed">Every paper written to exact academic standards, properly cited, formatted to spec, and delivered before your deadline.</p>

        <!-- Methodology-style stats boxes -->
        <div class="grid grid-cols-3 gap-3 pt-1">
          <div v-for="s in [['45k+','Papers delivered'],['98.6%','On-time rate'],['$15','From per page']]" :key="s[0]" class="rounded-xl border border-blue-900/50 bg-blue-950/40 p-3 text-center">
            <p class="text-xl font-black text-white">{{ s[0] }}</p>
            <p class="text-[10px] text-blue-400/50 mt-0.5">{{ s[1] }}</p>
          </div>
        </div>
      </div>

      <!-- Footer: keywords -->
      <div class="font-mono text-[10px] text-blue-700/40 space-y-1">
        <p>Keywords: reliability, citation accuracy, originality, deadline adherence</p>
        <p>DOI: research-paper-mate/academic-writing-services/2026</p>
      </div>
    </div>

    <!-- RIGHT PANEL: form -->
    <div class="relative z-10 flex flex-1 items-center justify-center px-8 py-12 bg-[#0d1b3e]/60">
      <div class="w-full max-w-[390px] space-y-4">
        <!-- Mobile logo -->
        <div class="flex items-center gap-2 mb-5 lg:hidden">
          <div class="h-8 w-8 rounded-xl bg-blue-900/60 border border-blue-800/40 flex items-center justify-center"><span class="font-black text-cyan-400 text-sm">R</span></div>
          <span class="font-mono text-xs font-semibold uppercase tracking-widest text-blue-300/60">ResearchPaperMate</span>
        </div>

        <div class="rounded-2xl border border-blue-900/50 bg-[#0d1b3e]/90 p-7 shadow-2xl shadow-black/70 backdrop-blur-sm space-y-5">
          <div>
            <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-cyan-500/70 mb-1.5">// Secure sign-in</p>
            <h2 class="text-xl font-bold text-white">Sign in to your account</h2>
            <p class="text-sm text-blue-200/35 mt-0.5">Access your research portal.</p>
          </div>

          <div class="flex gap-1 rounded-xl border border-blue-900/50 bg-[#080f2a]/60 p-1">
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='password'?'bg-blue-900/60 text-white shadow-sm':'text-blue-400/50 hover:text-blue-300'" type="button" @click="tab='password';error='';mfaRequired=false">Password</button>
            <button class="flex-1 rounded-lg py-2 text-xs font-semibold transition-all" :class="tab==='magic'?'bg-blue-900/60 text-white shadow-sm':'text-blue-400/50 hover:text-blue-300'" type="button" @click="tab='magic';magicState='idle';magicError=''">Magic link</button>
          </div>

          <form v-if="tab==='password'" class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="block text-[10px] font-semibold uppercase tracking-[0.3em] text-blue-400/50 mb-1.5" for="rpm-email">Email</label>
              <input id="rpm-email" v-model="form.email" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 text-sm text-white placeholder:text-blue-800 outline-none focus:border-cyan-700/60 focus:ring-2 focus:ring-cyan-700/20 transition-all" type="email" autocomplete="email" placeholder="researcher@example.com" required />
            </div>
            <div>
              <label class="block text-[10px] font-semibold uppercase tracking-[0.3em] text-blue-400/50 mb-1.5" for="rpm-pw">Password</label>
              <div class="relative">
                <input id="rpm-pw" v-model="form.password" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 pr-10 text-sm text-white placeholder:text-blue-800 outline-none focus:border-cyan-700/60 focus:ring-2 focus:ring-cyan-700/20 transition-all" :type="showPassword?'text':'password'" autocomplete="current-password" placeholder="••••••••" required />
                <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-blue-800 hover:text-cyan-400 transition-colors" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
              </div>
              <RouterLink tabindex="-1" class="mt-1.5 block text-right text-xs text-cyan-600/70 hover:text-cyan-400 transition-colors" :to="forgotLink">Forgot password?</RouterLink>
            </div>
            <div v-if="error" class="rounded-xl border border-red-900/40 bg-red-950/40 px-4 py-3 text-sm text-red-300">{{ error }}</div>
            <div v-if="mfaRequired" class="space-y-3">
              <div class="flex items-center gap-2 rounded-xl border border-amber-800/40 bg-amber-950/40 px-4 py-3"><ShieldCheck class="h-4 w-4 text-amber-400 shrink-0"/><p class="text-sm font-semibold text-amber-300">2-factor auth required</p></div>
              <input v-model="mfaCode" type="text" inputmode="numeric" maxlength="6" placeholder="6-digit code" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 text-center text-sm tracking-[0.4em] text-white placeholder:tracking-normal placeholder:text-blue-800 outline-none focus:border-cyan-700/60 transition-all" @keyup.enter="submitMfa" />
              <p v-if="mfaError" class="text-xs text-red-400">{{ mfaError }}</p>
              <button type="button" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#163e88,#1e40af)" :disabled="mfaCode.trim().length<6||auth.isLoading" @click="submitMfa"><Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Verifying…':'Verify' }}</button>
              <button type="button" class="w-full text-center text-xs text-blue-600 hover:text-blue-400 transition-colors" @click="mfaRequired=false;mfaCode='';mfaError=''">← Back to sign in</button>
            </div>
            <button v-if="!mfaRequired" class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 hover:brightness-110 active:scale-[0.98]" style="background:linear-gradient(135deg,#163e88,#1e40af,#0e7490);box-shadow:0 0 20px rgba(22,62,136,0.5)" :disabled="!canSubmit" type="submit">
              <Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Signing in…':'Sign in' }}
            </button>
          </form>

          <div v-else class="space-y-4">
            <template v-if="magicState!=='sent'">
              <p class="text-sm text-blue-200/40">One-click sign-in link. No password required. Expires in 15 minutes.</p>
              <input v-model="magicEmail" class="h-11 w-full rounded-xl border border-blue-900/50 bg-blue-950/40 px-4 text-sm text-white placeholder:text-blue-800 outline-none focus:border-cyan-700/60 transition-all" type="email" autocomplete="email" placeholder="researcher@example.com" @keydown.enter.prevent="canSendMagic&&sendMagicLink()" />
              <div v-if="magicError" class="text-sm text-red-400">{{ magicError }}</div>
              <button class="h-11 w-full rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50" style="background:linear-gradient(135deg,#163e88,#1e40af)" :disabled="!canSendMagic" type="button" @click="sendMagicLink"><Loader2 v-if="magicState==='sending'" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ magicState==='sending'?'Sending…':'Send magic link' }}</button>
            </template>
            <template v-else>
              <div class="rounded-xl border border-cyan-900/40 bg-cyan-950/30 p-5 text-center"><Mail class="mx-auto h-7 w-7 text-cyan-400"/><p class="mt-3 font-bold text-white">Transmission sent</p><p class="mt-1 text-sm text-blue-200/40">Link dispatched to <strong class="text-blue-200/70">{{ magicEmail }}</strong>.</p></div>
              <button class="w-full text-center text-xs text-blue-600 hover:text-blue-400" type="button" @click="magicState='idle';magicError=''">Try a different email</button>
            </template>
          </div>
        </div>

        <p class="text-center text-sm text-blue-700">New here? <RouterLink to="/auth/register" class="font-semibold text-cyan-400 hover:text-cyan-300 hover:underline">Create a free account</RouterLink></p>
        <div v-if="isDev" class="rounded-xl border border-blue-900/40 bg-blue-950/30 p-4"><p class="font-mono text-[10px] text-blue-700 mb-2">// dev preview</p><div class="grid grid-cols-3 gap-2"><button v-for="r in previewRoles" :key="r" class="h-8 rounded-lg border border-blue-900/30 text-xs font-semibold capitalize text-blue-400/40 hover:text-blue-300 transition-all" type="button" @click="preview(r as UserRole)">{{ r }}</button></div></div>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       GENERIC FALLBACK — clean minimal (dev / unbranded)
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else class="grid min-h-screen place-items-center bg-slate-50 px-4 py-10">
    <section class="w-full max-w-md">
      <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">
        <div class="mb-6">
          <div v-if="isBranded" class="mb-4 flex items-center gap-3">
            <img v-if="brandLogo" :src="brandLogo" :alt="brandName" class="h-9 w-auto object-contain" />
            <span v-else class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-ink">{{ brandName.slice(0,2).toUpperCase() }}</span>
            <span class="text-base font-semibold text-ink">{{ brandName }}</span>
          </div>
          <h1 class="text-2xl font-semibold tracking-tight text-ink">{{ isBranded ? `Sign in to ${brandName}` : "Sign in" }}</h1>
          <p class="mt-1.5 text-sm text-graphite">Use your account email and password to continue.</p>
        </div>
        <div class="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
          <button class="flex-1 rounded-md py-2 text-xs font-semibold transition-all" :class="tab==='password'?'bg-white text-ink shadow-sm':'text-graphite hover:text-ink'" type="button" @click="tab='password';error='';mfaRequired=false">Password</button>
          <button class="flex-1 rounded-md py-2 text-xs font-semibold transition-all" :class="tab==='magic'?'bg-white text-ink shadow-sm':'text-graphite hover:text-ink'" type="button" @click="tab='magic';magicState='idle';magicError=''">Magic link</button>
        </div>
        <form v-if="tab==='password'" class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink" for="fb-email">Email</label>
            <input id="fb-email" v-model="form.email" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors" autocomplete="email" type="email" placeholder="you@example.com" required />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink" for="fb-pw">Password</label>
            <div class="relative">
              <input id="fb-pw" v-model="form.password" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 pr-10 text-sm placeholder:text-slate-400 transition-colors" autocomplete="current-password" :type="showPassword?'text':'password'" placeholder="••••••••" required />
              <button type="button" tabindex="-1" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" class="h-4 w-4"/><Eye v-else class="h-4 w-4"/></button>
            </div>
            <RouterLink tabindex="-1" class="mt-1.5 block text-right text-xs font-medium text-signal hover:underline" :to="forgotLink">Forgot password?</RouterLink>
          </div>
          <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800">{{ error }}</div>
          <div v-if="mfaRequired" class="space-y-3">
            <div class="flex items-center gap-2 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3"><ShieldCheck class="h-4 w-4 text-amber-600 shrink-0"/><p class="text-sm font-semibold text-amber-900">Two-factor authentication required</p></div>
            <input v-model="mfaCode" type="text" inputmode="numeric" maxlength="6" placeholder="6-digit code" class="focus-ring h-11 w-full rounded-lg border border-slate-200 px-3 text-center text-sm tracking-widest placeholder:tracking-normal placeholder:text-slate-400" @keyup.enter="submitMfa" />
            <p v-if="mfaError" class="text-xs text-rose-600">{{ mfaError }}</p>
            <button type="button" class="focus-ring h-11 w-full rounded-lg bg-ink text-sm font-semibold text-white disabled:opacity-60" :disabled="mfaCode.trim().length<6||auth.isLoading" @click="submitMfa"><Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Verifying…':'Verify' }}</button>
            <button type="button" class="w-full text-center text-xs text-graphite hover:underline" @click="mfaRequired=false;mfaCode='';mfaError=''">Back to sign in</button>
          </div>
          <button v-if="!mfaRequired" class="focus-ring h-11 w-full rounded-lg bg-ink text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.98] disabled:opacity-60" :disabled="!canSubmit" type="submit"><Loader2 v-if="auth.isLoading" class="inline h-4 w-4 animate-spin mr-2"/>{{ auth.isLoading?'Signing in…':'Sign in' }}</button>
        </form>
        <div v-else class="space-y-4">
          <template v-if="magicState!=='sent'">
            <p class="text-sm text-graphite">One-click sign-in link to your inbox. Expires in 15 minutes.</p>
            <input v-model="magicEmail" class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors" autocomplete="email" type="email" placeholder="you@example.com" @keydown.enter.prevent="canSendMagic&&sendMagicLink()" />
            <div v-if="magicError" class="rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800">{{ magicError }}</div>
            <button class="focus-ring h-11 w-full rounded-lg bg-ink text-sm font-semibold text-white disabled:opacity-60" :disabled="!canSendMagic" type="button" @click="sendMagicLink"><Loader2 v-if="magicState==='sending'" class="inline h-4 w-4 animate-spin mr-2"/><Mail v-else class="inline h-4 w-4 mr-2"/>{{ magicState==='sending'?'Sending…':'Send magic link' }}</button>
          </template>
          <template v-else>
            <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-5 text-center"><Mail class="mx-auto h-8 w-8 text-emerald-500"/><p class="mt-3 font-semibold text-emerald-900">Check your inbox</p><p class="mt-1 text-sm text-emerald-800">Link sent to <strong>{{ magicEmail }}</strong>.</p></div>
            <button class="w-full text-center text-xs text-graphite hover:underline" type="button" @click="magicState='idle';magicError=''">Try a different email</button>
          </template>
        </div>
      </div>
      <p class="mt-4 text-center text-sm text-graphite">New here? <RouterLink to="/auth/register" class="ml-1 font-semibold text-berry hover:underline">Create a free account</RouterLink></p>
      <div v-if="isDev" class="mt-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wider text-graphite">Preview workspace</p>
        <div class="mt-3 grid grid-cols-3 gap-2">
          <button v-for="r in previewRoles" :key="r" class="focus-ring h-9 rounded-lg border border-slate-200 bg-slate-50 px-2 text-xs font-semibold capitalize text-ink transition-colors hover:bg-white" type="button" @click="preview(r as UserRole)">{{ r }}</button>
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
