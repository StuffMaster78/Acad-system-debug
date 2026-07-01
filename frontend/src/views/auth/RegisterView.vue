<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, Eye, EyeOff, Loader2, LogIn, Mail, Shield } from "@lucide/vue";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { getStoredUtm, clearStoredUtm } from "@/composables/useUtm";
import { useAnalytics } from "@/composables/useAnalytics";

// ─── Writer cosmos: stars ────────────────────────────────────────────────────
function hashRng(seed: number) {
  const s = Math.sin(seed) * 43758.5453123;
  return s - Math.floor(s);
}
const STARS = Array.from({ length: 140 }, (_, i) => ({
  x: hashRng(i * 127.1) * 100,
  y: hashRng(i * 311.7) * 100,
  r: [1, 1, 1, 1, 1.5, 2][Math.floor(hashRng(i * 52.7) * 6)],
  op: 0.3 + hashRng(i * 231.3) * 0.65,
  dur: `${3 + hashRng(i * 79.3) * 5}s`,
  del: `${hashRng(i * 193.1) * 8}s`,
}));

const router  = useRouter();
const auth    = useAuthStore();
const portal  = usePortalContextStore();
const { signUp } = useAnalytics();

// ── Step management ───────────────────────────────────────────────────────────
type Step = "form" | "verify";
const step = ref<Step>("form");

// ── Registration form ─────────────────────────────────────────────────────────
const form = reactive({
  email:      "",
  first_name: "",
  last_name:  "",
  password:   "",
  confirm:    "",
});

const showPassword = ref(false);
const agreedToTerms = ref(false);
const isSubmitting  = ref(false);
const formError     = ref("");

const brand = computed(() => portal.branding?.brand_name ?? "the platform")
const isWriterSurface = computed(() => portal.surface === "writer");

const passwordsMatch = computed(() =>
  !form.confirm || form.password === form.confirm
);

function slugifyEmail(email: string): string {
  return email.split("@")[0].replace(/[^a-z0-9]/gi, "_").toLowerCase().slice(0, 30)
    + "_" + Math.random().toString(36).slice(2, 6);
}

async function submitForm() {
  formError.value = "";
  if (!form.email || !form.password || !form.first_name) {
    formError.value = "Please fill in all required fields.";
    return;
  }
  if (form.password !== form.confirm) {
    formError.value = "Passwords do not match.";
    return;
  }
  if (form.password.length < 8) {
    formError.value = "Password must be at least 8 characters.";
    return;
  }
  if (!agreedToTerms.value) {
    formError.value = "Please accept the terms of service to continue.";
    return;
  }

  isSubmitting.value = true;
  try {
    const utm = getStoredUtm();
    await authApi.register({
      email:      form.email.trim().toLowerCase(),
      username:   slugifyEmail(form.email),
      first_name: form.first_name.trim(),
      last_name:  form.last_name.trim(),
      password:   form.password,
      ...utm,
    });
    step.value = "verify";
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string; errors?: string[] } } })
      ?.response?.data;
    formError.value = detail?.detail
      ?? detail?.errors?.join(" ")
      ?? "Registration failed. Please try again.";
  } finally {
    isSubmitting.value = false;
  }
}

// ── Email verification (OTP) ──────────────────────────────────────────────────
const otp = ref("");
const isVerifying = ref(false);
const verifyError = ref("");
const resent = ref(false);

// Token may arrive in URL if user clicked the email link
const urlParams = new URLSearchParams(window.location.search);
const tokenFromUrl = ref(urlParams.get("token") ?? "");

// If we land on /auth/register/confirm with a token, skip straight to verify
if (tokenFromUrl.value) step.value = "verify";

async function confirmEmail() {
  verifyError.value = "";
  if (!otp.value.trim()) {
    verifyError.value = "Please enter the code from your email.";
    return;
  }
  if (!tokenFromUrl.value) {
    verifyError.value = "Verification token missing. Click the link in your email.";
    return;
  }

  isVerifying.value = true;
  try {
    const { data } = await authApi.confirmRegistration(tokenFromUrl.value, otp.value.trim());
    clearStoredUtm();
    signUp("email");
    auth.adoptSession(
      { access: data.access_token ?? (data as any).access, refresh: data.refresh_token ?? (data as any).refresh },
      {
        id:        data.user?.id ?? (data as any).user_id,
        email:     data.user?.email ?? form.email,
        full_name: data.user?.full_name ?? `${form.first_name} ${form.last_name}`.trim(),
        role:      data.user?.role ?? (isWriterSurface.value ? "writer" : "client"),
      },
    );
    await router.push(portal.homeRoute);
  } catch {
    verifyError.value = "Invalid or expired code. Please try again or request a new one.";
  } finally {
    isVerifying.value = false;
  }
}

async function resendCode() {
  try {
    await authApi.resendRegistration(form.email || urlParams.get("email") || "");
    resent.value = true;
    setTimeout(() => { resent.value = false; }, 5000);
  } catch { /* non-fatal */ }
}
</script>

