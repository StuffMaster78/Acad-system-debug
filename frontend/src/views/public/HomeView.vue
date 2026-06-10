<script setup lang="ts">
import { computed, onMounted } from "vue";
import { RouterLink, useRouter } from "vue-router";
import {
  ArrowRight, BookOpen, CheckCircle2, Clock, DollarSign,
  GraduationCap, Lock, LogIn, Shield, Users, Zap,
} from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { roleHome } from "@/config/navigation";

const auth    = useAuthStore();
const portal  = usePortalContextStore();
const router  = useRouter();

const brand = computed(() => portal.branding?.brand_name || "Writers Creek");

onMounted(() => {
  if (auth.isAuthenticated && auth.role) {
    router.replace(roleHome[auth.role]);
  }
});
</script>

<template>

  <!-- ── WRITER PORTAL LANDING ─────────────────────────────────────────────── -->
  <template v-if="portal.surface === 'writer'">

    <!-- Hero -->
    <section class="relative overflow-hidden bg-gradient-to-br from-brand-800 via-brand-700 to-brand-600 text-white">
      <div class="absolute inset-0 opacity-10"
        style="background-image: radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 20%, white 1px, transparent 1px); background-size: 40px 40px;" />
      <div class="relative mx-auto max-w-4xl px-6 py-20 text-center sm:py-28">
        <span class="inline-block rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-medium tracking-wide mb-6">
          Now hiring writers
        </span>
        <h1 class="text-4xl font-extrabold leading-tight sm:text-5xl lg:text-6xl">
          Write. Get paid.<br />Work on your terms.
        </h1>
        <p class="mt-6 text-lg text-brand-100 max-w-xl mx-auto leading-relaxed">
          Join {{ brand }} and earn competitive rates on academic and professional writing assignments — on a schedule that works for you.
        </p>
        <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <RouterLink
            to="/auth/register"
            class="inline-flex items-center gap-2 rounded-xl bg-white px-7 py-3.5 text-base font-bold text-brand-700 shadow-lg hover:bg-brand-50 transition-colors"
          >
            Create your account <ArrowRight class="size-5" />
          </RouterLink>
          <RouterLink
            to="/auth/login"
            class="inline-flex items-center gap-2 rounded-xl border border-white/30 bg-white/10 px-7 py-3.5 text-base font-semibold text-white hover:bg-white/20 transition-colors"
          >
            <LogIn class="size-5" /> Sign in
          </RouterLink>
        </div>
        <p class="mt-6 text-sm text-brand-200">
          Already applied?
          <RouterLink to="/apply" class="underline hover:text-white">Check your application status</RouterLink>
        </p>
      </div>
    </section>

    <!-- Stats bar -->
    <section class="border-y border-slate-200 bg-white">
      <div class="mx-auto max-w-4xl grid grid-cols-3 divide-x divide-slate-200">
        <div class="px-6 py-6 text-center">
          <p class="text-3xl font-extrabold text-brand-700">$10–$25</p>
          <p class="mt-1 text-sm text-graphite">per page rate</p>
        </div>
        <div class="px-6 py-6 text-center">
          <p class="text-3xl font-extrabold text-brand-700">48h</p>
          <p class="mt-1 text-sm text-graphite">typical pay cycle</p>
        </div>
        <div class="px-6 py-6 text-center">
          <p class="text-3xl font-extrabold text-brand-700">100%</p>
          <p class="mt-1 text-sm text-graphite">remote work</p>
        </div>
      </div>
    </section>

    <!-- Benefits -->
    <section class="bg-slate-50 py-16 px-6">
      <div class="mx-auto max-w-4xl">
        <h2 class="text-2xl font-bold text-ink text-center mb-10">Why writers choose us</h2>
        <div class="grid gap-6 sm:grid-cols-3">
          <div class="rounded-2xl bg-white border border-slate-200 p-6 space-y-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-brand-50">
              <DollarSign class="size-5 text-brand-700" />
            </div>
            <h3 class="font-semibold text-ink">Competitive pay</h3>
            <p class="text-sm text-graphite leading-relaxed">Rates scale with your level and performance. Top writers earn significantly above market.</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-200 p-6 space-y-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-brand-50">
              <Clock class="size-5 text-brand-700" />
            </div>
            <h3 class="font-semibold text-ink">Flexible schedule</h3>
            <p class="text-sm text-graphite leading-relaxed">Pick the jobs that fit your timetable. No minimum hours — work as much or as little as you like.</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-200 p-6 space-y-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-brand-50">
              <Zap class="size-5 text-brand-700" />
            </div>
            <h3 class="font-semibold text-ink">Fast payments</h3>
            <p class="text-sm text-graphite leading-relaxed">Reliable, on-time payouts via your preferred method. Track every cent in your earnings dashboard.</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-200 p-6 space-y-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-brand-50">
              <BookOpen class="size-5 text-brand-700" />
            </div>
            <h3 class="font-semibold text-ink">Diverse subjects</h3>
            <p class="text-sm text-graphite leading-relaxed">Nursing, business, law, engineering, literature — write in the subjects you know best.</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-200 p-6 space-y-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-brand-50">
              <Users class="size-5 text-brand-700" />
            </div>
            <h3 class="font-semibold text-ink">Supportive team</h3>
            <p class="text-sm text-graphite leading-relaxed">A dedicated support team and clear guidelines mean you spend time writing, not troubleshooting.</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-200 p-6 space-y-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-brand-50">
              <GraduationCap class="size-5 text-brand-700" />
            </div>
            <h3 class="font-semibold text-ink">Level up over time</h3>
            <p class="text-sm text-graphite leading-relaxed">Our level system rewards quality. Better ratings unlock higher-paying jobs automatically.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="bg-white py-16 px-6">
      <div class="mx-auto max-w-3xl">
        <h2 class="text-2xl font-bold text-ink text-center mb-12">How it works</h2>
        <div class="relative">
          <!-- Connector line -->
          <div class="absolute left-5 top-8 bottom-8 w-px bg-slate-200 hidden sm:block" />
          <div class="space-y-8">
            <div class="flex gap-5 items-start">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-white font-bold text-sm z-10">1</div>
              <div class="pt-1.5">
                <h3 class="font-semibold text-ink">Create your account</h3>
                <p class="mt-1 text-sm text-graphite">Register with your email, set a password, and verify your account. Takes under two minutes.</p>
              </div>
            </div>
            <div class="flex gap-5 items-start">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-white font-bold text-sm z-10">2</div>
              <div class="pt-1.5">
                <h3 class="font-semibold text-ink">Pass the vetting tests</h3>
                <p class="mt-1 text-sm text-graphite">Complete a grammar quiz and a writing sample. Our editors review your work within 1–3 business days.</p>
              </div>
            </div>
            <div class="flex gap-5 items-start">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-white font-bold text-sm z-10">3</div>
              <div class="pt-1.5">
                <h3 class="font-semibold text-ink">Start taking assignments</h3>
                <p class="mt-1 text-sm text-graphite">Once approved, browse available jobs, claim what fits your schedule, and start earning immediately.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="bg-brand-700 py-14 px-6 text-center text-white">
      <h2 class="text-2xl font-bold">Ready to start earning?</h2>
      <p class="mt-3 text-brand-200 text-sm max-w-md mx-auto">Join hundreds of writers already earning with {{ brand }}. The application takes 5 minutes.</p>
      <div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
        <RouterLink
          to="/auth/register"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-base font-bold text-brand-700 hover:bg-brand-50 transition-colors shadow-lg"
        >
          Apply now <ArrowRight class="size-5" />
        </RouterLink>
        <RouterLink
          to="/auth/login"
          class="inline-flex items-center gap-2 text-sm font-medium text-brand-200 hover:text-white transition-colors"
        >
          Already have an account? Sign in
        </RouterLink>
      </div>
    </section>

  </template>

  <!-- ── STAFF PORTAL LANDING ───────────────────────────────────────────────── -->
  <template v-else-if="portal.surface === 'staff'">
    <div class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-16 bg-slate-50">
      <div class="w-full max-w-sm space-y-8 text-center">

        <!-- Logo / initials -->
        <div class="flex flex-col items-center gap-3">
          <div class="flex size-16 items-center justify-center rounded-2xl bg-brand-700 text-white text-xl font-bold shadow-lg">
            {{ brand.slice(0, 2).toUpperCase() }}
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest text-graphite mb-1">Staff Portal</p>
            <h1 class="text-2xl font-bold text-ink">{{ brand }}</h1>
          </div>
        </div>

        <!-- Info cards -->
        <div class="space-y-3 text-left">
          <div class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4">
            <Shield class="size-5 text-brand-700 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm font-semibold text-ink">Restricted access</p>
              <p class="text-xs text-graphite mt-0.5">This portal is for authorised staff only. Accounts are created by your administrator.</p>
            </div>
          </div>
          <div class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4">
            <CheckCircle2 class="size-5 text-brand-700 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm font-semibold text-ink">Operations, support & editorial</p>
              <p class="text-xs text-graphite mt-0.5">Manage orders, writers, support tickets, and content from one unified workspace.</p>
            </div>
          </div>
        </div>

        <!-- Sign in CTA -->
        <RouterLink
          to="/auth/login"
          class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-brand-700 py-3.5 text-sm font-bold text-white shadow-sm hover:bg-brand-800 transition-colors"
        >
          <Lock class="size-4" /> Sign in to your account
        </RouterLink>

        <p class="text-xs text-slate-400">
          Need access? Contact your system administrator.
        </p>
      </div>
    </div>
  </template>

  <!-- ── FALLBACK (client / unresolved surface) ─────────────────────────────── -->
  <template v-else>
    <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-12">
      <div class="w-full max-w-sm text-center space-y-6">
        <div v-if="portal.branding" class="flex flex-col items-center gap-3">
          <img v-if="portal.branding.logo_url" :src="portal.branding.logo_url" :alt="brand" class="h-12 w-auto object-contain" />
          <div v-else class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-700 text-white text-base font-bold">
            {{ brand.slice(0, 2).toUpperCase() }}
          </div>
          <p class="text-lg font-semibold text-ink">{{ brand }}</p>
        </div>
        <div>
          <h1 class="text-2xl font-semibold text-ink">Welcome back</h1>
          <p class="mt-2 text-sm text-graphite">Sign in to open your workspace.</p>
        </div>
        <RouterLink
          to="/auth/login"
          class="inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-brand-700 text-sm font-bold text-white hover:bg-brand-800 transition-colors"
        >
          <LogIn class="size-4" /> Sign in
        </RouterLink>
      </div>
    </div>
  </template>

</template>
