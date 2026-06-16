<script setup lang="ts">
import { computed, onMounted } from "vue";
import { RouterLink, useRouter } from "vue-router";
import {
  ArrowRight, BookOpen, CheckCircle2, Clock,
  DollarSign, GraduationCap, LogIn, Shield, Users, Zap,
} from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { roleHome } from "@/config/navigation";

const auth   = useAuthStore();
const portal = usePortalContextStore();
const router = useRouter();

const brand = computed(() => portal.branding?.brand_name || "Writers Creek");

onMounted(() => {
  if (auth.isAuthenticated && auth.role) {
    router.replace(roleHome[auth.role]);
  }
});
</script>

<template>

  <!-- ── WRITER PORTAL ──────────────────────────────────────────────────────── -->
  <template v-if="portal.surface === 'writer'">

    <!-- Hero -->
    <section class="relative bg-slate-900 text-white overflow-hidden">
      <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.025)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.025)_1px,transparent_1px)] bg-[size:44px_44px]" />
      <div class="relative mx-auto max-w-4xl px-6 py-24 text-center sm:py-36">
        <span class="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/8 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest mb-8 text-slate-300">
          <span class="size-1.5 rounded-full bg-emerald-400" />
          Academic writing platform
        </span>
        <h1 class="text-4xl font-extrabold leading-tight tracking-tight sm:text-6xl">
          Write at the<br class="hidden sm:block" />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">highest standard.</span>
        </h1>
        <p class="mt-6 text-base text-slate-400 max-w-xl mx-auto leading-relaxed sm:text-lg">
          {{ brand }} is a selective academic writing network. Competitive per-page rates, flexible assignments, and reliable bi-weekly payouts — for writers who take their craft seriously.
        </p>
        <div class="mt-10">
          <RouterLink
            to="/auth/login"
            class="inline-flex items-center gap-2 rounded-lg bg-white px-8 py-3.5 text-sm font-bold text-slate-900 hover:bg-slate-100 transition-colors shadow-sm"
          >
            <LogIn class="size-4" /> Sign in to your workspace
          </RouterLink>
        </div>
        <p class="mt-5 text-xs text-slate-500">
          Access is by invitation. Contact your administrator if you need an account.
        </p>
      </div>
    </section>

    <!-- Stats bar -->
    <section class="border-y border-slate-200 bg-white">
      <div class="mx-auto max-w-4xl grid grid-cols-2 divide-x divide-slate-200 sm:grid-cols-4">
        <div v-for="stat in [
          { value: 'Bi-weekly',       label: 'Payout cycle' },
          { value: '100% remote',     label: 'Work from anywhere' },
          { value: '4 writer levels', label: 'Advancement path' },
          { value: 'Academic focus',  label: 'Specialist niche' },
        ]" :key="stat.label" class="px-6 py-5 text-center">
          <p class="text-base font-bold text-ink sm:text-lg">{{ stat.value }}</p>
          <p class="mt-0.5 text-xs text-graphite">{{ stat.label }}</p>
        </div>
      </div>
    </section>

    <!-- Earnings / rate tiers -->
    <section class="bg-slate-50 py-16 px-6">
      <div class="mx-auto max-w-3xl">
        <div class="text-center mb-10">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Compensation</p>
          <h2 class="text-2xl font-bold text-ink">Transparent, competitive rates</h2>
          <p class="mt-2 text-sm text-graphite max-w-md mx-auto">Your per-page rate rises as you advance through writer levels. Quality assignments unlock higher tiers automatically.</p>
        </div>
        <div class="grid gap-3 sm:grid-cols-4">
          <div v-for="tier in [
            { level: 'Entry',    rate: '$4–6',   badge: 'bg-slate-100 text-slate-700' },
            { level: 'Standard', rate: '$6–9',   badge: 'bg-sky-50 text-sky-700' },
            { level: 'Senior',   rate: '$9–13',  badge: 'bg-indigo-50 text-indigo-700' },
            { level: 'Expert',   rate: '$13–18', badge: 'bg-amber-50 text-amber-700' },
          ]" :key="tier.level" class="rounded-xl border border-slate-200 bg-white p-5 text-center space-y-2">
            <span class="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="tier.badge">{{ tier.level }}</span>
            <p class="text-2xl font-extrabold text-ink">{{ tier.rate }}</p>
            <p class="text-xs text-graphite">per page</p>
          </div>
        </div>
        <p class="mt-4 text-center text-xs text-slate-400">Base rates. Actual rates vary by order type, deadline, and academic level.</p>
      </div>
    </section>

    <!-- Benefits -->
    <section class="bg-white py-16 px-6">
      <div class="mx-auto max-w-4xl">
        <div class="text-center mb-10">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Why writers choose us</p>
          <h2 class="text-2xl font-bold text-ink">Built for professional writers</h2>
        </div>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="card in [
            { icon: DollarSign,    title: 'Rates that reward quality', body: 'Every positive review and on-time delivery moves you closer to the next pay tier.' },
            { icon: Clock,         title: 'Work on your schedule',     body: 'Pick assignments that fit your timetable. No minimum hours, no fixed shifts.' },
            { icon: Zap,           title: 'Reliable bi-weekly pay',    body: 'Payouts processed every two weeks, on time. Track your full earnings history in the dashboard.' },
            { icon: BookOpen,      title: 'Academic specialisation',   body: 'Nursing, law, business, STEM, humanities — write in the fields where your expertise stands out.' },
            { icon: GraduationCap, title: 'Clear advancement path',    body: 'Four writer levels. Move up based on performance metrics, not time served.' },
            { icon: Users,         title: 'Dedicated support team',    body: 'A responsive team handles disputes, client clarifications, and platform issues — so you focus on writing.' },
          ]" :key="card.title" class="flex gap-4 rounded-xl border border-slate-200 bg-slate-50/60 p-5">
            <div class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-white border border-slate-200 shadow-sm">
              <component :is="card.icon" class="size-4 text-slate-600" />
            </div>
            <div>
              <p class="text-sm font-semibold text-ink">{{ card.title }}</p>
              <p class="mt-1 text-xs text-graphite leading-relaxed">{{ card.body }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works (invitation-only framing) -->
    <section class="bg-slate-50 border-t border-slate-200 py-16 px-6">
      <div class="mx-auto max-w-2xl">
        <div class="text-center mb-10">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Getting started</p>
          <h2 class="text-2xl font-bold text-ink">From invitation to first assignment</h2>
        </div>
        <div class="space-y-5">
          <div v-for="(s, i) in [
            { title: 'Receive your invitation',    body: 'Our team reaches out directly. You\'ll receive account credentials and onboarding instructions by email.' },
            { title: 'Complete the vetting tests', body: 'A grammar assessment and a writing sample reviewed by our editorial team. Results within 1–3 business days.' },
            { title: 'Start claiming assignments', body: 'Once approved, browse the available order pool, claim what fits your expertise, and begin earning.' },
          ]" :key="s.title" class="flex gap-4 items-start">
            <div class="flex size-8 shrink-0 items-center justify-center rounded-full bg-slate-900 text-white text-xs font-bold mt-0.5">{{ i + 1 }}</div>
            <div class="pt-0.5">
              <p class="text-sm font-semibold text-ink">{{ s.title }}</p>
              <p class="mt-1 text-sm text-graphite leading-relaxed">{{ s.body }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="bg-slate-900 py-14 px-6 text-center">
      <h2 class="text-xl font-bold text-white">Already part of the team?</h2>
      <p class="mt-2 text-sm text-slate-400 max-w-xs mx-auto">Sign in to access your workspace, view open assignments, and track your earnings.</p>
      <RouterLink
        to="/auth/login"
        class="mt-8 inline-flex items-center gap-2 rounded-lg bg-white px-8 py-3.5 text-sm font-bold text-slate-900 hover:bg-slate-100 transition-colors"
      >
        <LogIn class="size-4" /> Sign in
      </RouterLink>
    </section>

  </template>

  <!-- ── STAFF PORTAL ───────────────────────────────────────────────────────── -->
  <template v-else-if="portal.surface === 'staff'">
    <div class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-16 bg-white">
      <div class="w-full max-w-xs space-y-8 text-center">

        <div class="flex flex-col items-center gap-3">
          <div class="flex size-12 items-center justify-center rounded-xl bg-ink text-white text-sm font-bold tracking-tight">
            {{ brand.slice(0, 2).toUpperCase() }}
          </div>
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-widest text-graphite">Staff Portal</p>
            <h1 class="mt-1 text-xl font-semibold text-ink">{{ brand }}</h1>
          </div>
        </div>

        <div class="space-y-2 text-left">
          <div class="flex items-start gap-3 rounded-lg border border-slate-200 p-4">
            <Shield class="size-4 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm font-medium text-ink">Authorised staff only</p>
              <p class="text-xs text-graphite mt-0.5 leading-relaxed">Accounts are created by your administrator. Contact them if you need access.</p>
            </div>
          </div>
          <div class="flex items-start gap-3 rounded-lg border border-slate-200 p-4">
            <CheckCircle2 class="size-4 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm font-medium text-ink">Operations, support & editorial</p>
              <p class="text-xs text-graphite mt-0.5 leading-relaxed">Manage orders, writers, support tickets, and content from one workspace.</p>
            </div>
          </div>
        </div>

        <RouterLink
          to="/auth/login"
          class="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-ink py-3 text-sm font-semibold text-white hover:bg-graphite transition-colors"
        >
          <LogIn class="size-4" /> Sign in
        </RouterLink>

      </div>
    </div>
  </template>

  <!-- ── FALLBACK ────────────────────────────────────────────────────────────── -->
  <template v-else>
    <div class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-12 bg-white">
      <div class="w-full max-w-xs text-center space-y-6">
        <div v-if="portal.branding" class="flex flex-col items-center gap-3">
          <img v-if="portal.branding.logo_url" :src="portal.branding.logo_url" :alt="brand" class="h-10 w-auto object-contain" />
          <div v-else class="flex h-10 w-10 items-center justify-center rounded-lg bg-ink text-white text-sm font-bold">
            {{ brand.slice(0, 2).toUpperCase() }}
          </div>
          <p class="text-sm font-medium text-ink">{{ brand }}</p>
        </div>
        <div>
          <h1 class="text-xl font-semibold text-ink">Welcome back</h1>
          <p class="mt-1.5 text-sm text-graphite">Sign in to open your workspace.</p>
        </div>
        <RouterLink
          to="/auth/login"
          class="inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-ink text-sm font-semibold text-white hover:bg-graphite transition-colors"
        >
          <LogIn class="size-4" /> Sign in
        </RouterLink>
      </div>
    </div>
  </template>

</template>
