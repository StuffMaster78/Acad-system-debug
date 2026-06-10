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
    <section class="bg-brand-800 text-white">
      <div class="mx-auto max-w-3xl px-6 py-20 text-center sm:py-28">
        <span class="inline-block rounded-full border border-white/20 bg-white/10 px-4 py-1 text-xs font-semibold uppercase tracking-widest mb-7">
          Now hiring writers
        </span>
        <h1 class="text-4xl font-bold leading-tight sm:text-5xl">
          Write. Get paid.<br class="hidden sm:block" /> Work on your terms.
        </h1>
        <p class="mt-5 text-base text-brand-200 max-w-lg mx-auto leading-relaxed">
          Join {{ brand }} and earn competitive rates on academic and professional writing — on a schedule that fits your life.
        </p>
        <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
          <RouterLink
            to="/auth/register"
            class="inline-flex items-center gap-2 rounded-lg bg-white px-7 py-3 text-sm font-semibold text-brand-800 hover:bg-slate-100 transition-colors"
          >
            Create your account <ArrowRight class="size-4" />
          </RouterLink>
          <RouterLink
            to="/auth/login"
            class="inline-flex items-center gap-2 rounded-lg border border-white/25 px-7 py-3 text-sm font-medium text-white hover:bg-white/10 transition-colors"
          >
            <LogIn class="size-4" /> Sign in
          </RouterLink>
        </div>
        <p class="mt-5 text-xs text-brand-300">
          Already applied?
          <RouterLink to="/apply" class="underline hover:text-white">Check your application</RouterLink>
        </p>
      </div>
    </section>

    <!-- Stats bar -->
    <section class="border-y border-slate-200 bg-white">
      <div class="mx-auto max-w-3xl grid grid-cols-2 divide-x divide-slate-200">
        <div class="px-6 py-5 text-center">
          <p class="text-xl font-semibold text-ink">48 hours</p>
          <p class="mt-0.5 text-xs text-graphite">typical pay cycle</p>
        </div>
        <div class="px-6 py-5 text-center">
          <p class="text-xl font-semibold text-ink">100% remote</p>
          <p class="mt-0.5 text-xs text-graphite">work from anywhere</p>
        </div>
      </div>
    </section>

    <!-- Benefits -->
    <section class="bg-slate-50 py-16 px-6">
      <div class="mx-auto max-w-4xl">
        <h2 class="text-xl font-semibold text-ink text-center mb-8">Why writers choose us</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="card in [
            { icon: DollarSign, title: 'Competitive pay', body: 'Rates scale with your level and performance. Top writers earn well above market rates.' },
            { icon: Clock,       title: 'Flexible hours',  body: 'Pick jobs that fit your timetable. No minimum hours — work as much or as little as you like.' },
            { icon: Zap,         title: 'Fast payments',   body: 'Reliable, on-time payouts via your preferred method. Track every cent in your dashboard.' },
            { icon: BookOpen,    title: 'Wide subjects',   body: 'Nursing, business, law, engineering, literature — write in the subjects you know best.' },
            { icon: Users,       title: 'Supportive team', body: 'A dedicated team and clear guidelines mean you spend your time writing, not troubleshooting.' },
            { icon: GraduationCap, title: 'Level up',      body: 'Our level system rewards quality. Better ratings unlock higher-paying jobs automatically.' },
          ]" :key="card.title"
            class="rounded-xl border border-slate-200 bg-white p-5 space-y-2.5"
          >
            <div class="flex size-8 items-center justify-center rounded-lg bg-slate-100">
              <component :is="card.icon" class="size-4 text-slate-600" />
            </div>
            <p class="text-sm font-semibold text-ink">{{ card.title }}</p>
            <p class="text-sm text-graphite leading-relaxed">{{ card.body }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="bg-white py-16 px-6">
      <div class="mx-auto max-w-2xl">
        <h2 class="text-xl font-semibold text-ink text-center mb-10">How it works</h2>
        <div class="space-y-6">
          <div v-for="(step, i) in [
            { title: 'Create your account',     body: 'Register with your email and verify it. Takes under two minutes.' },
            { title: 'Pass the vetting tests',  body: 'Complete a grammar quiz and a writing sample. Our editors review within 1–3 business days.' },
            { title: 'Start taking assignments', body: 'Once approved, browse open jobs, claim what fits your schedule, and start earning.' },
          ]" :key="step.title" class="flex gap-4 items-start">
            <div class="flex size-7 shrink-0 items-center justify-center rounded-full border-2 border-brand-700 text-brand-700 text-xs font-semibold mt-0.5">
              {{ i + 1 }}
            </div>
            <div>
              <p class="text-sm font-semibold text-ink">{{ step.title }}</p>
              <p class="mt-1 text-sm text-graphite leading-relaxed">{{ step.body }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="border-t border-slate-200 bg-slate-50 py-12 px-6 text-center">
      <h2 class="text-xl font-semibold text-ink">Ready to start?</h2>
      <p class="mt-2 text-sm text-graphite max-w-sm mx-auto">The application takes 5 minutes. Join the {{ brand }} team today.</p>
      <div class="mt-7 flex flex-col sm:flex-row items-center justify-center gap-3">
        <RouterLink
          to="/auth/register"
          class="inline-flex items-center gap-2 rounded-lg bg-brand-700 px-7 py-3 text-sm font-semibold text-white hover:bg-brand-800 transition-colors"
        >
          Apply now <ArrowRight class="size-4" />
        </RouterLink>
        <RouterLink to="/auth/login" class="text-sm text-graphite hover:text-ink transition-colors">
          Already have an account? Sign in
        </RouterLink>
      </div>
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