<template>
  <!-- ═══════════════════════════════════════════════════════════════
       WRITER SURFACE — Cosmos theme (invitation-only gate)
  ═══════════════════════════════════════════════════════════════ -->
  <div v-if="isWriterSurface" class="writer-cosmos relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden bg-[#04060f] font-sans px-5 py-16">

    <!-- Starfield -->
    <div class="pointer-events-none absolute inset-0 z-0" aria-hidden="true">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" class="absolute inset-0">
        <circle
          v-for="(s, i) in STARS" :key="i"
          :cx="`${s.x}%`" :cy="`${s.y}%`" :r="s.r"
          fill="white" :fill-opacity="s.op"
          :style="{ animation: `wink ${s.dur} ${s.del} ease-in-out infinite` }"
        />
      </svg>
    </div>

    <!-- Ambient glows -->
    <div class="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div class="absolute -left-32 -top-20 h-96 w-96 rounded-full bg-[#7c3aed]/18 blur-[120px]" />
      <div class="absolute -right-20 top-1/3 h-80 w-80 rounded-full bg-[#06b6d4]/12 blur-[100px]" />
      <div class="absolute bottom-0 left-1/2 h-72 w-[600px] -translate-x-1/2 rounded-full bg-[#8b5cf6]/10 blur-[120px]" />
    </div>

    <!-- Grid overlay -->
    <div
      class="pointer-events-none absolute inset-0 z-0 opacity-[0.025]"
      style="background-image:linear-gradient(rgba(139,92,246,0.5) 1px,transparent 1px),linear-gradient(90deg,rgba(139,92,246,0.5) 1px,transparent 1px);background-size:48px 48px;"
      aria-hidden="true"
    />

    <!-- Content -->
    <div class="relative z-10 w-full max-w-md space-y-6 text-center">

      <!-- Logo mark -->
      <div class="flex items-center justify-center gap-2.5">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-[#7c3aed]/20 ring-1 ring-[#7c3aed]/30">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="font-mono text-sm font-semibold tracking-widest text-white/60 uppercase">{{ brand }}</span>
      </div>

      <!-- Headline -->
      <div class="space-y-3">
        <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.3em] text-[#06b6d4]">// access control</p>
        <h1 class="text-4xl font-black leading-tight text-white">
          Writer access is<br/>
          <span class="bg-gradient-to-r from-[#8b5cf6] via-[#06b6d4] to-white bg-clip-text text-transparent">by invitation.</span>
        </h1>
        <p class="text-base text-white/45 max-w-sm mx-auto leading-relaxed">
          Writer accounts are provisioned by our team. If you've been invited, your credentials were sent by email.
        </p>
      </div>

      <!-- Glass card -->
      <div class="rounded-2xl border border-white/10 bg-[#0c1225]/70 p-6 shadow-2xl shadow-black/50 backdrop-blur-xl space-y-4 text-left">
        <div class="flex items-start gap-3.5 text-sm">
          <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#7c3aed]/20">
            <Shield class="size-3.5 text-[#a78bfa]" />
          </div>
          <p class="text-white/55">Accounts are created by administrators. Self-registration is not available on the writer portal.</p>
        </div>
        <div class="flex items-start gap-3.5 text-sm">
          <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#06b6d4]/20">
            <Mail class="size-3.5 text-[#06b6d4]" />
          </div>
          <p class="text-white/55">Check your email for login credentials. If you haven't received them, contact our admin team.</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="space-y-3">
        <RouterLink
          to="/writer/login"
          class="cosmos-btn inline-flex w-full items-center justify-center gap-2 rounded-xl py-3.5 text-sm font-bold text-white transition-all"
        >
          <LogIn class="size-4" />
          Sign in to your workspace
        </RouterLink>
        <RouterLink
          to="/apply"
          class="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-3 text-sm font-semibold text-white/60 hover:border-[#7c3aed]/40 hover:text-white/80 transition-all backdrop-blur-sm"
        >
          <ArrowRight class="size-4" />
          Apply to join the writer team
        </RouterLink>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       CLIENT / ALL OTHER SURFACES — clean minimal design
  ═══════════════════════════════════════════════════════════════ -->
  <div v-else class="flex min-h-screen flex-col bg-slate-50">

    <!-- Header -->
    <header class="flex h-16 items-center px-6 border-b border-slate-200 bg-white">
      <a href="/" class="text-base font-bold text-ink tracking-tight">
        {{ brand }}
      </a>
      <span class="ml-auto text-sm text-graphite">
        Already have an account?
        <RouterLink to="/auth/login" class="ml-1 font-semibold text-berry hover:underline">Sign in</RouterLink>
      </span>
    </header>

    <main class="flex flex-1 items-start justify-center px-4 py-12">
      <div class="w-full max-w-md space-y-6">

        <!-- ── REGISTRATION FORM ─────────────────────────────────────────── -->
        <template v-if="step === 'form'">
          <div class="text-center">
            <h1 class="text-2xl font-bold text-ink">Create your account</h1>
            <p class="mt-1.5 text-sm text-graphite">Place orders, track progress, download completed work.</p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm space-y-5">

            <!-- Error banner -->
            <div v-if="formError" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {{ formError }}
            </div>

            <!-- Name row -->
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-wide text-graphite">First name <span class="text-berry">*</span></span>
                <input
                  v-model="form.first_name"
                  type="text"
                  autocomplete="given-name"
                  placeholder="Jane"
                  class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm"
                />
              </label>
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Last name</span>
                <input
                  v-model="form.last_name"
                  type="text"
                  autocomplete="family-name"
                  placeholder="Smith"
                  class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm"
                />
              </label>
            </div>

            <!-- Email -->
            <label class="block space-y-1.5">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Email address <span class="text-berry">*</span></span>
              <input
                v-model="form.email"
                type="email"
                autocomplete="email"
                placeholder="jane@example.com"
                class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm"
              />
            </label>

            <!-- Password -->
            <label class="block space-y-1.5">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Password <span class="text-berry">*</span></span>
              <div class="relative mt-1">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="At least 8 characters"
                  class="focus-ring h-10 w-full rounded-lg border border-slate-200 px-3 pr-10 text-sm"
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-ink"
                  @click="showPassword = !showPassword"
                >
                  <EyeOff v-if="showPassword" class="size-4" />
                  <Eye v-else class="size-4" />
                </button>
              </div>
            </label>

            <!-- Confirm password -->
            <label class="block space-y-1.5">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Confirm password <span class="text-berry">*</span></span>
              <input
                v-model="form.confirm"
                type="password"
                autocomplete="new-password"
                placeholder="Repeat password"
                class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm"
                :class="!passwordsMatch ? 'border-rose-400' : ''"
              />
              <p v-if="!passwordsMatch" class="text-xs text-rose-600">Passwords do not match.</p>
            </label>

            <!-- Terms -->
            <label class="flex items-start gap-3 cursor-pointer text-sm text-graphite">
              <input v-model="agreedToTerms" type="checkbox" class="mt-0.5 rounded accent-berry" />
              <span>
                I agree to the
                <RouterLink to="/legal/terms_of_service" target="_blank" class="text-berry hover:underline">Terms of Service</RouterLink>
                and
                <RouterLink to="/legal/privacy_policy" target="_blank" class="text-berry hover:underline">Privacy Policy</RouterLink>.
              </span>
            </label>

            <!-- Submit -->
            <button
              :disabled="isSubmitting || !passwordsMatch"
              class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-xl bg-berry py-3 text-sm font-bold text-white shadow-sm hover:bg-rose-700 disabled:opacity-60 transition-colors"
              type="button"
              @click="submitForm"
            >
              <Loader2 v-if="isSubmitting" class="size-4 animate-spin" />
              <template v-else>
                Create account <ArrowRight class="size-4" />
              </template>
            </button>

          </div>

          <p class="text-center text-xs text-graphite">
            By creating an account you agree to receive transactional emails from {{ brand }}.
          </p>
        </template>

        <!-- ── EMAIL VERIFICATION (non-writer only) ──────────────────────── -->
        <template v-else>
          <div class="text-center">
            <div class="mx-auto mb-4 flex size-14 items-center justify-center rounded-full bg-berry/10">
              <Mail class="size-7 text-berry" />
            </div>
            <h1 class="text-2xl font-bold text-ink">Check your email</h1>
            <p class="mt-1.5 text-sm text-graphite max-w-sm mx-auto">
              We sent a 6-digit verification code to
              <strong class="text-ink">{{ form.email || "your email" }}</strong>.
              Enter it below to activate your account.
            </p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm space-y-5">

            <div v-if="verifyError" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {{ verifyError }}
            </div>

            <div v-if="resent" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              A new code has been sent to your email.
            </div>

            <label class="block space-y-1.5">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Verification code</span>
              <input
                v-model="otp"
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="6-digit code"
                class="focus-ring mt-1 h-12 w-full rounded-lg border border-slate-200 px-3 text-center text-xl font-mono tracking-widest"
                @keyup.enter="confirmEmail"
              />
            </label>

            <button
              :disabled="isVerifying || otp.length < 6"
              class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-xl bg-berry py-3 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-60 transition-colors"
              type="button"
              @click="confirmEmail"
            >
              <Loader2 v-if="isVerifying" class="size-4 animate-spin" />
              <template v-else>Verify &amp; continue <ArrowRight class="size-4" /></template>
            </button>

            <p class="text-center text-xs text-graphite">
              Didn't receive it?
              <button class="ml-1 text-berry hover:underline font-medium" @click="resendCode">Resend code</button>
            </p>
          </div>
        </template>

      </div>
    </main>
  </div>
</template>

<style scoped>
@keyframes wink {
  0%, 100% { opacity: var(--op, 0.6); }
  50%       { opacity: calc(var(--op, 0.6) * 0.2); }
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
.cosmos-btn:hover {
  box-shadow: 0 0 36px rgba(124, 58, 237, 0.5), 0 6px 20px rgba(0,0,0,0.5);
  filter: brightness(1.08);
}
</style>
