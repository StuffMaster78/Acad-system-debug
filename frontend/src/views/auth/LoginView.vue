<script setup lang="ts">
import { computed, reactive, ref } from "vue";
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
const brandName = computed(() => portalCtx.branding?.brand_name || "");
const brandLogo = computed(() => portalCtx.branding?.logo_url || "");

type Tab = "password" | "magic";
const tab = ref<Tab>("password");

const error = ref("");
const mfaRequired = ref(false);
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
  try {
    await auth.login(form);
    const redirect = route.query.redirect?.toString();
    await router.push(redirect || (auth.role ? roleHome[auth.role] : "/client"));
  } catch (err) {
    if (err instanceof MfaRequiredError) {
      mfaRequired.value = true;
    } else {
      error.value = "We could not sign you in with those details.";
    }
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
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md">
      <!-- Card -->
      <div class="rounded-lg border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">
        <!-- Header -->
        <div class="mb-6">
          <!-- Brand identity (shown when on a registered tenant domain) -->
          <div v-if="isBranded" class="mb-4 flex items-center gap-3">
            <img v-if="brandLogo" :src="brandLogo" :alt="brandName" class="h-9 w-auto object-contain" />
            <span v-else class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-ink">
              {{ brandName.slice(0, 2).toUpperCase() }}
            </span>
            <span class="text-base font-semibold text-ink">{{ brandName }}</span>
          </div>
          <h1 class="text-2xl font-semibold tracking-tight text-ink">
            {{ isBranded ? `Sign in to ${brandName}` : "Sign in" }}
          </h1>
          <p class="mt-1.5 text-sm text-graphite">
            {{ isBranded ? "Use your account email and password to continue." : "Use your platform account to open the correct workspace." }}
          </p>
        </div>

        <!-- Tab switcher -->
        <div class="mb-6 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
          <button
            class="flex-1 rounded-md py-2 text-xs font-semibold transition-all"
            :class="tab === 'password' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
            type="button"
            @click="tab = 'password'; error = ''; mfaRequired = false"
          >
            Password
          </button>
          <button
            class="flex-1 rounded-md py-2 text-xs font-semibold transition-all"
            :class="tab === 'magic' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
            type="button"
            @click="tab = 'magic'; magicState = 'idle'; magicError = ''"
          >
            Magic link
          </button>
        </div>

        <!-- Password tab -->
        <form v-if="tab === 'password'" class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink" for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300"
              autocomplete="email"
              type="email"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label class="text-sm font-medium text-ink" for="password">Password</label>
              <RouterLink class="text-xs font-medium text-signal hover:underline" to="/auth/forgot-password">
                Forgot password?
              </RouterLink>
            </div>
            <input
              id="password"
              v-model="form.password"
              class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300"
              autocomplete="current-password"
              type="password"
              placeholder="••••••••"
              required
            />
          </div>

          <Transition
            enter-active-class="transition-all duration-200"
            enter-from-class="opacity-0 -translate-y-1"
            leave-active-class="transition-all duration-150"
            leave-to-class="opacity-0"
          >
            <div
              v-if="error"
              class="flex items-start gap-2.5 rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800"
              role="alert"
            >
              <span class="mt-0.5 h-4 w-4 shrink-0 text-rose-500" aria-hidden="true"></span>
              {{ error }}
            </div>
          </Transition>

          <div
            v-if="mfaRequired"
            class="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm"
            role="alert"
          >
            <ShieldCheck class="mt-0.5 h-4 w-4 shrink-0 text-amber-600" aria-hidden="true" />
            <div>
              <p class="font-semibold text-amber-900">Two-factor authentication required</p>
              <p class="mt-0.5 text-xs leading-relaxed text-amber-800">
                Please contact your administrator or sign in from a trusted device.
              </p>
            </div>
          </div>

          <button
            class="focus-ring relative inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="!canSubmit"
            type="submit"
          >
            <Loader2 v-if="auth.isLoading" class="h-4 w-4 animate-spin" aria-hidden="true" />
            {{ auth.isLoading ? "Signing in…" : "Sign in" }}
          </button>
        </form>

        <!-- Magic link tab -->
        <div v-else class="space-y-4">
          <template v-if="magicState !== 'sent'">
            <p class="text-sm text-graphite">
              Enter your email and we'll send a one-click sign-in link. No password needed. Links expire in 15 minutes and work once only.
            </p>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink" for="magic-email">Email</label>
              <input
                id="magic-email"
                v-model="magicEmail"
                class="focus-ring h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300"
                autocomplete="email"
                type="email"
                placeholder="you@example.com"
                @keydown.enter.prevent="canSendMagic && sendMagicLink()"
              />
            </div>
            <div
              v-if="magicError"
              class="rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800"
              role="alert"
            >
              {{ magicError }}
            </div>
            <button
              class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="!canSendMagic"
              type="button"
              @click="sendMagicLink"
            >
              <Loader2 v-if="magicState === 'sending'" class="h-4 w-4 animate-spin" />
              <Mail v-else class="h-4 w-4" />
              {{ magicState === 'sending' ? 'Sending…' : 'Send magic link' }}
            </button>
          </template>

          <template v-else>
            <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-5 text-center">
              <Mail class="mx-auto h-8 w-8 text-emerald-500" />
              <p class="mt-3 font-semibold text-emerald-900">Check your inbox</p>
              <p class="mt-1 text-sm text-emerald-800">
                A sign-in link was sent to <strong>{{ magicEmail }}</strong>. Click it to sign in — it works once and expires in 15 minutes.
              </p>
            </div>
            <button
              class="w-full text-center text-xs text-graphite hover:text-ink hover:underline"
              type="button"
              @click="magicState = 'idle'; magicError = ''"
            >
              Try a different email
            </button>
          </template>
        </div>
      </div>

      <!-- Dev preview panel -->
      <div v-if="isDev" class="mt-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wider text-graphite">Preview workspace</p>
        <div class="mt-3 grid grid-cols-3 gap-2">
          <button
            v-for="roleName in previewRoles"
            :key="roleName"
            class="focus-ring h-9 rounded-lg border border-slate-200 bg-slate-50 px-2 text-xs font-semibold capitalize text-ink transition-colors hover:border-slate-300 hover:bg-white"
            type="button"
            @click="preview(roleName)"
          >
            {{ roleName }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
